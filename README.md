# Quarkdown MCP 服务器 (v1.1)

一个模型上下文协议 (MCP) 服务器，提供全面的 Quarkdown 文档处理功能。该服务器使 AI 助手能够通过标准化接口编译、验证、预览和批量处理 Quarkdown 文档。

> **最新版本 v1.1** - 包含重要的命令行兼容性修正、增强语法验证和改进的错误处理机制。

## 关于 Quarkdown

Quarkdown 是一个现代化、可扩展的 Markdown 处理器，它扩展了 CommonMark 和 GitHub Flavored Markdown，具有强大的功能：

- **高级语法**：函数、变量、条件语句、循环等
- **多种输出格式**：HTML、PDF、LaTeX、Markdown、DOCX
- **模板系统**：可自定义的主题和文档类型
- **标准库**：用于布局、数学、数据处理和可视化的内置模块
- **交互元素**：幻灯片、可折叠部分和动态内容

## 功能特性

### 🚀 核心 MCP 工具

- **文档编译** (`compile_document`)：将 Quarkdown 源码转换为 HTML、PDF、LaTeX、Markdown 格式
- **项目创建** (`create_project`)：使用模板生成新的 Quarkdown 项目（基础、演示、书籍、文章）
- **语法验证** (`validate_markdown`)：检查文档语法，支持严格模式和全面的错误报告
- **预览服务器** (`preview_server`)：启动本地开发服务器，支持实时重载和主题
- **批量处理** (`convert_batch`)：高效并行处理多个文档

### 🎯 核心能力

- **多格式输出**：支持 HTML、PDF、LaTeX、Markdown、DOCX
- **模板系统**：应用自定义模板和主题（基础、演示、书籍、文章）
- **实时预览**：实时文档预览，支持自动重载
- **批量操作**：并行处理多个文档，可配置工作线程数
- **错误处理**：全面验证和详细错误报告
- **项目管理**：完整的项目脚手架，支持 Git 初始化

## 安装

### 前置要求

- Python 3.8 或更高版本（推荐 Python 3.11+）
- Java 11 或更高版本（用于 Quarkdown JAR 执行）
- Quarkdown JAR 文件（包含在 `quarkdown/build/libs/` 目录中）

### 快速安装

```bash
# 克隆仓库
git clone <repository-url>
cd quarkdown-mcp

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 Windows: venv\Scripts\activate

# 安装核心依赖
pip install -r requirements.txt

# 以开发模式安装
pip install -e .
```

### 开发环境设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 系统: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"

# 或者单独安装开发依赖
pip install -r requirements.txt
pip install pytest>=7.0.0 pytest-asyncio>=0.21.0 pytest-cov>=4.0.0
pip install black>=23.0.0 isort>=5.12.0 flake8>=6.0.0 mypy>=1.0.0

# 安装 pre-commit 钩子（如果使用）
pre-commit install
```

## 配置

### 环境变量

```bash
# 必需：Quarkdown JAR 文件路径（使用实际的绝对路径）
export QUARKDOWN_JAR_PATH="/path/to/quarkdown-mcp/quarkdown/build/libs/quarkdown.jar"

# 可选：处理临时目录
export QUARKDOWN_TEMP_DIR="/tmp/quarkdown"

# 可选：日志级别
export QUARKDOWN_LOG_LEVEL="INFO"
```

### MCP 客户端配置

添加到您的 MCP 客户端配置：

```json
{
  "mcpServers": {
    "quarkdown": {
      "command": "python",
      "args": ["-m", "quarkdown_mcp.server"],
      "cwd": "/path/to/quarkdown-mcp/src",
      "env": {
        "QUARKDOWN_JAR_PATH": "/path/to/quarkdown-mcp/quarkdown/build/libs/quarkdown.jar"
      }
    }
  }
}
```

### Quarkdown JAR 位置

Quarkdown JAR 文件包含在此仓库中，实际位置为：
```
quarkdown-mcp/quarkdown/build/libs/quarkdown.jar
```

确保在配置中使用此 JAR 文件的绝对路径。

## 运行服务器

### 启动 MCP 服务器

```bash
# 进入源代码目录
cd /path/to/quarkdown-mcp/src

