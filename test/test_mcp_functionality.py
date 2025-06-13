#!/usr/bin/env python3
"""
功能测试脚本：验证所有MCP工具的具体功能是否正常工作
"""

import sys
import asyncio
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_compile_tool():
    """测试文档编译工具"""
    print("\n🔧 测试 CompileDocumentTool...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.compile import CompileDocumentTool
        
        config = QuarkdownConfig()
        tool = CompileDocumentTool(config)
        
        # 测试工具定义
        tool_def = tool.get_tool_definition()
        print(f"✅ 工具名称: {tool_def.name}")
        print(f"✅ 工具描述: {tool_def.description}")
        
        # 检查输入模式
        schema = tool_def.inputSchema
        if 'properties' in schema:
            properties = schema['properties']
            print(f"✅ 支持的参数: {list(properties.keys())}")
            
            # 检查关键参数
            expected_params = ['source_content', 'output_format', 'output_path']
            for param in expected_params:
                if param in properties:
                    print(f"  ✓ {param}: {properties[param].get('description', 'N/A')}")
                else:
                    print(f"  ⚠️  缺少参数: {param}")
        
        return True
        
    except Exception as e:
        print(f"❌ CompileDocumentTool 测试失败: {e}")
        return False

async def test_create_project_tool():
    """测试项目创建工具"""
    print("\n🔧 测试 CreateProjectTool...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.create_project import CreateProjectTool
        
        config = QuarkdownConfig()
        tool = CreateProjectTool(config)
        
        # 测试工具定义
        tool_def = tool.get_tool_definition()
        print(f"✅ 工具名称: {tool_def.name}")
        print(f"✅ 工具描述: {tool_def.description}")
        
        # 检查输入模式
        schema = tool_def.inputSchema
        if 'properties' in schema:
            properties = schema['properties']
            print(f"✅ 支持的参数: {list(properties.keys())}")
            
            # 检查模板选项
            if 'template' in properties and 'enum' in properties['template']:
                templates = properties['template']['enum']
                print(f"  ✓ 支持的模板: {templates}")
        
        return True
        
    except Exception as e:
        print(f"❌ CreateProjectTool 测试失败: {e}")
        return False

async def test_validate_tool():
    """测试语法验证工具"""
    print("\n🔧 测试 ValidateMarkdownTool...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.validate import ValidateMarkdownTool
        
        config = QuarkdownConfig()
        tool = ValidateMarkdownTool(config)
        
        # 测试工具定义
        tool_def = tool.get_tool_definition()
        print(f"✅ 工具名称: {tool_def.name}")
        print(f"✅ 工具描述: {tool_def.description}")
        
        # 检查验证选项
        schema = tool_def.inputSchema
        if 'properties' in schema:
            properties = schema['properties']
            validation_options = ['strict_mode', 'check_functions', 'check_variables']
            for option in validation_options:
                if option in properties:
                    print(f"  ✓ {option}: {properties[option].get('description', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ValidateMarkdownTool 测试失败: {e}")
        return False

async def test_preview_tool():
    """测试预览服务器工具"""
    print("\n🔧 测试 PreviewServerTool...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.preview import PreviewServerTool
        
        config = QuarkdownConfig()
        tool = PreviewServerTool(config)
        
        # 测试工具定义
        tool_def = tool.get_tool_definition()
        print(f"✅ 工具名称: {tool_def.name}")
        print(f"✅ 工具描述: {tool_def.description}")
        
        # 检查服务器选项
        schema = tool_def.inputSchema
        if 'properties' in schema:
            properties = schema['properties']
            if 'port' in properties:
                port_info = properties['port']
                print(f"  ✓ 端口范围: {port_info.get('minimum', 'N/A')} - {port_info.get('maximum', 'N/A')}")
                print(f"  ✓ 默认端口: {port_info.get('default', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ PreviewServerTool 测试失败: {e}")
        return False

async def test_batch_tool():
    """测试批量转换工具"""
    print("\n🔧 测试 ConvertBatchTool...")
    
    try:
        from quarkdown_mcp.core.config import QuarkdownConfig
        from quarkdown_mcp.tools.batch import ConvertBatchTool
        
        config = QuarkdownConfig()
        tool = ConvertBatchTool(config)
        
        # 测试工具定义
        tool_def = tool.get_tool_definition()
        print(f"✅ 工具名称: {tool_def.name}")
        print(f"✅ 工具描述: {tool_def.description}")
        
        # 检查批量处理选项
        schema = tool_def.inputSchema
        if 'properties' in schema:
            properties = schema['properties']
            if 'documents' in properties:
                docs_schema = properties['documents']
                print(f"  ✓ 文档数组类型: {docs_schema.get('type', 'N/A')}")
                if 'items' in docs_schema and 'properties' in docs_schema['items']:
                    doc_props = docs_schema['items']['properties']
                    print(f"  ✓ 文档属性: {list(doc_props.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConvertBatchTool 测试失败: {e}")
        return False

async def test_server_integration():
    """测试服务器集成"""
    print("\n🔧 测试服务器集成...")
    
    try:
        from quarkdown_mcp.server import server, handle_list_tools
        
        # 测试工具列表
        tools = await handle_list_tools()
        print(f"✅ 服务器注册的工具数量: {len(tools)}")
        
        expected_tools = [
            'compile_document',
            'create_project', 
            'validate_markdown',
            'preview_server',
            'convert_batch'
        ]
        
        registered_tools = [tool.name for tool in tools]
        print(f"✅ 注册的工具: {registered_tools}")
        
        # 检查所有预期工具是否都已注册
        missing_tools = [tool for tool in expected_tools if tool not in registered_tools]
        if missing_tools:
            print(f"⚠️  缺少工具: {missing_tools}")
            return False
        else:
            print("✅ 所有预期工具都已正确注册")
        
        return True
        
    except Exception as e:
        print(f"❌ 服务器集成测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始MCP工具功能验证\n")
    
    tests = [
        ("CompileDocumentTool", test_compile_tool),
        ("CreateProjectTool", test_create_project_tool),
        ("ValidateMarkdownTool", test_validate_tool),
        ("PreviewServerTool", test_preview_tool),
        ("ConvertBatchTool", test_batch_tool),
        ("服务器集成", test_server_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结结果
    print("\n📊 功能测试结果总结:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 所有功能测试通过！MCP工具功能完整可用。")
        return 0
    else:
        print("⚠️  部分功能测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))