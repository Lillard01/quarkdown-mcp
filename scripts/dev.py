#!/usr/bin/env python3
"""Development utilities for Quarkdown MCP.

Provides commands for development, testing, and deployment.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a shell command."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=check)
    return result


def setup_dev_environment():
    """Set up development environment."""
    print("Setting up development environment...")
    
    # Install in development mode
    run_command([sys.executable, "-m", "pip", "install", "-e", ".[dev]"])
    
    # Install pre-commit hooks
    try:
        run_command(["pre-commit", "install"])
    except subprocess.CalledProcessError:
        print("Warning: pre-commit not available, skipping hooks installation")
    
    print("Development environment setup complete!")


def run_tests(coverage=False, integration=False):
    """Run tests."""
    cmd = [sys.executable, "-m", "pytest"]
    
    if coverage:
        cmd.extend(["--cov=quarkdown_mcp", "--cov-report=html", "--cov-report=term"])
    
    if integration:
        cmd.append("tests/integration")
    else:
        cmd.append("tests/unit")
    
    cmd.extend(["-v", "--tb=short"])
    
    run_command(cmd)


def run_linting():
    """Run code linting."""
    print("Running code linting...")
    
    # Black formatting
    try:
        run_command(["black", "--check", "src", "tests", "scripts"])
        print("✓ Black formatting check passed")
    except subprocess.CalledProcessError:
        print("✗ Black formatting check failed")
        run_command(["black", "src", "tests", "scripts"])
        print("✓ Code formatted with Black")
    
    # isort import sorting
    try:
        run_command(["isort", "--check-only", "src", "tests", "scripts"])
        print("✓ isort import check passed")
    except subprocess.CalledProcessError:
        print("✗ isort import check failed")
        run_command(["isort", "src", "tests", "scripts"])
        print("✓ Imports sorted with isort")
    
    # Flake8 linting
    try:
        run_command(["flake8", "src", "tests", "scripts"])
        print("✓ Flake8 linting passed")
    except subprocess.CalledProcessError:
        print("✗ Flake8 linting failed")
    
    # MyPy type checking
    try:
        run_command(["mypy", "src"])
        print("✓ MyPy type checking passed")
    except subprocess.CalledProcessError:
        print("✗ MyPy type checking failed")


def run_security_check():
    """Run security checks."""
    print("Running security checks...")
    
    try:
        run_command(["bandit", "-r", "src"])
        print("✓ Bandit security check passed")
    except subprocess.CalledProcessError:
        print("✗ Bandit security check failed")


def build_package():
    """Build the package."""
    print("Building package...")
    
    # Clean previous builds
    import shutil
    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
    
    # Build package
    run_command([sys.executable, "-m", "build"])
    
    print("Package built successfully!")


def create_test_jar():
    """Create a mock Quarkdown JAR for testing."""
    print("Creating mock Quarkdown JAR for testing...")
    
    jar_content = '''
#!/usr/bin/env python3
"""Mock Quarkdown JAR for testing."""

import json
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Mock Quarkdown")
    parser.add_argument("command", choices=["compile", "validate", "preview", "create", "help", "version"])
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--format", "-f", help="Output format")
    parser.add_argument("--port", "-p", type=int, help="Port number")
    parser.add_argument("--template", "-t", help="Project template")
    
    args = parser.parse_args()
    
    if args.command == "compile":
        output = f"<html><h1>Mock Output</h1><p>Compiled from {args.input or 'stdin'}</p></html>"
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
    
    elif args.command == "validate":
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {"lines": 10, "words": 50, "characters": 300}
        }
        print(json.dumps(result))
    
    elif args.command == "preview":
        print(f"Preview server started on port {args.port or 8080}")
        print(f"URL: http://localhost:{args.port or 8080}")
    
    elif args.command == "create":
        print(f"Project created with template: {args.template or 'default'}")
    
    elif args.command == "version":
        print("Mock Quarkdown 1.0.0")
    
    elif args.command == "help":
        parser.print_help()

if __name__ == "__main__":
    main()
'''
    
    # Create mock JAR directory
    jar_dir = Path("test_data")
    jar_dir.mkdir(exist_ok=True)
    
    # Write mock JAR script
    jar_file = jar_dir / "mock_quarkdown.py"
    jar_file.write_text(jar_content)
    jar_file.chmod(0o755)
    
    print(f"Mock Quarkdown JAR created at: {jar_file}")
    print("You can use this for testing by setting QUARKDOWN_JAR_PATH to this file")


def run_demo():
    """Run a demo of the MCP server."""
    print("Running Quarkdown MCP demo...")
    
    # Create demo content
    demo_content = '''
# Demo Document

## Introduction

This is a demo document for Quarkdown MCP.

## Features

- **Document compilation** to multiple formats
- **Syntax validation** with detailed error reporting
- **Live preview** with auto-reload
- **Batch processing** for multiple documents
- **Project creation** with templates

## Code Example

```python
def hello_quarkdown():
    print("Hello from Quarkdown MCP!")
```

## Conclusion

Quarkdown MCP makes document processing easy and efficient.
'''
    
    # Create demo directory
    demo_dir = Path("demo")
    demo_dir.mkdir(exist_ok=True)
    
    # Write demo document
    demo_file = demo_dir / "demo.qmd"
    demo_file.write_text(demo_content)
    
    print(f"Demo document created at: {demo_file}")
    print("\nTo test the MCP server:")
    print("1. Set up your MCP client configuration")
    print("2. Start the MCP server")
    print("3. Use the demo document for testing")
    
    # Show example MCP client commands
    print("\nExample MCP tool calls:")
    print("- compile_document: Compile the demo document to HTML")
    print("- validate_markdown: Validate the demo document syntax")
    print("- preview_server: Start a live preview server")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Quarkdown MCP development utilities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Set up development environment")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("--integration", action="store_true", help="Run integration tests")
    
    # Lint command
    subparsers.add_parser("lint", help="Run code linting")
    
    # Security command
    subparsers.add_parser("security", help="Run security checks")
    
    # Build command
    subparsers.add_parser("build", help="Build the package")
    
    # Create test JAR command
    subparsers.add_parser("create-test-jar", help="Create mock Quarkdown JAR for testing")
    
    # Demo command
    subparsers.add_parser("demo", help="Set up demo environment")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_dev_environment()
    elif args.command == "test":
        run_tests(coverage=args.coverage, integration=args.integration)
    elif args.command == "lint":
        run_linting()
    elif args.command == "security":
        run_security_check()
    elif args.command == "build":
        build_package()
    elif args.command == "create-test-jar":
        create_test_jar()
    elif args.command == "demo":
        run_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()