# 以模块方式运行服务器
python -m quarkdown_mcp.server
```

### 验证配置

```bash
# 运行配置测试脚本
python tests/test_server_config.py
```

### 文档编译

```python
# 将 Quarkdown 编译为 HTML
result = await mcp_client.call_tool("compile_document", {
    "source_content": "# Hello Quarkdown\n\nThis is a **sample** document.",
    "output_format": "html",
    "template": "academic"
})
```

### 项目创建

```python
# 创建新的 Quarkdown 项目
result = await mcp_client.call_tool("create_project", {
    "project_name": "my-document",
    "project_path": "/path/to/projects",
    "template": "book",
    "include_examples": True
})
```

### 语法验证

```python
# 基础语法验证
result = await mcp_client.call_tool("validate_markdown", {
    "source_content": "# Document\n\n{{ invalid_function() }}",
    "strict_mode": False,
    "check_functions": True
})

# 严格模式验证（推荐）
result = await mcp_client.call_tool("validate_markdown", {
    "source_content": "# Document\n\n.callout\n\n![](image.png)\n\n{{ func(",
    "strict_mode": True,
    "check_functions": True,
    "check_variables": True
})
# 返回详细的错误和警告信息，包括：
# - Callout 缺少 type 参数
# - 图片缺少 alt 文本
# - 函数调用语法错误
```

### 预览服务器

```python
# 启动预览服务器
result = await mcp_client.call_tool("preview_server", {
    "source_content": "# Live Preview\n\nEdit and see changes!",
    "port": 8080,
    "auto_reload": True,
    "theme": "dark"
})
```

### 批量处理

```python
# 处理多个文档
result = await mcp_client.call_tool("convert_batch", {
    "documents": [
        {"name": "doc1", "content": "# Document 1"},
        {"name": "doc2", "content": "# Document 2"}
    ],
    "output_format": "pdf",
    "parallel_processing": True,
    "generate_index": True
})
```

## 工具参考

### compile_document

将 Quarkdown 源内容编译为各种输出格式。

**参数：**
- `source_content` (string, 可选)：Quarkdown 源内容（input_file 的替代选项）
- `input_file` (string, 可选)：输入 Quarkdown 文件路径
- `output_format` (string)：输出格式（html、pdf、tex、md）
- `output_file` (string, 可选)：输出文件路径
- `pretty_output` (boolean)：启用美化格式
- `wrap_output` (boolean)：启用输出包装
- `working_directory` (string, 可选)：编译工作目录

### create_project

创建具有目录结构和模板的新 Quarkdown 项目。

**参数：**
- `project_path` (string, 必需)：创建项目的目录路径
- `project_name` (string, 可选)：项目名称
- `template` (string)：项目模板（basic、presentation、book、article）
- `include_examples` (boolean)：包含示例文件
- `include_docs` (boolean)：包含文档
- `git_init` (boolean)：初始化 Git 仓库

### validate_markdown

验证 Quarkdown 文档语法并报告错误。

**参数：**
- `source_content` (string, 必需)：要验证的内容
- `strict_mode` (boolean)：启用严格验证模式
- `check_functions` (boolean)：验证函数语法
- `check_variables` (boolean)：验证变量引用
- `check_links` (boolean)：验证外部链接

### preview_server

启动具有实时重载功能的本地预览服务器。

**参数：**
- `source_content` (string, 必需)：要预览的内容
- `port` (integer)：服务器端口（默认：8080）
- `auto_reload` (boolean)：启用自动重载
- `theme` (string)：预览主题
- `watch_files` (array)：要监视变化的其他文件
- `open_browser` (boolean)：启动时自动打开浏览器

### convert_batch

在批处理模式下并行处理多个文档。

**参数：**
- `documents` (array, 必需)：包含名称、内容和可选 output_file 的文档列表
- `output_format` (string)：输出格式（html、pdf、latex、markdown、docx）
- `output_directory` (string, 可选)：输出文件目录
- `template` (string, 可选)：应用于所有文档的模板
- `parallel_processing` (boolean)：启用并行处理
- `max_workers` (integer)：最大并行工作线程数（默认：4）

## 架构

### 项目结构

```
quarkdown-mcp/
├── .github/                  # GitHub Actions 工作流程
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── LICENSE
├── README.md                 # 本文件
├── config.example.json       # MCP 服务器配置文件示例
├── pyproject.toml            # 项目构建和依赖管理 (PEP 517/518)
├── quarkdown/                # Quarkdown JAR 包及其相关文件 (子模块或直接包含)
├── requirements-dev.txt      # 开发环境额外依赖
├── requirements.txt          # 核心依赖
├── rewritten_docs/           # (可能是文档重写或示例输出目录)
├── scripts/                  # 辅助脚本 (如开发、测试运行器)
│   ├── dev.py
│   └── test_runner.py
├── setup.cfg                 # setuptools 配置文件 (部分项目可能仍在使用)
├── setup.py                  # setuptools 构建脚本 (如果 pyproject.toml 不完整或用于旧版兼容)
├── src/                      # 主要源代码
│   └── quarkdown_mcp/
│       ├── __init__.py
│       ├── core/               # 核心逻辑 (配置、JAR 包装器等)
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── wrapper.py
│       ├── server.py           # MCP 服务器主入口
│       └── tools/              # MCP 工具实现
│           ├── __init__.py
│           ├── base.py
│           ├── batch.py
│           ├── compile.py
│           ├── create_project.py
│           ├── preview.py
│           └── validate.py
├── record/
│   └── record.md             # 项目改进和测试记录
├── tests/                    # 测试脚本
│   ├── check_mcp.py
│   ├── final_test.py
│   ├── functional_test.py
│   ├── quick_test.py
│   ├── test_import.py
│   ├── test_improvements.py
│   └── test_server_config.py
└── test_document.qmd         # Quarkdown 测试文档示例
```

### 核心组件

- **Server**：主 MCP 服务器实现，包含工具注册
- **Config**：配置管理和验证
- **Wrapper**：用于 Quarkdown 执行的 Java 子进程包装器
- **Tools**：遵循 MCP 协议的各个工具实现

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行覆盖率测试
pytest --cov=quarkdown_mcp

# 运行特定测试类别
pytest -m unit
pytest -m integration
```

