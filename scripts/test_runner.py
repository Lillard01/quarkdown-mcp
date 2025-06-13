#!/usr/bin/env python3
"""
测试运行器 - 支持分步测试和快速执行

这个脚本提供了多种测试执行模式，帮助开发者快速验证代码质量。
支持单独运行不同类型的测试，避免长时间等待。
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """测试运行器类，管理不同类型的测试执行"""
    
    def __init__(self, project_root: Path):
        """初始化测试运行器
        
        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.venv_python = project_root / "venv" / "bin" / "python"
        self.venv_pip = project_root / "venv" / "bin" / "pip"
        
    def run_command(self, cmd: List[str], description: str) -> bool:
        """执行命令并显示结果
        
        Args:
            cmd: 要执行的命令列表
            description: 命令描述
            
        Returns:
            bool: 命令是否成功执行
        """
        print(f"\n🔄 {description}...")
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print(f"✅ {description} 成功")
                if result.stdout.strip():
                    print(f"输出: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ {description} 失败 (退出码: {result.returncode})")
                if result.stderr.strip():
                    print(f"错误: {result.stderr.strip()}")
                if result.stdout.strip():
                    print(f"输出: {result.stdout.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} 超时")
            return False
        except Exception as e:
            print(f"💥 {description} 异常: {e}")
            return False
    
    def install_package(self) -> bool:
        """安装项目包到虚拟环境"""
        # 使用bash来避免zsh的glob问题
        cmd = ["bash", "-c", f"{self.venv_pip} install -e '.[dev]'"]
        return self.run_command(cmd, "安装项目包")
    
    def run_unit_tests(self, verbose: bool = False, specific_file: Optional[str] = None) -> bool:
        """运行单元测试
        
        Args:
            verbose: 是否显示详细输出
            specific_file: 指定测试文件
            
        Returns:
            bool: 测试是否通过
        """
        cmd = [str(self.venv_python), "-m", "pytest", "tests/unit/"]
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.extend(["-q", "--tb=short"])
            
        if specific_file:
            cmd[-1] = f"tests/unit/{specific_file}"
            
        # 添加快速执行选项
        cmd.extend([
            "-x",  # 遇到第一个失败就停止
            "--maxfail=3",  # 最多3个失败
            "-m", "not slow"  # 跳过慢测试
        ])
        
        return self.run_command(cmd, "单元测试")
    
    def run_config_tests(self) -> bool:
        """运行配置相关测试"""
        cmd = [
            str(self.venv_python), "-m", "pytest", 
            "tests/unit/test_config.py",
            "-v", "-x", "--tb=short"
        ]
        return self.run_command(cmd, "配置测试")
    
    def run_tools_tests(self) -> bool:
        """运行工具相关测试"""
        cmd = [
            str(self.venv_python), "-m", "pytest", 
            "tests/unit/test_tools.py",
            "-v", "-x", "--tb=short"
        ]
        return self.run_command(cmd, "工具测试")
    
    def run_wrapper_tests(self) -> bool:
        """运行包装器相关测试"""
        cmd = [
            str(self.venv_python), "-m", "pytest", 
            "tests/unit/test_wrapper.py",
            "-v", "-x", "--tb=short"
        ]
        return self.run_command(cmd, "包装器测试")
    
    def run_integration_tests(self) -> bool:
        """运行集成测试"""
        cmd = [
            str(self.venv_python), "-m", "pytest", 
            "tests/integration/",
            "-v", "-x", "--tb=short",
            "-m", "not slow"
        ]
        return self.run_command(cmd, "集成测试")
    
    def run_syntax_check(self) -> bool:
        """运行语法检查"""
        cmd = [str(self.venv_python), "-m", "py_compile", "src/quarkdown_mcp/server.py"]
        return self.run_command(cmd, "语法检查")
    
    def run_import_check(self) -> bool:
        """运行导入检查"""
        cmd = [str(self.venv_python), "-c", "import quarkdown_mcp; print('导入成功')"]
        return self.run_command(cmd, "导入检查")
    
    def run_quick_smoke_test(self) -> bool:
        """运行快速冒烟测试"""
        print("\n🚀 开始快速冒烟测试...")
        
        # 首先确保包已安装
        if not self.install_package():
            print("\n💥 包安装失败")
            return False
        
        tests = [
            ("语法检查", self.run_syntax_check),
            ("导入检查", self.run_import_check),
            ("配置测试", self.run_config_tests)
        ]
        
        for name, test_func in tests:
            if not test_func():
                print(f"\n💥 快速测试在 {name} 阶段失败")
                return False
                
        print("\n✅ 快速冒烟测试全部通过")
        return True
    
    def run_step_by_step_tests(self) -> bool:
        """分步运行所有测试"""
        print("\n📋 开始分步测试...")
        
        # 首先安装包
        if not self.install_package():
            print("\n💥 包安装失败")
            return False
        
        steps = [
            ("语法检查", self.run_syntax_check),
            ("导入检查", self.run_import_check),
            ("配置测试", self.run_config_tests),
            ("包装器测试", self.run_wrapper_tests),
            ("工具测试", self.run_tools_tests),
            ("集成测试", self.run_integration_tests)
        ]
        
        passed = 0
        total = len(steps)
        
        for i, (name, test_func) in enumerate(steps, 1):
            print(f"\n📍 步骤 {i}/{total}: {name}")
            if test_func():
                passed += 1
                print(f"✅ 步骤 {i} 完成")
            else:
                print(f"❌ 步骤 {i} 失败")
                print(f"\n📊 测试结果: {passed}/{i} 步骤通过")
                return False
                
        print(f"\n🎉 所有测试步骤完成! {passed}/{total} 步骤通过")
        return True


