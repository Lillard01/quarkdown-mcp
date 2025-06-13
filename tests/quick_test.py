#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证 Quarkdown MCP 服务器基本功能

这个脚本用于快速验证项目的核心组件是否正常工作，
避免长时间等待的测试过程。
"""

import sys
import os
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """测试模块导入功能"""
    print("🔍 测试模块导入...")
    
    try:
        import quarkdown_mcp
        print(f"✅ quarkdown_mcp 导入成功")
        
        from quarkdown_mcp.server import main
        print("✅ server.main 导入成功")
        
        from quarkdown_mcp.core.config import QuarkdownConfig
        print("✅ QuarkdownConfig 导入成功")
        
        from quarkdown_mcp.core.wrapper import QuarkdownWrapper
        print("✅ QuarkdownWrapper 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def test_config_creation():
    """测试配置创建功能"""
    print("\n🔧 测试配置创建...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        
        # 测试默认配置
        config = QuarkdownConfig()
        print(f"✅ 默认配置创建成功")
        print(f"   - JAR 路径: {config.jar_path}")
        print(f"   - 临时目录: {config.temp_dir}")
        
        return True
    except Exception as e:
        print(f"❌ 配置创建失败: {e}")
        return False

def test_wrapper_creation():
    """测试包装器创建功能"""
    print("\n🎯 测试包装器创建...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.core.wrapper import QuarkdownWrapper
        
        config = QuarkdownConfig()
        wrapper = QuarkdownWrapper(config)
        print("✅ QuarkdownWrapper 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 包装器创建失败: {e}")
        return False

def test_tools_import():
    """测试工具模块导入"""
    print("\n🛠️ 测试工具模块导入...")
    
    try:
        from quarkdown_mcp.tools.compile import CompileDocumentTool
        print("✅ CompileDocumentTool 导入成功")
        
        from quarkdown_mcp.tools.validate import ValidateMarkdownTool
        print("✅ ValidateMarkdownTool 导入成功")
        
        from quarkdown_mcp.tools.preview import PreviewServerTool
        print("✅ PreviewServerTool 导入成功")
        
        from quarkdown_mcp.tools.create_project import CreateProjectTool
        print("✅ CreateProjectTool 导入成功")
        
        from quarkdown_mcp.tools.batch import ConvertBatchTool
        print("✅ ConvertBatchTool 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 工具导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 意外错误: {e}")
        return False

def test_java_detection():
    """测试 Java 环境检测"""
    print("\n☕ 测试 Java 环境检测...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        
        config = QuarkdownConfig()
        java_command = config.get_java_command()
        print(f"✅ Java 命令检测成功: {' '.join(java_command)}")
        
        return True
    except Exception as e:
        print(f"❌ Java 环境检测失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Quarkdown MCP 快速测试开始\n")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_creation,
        test_wrapper_creation,
        test_tools_import,
        test_java_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！MCP 服务器基本功能正常。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关组件。")
        return 1

if __name__ == "__main__":
    sys.exit(main())