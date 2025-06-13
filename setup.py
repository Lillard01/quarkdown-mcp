#!/usr/bin/env python3
"""
Quarkdown MCP Server Setup Configuration

This setup.py file enables installation of the Quarkdown MCP server
with optional development dependencies.

Installation:
    # Core installation
    pip install -e .
    
    # Development installation with all dev tools
    pip install -e ".[dev]"
    
    # Testing only
    pip install -e ".[test]"
    
    # Documentation only
    pip install -e ".[docs]"
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
def read_requirements(filename):
    """Read requirements from a file, filtering out comments and empty lines."""
    requirements = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    requirements.append(line)
    except FileNotFoundError:
        pass
    return requirements

# Core requirements
install_requires = read_requirements('requirements.txt')

# Development requirements
dev_requires = read_requirements('requirements-dev.txt')

# Test-only requirements
test_requires = [
    'pytest>=7.0.0',
    'pytest-asyncio>=0.21.0',
    'pytest-cov>=4.0.0',
    'pytest-mock>=3.10.0',
    'pytest-xdist>=3.2.0',
]

# Documentation requirements
docs_requires = [
    'sphinx>=6.0.0',
    'sphinx-rtd-theme>=1.2.0',
    'sphinx-autodoc-typehints>=1.22.0',
]

# Linting and formatting requirements
lint_requires = [
    'black>=23.0.0',
    'isort>=5.12.0',
    'flake8>=6.0.0',
    'mypy>=1.0.0',
    'pre-commit>=3.0.0',
    'autoflake>=2.0.0',
]

setup(
    name="quarkdown-mcp",
    version="1.0.0",
    description="A Model Context Protocol (MCP) server for Quarkdown document processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Quarkdown MCP Team",
    author_email="contact@quarkdown-mcp.dev",
    url="https://github.com/your-org/quarkdown-mcp",
    license="MIT",
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        "quarkdown_mcp": [
            "*.json",
            "*.yaml",
            "*.yml",
            "templates/*",
            "config/*",
        ],
    },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Core dependencies
    install_requires=install_requires,
    
    # Optional dependencies
    extras_require={
        "dev": dev_requires,
        "test": test_requires,
        "docs": docs_requires,
        "lint": lint_requires,
        "all": dev_requires + test_requires + docs_requires + lint_requires,
    },
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "quarkdown-mcp=quarkdown_mcp.server:main",
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Topic :: Documentation",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "mcp",
        "model-context-protocol",
        "quarkdown",
        "markdown",
        "document-processing",
        "ai-tools",
        "llm-tools",
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/your-org/quarkdown-mcp/issues",
        "Source": "https://github.com/your-org/quarkdown-mcp",
        "Documentation": "https://quarkdown-mcp.readthedocs.io/",
    },
)