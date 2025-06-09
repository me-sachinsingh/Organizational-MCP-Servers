#!/usr/bin/env python3
"""
Quick test to verify server initialization works correctly.
"""

import sys
import os
from pathlib import Path

# Add the shared core to Python path
sys.path.append(str(Path(__file__).parent / "mcp-shared-core"))

# Import the server class
from mcp_protocols_server import ProtocolKnowledgeServer

def test_server_initialization():
    """Test that the server can be initialized without errors."""
    try:
        print("Testing ProtocolKnowledgeServer initialization...")
        
        # Try to create a server instance
        server = ProtocolKnowledgeServer(data_dir="test_data", port=8001)
        
        print("✅ Server initialization successful!")
        print(f"  - Server Name: {server.server_name}")
        print(f"  - Domain: {server.domain}")
        print(f"  - Port: {server.port}")
        print(f"  - Data Directory: {server.data_dir}")
        print(f"  - Protocol Categories: {len(server.protocol_categories)} defined")
        
        return True
        
    except Exception as e:
        print(f"❌ Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server_initialization()
    sys.exit(0 if success else 1)
