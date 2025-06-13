#!/usr/bin/env python3
"""
Test script to verify the improvements made to the Quarkdown MCP project.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from quarkdown_mcp.core.config import QuarkdownConfig
    from quarkdown_mcp.core.wrapper import QuarkdownWrapper
    print("✅ Successfully imported QuarkdownConfig and QuarkdownWrapper")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 1: Config create_temp_dir method
print("\n🧪 Testing QuarkdownConfig.create_temp_dir method...")
try:
    config = QuarkdownConfig()
    temp_dir = config.create_temp_dir("test_")
    print(f"✅ create_temp_dir method works: {temp_dir}")
    
    # Check if directory exists
    if temp_dir.exists():
        print("✅ Temporary directory was created successfully")
        # Clean up
        temp_dir.rmdir()
        print("✅ Temporary directory cleaned up")
    else:
        print("❌ Temporary directory was not created")
except Exception as e:
    print(f"❌ create_temp_dir test failed: {e}")

# Test 2: Wrapper syntax validation improvements
print("\n🧪 Testing improved validate_syntax method...")
try:
    # Create a mock config for testing (without requiring JAR file)
    class MockConfig:
        def __init__(self):
            self.temp_dir = "/tmp"
            self.encoding = "utf-8"
            self.java_executable = "java"
            self.jar_path = "/mock/path/quarkdown.jar"
            self.timeout = 300
            
        def create_temp_file(self, content="", suffix=".qmd"):
            import tempfile
            import uuid
            temp_file = Path(tempfile.gettempdir()) / f"temp_{uuid.uuid4().hex[:8]}{suffix}"
            if content:
                temp_file.write_text(content, encoding=self.encoding)
            return temp_file
            
        def create_temp_dir(self, prefix="quarkdown_"):
            import tempfile
            import uuid
            temp_dir = Path(tempfile.gettempdir()) / f"{prefix}{uuid.uuid4().hex[:8]}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir
            
        def cleanup_temp_file(self, file_path):
            try:
                if file_path.exists():
                    file_path.unlink()
            except:
                pass
    
    mock_config = MockConfig()
    wrapper = QuarkdownWrapper(mock_config)
    
    # Test the _check_quarkdown_syntax method
    test_content = """
# Test Document

This is a test with .callout without type parameter.

.function(incomplete

:::: unknown-container
Content
::::

![](image.png)
"""
    
    errors, warnings = wrapper._check_quarkdown_syntax(test_content)
    print(f"✅ _check_quarkdown_syntax method works")
    print(f"   Found {len(errors)} errors and {len(warnings)} warnings")
    
    if warnings:
        print("   Warnings detected:")
        for warning in warnings:
            print(f"     - {warning}")
    
    if errors:
        print("   Errors detected:")
        for error in errors:
            print(f"     - {error}")
            
except Exception as e:
    print(f"❌ validate_syntax test failed: {e}")

print("\n🎉 Test completed!")