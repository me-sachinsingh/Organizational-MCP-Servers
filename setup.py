#!/usr/bin/env python3
"""
Organizational MCP Servers Setup and Deployment Script
Automates the setup, testing, and deployment of MCP servers.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
from typing import List, Dict, Optional

def run_command(command: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a shell command and return success status"""
    try:
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    return run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_environment():
    """Set up environment configuration"""
    print("⚙️ Setting up environment...")
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("Created .env file from template")
        print("⚠️ Please edit .env file with your specific configuration")
    
    # Create data directories
    data_dirs = [
        "data",
        "data/protocols", 
        "data/it-knowledge",
        "data/coding-guidelines",
        "data/vector_db",
        "logs"
    ]
    
    for dir_path in data_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def test_servers():
    """Run tests for all servers"""
    print("🧪 Running tests...")
    
    test_commands = [
        ["python", "-m", "pytest", "mcp-shared-core/tests/", "-v"],
        ["python", "-m", "pytest", "mcp-protocols-server/", "-v"],
        ["python", "-m", "pytest", "mcp-it-knowledge-server/", "-v"],
        ["python", "-m", "pytest", "mcp-coding-guidelines-server/", "-v"],
    ]
    
    success = True
    for cmd in test_commands:
        if not run_command(cmd):
            success = False
    
    return success

def start_server(server_name: str, port: int):
    """Start a specific MCP server"""
    print(f"🚀 Starting {server_name} server on port {port}...")
    
    server_map = {
        "protocols": ("mcp-protocols-server", "mcp_protocols_server.py"),
        "it-knowledge": ("mcp-it-knowledge-server", "mcp_it_server.py"),
        "coding-guidelines": ("mcp-coding-guidelines-server", "mcp_coding_server.py"),
        "discovery": ("mcp-discovery-service", "discovery_server.py"),
        "admin": ("mcp-admin-dashboard", "admin_server.py")
    }
    
    if server_name not in server_map:
        print(f"❌ Unknown server: {server_name}")
        return False
    
    server_dir, server_file = server_map[server_name]
    server_path = Path(server_dir) / server_file
    
    if not server_path.exists():
        print(f"❌ Server file not found: {server_path}")
        return False
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path("mcp-shared-core").absolute()) + os.pathsep + env.get("PYTHONPATH", "")
    
    return run_command([sys.executable, str(server_path)], cwd=Path(server_dir))

def main():
    """Main setup and deployment function"""
    parser = argparse.ArgumentParser(description="Organizational MCP Servers Setup")
    parser.add_argument("action", choices=["setup", "test", "start", "install"], 
                       help="Action to perform")
    parser.add_argument("--server", choices=["protocols", "it-knowledge", "coding-guidelines", "discovery", "admin"],
                       help="Specific server to start (for 'start' action)")
    parser.add_argument("--port", type=int, help="Port to run server on")
    
    args = parser.parse_args()
    
    if args.action == "install":
        if install_dependencies():
            print("✅ Dependencies installed successfully")
        else:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    elif args.action == "setup":
        print("🏗️ Setting up Organizational MCP Servers...")
        
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
        
        setup_environment()
        print("✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your configuration")
        print("2. Run 'python setup.py test' to run tests")
        print("3. Run 'python setup.py start --server protocols' to start a server")
    
    elif args.action == "test":
        if test_servers():
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            sys.exit(1)
    
    elif args.action == "start":
        if not args.server:
            print("❌ Please specify --server for start action")
            sys.exit(1)
        
        port = args.port or {
            "protocols": 8001,
            "it-knowledge": 8002, 
            "coding-guidelines": 8003,
            "discovery": 8000,
            "admin": 8080
        }.get(args.server, 8000)
        
        if start_server(args.server, port):
            print(f"✅ {args.server} server started successfully on port {port}")
        else:
            print(f"❌ Failed to start {args.server} server")
            sys.exit(1)

if __name__ == "__main__":
    main()
