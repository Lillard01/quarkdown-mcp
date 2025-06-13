#!/usr/bin/env python3
"""Simple test script to check module imports."""

try:
    import quarkdown_mcp
    print(f"✓ quarkdown_mcp imported successfully, version: {quarkdown_mcp.__version__}")
    
    import quarkdown_mcp.server
    print("✓ quarkdown_mcp.server imported successfully")
    
    from quarkdown_mcp.server import main
    print("✓ main function imported successfully")
    
    print("\n🎉 All imports successful! MCP server is ready.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")