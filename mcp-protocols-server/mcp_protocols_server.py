#!/usr/bin/env python3
"""
Protocol Knowledge MCP Server

A specialized MCP server for hardware protocol knowledge management.
Supports PCIE, UCIE, Ethernet, USB, SATA, NVMe, and other protocol specifications.

Features:
- PDF specification document ingestion
- Protocol comparison and analysis
- Technical detail extraction
- Standards compliance checking
- Vector-based semantic search

Usage:
    python mcp_protocols_server.py
"""

import asyncio
import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import sys
sys.path.append(str(Path(__file__).parent.parent / "mcp-shared-core"))
from mcp_knowledge_core import BaseKnowledgeServer, DocumentProcessor, VectorDatabase, DocumentDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolKnowledgeServer(BaseKnowledgeServer):
    """
    Specialized MCP server for protocol knowledge management.
    """
    def __init__(self, data_dir: str = "data/protocols", port: int = 8000):
        super().__init__(
            server_name="Protocol Knowledge Server",
            domain="protocols",
            port=port
        )
        self.data_dir = data_dir
        
        # Protocol-specific categories
        self.protocol_categories = {
            "pcie": "PCI Express specifications and standards",
            "ucie": "Universal Chiplet Interconnect Express",
            "ethernet": "Ethernet networking protocols",
            "usb": "Universal Serial Bus specifications",
            "sata": "Serial ATA storage interface",
            "nvme": "NVM Express storage protocol",
            "ddr": "DDR memory specifications",
            "thunderbolt": "Thunderbolt interface standards",
            "displayport": "DisplayPort video interface",
            "hdmi": "HDMI multimedia interface"
        }
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Define MCP tools specific to protocol knowledge.
        """
        base_tools = super().get_mcp_tools()
        
        protocol_tools = [
            {
                "name": "search_protocol_specs",
                "description": "Search protocol specifications and standards documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for protocol specifications"
                        },
                        "protocol_type": {
                            "type": "string",
                            "enum": list(self.protocol_categories.keys()) + ["all"],
                            "description": "Specific protocol type to search within"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 5,
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "compare_protocols",
                "description": "Compare features and specifications between different protocols",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "protocol1": {
                            "type": "string",
                            "description": "First protocol to compare"
                        },
                        "protocol2": {
                            "type": "string",
                            "description": "Second protocol to compare"
                        },
                        "comparison_aspects": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific aspects to compare (e.g., speed, power, compatibility)"
                        }
                    },
                    "required": ["protocol1", "protocol2"]
                }
            },
            {
                "name": "get_protocol_versions",
                "description": "Get version history and evolution of a specific protocol",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "protocol": {
                            "type": "string",
                            "description": "Protocol name to get version information for"
                        }
                    },
                    "required": ["protocol"]
                }
            },
            {
                "name": "analyze_compatibility",
                "description": "Analyze compatibility between protocol versions or different protocols",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_protocol": {
                            "type": "string",
                            "description": "Source protocol or version"
                        },
                        "target_protocol": {
                            "type": "string",
                            "description": "Target protocol or version"
                        }
                    },
                    "required": ["source_protocol", "target_protocol"]
                }
            }
        ]
        
        return base_tools + protocol_tools
    
    async def handle_mcp_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP tool calls specific to protocol knowledge.
        """
        if method == "search_protocol_specs":
            return await self._search_protocol_specs(params)
        elif method == "compare_protocols":
            return await self._compare_protocols(params)
        elif method == "get_protocol_versions":
            return await self._get_protocol_versions(params)
        elif method == "analyze_compatibility":
            return await self._analyze_compatibility(params)
        else:
            # Delegate to base class for common tools
            return await super().handle_mcp_call(method, params)
    
    async def _search_protocol_specs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for protocol specifications with protocol-specific filtering.
        """
        query = params["query"]
        protocol_type = params.get("protocol_type", "all")
        max_results = params.get("max_results", 5)
        
        try:
            # Add protocol-specific context to query if specified
            if protocol_type != "all" and protocol_type in self.protocol_categories:
                enhanced_query = f"{query} {protocol_type} {self.protocol_categories[protocol_type]}"
            else:
                enhanced_query = query
            
            # Search using vector database
            results = await self.vector_db.search(enhanced_query, limit=max_results)
            
            # Filter by protocol type if specified
            if protocol_type != "all":
                filtered_results = []
                for result in results:
                    # Check if document metadata contains protocol type
                    doc_info = await self.doc_db.get_document(result["metadata"]["document_id"])
                    if doc_info and protocol_type.lower() in doc_info["tags"].lower():
                        filtered_results.append(result)
                results = filtered_results[:max_results]
            
            # Format results for MCP response
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result["content"],
                    "score": result["score"],
                    "document": result["metadata"]["filename"],
                    "chunk_id": result["metadata"]["chunk_id"]
                })
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Found {len(formatted_results)} protocol specification results for '{query}':\n\n" +
                               "\n\n".join([
                                   f"**{r['document']}** (Score: {r['score']:.3f})\n{r['content']}"
                                   for r in formatted_results
                               ])
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error searching protocol specs: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error searching protocol specifications: {str(e)}"
                    }
                ]
            }
    
    async def _compare_protocols(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare features between different protocols.
        """
        protocol1 = params["protocol1"]
        protocol2 = params["protocol2"]
        aspects = params.get("comparison_aspects", ["speed", "power", "compatibility"])
        
        try:
            # Search for information about both protocols
            queries = []
            for protocol in [protocol1, protocol2]:
                for aspect in aspects:
                    queries.append(f"{protocol} {aspect} specification features")
            
            # Collect search results
            comparison_data = {}
            for i, protocol in enumerate([protocol1, protocol2]):
                protocol_results = []
                for aspect in aspects:
                    query = f"{protocol} {aspect} specification features"
                    results = await self.vector_db.search(query, limit=3)
                    protocol_results.extend(results)
                comparison_data[protocol] = protocol_results
            
            # Format comparison results
            comparison_text = f"# Protocol Comparison: {protocol1} vs {protocol2}\n\n"
            
            for aspect in aspects:
                comparison_text += f"## {aspect.title()}\n\n"
                
                for protocol in [protocol1, protocol2]:
                    comparison_text += f"### {protocol}\n"
                    relevant_results = [
                        r for r in comparison_data[protocol] 
                        if aspect.lower() in r["content"].lower()
                    ]
                    
                    if relevant_results:
                        comparison_text += f"{relevant_results[0]['content'][:300]}...\n\n"
                    else:
                        comparison_text += f"No specific {aspect} information found for {protocol}.\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": comparison_text
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error comparing protocols: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error comparing protocols: {str(e)}"
                    }
                ]
            }
    
    async def _get_protocol_versions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get version history for a specific protocol.
        """
        protocol = params["protocol"]
        
        try:
            # Search for version-related information
            version_queries = [
                f"{protocol} version history evolution",
                f"{protocol} 1.0 2.0 3.0 4.0 5.0 specifications",
                f"{protocol} generation timeline development"
            ]
            
            all_results = []
            for query in version_queries:
                results = await self.vector_db.search(query, limit=5)
                all_results.extend(results)
            
            # Remove duplicates and sort by relevance
            unique_results = {}
            for result in all_results:
                chunk_id = result["metadata"]["chunk_id"]
                if chunk_id not in unique_results or result["score"] > unique_results[chunk_id]["score"]:
                    unique_results[chunk_id] = result
            
            sorted_results = sorted(unique_results.values(), key=lambda x: x["score"], reverse=True)
            
            # Format version history
            version_text = f"# {protocol.upper()} Version History and Evolution\n\n"
            
            for i, result in enumerate(sorted_results[:5]):
                version_text += f"## Source {i+1}: {result['metadata']['filename']}\n"
                version_text += f"{result['content']}\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": version_text
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting protocol versions: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error retrieving protocol version information: {str(e)}"
                    }
                ]
            }
    
    async def _analyze_compatibility(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze compatibility between protocols or versions.
        """
        source_protocol = params["source_protocol"]
        target_protocol = params["target_protocol"]
        
        try:
            # Search for compatibility information
            compatibility_queries = [
                f"{source_protocol} {target_protocol} compatibility backward forward",
                f"{source_protocol} compatible with {target_protocol}",
                f"{target_protocol} supports {source_protocol}",
                f"interoperability {source_protocol} {target_protocol}"
            ]
            
            all_results = []
            for query in compatibility_queries:
                results = await self.vector_db.search(query, limit=3)
                all_results.extend(results)
            
            # Format compatibility analysis
            compatibility_text = f"# Compatibility Analysis: {source_protocol} ↔ {target_protocol}\n\n"
            
            if all_results:
                compatibility_text += "## Compatibility Information Found:\n\n"
                for i, result in enumerate(all_results[:5]):
                    compatibility_text += f"### Reference {i+1} ({result['metadata']['filename']})\n"
                    compatibility_text += f"{result['content']}\n\n"
            else:
                compatibility_text += "## No specific compatibility information found\n\n"
                compatibility_text += "Please check official specifications or contact protocol vendors for detailed compatibility information.\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": compatibility_text
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing compatibility: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error analyzing compatibility: {str(e)}"
                    }
                ]            }