### 代码质量

```bash
# 格式化代码
black src/ tests/
isort src/ tests/

# 代码检查
flake8 src/ tests/
mypy src/

# 运行所有质量检查
pre-commit run --all-files
```

### 构建分发包

```bash
# 构建包
python -m build

# 本地安装
pip install dist/quarkdown_mcp-*.whl
```

## 最新改进 (v1.1)

### 🎯 核心改进

- **命令行兼容性修正**: 修正了与 Quarkdown CLI 的参数映射问题，确保编译功能正常工作
- **增强语法验证**: 新增 `strict_mode` 支持和 Quarkdown 特定语法检查
- **改进错误处理**: 更准确的编译状态判断和详细的错误报告
- **配置类扩展**: 添加 `create_temp_dir` 方法，支持临时目录管理
- **代码质量提升**: 清理重复代码，增强代码健壮性

### 📋 改进详情

1. **命令行参数修正**
   - 修正 `--output-format` → `-r` (render target)
   - 修正 `--output-path` → `-o` (output directory)
   - 添加 `--pretty` 和 `--nowrap` 选项支持

2. **语法验证增强**
   - 支持 `strict_mode` 参数
   - 检查 `.callout` 缺少 type 参数
   - 检查函数调用语法错误
   - 检查未知容器类型
   - 检查图片缺少 alt 文本

3. **错误处理改进**
   - 检查返回码和输出内容中的错误模式
   - 详细的错误和警告分类
   - 更友好的错误消息

## 故障排除

### 常见问题

1. **MCP 服务器启动错误**
   - **问题**: `TypeError: Server.get_capabilities() missing 2 required positional arguments`
   - **解决方案**: 确保使用 MCP SDK 1.0+ 版本，服务器代码已更新以支持新的 API
   
