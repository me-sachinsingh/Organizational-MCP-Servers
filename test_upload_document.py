#!/usr/bin/env python3
"""
Test script to upload a sample document to the Protocol Knowledge MCP Server
"""

import requests
import json
from pathlib import Path
import tempfile

# Server configuration
SERVER_URL = "http://localhost:8001"
UPLOAD_ENDPOINT = f"{SERVER_URL}/upload"
HEALTH_ENDPOINT = f"{SERVER_URL}/health"
DOCUMENTS_ENDPOINT = f"{SERVER_URL}/documents"

def test_server_health():
    """Test if the server is running and healthy."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Server is healthy!")
            print(f"   Server: {health_data.get('server')}")
            print(f"   Version: {health_data.get('version')}")
            print(f"   Protocols: {', '.join(health_data.get('protocols_supported', []))}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the Protocol Knowledge MCP Server is running on http://localhost:8001")
        return False

def create_sample_protocol_document():
    """Create a sample protocol document for testing."""
    sample_content = """
# PCI Express 4.0 Specification Overview

## Introduction
PCI Express (PCIe) 4.0 is the fourth generation of the PCI Express interface standard. 
It doubles the bandwidth of PCIe 3.0 from 8 GT/s to 16 GT/s per lane.

## Key Features
- Data rate: 16 GT/s per lane
- Encoding: 128b/130b encoding scheme
- Bandwidth: Up to 64 GB/s for x16 configuration
- Backward compatibility with PCIe 3.0, 2.0, and 1.0
- Improved signal integrity and error correction

## Technical Specifications
- Lane width options: x1, x2, x4, x8, x16
- Power consumption: Optimized for better efficiency
- Latency: Reduced compared to previous generations
- Maximum link length: Varies by implementation

## Applications
- High-performance computing
- Graphics cards (GPUs)
- NVMe SSDs
- Network interface cards
- Enterprise storage solutions

## Compatibility
PCIe 4.0 devices are backward compatible with PCIe 3.0 slots, but will operate at PCIe 3.0 speeds.
PCIe 3.0 devices can be installed in PCIe 4.0 slots and will operate normally.

## Performance Comparison
| Version | Data Rate | Encoding | Bandwidth (x16) |
|---------|-----------|----------|-----------------|
| PCIe 1.0| 2.5 GT/s  | 8b/10b   | 4 GB/s         |
| PCIe 2.0| 5 GT/s    | 8b/10b   | 8 GB/s         |
| PCIe 3.0| 8 GT/s    | 128b/130b| 16 GB/s        |
| PCIe 4.0| 16 GT/s   | 128b/130b| 32 GB/s        |
"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(sample_content)
        return f.name

def upload_sample_document():
    """Upload a sample protocol document to the server."""
    print("\n📄 Creating sample PCIe 4.0 specification document...")
    
    # Create sample document
    temp_file = create_sample_protocol_document()
    temp_path = Path(temp_file)
    
    try:
        print(f"📤 Uploading document: {temp_path.name}")
        
        # Prepare the file and form data
        with open(temp_path, 'rb') as file:
            files = {
                'file': (temp_path.name, file, 'text/plain')
            }
            data = {
                'tags': 'pcie,specification,hardware,protocol',
                'description': 'Sample PCIe 4.0 specification document for testing'
            }
            
            # Upload the document
            response = requests.post(UPLOAD_ENDPOINT, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Document uploaded successfully!")
                print(f"   Document ID: {result.get('document_id')}")
                print(f"   Filename: {result.get('filename')}")
                print(f"   Status: {result.get('status')}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload error: {e}")
        return False
    finally:
        # Clean up temporary file
        temp_path.unlink(missing_ok=True)

def list_documents():
    """List all documents in the server."""
    try:
        print("\n📋 Listing all documents...")
        response = requests.get(DOCUMENTS_ENDPOINT, timeout=10)
        
        if response.status_code == 200:
            documents = response.json()
            if documents:
                print(f"✅ Found {len(documents)} documents:")
                for i, doc in enumerate(documents, 1):
                    print(f"   {i}. {doc.get('filename')} (ID: {doc.get('id')})")
                    print(f"      Status: {doc.get('status')} | Chunks: {doc.get('chunk_count', 0)}")
                    print(f"      Tags: {doc.get('tags', 'N/A')}")
                    print(f"      Upload Date: {doc.get('upload_date', 'N/A')}")
                    print()
            else:
                print("📝 No documents found in the knowledge base.")
            return True
        else:
            print(f"❌ Failed to list documents: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing documents: {e}")
        return False

def test_mcp_search():
    """Test MCP search functionality with the uploaded document."""
    print("\n🔍 Testing MCP search functionality...")
    
    mcp_request = {
        "jsonrpc": "2.0",
        "id": "test-search-1",
        "method": "tools/call",
        "params": {
            "name": "search_knowledge",
            "arguments": {
                "query": "PCIe 4.0 bandwidth specifications",
                "limit": 3
            }
        }
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/mcp", json=mcp_request, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP search successful!")
            
            if "result" in result and "content" in result["result"]:
                for content in result["result"]["content"]:
                    if content["type"] == "text":
                        print("📄 Search Results:")
                        print(content["text"][:500] + "..." if len(content["text"]) > 500 else content["text"])
            return True
        else:
            print(f"❌ MCP search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ MCP search error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Protocol Knowledge MCP Server - Document Upload Test")
    print("=" * 60)
    
    # Test server health
    if not test_server_health():
        return False
    
    # List existing documents
    list_documents()
    
    # Upload sample document
    if not upload_sample_document():
        return False
    
    # Wait a moment for processing
    print("\n⏳ Waiting for document processing...")
    import time
    time.sleep(3)
    
    # List documents again to see the new one
    list_documents()
    
    # Test MCP search
    test_mcp_search()
    
    print("\n✅ Document upload test completed!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Some tests failed. Check the server logs for more details.")
        exit(1)
    else:
        print("\n🎉 All tests passed successfully!")