def main():
    """主函数 - 解析命令行参数并执行相应的测试"""
    parser = argparse.ArgumentParser(
        description="Quarkdown MCP 测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/test_runner.py --quick          # 快速冒烟测试
  python scripts/test_runner.py --step-by-step  # 分步测试
  python scripts/test_runner.py --unit          # 单元测试
  python scripts/test_runner.py --config        # 配置测试
  python scripts/test_runner.py --tools         # 工具测试
        """
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="运行快速冒烟测试"
    )
    
    parser.add_argument(
        "--step-by-step", "-s",
        action="store_true",
        help="分步运行所有测试"
    )
    
    parser.add_argument(
        "--unit", "-u",
        action="store_true",
        help="运行单元测试"
    )
    
    parser.add_argument(
        "--config", "-c",
        action="store_true",
        help="运行配置测试"
    )
    
    parser.add_argument(
        "--tools", "-t",
        action="store_true",
        help="运行工具测试"
    )
    
    parser.add_argument(
        "--wrapper", "-w",
        action="store_true",
        help="运行包装器测试"
    )
    
    parser.add_argument(
        "--integration", "-i",
        action="store_true",
        help="运行集成测试"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="指定测试文件 (例如: test_config.py)"
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="仅安装项目包"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)
    
    # 检查虚拟环境
    if not runner.venv_python.exists():
        print("❌ 虚拟环境未找到，请先运行: python -m venv venv")
        sys.exit(1)
    
    success = True
    
    # 根据参数执行相应的测试
    if args.install:
        success = runner.install_package()
    elif args.quick:
        success = runner.run_quick_smoke_test()
    elif args.step_by_step:
        success = runner.run_step_by_step_tests()
    elif args.unit:
        # 先安装包
        if runner.install_package():
            success = runner.run_unit_tests(args.verbose, args.file)
        else:
            success = False
    elif args.config:
        if runner.install_package():
            success = runner.run_config_tests()
        else:
            success = False
    elif args.tools:
        if runner.install_package():
            success = runner.run_tools_tests()
        else:
            success = False
    elif args.wrapper:
        if runner.install_package():
            success = runner.run_wrapper_tests()
        else:
            success = False
    elif args.integration:
        if runner.install_package():
            success = runner.run_integration_tests()
        else:
            success = False
    else:
        # 默认运行快速测试
        print("未指定测试类型，运行快速冒烟测试...")
        success = runner.run_quick_smoke_test()
    
    if success:
        print("\n🎉 测试完成!")
        sys.exit(0)
    else:
        print("\n💥 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()