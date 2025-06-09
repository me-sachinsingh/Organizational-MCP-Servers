#!/usr/bin/env python3
"""
Test client for Protocol Knowledge MCP Server

This script tests the protocol knowledge server functionality.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

async def test_protocol_server():
    """Test the Protocol Knowledge MCP Server functionality."""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Protocol Knowledge MCP Server")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health check
        print("\n1. Testing health check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check passed: {health_data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return
        
        # Test 2: MCP capabilities
        print("\n2. Testing MCP capabilities...")
        try:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            async with session.post(f"{base_url}/mcp", json=mcp_request) as response:
                if response.status == 200:
                    init_response = await response.json()
                    print(f"✅ MCP initialization successful")
                    print(f"   Server: {init_response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
                else:
                    print(f"❌ MCP initialization failed: {response.status}")
        except Exception as e:
            print(f"❌ MCP initialization error: {e}")
        
        # Test 3: List tools
        print("\n3. Testing tools list...")
        try:
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            async with session.post(f"{base_url}/mcp", json=tools_request) as response:
                if response.status == 200:
                    tools_response = await response.json()
                    tools = tools_response.get('result', {}).get('tools', [])
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool['description']}")
                else:
                    print(f"❌ Tools list failed: {response.status}")
        except Exception as e:
            print(f"❌ Tools list error: {e}")
        
        # Test 4: Test search without documents (should handle gracefully)
        print("\n4. Testing search with empty database...")
        try:
            search_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "search_protocol_specs",
                    "arguments": {
                        "query": "PCIE 4.0 specifications",
                        "protocol_type": "pcie",
                        "max_results": 3
                    }
                }
            }
            
            async with session.post(f"{base_url}/mcp", json=search_request) as response:
                if response.status == 200:
                    search_response = await response.json()
                    result = search_response.get('result', {})
                    print("✅ Search completed (empty database expected)")
                    if 'content' in result and result['content']:
                        print(f"   Result: {result['content'][0]['text'][:100]}...")
                else:
                    print(f"❌ Search failed: {response.status}")
        except Exception as e:
            print(f"❌ Search error: {e}")
        
        # Test 5: Test document listing (should be empty)
        print("\n5. Testing document listing...")
        try:
            async with session.get(f"{base_url}/documents") as response:
                if response.status == 200:
                    docs = await response.json()
                    print(f"✅ Document listing successful: {len(docs)} documents")
                else:
                    print(f"❌ Document listing failed: {response.status}")
        except Exception as e:
            print(f"❌ Document listing error: {e}")

    print("\n" + "=" * 50)
    print("🎉 Protocol Knowledge Server test completed!")
    print("\n📋 Next steps:")
    print("1. Upload some protocol specification PDFs using /upload endpoint")
    print("2. Test search functionality with actual documents")
    print("3. Try protocol comparison and version analysis tools")
    print("4. Configure in VS Code MCP settings for GitHub Copilot integration")

if __name__ == "__main__":
    print("Starting Protocol Knowledge Server test...")
    print("Make sure the server is running on localhost:8001")
    print("You can start it with: python mcp_protocols_server.py")
    print("\nPress Ctrl+C to cancel, or wait 3 seconds to continue...")
    
    try:
        # Give user a chance to cancel
        import time
        time.sleep(3)
        
        # Run the test
        asyncio.run(test_protocol_server())
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)