# Import for lifespan
from contextlib import asynccontextmanager

# Global server instance
server = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    global server
    # Startup
    server = ProtocolKnowledgeServer()
    logger.info("Protocol Knowledge MCP Server initialized")
    yield
    # Shutdown (if needed)
    logger.info("Protocol Knowledge MCP Server shutting down")

# FastAPI application setup
app = FastAPI(
    title="Protocol Knowledge MCP Server",
    description="MCP server for hardware protocol specifications and knowledge",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add all the FastAPI routes from the base server
@app.post("/mcp")
async def mcp_endpoint(request: dict):
    """Main MCP endpoint for JSON-RPC calls."""
    return await server.handle_mcp_request(request)

@app.get("/mcp/sse")
@app.post("/mcp/sse")
async def sse_endpoint():
    """SSE endpoint for streaming MCP communication."""
    client_id = f"mcp_client_{datetime.now().timestamp()}_{id(object())}"
    return StreamingResponse(
        server.sse_generator(client_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.options("/mcp/sse")
async def sse_options():
    """Handle CORS preflight for SSE endpoint."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    tags: str = Form(""),
    description: str = Form("")
):
    """Upload and process a protocol specification document."""
    if not server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return await server.handle_document_upload(file, tags=tags)

@app.get("/documents")
async def list_documents():
    """List all uploaded protocol documents."""
    if not server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    return server.doc_db.get_documents(domain="protocols")

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a protocol document."""
    if not server:
        raise HTTPException(status_code=500, detail="Server not initialized")
    
    # This method needs to be implemented
    raise HTTPException(status_code=501, detail="Delete document not yet implemented")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "Protocol Knowledge MCP Server",
        "version": "1.0.0",
        "protocols_supported": list(server.protocol_categories.keys()) if server else []
    }

if __name__ == "__main__":
    import uvicorn
    
    # Ensure data directory exists
    data_dir = Path("data/protocols")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting Protocol Knowledge MCP Server...")
    print("📚 Supported protocols:", ", ".join([
        "PCIE", "UCIE", "Ethernet", "USB", "SATA", 
        "NVMe", "DDR", "Thunderbolt", "DisplayPort", "HDMI"
    ]))
    print("🌐 Server will be available at: http://localhost:8001")
    print("📡 MCP endpoint: http://localhost:8001/mcp")
    print("🔄 SSE endpoint: http://localhost:8001/mcp/sse")
    print("📄 Upload endpoint: http://localhost:8001/upload")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
