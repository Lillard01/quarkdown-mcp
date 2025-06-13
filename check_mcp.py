#!/usr/bin/env python3

try:
    import mcp
    print(f"MCP version: {getattr(mcp, '__version__', 'unknown')}")
    print(f"MCP modules: {dir(mcp)}")
    
    import mcp.server
    print(f"MCP server modules: {dir(mcp.server)}")
    
    try:
        from mcp.server.models import CallToolRequest, ListToolsRequest
        print("✓ Successfully imported CallToolRequest, ListToolsRequest from mcp.server.models")
    except ImportError as e:
        print(f"✗ Failed to import from mcp.server.models: {e}")
        
    try:
        from mcp.types import CallToolRequest, ListToolsRequest
        print("✓ Successfully imported CallToolRequest, ListToolsRequest from mcp.types")
    except ImportError as e:
        print(f"✗ Failed to import from mcp.types: {e}")
        
    try:
        from mcp import types
        print(f"MCP types: {dir(types)}")
    except ImportError as e:
        print(f"✗ Failed to import mcp.types: {e}")
        
except ImportError as e:
    print(f"Failed to import mcp: {e}")