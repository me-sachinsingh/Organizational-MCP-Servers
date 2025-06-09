# Organizational MCP Servers

A comprehensive suite of specialized MCP (Model Context Protocol) servers for organizational knowledge management, designed to work with GitHub Copilot Chat for secure, private AI-assisted information retrieval.

## 🎯 **Project Overview**

This project creates domain-specific MCP servers that maintain local knowledge bases with vector embeddings, enabling intelligent information retrieval without sending data to external services.

## 🏗️ **Architecture**

```
Organizational-MCP-Servers/
├── mcp-shared-core/              # Shared infrastructure and utilities
├── mcp-protocols-server/         # Hardware protocols knowledge base
├── mcp-it-knowledge-server/      # IT/Infrastructure knowledge base
├── mcp-coding-guidelines-server/ # Code review and guidelines
├── mcp-discovery-service/        # Server discovery and management
├── mcp-admin-dashboard/          # Web-based administration
├── docs/                         # Documentation
├── scripts/                      # Deployment and utility scripts
└── config/                       # Configuration files
```

## 🚀 **Getting Started**

### Prerequisites

- Python 3.8+
- Windows/Linux/macOS
- GitHub Copilot Chat (for AI agent integration)

### Installation

1. **Clone or create the project structure**
   ```bash
   cd Organizational-MCP-Servers
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start with the shared core**
   ```bash
   cd mcp-shared-core
   python -m pytest tests/  # Run tests
   ```

4. **Deploy a specialized server**
   ```bash
   cd mcp-protocols-server
   python protocols_server.py
   ```

## 📚 **Specialized Servers**

### 1. **Protocol Knowledge Server**
- **Domain**: PCIE, UCIE, Ethernet, USB, SATA, NVMe, etc.
- **Features**: PDF specification ingestion, protocol comparison, technical detail extraction

### 2. **IT Knowledge Server**
- **Domain**: Infrastructure, Security, Networking, DevOps
- **Features**: Best practices database, troubleshooting guides, security policies

### 3. **Coding Guidelines Server**
- **Domain**: Code quality, standards, best practices
- **Features**: Code review automation, style guide enforcement, security scanning

## 🔐 **Security Features**

- ✅ **Local-Only Processing** - No external API calls
- ✅ **Air-Gapped Deployment** - Can run completely offline
- ✅ **Encrypted Storage** - Secure document and vector storage
- ✅ **Access Control** - Role-based permissions and audit logging

## 🛠️ **Technology Stack**

- **FastAPI** - HTTP server framework
- **ChromaDB** - Local vector database
- **Sentence Transformers** - Local embedding generation
- **PyMuPDF** - PDF processing
- **SQLite** - Document metadata storage
- **MCP Protocol** - Standard communication with GitHub Copilot

## 📖 **Documentation**

- [Architecture Overview](docs/ORGANIZATIONAL_MCP_ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [API Reference](docs/API.md)

## 🚀 **Quick Start Example**

1. **Start the Protocol Knowledge Server:**
   ```bash
   cd mcp-protocols-server
   python protocols_server.py
   ```

2. **Upload a protocol specification:**
   ```bash
   curl -X POST "http://localhost:8001/upload" \
        -F "file=@pcie_spec.pdf" \
        -F "domain=protocols" \
        -F "tags=pcie,specification"
   ```

3. **Configure MCP client:**
   ```json
   {
     "servers": {
       "protocols": {
         "type": "sse",
         "url": "http://localhost:8001/mcp/sse"
       }
     }
   }
   ```

4. **Query via GitHub Copilot:**
   ```
   @protocols What are the key differences between PCIe 4.0 and PCIe 5.0?
   ```

## 🔄 **Development Workflow**

1. **Phase 1**: Foundation (✅ Complete)
   - Shared core library
   - Base MCP server template
   - Document ingestion pipeline

2. **Phase 2**: Protocol Server (🔄 In Progress)
   - PDF ingestion for protocol specs
   - Protocol-specific knowledge extraction
   - Query interface for technical details

3. **Phase 3**: IT Knowledge Server (📋 Planned)
   - IT documentation ingestion
   - Best practices database
   - Troubleshooting assistance

4. **Phase 4**: Coding Guidelines Server (📋 Planned)
   - Code analysis integration
   - Guidelines enforcement
   - Review automation

5. **Phase 5**: Management & Discovery (📋 Planned)
   - Central discovery service
   - Admin dashboard
   - Performance monitoring

## 🤝 **Contributing**

1. Follow the established project structure
2. Add tests for new functionality
3. Update documentation
4. Ensure security best practices

## 📄 **License**

Private organizational use. All rights reserved.

## 📞 **Support**

For internal organizational support, contact the development team.
