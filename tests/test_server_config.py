#!/usr/bin/env python3
"""Test script to verify MCP server configuration."""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from quarkdown_mcp.server import create_server, get_capabilities
    from quarkdown_mcp.core.config import QuarkdownConfig
    
    print("✅ Successfully imported MCP server modules")
    
    # Test configuration
    config = QuarkdownConfig()
    print(f"✅ Configuration loaded: JAR path = {config.jar_path}")
    
    # Test server creation
    server = create_server()
    print(f"✅ Server created: {server}")
    
    # Test capabilities
    capabilities = get_capabilities()
    print(f"✅ Capabilities loaded: {len(capabilities.get('tools', {}))} tools available")
    
    for tool_name in capabilities.get('tools', {}).keys():
        print(f"  - {tool_name}")
    
    print("\n🎉 MCP server configuration is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)