2. **模块导入错误**
   - **问题**: `ModuleNotFoundError: No module named 'quarkdown_mcp.tools.xxx'`
   - **解决方案**: 确保在 `src` 目录下运行服务器：`cd src && python -m quarkdown_mcp.server`
   
3. **找不到 Java**
   - **问题**: Java 未安装或不在 PATH 中
   - **解决方案**: 确保安装了 Java 11+ 并在 PATH 中
   
4. **找不到 JAR 文件**
   - **问题**: `QUARKDOWN_JAR_PATH` 环境变量未设置或路径错误
   - **解决方案**: 设置正确的绝对路径：`/path/to/quarkdown-mcp/quarkdown/build/libs/quarkdown.jar`
   
5. **权限错误**
   - **问题**: 临时目录权限不足
   - **解决方案**: 检查临时目录的文件权限，或设置 `QUARKDOWN_TEMP_DIR` 到可写目录
   
6. **端口冲突**
   - **问题**: 预览服务器端口被占用
   - **解决方案**: 为预览服务器使用不同端口

7. **编译失败问题** (新增)
   - **问题**: 编译返回成功但实际失败
   - **解决方案**: 检查输出日志中的错误信息，确保 Quarkdown 语法正确
   
8. **语法验证问题** (新增)
   - **问题**: 语法检查报告不准确
   - **解决方案**: 使用 `strict_mode: true` 获得更详细的检查结果

### 调试模式

```bash
# 启用调试日志
export QUARKDOWN_LOG_LEVEL="DEBUG"
cd src
python -m quarkdown_mcp.server
```

### 版本兼容性

- **MCP SDK**: 需要 1.0.0 或更高版本
- **Python**: 支持 3.8+，推荐 3.11+
- **Java**: 需要 11 或更高版本

### 性能调优

- 根据系统资源调整批处理的 `max_workers`
- 使用 SSD 存储临时文件以提高 I/O 性能
- 为大文档处理增加 JVM 堆大小

## 贡献

我们欢迎贡献！详情请参阅我们的[贡献指南](CONTRIBUTING.md)。

### 开发工作流程

1. Fork 仓库
2. 创建功能分支
3. 进行更改并添加测试
4. 运行质量检查
5. 提交 pull request

### 代码标准

- 遵循 PEP 8 风格指南
- 为所有函数添加类型提示
- 编写全面的测试
- 更新文档

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 致谢

- [Quarkdown](https://github.com/iamgio/quarkdown) - 底层文档处理引擎
- [Model Context Protocol](https://modelcontextprotocol.io/) - 协议规范
- 贡献者和维护者

## 更新日志

### v1.1 (2024-12)

**🔧 重要修复**
- 修正了与 Quarkdown CLI 的命令行参数映射问题
- 修正 `--output-format` → `-r` 和 `--output-path` → `-o`
- 添加 `--pretty` 和 `--nowrap` 选项支持

**✨ 新功能**
- 增强语法验证：支持 `strict_mode` 参数
- 新增 Quarkdown 特定语法检查（callout、函数、容器、图片）
- 配置类新增 `create_temp_dir` 方法

**🛠️ 改进**
- 更准确的编译状态判断和错误检测
- 详细的错误和警告分类
- 清理重复代码，提升代码质量
- 更友好的错误消息和建议

**📋 测试**
- 添加改进功能的验证测试
- 确保向后兼容性

### v1.0 (2024-11)
- 初始版本发布
- 基础 MCP 工具实现
- 支持文档编译、项目创建、语法验证、预览服务器、批量处理

## 支持

- 📖 [文档](https://quarkdown-mcp.readthedocs.io)
- 🐛 [问题跟踪](https://github.com/quarkdown/quarkdown-mcp/issues)
- 💬 [讨论](https://github.com/quarkdown/quarkdown-mcp/discussions)
- 📧 [邮件支持](mailto:support@quarkdown-mcp.org)
- 📁 [改进记录](record/record.md)