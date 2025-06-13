#!/usr/bin/env python3
"""
测试脚本：验证所有MCP工具是否完整可用
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_tool_imports():
    """测试所有工具是否可以正常导入"""
    print("🔍 测试MCP工具导入...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        print("✅ QuarkdownConfig 导入成功")
    except Exception as e:
        print(f"❌ QuarkdownConfig 导入失败: {e}")
        return False
    
    try:
        from quarkdown_mcp.tools.compile import CompileDocumentTool
        print("✅ CompileDocumentTool 导入成功")
    except Exception as e:
        print(f"❌ CompileDocumentTool 导入失败: {e}")
        return False
    
    try:
        from quarkdown_mcp.tools.create_project import CreateProjectTool
        print("✅ CreateProjectTool 导入成功")
    except Exception as e:
        print(f"❌ CreateProjectTool 导入失败: {e}")
        return False
    
    try:
        from quarkdown_mcp.tools.validate import ValidateMarkdownTool
        print("✅ ValidateMarkdownTool 导入成功")
    except Exception as e:
        print(f"❌ ValidateMarkdownTool 导入失败: {e}")
        return False
    
    try:
        from quarkdown_mcp.tools.preview import PreviewServerTool
        print("✅ PreviewServerTool 导入成功")
    except Exception as e:
        print(f"❌ PreviewServerTool 导入失败: {e}")
        return False
    
    try:
        from quarkdown_mcp.tools.batch import ConvertBatchTool
        print("✅ ConvertBatchTool 导入成功")
    except Exception as e:
        print(f"❌ ConvertBatchTool 导入失败: {e}")
        return False
    
    return True

def test_tool_initialization():
    """测试工具是否可以正常初始化"""
    print("\n🔧 测试MCP工具初始化...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.compile import CompileDocumentTool
        from quarkdown_mcp.tools.create_project import CreateProjectTool
        from quarkdown_mcp.tools.validate import ValidateMarkdownTool
        from quarkdown_mcp.tools.preview import PreviewServerTool
        from quarkdown_mcp.tools.batch import ConvertBatchTool
        
        # 尝试创建配置（可能会因为JAR文件不存在而失败，但这是预期的）
        try:
            config = QuarkdownConfig()
            print("✅ QuarkdownConfig 初始化成功")
        except FileNotFoundError as e:
            print(f"⚠️  QuarkdownConfig 初始化失败（JAR文件未找到）: {e}")
            # 使用模拟配置继续测试
            config = None
        
        # 测试工具定义获取（不需要实际的config）
        tools_info = [
            ("CompileDocumentTool", CompileDocumentTool),
            ("CreateProjectTool", CreateProjectTool),
            ("ValidateMarkdownTool", ValidateMarkdownTool),
            ("PreviewServerTool", PreviewServerTool),
            ("ConvertBatchTool", ConvertBatchTool)
        ]
        
        for tool_name, tool_class in tools_info:
            try:
                if config:
                    tool = tool_class(config)
                    tool_def = tool.get_tool_definition()
                    print(f"✅ {tool_name} 初始化成功 - 工具名: {tool_def.name}")
                else:
                    print(f"⚠️  {tool_name} 跳过初始化（配置不可用）")
            except Exception as e:
                print(f"❌ {tool_name} 初始化失败: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 工具初始化测试失败: {e}")
        return False

def test_jar_file():
    """测试Quarkdown JAR文件是否存在"""
    print("\n📦 测试Quarkdown JAR文件...")
    
    jar_path = Path(__file__).parent / "quarkdown" / "build" / "libs" / "quarkdown.jar"
    
    if jar_path.exists():
        print(f"✅ JAR文件存在: {jar_path}")
        print(f"📏 文件大小: {jar_path.stat().st_size / 1024 / 1024:.2f} MB")
        return True
    else:
        print(f"❌ JAR文件不存在: {jar_path}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始MCP工具完整性检查\n")
    
    results = []
    
    # 测试导入
    results.append(("工具导入", test_tool_imports()))
    
    # 测试初始化
    results.append(("工具初始化", test_tool_initialization()))
    
    # 测试JAR文件
    results.append(("JAR文件", test_jar_file()))
    
    # 总结结果
    print("\n📊 测试结果总结:")
    print("=" * 40)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 40)
    
    if all_passed:
        print("🎉 所有测试通过！MCP工具完整可用。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())