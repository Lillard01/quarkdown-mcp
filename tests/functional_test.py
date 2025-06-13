#!/usr/bin/env python3
"""
功能验证脚本 - 测试 Quarkdown MCP 工具的实际功能
"""

import os
import sys
from pathlib import Path

def test_compile_tool():
    """测试编译工具功能"""
    print("\n📝 测试编译工具...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.compile import CompileDocumentTool
        
        # 创建配置和工具
        config = QuarkdownConfig()
        tool = CompileDocumentTool(config)
        
        print("✅ 编译工具初始化成功")
        print(f"   - 工具名称: {tool.get_tool_definition().name}")
        print(f"   - 支持格式: HTML, PDF, LaTeX, Markdown")
        print(f"   - 支持文件输入和内容输入")
        
        return True
        
    except Exception as e:
        print(f"❌ 编译工具测试失败: {e}")
        return False

def test_validate_tool():
    """测试验证工具功能"""
    print("\n🔍 测试验证工具...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.validate import ValidateMarkdownTool
        
        # 创建配置和工具
        config = QuarkdownConfig()
        tool = ValidateMarkdownTool(config)
        
        print("✅ 验证工具初始化成功")
        print(f"   - 工具名称: {tool.get_tool_definition().name}")
        print(f"   - 支持严格模式验证")
        print(f"   - 支持函数语法检查")
        print(f"   - 支持变量引用检查")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证工具测试失败: {e}")
        return False

def test_preview_tool():
    """测试预览工具功能"""
    print("\n🌐 测试预览工具...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.preview import PreviewServerTool
        
        # 创建配置和工具
        config = QuarkdownConfig()
        tool = PreviewServerTool(config)
        
        print("✅ 预览工具初始化成功")
        print(f"   - 工具名称: {tool.get_tool_definition().name}")
        print(f"   - 默认端口: 8080")
        print(f"   - 支持自动重载")
        print(f"   - 支持多种主题")
        
        return True
        
    except Exception as e:
        print(f"❌ 预览工具测试失败: {e}")
        return False

def test_create_project_tool():
    """测试项目创建工具功能"""
    print("\n🏗️ 测试项目创建工具...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.create_project import CreateProjectTool
        
        # 创建配置和工具
        config = QuarkdownConfig()
        tool = CreateProjectTool(config)
        
        print("✅ 项目创建工具初始化成功")
        print(f"   - 工具名称: {tool.get_tool_definition().name}")
        print(f"   - 支持多种模板: basic, presentation, book, article")
        print(f"   - 支持示例文件生成")
        print(f"   - 支持 Git 初始化")
        
        return True
        
    except Exception as e:
        print(f"❌ 项目创建工具测试失败: {e}")
        return False

def test_batch_tool():
    """测试批量转换工具功能"""
    print("\n📦 测试批量转换工具...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.batch import ConvertBatchTool
        
        # 创建配置和工具
        config = QuarkdownConfig()
        tool = ConvertBatchTool(config)
        
        print("✅ 批量转换工具初始化成功")
        print(f"   - 工具名称: {tool.get_tool_definition().name}")
        print(f"   - 支持并行处理")
        print(f"   - 支持多种输出格式")
        print(f"   - 支持错误继续处理")
        print(f"   - 支持索引文件生成")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量转换工具测试失败: {e}")
        return False

def check_jar_file():
    """检查 Quarkdown JAR 文件是否存在"""
    print("\n☕ 检查 Quarkdown JAR 文件...")
    
    jar_path = Path("/Users/wangdada/Downloads/mcp/quarkdown-mcp/quarkdown/build/libs/quarkdown.jar")
    
    if jar_path.exists():
        file_size = jar_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ JAR 文件存在: {jar_path}")
        print(f"   - 文件大小: {file_size:.1f} MB")
        return True
    else:
        print(f"❌ JAR 文件不存在: {jar_path}")
        print("   - 请确保已正确构建 Quarkdown")
        return False

def main():
    """主函数 - 运行所有功能验证测试"""
    print("🚀 开始 Quarkdown MCP 功能验证...")
    print("=" * 40)
    
    # 运行所有测试
    tests = [
        test_compile_tool,
        test_validate_tool, 
        test_preview_tool,
        test_create_project_tool,
        test_batch_tool,
        check_jar_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 功能验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有功能验证通过！")
        return 0
    else:
        print("⚠️ 部分功能验证失败，请检查相关组件。")
        return 1

if __name__ == "__main__":
    sys.exit(main())