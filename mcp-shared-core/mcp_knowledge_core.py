#!/usr/bin/env python3
"""
MCP Knowledge Server Core Infrastructure
Shared components for organizational MCP servers with document ingestion,
vector database, and knowledge retrieval capabilities.
"""

import json
import asyncio
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sqlite3

# Document processing
import fitz  # PyMuPDF for PDF processing
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# MCP and HTTP infrastructure
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document ingestion and text extraction"""
    
    def __init__(self, supported_formats: List[str] = None):
        self.supported_formats = supported_formats or ['.pdf', '.txt', '.md']
    
    async def extract_text_from_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF with page-level chunking"""
        chunks = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text.strip():  # Only add non-empty pages
                    chunks.append({
                        'text': text,
                        'page': page_num + 1,
                        'source': str(file_path),
                        'chunk_type': 'page'
                    })
            doc.close()
            return chunks
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return []
    
    async def extract_text_from_txt(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple chunking by paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            chunks = []
            for i, paragraph in enumerate(paragraphs):
                chunks.append({
                    'text': paragraph,
                    'chunk_id': i + 1,
                    'source': str(file_path),
                    'chunk_type': 'paragraph'
                })
            return chunks
        except Exception as e:
            logger.error(f"Error extracting text from TXT {file_path}: {e}")
            return []
    
    async def process_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a document and return text chunks"""
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return await self.extract_text_from_pdf(file_path)
        elif file_extension in ['.txt', '.md']:
            return await self.extract_text_from_txt(file_path)
        else:
            logger.warning(f"Unsupported file format: {file_extension}")
            return []

class VectorDatabase:
    """Manages vector embeddings and similarity search"""
    
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": f"Knowledge base for {collection_name}"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        return self.embedding_model.encode(text).tolist()
    
    async def add_documents(self, chunks: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> int:
        """Add document chunks to the vector database"""
        if not chunks:
            return 0
        
        documents = []
        embeddings = []
        ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            text = chunk['text']
            if len(text.strip()) < 10:  # Skip very short chunks
                continue
            
            # Generate unique ID
            chunk_id = hashlib.md5(
                f"{chunk.get('source', '')}{i}{text[:100]}".encode()
            ).hexdigest()
            
            # Generate embedding
            embedding = self.generate_embedding(text)
              # Prepare metadata - ensure all values are proper types, no None values
            chunk_metadata = {
                'source': str(chunk.get('source', '')),
                'chunk_type': str(chunk.get('chunk_type', 'unknown')),
                'timestamp': datetime.now().isoformat(),
                'text_length': len(text)
            }
            
            # Add optional fields only if they have valid values
            if chunk.get('page') is not None:
                chunk_metadata['page'] = int(chunk.get('page'))
            
            if chunk.get('chunk_id') is not None:
                chunk_metadata['chunk_id'] = str(chunk.get('chunk_id'))
            
            # Add custom metadata if provided, ensuring proper types
            if metadata:
                for key, value in metadata.items():
                    if value is not None:
                        # Convert to ChromaDB-compatible types
                        if isinstance(value, (str, int, float, bool)):
                            chunk_metadata[key] = value
                        else:
                            chunk_metadata[key] = str(value)
            
            documents.append(text)
            embeddings.append(embedding)
            ids.append(chunk_id)
            metadatas.append(chunk_metadata)
        
        # Add to ChromaDB
        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} chunks to vector database")
            return len(documents)
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {e}")
            return 0
    
    async def search(self, query: str, top_k: int = 5, filter_metadata: Dict = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Format results
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'id': results['ids'][0][i]
                    }
                    search_results.append(result)
            
            return search_results
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'persist_directory': str(self.persist_directory)
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

class DocumentDatabase:
    """SQLite database for document metadata and management"""
    
    def __init__(self, db_path: str = "./documents.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_processed TIMESTAMP,
                chunk_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                metadata TEXT,
                domain TEXT,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                operation TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                details TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, filename: str, file_path: str, file_hash: str, 
                    file_size: int, domain: str = None, tags: List[str] = None, 
                    metadata: Dict = None) -> int:
        """Add a document record to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO documents 
                (filename, file_path, file_hash, file_size, domain, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                filename, 
                str(file_path), 
                file_hash, 
                file_size,
                domain,
                json.dumps(tags) if tags else None,
                json.dumps(metadata) if metadata else None
            ))
            
            document_id = cursor.lastrowid
            conn.commit()
            return document_id
        except sqlite3.IntegrityError:
            logger.warning(f"Document with hash {file_hash} already exists")
            return -1
        finally:
            conn.close()
    
    def update_document_status(self, document_id: int, status: str, chunk_count: int = None):
        """Update document processing status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if chunk_count is not None:
            cursor.execute('''
                UPDATE documents 
                SET status = ?, chunk_count = ?, last_processed = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, chunk_count, document_id))
        else:
            cursor.execute('''
                UPDATE documents 
                SET status = ?, last_processed = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, document_id))
        
        conn.commit()
        conn.close()
    
    def get_documents(self, domain: str = None, status: str = None) -> List[Dict[str, Any]]:
        """Get documents from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM documents WHERE 1=1"
        params = []
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY upload_date DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        columns = [description[0] for description in cursor.description]
        documents = []
        for row in rows:
            doc = dict(zip(columns, row))
            # Parse JSON fields
            if doc['tags']:
                doc['tags'] = json.loads(doc['tags'])
            if doc['metadata']:
                doc['metadata'] = json.loads(doc['metadata'])
            documents.append(doc)
        
        conn.close()
        return documents

