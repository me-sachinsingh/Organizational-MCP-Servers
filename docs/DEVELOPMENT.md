# Development Guide - Organizational MCP Servers

## 🏗️ **Project Architecture**

This project implements a modular architecture with shared core infrastructure and specialized MCP servers:

```
Organizational-MCP-Servers/
├── mcp-shared-core/              # 🔧 Shared infrastructure
│   ├── mcp_knowledge_core.py     # Core classes and utilities
│   ├── tests/                    # Core infrastructure tests
│   └── __init__.py
├── mcp-protocols-server/         # 🔌 Hardware protocols knowledge
├── mcp-it-knowledge-server/      # 💻 IT infrastructure knowledge  
├── mcp-coding-guidelines-server/ # 📝 Code quality and standards
├── mcp-discovery-service/        # 🔍 Server discovery and management
├── mcp-admin-dashboard/          # 🖥️ Web-based administration
├── docs/                         # 📚 Documentation
├── scripts/                      # 🛠️ Utility scripts
└── config/                       # ⚙️ Configuration files
```

## 🚀 **Quick Start**

### 1. Environment Setup

```bash
# Install dependencies
python setup.py install

# Set up environment
python setup.py setup

# Edit configuration
cp .env.example .env
# Edit .env with your settings
```

### 2. Run Tests

```bash
python setup.py test
```

### 3. Start a Server

```bash
# Start protocols server
python setup.py start --server protocols --port 8001

# Start IT knowledge server  
python setup.py start --server it-knowledge --port 8002
```

## 🏛️ **Core Architecture Components**

### BaseKnowledgeServer

The foundation class for all specialized MCP servers:

```python
from mcp_knowledge_core import BaseKnowledgeServer

class MySpecializedServer(BaseKnowledgeServer):
    def __init__(self, data_dir: str = "data/my_domain"):
        super().__init__(
            server_name="My Specialized Server",
            server_version="1.0.0", 
            description="Domain-specific knowledge server",
            data_dir=data_dir
        )
    
    def get_specialized_tools(self) -> List[Dict[str, Any]]:
        """Return domain-specific MCP tools"""
        return [
            {
                "name": "my_specialized_tool",
                "description": "Does something domain-specific",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    }
                }
            }
        ]
```

### DocumentProcessor

Handles document ingestion and text extraction:

```python
from mcp_knowledge_core import DocumentProcessor

processor = DocumentProcessor(supported_formats=['.pdf', '.txt', '.md'])

# Extract text from PDF
chunks = await processor.extract_text_from_pdf(pdf_path)

# Process plain text
chunks = await processor.process_text_document(text_content, source_info)
```

### VectorDatabase

Manages vector embeddings and similarity search:

```python
from mcp_knowledge_core import VectorDatabase

vector_db = VectorDatabase(
    persist_directory="data/vector_db",
    collection_name="my_collection"
)

# Add documents
await vector_db.add_documents(chunks, metadatas)

# Search
results = await vector_db.similarity_search(query, n_results=10)
```

### DocumentDatabase

Handles document metadata storage:

```python
from mcp_knowledge_core import DocumentDatabase

doc_db = DocumentDatabase("data/documents.db")

# Store document metadata
doc_id = await doc_db.store_document(
    filename="spec.pdf",
    file_hash="abc123",
    file_size=1024000,
    domain="protocols",
    tags=["pcie", "specification"]
)
```

## 🛠️ **Creating a New Specialized Server**

### 1. Create Server Directory

```bash
mkdir mcp-my-domain-server
cd mcp-my-domain-server
```

### 2. Implement Server Class

Create `mcp_my_domain_server.py`:

```python
#!/usr/bin/env python3
"""
My Domain MCP Server
Specialized knowledge server for my domain.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-shared-core'))

from mcp_knowledge_core import BaseKnowledgeServer
from typing import Dict, List, Any

class MyDomainServer(BaseKnowledgeServer):
    def __init__(self, data_dir: str = "data/my_domain"):
        super().__init__(
            server_name="My Domain Server",
            server_version="1.0.0",
            description="Specialized knowledge server for my domain",
            data_dir=data_dir
        )
        
        # Domain-specific initialization
        self.setup_domain_specific_features()
    
    def setup_domain_specific_features(self):
        """Initialize domain-specific features"""
        # Add your domain-specific setup here
        pass
    
    def get_specialized_tools(self) -> List[Dict[str, Any]]:
        """Return domain-specific MCP tools"""
        return [
            {
                "name": "analyze_my_domain_document",
                "description": "Analyze documents specific to my domain",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "analysis_type": {"type": "string"}
                    },
                    "required": ["document_id"]
                }
            },
            {
                "name": "search_my_domain_knowledge",
                "description": "Search domain-specific knowledge base",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {"type": "object"}
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def handle_analyze_my_domain_document(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle domain-specific document analysis"""
        document_id = arguments.get("document_id")
        analysis_type = arguments.get("analysis_type", "general")
        
        # Implement your domain-specific analysis
        result = await self.perform_domain_analysis(document_id, analysis_type)
        
        return {
            "analysis_result": result,
            "document_id": document_id,
            "analysis_type": analysis_type
        }
    
    async def handle_search_my_domain_knowledge(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle domain-specific knowledge search"""
        query = arguments.get("query")
        filters = arguments.get("filters", {})
        
        # Use base class search with domain-specific filtering
        results = await self.vector_db.similarity_search(
            query, 
            n_results=10,
            where=filters
        )
        
        return {
            "results": results,
            "query": query,
            "total_results": len(results)
        }

if __name__ == "__main__":
    server = MyDomainServer()
    server.run(port=8004)  # Choose unique port
```

### 3. Add Tests

Create `test_my_domain_server.py`:

```python
import pytest
import asyncio
from mcp_my_domain_server import MyDomainServer

@pytest.fixture
def server():
    return MyDomainServer(data_dir="test_data")

@pytest.mark.asyncio
async def test_server_initialization(server):
    assert server.server_name == "My Domain Server"
    assert server.server_version == "1.0.0"

@pytest.mark.asyncio 
async def test_specialized_tools(server):
    tools = server.get_specialized_tools()
    assert len(tools) >= 2
    assert any(tool["name"] == "analyze_my_domain_document" for tool in tools)

@pytest.mark.asyncio
async def test_domain_specific_search(server):
    # Add test documents first
    await server.add_test_documents()
    
    # Test search
    result = await server.handle_search_my_domain_knowledge({
        "query": "test query"
    })
    
    assert "results" in result
    assert "query" in result
```

## 🔧 **Development Workflow**

### 1. Local Development

```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run specific server for development
cd mcp-my-domain-server
python mcp_my_domain_server.py
```

### 2. Testing

```bash
# Run all tests
python setup.py test

# Run specific server tests
cd mcp-my-domain-server
python -m pytest test_my_domain_server.py -v

# Run with coverage
python -m pytest --cov=mcp_my_domain_server test_my_domain_server.py
```

### 3. Integration Testing

```bash
# Test MCP protocol compliance
python scripts/test_mcp_compliance.py --server my-domain --port 8004

# Test document upload and processing
python scripts/test_document_pipeline.py --server my-domain
```

## 📋 **Best Practices**

### 1. Code Organization

- Keep domain-specific logic in specialized servers
- Use shared core for common functionality
- Follow consistent naming conventions
- Add comprehensive docstrings

### 2. Error Handling

```python
try:
    result = await self.process_document(document)
except DocumentProcessingError as e:
    logger.error(f"Document processing failed: {e}")
    return {"error": str(e), "code": "PROCESSING_FAILED"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Internal server error", "code": "INTERNAL_ERROR"}
```

### 3. Security Considerations

- Validate all input parameters
- Sanitize file uploads
- Use secure file storage paths
- Implement proper access controls
- Log security-relevant events

### 4. Performance Optimization

- Use async/await for I/O operations
- Implement proper caching strategies
- Optimize vector database queries
- Monitor memory usage for large documents

### 5. Configuration Management

```python
import os
from pathlib import Path

class ServerConfig:
    def __init__(self):
        self.data_dir = os.getenv("DATA_DIR", "data")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
```

## 🔍 **Debugging and Monitoring**

### 1. Logging Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 2. Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper
```

### 3. Health Checks

All servers automatically include health check endpoints:

- `GET /health` - Basic health status
- `GET /health/detailed` - Detailed system status
- `GET /metrics` - Performance metrics

## 📚 **Additional Resources**

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## 🤝 **Contributing**

1. Create a feature branch from main
2. Implement your changes with tests
3. Run the full test suite
4. Update documentation as needed
5. Submit a pull request with detailed description

## 🆘 **Troubleshooting**

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes mcp-shared-core
2. **Port Conflicts**: Check that server ports are available
3. **Database Locks**: Ensure only one server instance per data directory
4. **Memory Issues**: Monitor embeddings model memory usage
5. **File Permissions**: Verify write access to data directories

### Debug Mode

```bash
# Run server in debug mode
PYTHONPATH=mcp-shared-core python mcp_my_domain_server.py --debug

# Enable verbose logging
LOG_LEVEL=DEBUG python mcp_my_domain_server.py
```