class BaseKnowledgeServer:
    """Base class for specialized MCP knowledge servers"""
    
    def __init__(self, server_name: str, domain: str, port: int = 8000):
        self.server_name = server_name
        self.domain = domain
        self.port = port
        
        # Initialize components
        self.app = FastAPI(title=f"MCP {server_name} Server", version="1.0.0")
        self.document_processor = DocumentProcessor()
        self.vector_db = VectorDatabase(collection_name=f"{domain}_knowledge")
        self.doc_db = DocumentDatabase(f"./{domain}_documents.db")
        
        # Setup middleware and routes
        self.setup_middleware()
        self.setup_base_routes()
        self.setup_mcp_routes()
        
        # Store for active SSE connections
        self.clients = {}
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_base_routes(self):
        """Setup basic HTTP routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": f"MCP {self.server_name} Knowledge Server",
                "domain": self.domain,
                "version": "1.0.0",
                "protocol": "HTTP"
            }
        
        @self.app.get("/health")
        async def health():
            stats = self.vector_db.get_collection_stats()
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "server": self.server_name,
                "domain": self.domain,
                "vector_db_stats": stats
            }
        
        @self.app.post("/upload")
        async def upload_document(
            file: UploadFile = File(...),
            domain: str = None,
            tags: str = None
        ):
            """Upload and process a document"""
            return await self.handle_document_upload(file, domain, tags)
        
        @self.app.get("/documents")
        async def list_documents(domain: str = None, status: str = None):
            """List documents in the knowledge base"""
            return self.doc_db.get_documents(domain=domain, status=status)
        
        @self.app.get("/search")
        async def search_knowledge(q: str, limit: int = 5):
            """Search the knowledge base"""
            results = await self.vector_db.search(q, top_k=limit)
            return {"query": q, "results": results}
    
    def setup_mcp_routes(self):
        """Setup MCP protocol routes"""
        
        @self.app.post("/mcp")
        async def mcp_endpoint(request: Request):
            """Main MCP JSON-RPC endpoint"""
            try:
                body = await request.json()
                response = await self.handle_mcp_request(body)
                return JSONResponse(content=response)
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                    },
                    status_code=500
                )
        
        @self.app.get("/mcp/sse")
        async def sse_endpoint():
            """SSE endpoint for MCP streaming"""
            client_id = f"mcp_client_{int(datetime.now().timestamp())}_{id(object())}"
            return StreamingResponse(
                self.sse_generator(client_id),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
    
    async def handle_document_upload(self, file: UploadFile, domain: str = None, tags: str = None):
        """Handle document upload and processing"""
        try:
            # Create uploads directory
            upload_dir = Path("./uploads")
            upload_dir.mkdir(exist_ok=True)
            
            # Save uploaded file
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Calculate file hash
            file_hash = hashlib.md5(content).hexdigest()
            file_size = len(content)
            
            # Parse tags
            tag_list = None
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",")]
            
            # Add to document database
            doc_id = self.doc_db.add_document(
                filename=file.filename,
                file_path=str(file_path),
                file_hash=file_hash,
                file_size=file_size,
                domain=domain or self.domain,
                tags=tag_list
            )
            
            if doc_id == -1:
                return {"error": "Document already exists", "status": "duplicate"}
            
            # Process document asynchronously
            asyncio.create_task(self.process_document_async(doc_id, file_path))
            
            return {
                "message": "Document uploaded successfully",
                "document_id": doc_id,
                "filename": file.filename,
                "status": "processing"
            }
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def process_document_async(self, doc_id: int, file_path: Path):
        """Process document in background"""
        try:
            # Extract text chunks
            chunks = await self.document_processor.process_document(file_path)
            
            if not chunks:
                self.doc_db.update_document_status(doc_id, "failed", 0)
                return
            
            # Add to vector database
            chunk_count = await self.vector_db.add_documents(
                chunks, 
                metadata={"document_id": doc_id, "domain": self.domain}
            )
            
            # Update status
            self.doc_db.update_document_status(doc_id, "completed", chunk_count)
            logger.info(f"Successfully processed document {doc_id} with {chunk_count} chunks")
            
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {e}")
            self.doc_db.update_document_status(doc_id, "failed", 0)
    
    async def handle_mcp_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC requests"""
        if not isinstance(request_data, dict):
            return {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": "Invalid Request"}
            }
        
        jsonrpc = request_data.get("jsonrpc")
        method = request_data.get("method")
        request_id = request_data.get("id")
        params = request_data.get("params", {})
        
        if jsonrpc != "2.0":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32600, "message": "Invalid Request"}
            }
        
        try:
            if method == "initialize":
                return self.handle_initialize(request_id)
            elif method == "tools/list":
                return self.handle_tools_list(request_id)
            elif method == "tools/call":
                return await self.handle_tools_call(request_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": "Method not found"}
                }
        except Exception as e:
            logger.error(f"Error in MCP method {method}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
    
    def handle_initialize(self, request_id: str) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {"listChanged": False},
                    "experimental": {
                        "http": True,
                        "sse": True
                    }
                },
                "serverInfo": {
                    "name": f"mcp-{self.domain}-server",
                    "version": "1.0.0",
                    "description": f"Knowledge server for {self.domain} domain"
                }
            }
        }
    
    def handle_tools_list(self, request_id: str) -> Dict[str, Any]:
        """Handle tools/list request - to be overridden by subclasses"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.get_available_tools()
            }
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools - to be overridden by subclasses"""
        return [
            {
                "name": "search_knowledge",
                "description": f"Search the {self.domain} knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Maximum number of results", "default": 5}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_documents",
                "description": f"List documents in the {self.domain} knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "description": "Filter by status"}
                    }
                }
            }
        ]
    
    async def handle_tools_call(self, request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "search_knowledge":
                return await self.search_knowledge_tool(request_id, arguments)
            elif tool_name == "list_documents":
                return await self.list_documents_tool(request_id, arguments)
            else:
                # Allow subclasses to handle additional tools
                return await self.handle_custom_tool(request_id, tool_name, arguments)
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Error in tool {tool_name}: {str(e)}"}
            }
    
    async def search_knowledge_tool(self, request_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search knowledge base tool"""
        query = arguments.get("query")
        limit = arguments.get("limit", 5)
        
        if not query:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Missing required parameter 'query'"}
            }
        
        results = await self.vector_db.search(query, top_k=limit)
        
        # Format results for MCP response
        content_parts = []
        if results:
            content_parts.append({
                "type": "text",
                "text": f"Found {len(results)} results for query: '{query}'\n"
            })
            
            for i, result in enumerate(results, 1):
                similarity = result.get('similarity_score', 0)
                source = result.get('metadata', {}).get('source', 'Unknown')
                page = result.get('metadata', {}).get('page')
                
                location_info = f" (Page {page})" if page else ""
                content_parts.append({
                    "type": "text",
                    "text": f"\n**Result {i}** (Similarity: {similarity:.2f})\n"
                           f"Source: {source}{location_info}\n"
                           f"Content: {result['text'][:500]}...\n"
                })
        else:
            content_parts.append({
                "type": "text",
                "text": f"No results found for query: '{query}'"
            })
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": content_parts,
                "isError": False
            }
        }
    
    async def list_documents_tool(self, request_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List documents tool"""
        status = arguments.get("status")
        documents = self.doc_db.get_documents(domain=self.domain, status=status)
        
        content_parts = []
        if documents:
            content_parts.append({
                "type": "text",
                "text": f"Found {len(documents)} documents in {self.domain} knowledge base:\n"
            })
            
            for doc in documents:
                content_parts.append({
                    "type": "text",
                    "text": f"• {doc['filename']} - Status: {doc['status']} - Chunks: {doc['chunk_count']} - Upload: {doc['upload_date']}\n"
                })
        else:
            content_parts.append({
                "type": "text",
                "text": f"No documents found in {self.domain} knowledge base"
            })
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": content_parts,
                "isError": False
            }
        }
    
    async def handle_custom_tool(self, request_id: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle custom tools - to be overridden by subclasses"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
        }
    
    async def sse_generator(self, client_id: str):
        """Generate Server-Sent Events for MCP streaming"""
        if client_id not in self.clients:
            self.clients[client_id] = asyncio.Queue()
        
        try:
            # Send initial connection event
            init_response = self.handle_initialize("init")
            yield f"data: {json.dumps(init_response)}\n\n"
            
            while True:
                try:
                    # Wait for events with timeout
                    event_data = await asyncio.wait_for(
                        self.clients[client_id].get(), 
                        timeout=30.0
                    )
                    
                    yield f"data: {json.dumps(event_data)}\n\n"
                    
                    if event_data.get("completed", False):
                        break
                        
                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"data: {json.dumps({'event': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    
        except Exception as e:
            logger.error(f"SSE error for client {client_id}: {e}")
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
    
    def run(self, host: str = "0.0.0.0", port: int = None):
        """Run the server"""
        actual_port = port or self.port
        print(f"Starting MCP {self.server_name} Knowledge Server...")
        print(f"Domain: {self.domain}")
        print(f"Server will be available at:")
        print(f"  - Main endpoint: http://localhost:{actual_port}/mcp")
        print(f"  - Health check: http://localhost:{actual_port}/health")
        print(f"  - SSE endpoint: http://localhost:{actual_port}/mcp/sse")
        print(f"  - Upload endpoint: http://localhost:{actual_port}/upload")
        print(f"  - Documentation: http://localhost:{actual_port}/docs")
        
        uvicorn.run(
            self.app,
            host=host,
            port=actual_port,
            log_level="info"
        )
