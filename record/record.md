# Quarkdown MCP 项目更新记录

## 项目概述
Quarkdown MCP 是一个基于 Model Context Protocol (MCP) 的服务器，为 Quarkdown 文档处理提供标准化接口。

## 最新更新时间
2024年12月19日

## 项目配置文件更新记录

### 最新更新 - MCP 服务器模块导入问题修复
**更新时间**: 2024年12月6日

#### 问题描述
用户在使用 `config.example.json` 配置 MCP 服务器时遇到 `ModuleNotFoundError: No module named 'quarkdown_mcp'` 错误。

#### 解决方案
1. **修复 pyproject.toml 语法错误**:
   - 发现第124行 `package-dir` 配置格式错误
   - 修正为正确的 TOML 对象格式: `package-dir = {"" = "src"}`

2. **重新安装包**:
   - 使用 `./venv/bin/pip install -e .` 重新安装开发版本
   - 成功将版本从 0.1.0 升级到 1.0.0

3. **验证模块导入**:
   - 创建 `test_import.py` 测试脚本
   - 确认 `quarkdown_mcp` 模块和 `quarkdown_mcp.server` 可以正常导入

4. **更新配置文件**:
   - 修改 `config.example.json` 中的 Python 路径
   - 从 `"python"` 改为 `"/Users/wangdada/Downloads/mcp/quarkdown-mcp/venv/bin/python"`

#### 修复结果
- ✅ 模块导入成功
- ✅ MCP 服务器可以正常启动
- ✅ 配置文件路径正确

---

## 项目配置文件更新

### 更新内容概览
1. **README.md** - 完善项目文档和使用指南
2. **requirements.txt** - 重构依赖管理和分类
3. **requirements-dev.txt** - 新增开发依赖配置
4. **setup.py** - 新增传统安装配置
5. **pyproject.toml** - 更新现代Python项目配置
6. **setup.cfg** - 新增工具配置文件

### 1. README.md 更新

#### 主要改进
- **JAR 路径更新**：修正为实际路径 `quarkdown/build/libs/quarkdown.jar`
- **安装指南增强**：添加虚拟环境创建步骤
- **配置说明完善**：提供具体的绝对路径示例
- **运行指南详细化**：包含启动命令和验证步骤
- **故障排除扩展**：新增6个常见问题的解决方案

#### 新增故障排除内容
1. MCP 服务器启动错误（TypeError 解决方案）
2. 模块导入错误（相对导入问题）
3. Java 环境问题
4. JAR 文件路径配置
5. 权限错误处理
6. 端口冲突解决

#### 版本兼容性说明
- MCP SDK: 需要 1.0.0+
- Python: 支持 3.8+，推荐 3.11+
- Java: 需要 11+

### 2. requirements.txt 重构

#### 核心依赖优化
```txt
# 核心依赖 - 运行 MCP 服务器所需的最小依赖
mcp>=1.0.0
pathlib2>=2.3.0; python_version<'3.4'
typing-extensions>=4.0.0; python_version<'3.8'
```

#### 开发依赖分类
- 测试框架（pytest 系列）
- 代码格式化和检查（black, isort, flake8, mypy）
- 性能监控（psutil, aiofiles）
- 文档生成（sphinx 系列）
- 安全扫描（bandit, safety）

### 3. requirements-dev.txt 新增

#### 完整开发工具链
```txt
# 测试框架
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-xdist>=3.2.0

# 代码质量
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0

# 性能和调试
psutil>=5.9.0
memory-profiler>=0.60.0
ipdb>=0.13.0
rich>=13.0.0
```

### 4. setup.py 新增

#### 传统安装支持
- 支持 `pip install -e .` 和 `pip install -e ".[dev]"`
- 完整的元数据配置
- 多种可选依赖组合
- 控制台脚本入口点

### 5. pyproject.toml 更新

#### 版本升级
- 版本号：0.1.0 → 1.0.0
- 开发状态：Alpha → Beta

#### 依赖分组优化
```toml
[project.optional-dependencies]
test = ["pytest>=7.0.0", ...]
lint = ["black>=23.0.0", ...]
docs = ["sphinx>=6.0.0", ...]
performance = ["psutil>=5.9.0", ...]
security = ["bandit>=1.7.0", ...]
debug = ["ipdb>=0.13.0", ...]
build = ["build>=0.10.0", ...]
analysis = ["radon>=6.0.0", ...]
dev = ["quarkdown-mcp[test,lint,docs,performance,security,debug,build,analysis]"]
```

#### 工具配置完善
- **Black**: 代码格式化配置
- **isort**: 导入排序配置
- **MyPy**: 类型检查配置
- **Pytest**: 测试框架配置
- **Coverage**: 代码覆盖率配置
- **Bandit**: 安全扫描配置

### 6. setup.cfg 新增

#### Flake8 配置
```cfg
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
max-complexity = 10
per-file-ignores =
    __init__.py:F401
    tests/*:S101,S106
```

#### Coverage 配置
- 源码目录配置
- 排除文件设置
- 报告格式配置

## 安装方式更新

### 核心安装
```bash
# 最小安装
pip install -r requirements.txt

# 或使用 setup.py
pip install -e .
```

### 开发环境安装
```bash
# 方式1：分别安装
pip install -r requirements.txt -r requirements-dev.txt

# 方式2：使用 setup.py
pip install -e ".[dev]"

# 方式3：选择性安装
pip install -e ".[test,lint]"
```

## MCP 服务器修复历史

### 最新修复记录 (2024-12-27)

### 问题描述
用户在配置并运行 MCP 服务器时遇到以下错误：
```
TypeError: Server.get_capabilities() missing 2 required positional arguments: 'notification_options' and 'experimental_capabilities'
```

### 根本原因分析
1. **MCP SDK 版本兼容性问题**：项目使用的是 MCP 1.0+ 版本，但代码中的 `get_capabilities()` 方法调用方式不符合新版本要求
2. **NotificationOptions 缺失**：新版本 MCP SDK 要求正确初始化 `NotificationOptions` 对象
3. **模块导入路径错误**：工具模块的导入路径与实际文件名不匹配

### 解决方案

#### 1. 修复 NotificationOptions 导入和使用
- 添加正确的导入：`from mcp.server.lowlevel import NotificationOptions`
- 创建 NotificationOptions 实例：
  ```python
  notification_options = NotificationOptions(
      tools_changed=True,
      resources_changed=True,
      prompts_changed=True
  )
  ```

#### 2. 重构服务器初始化
- 移除直接调用 `server.get_capabilities()` 的方式
- 创建独立的 `get_capabilities()` 函数
- 在 `InitializationOptions` 中正确传递参数：
  ```python
  InitializationOptions(
      server_name="quarkdown-mcp",
      server_version="1.0.0",
      capabilities=get_capabilities(),
      notification_options=notification_options,
      experimental_capabilities={}
  )
  ```

#### 3. 修正模块导入路径
修正工具模块导入，使用实际存在的文件名：
- `compile_document` → `compile`
- `validate_markdown` → `validate`
- `preview_server` → `preview`
- `convert_batch` → `batch`

### 验证结果
- ✅ 成功导入所有 MCP 服务器模块
- ✅ 配置正确加载，JAR 路径指向正确位置
- ✅ 服务器实例创建成功
- ✅ 5个工具正确注册：
  - compile_document
  - create_project
  - validate_markdown
  - preview_server
  - convert_batch

### 技术要点
1. **MCP 协议兼容性**：确保代码与 MCP 1.0+ SDK 兼容
2. **通知机制**：正确配置工具、资源和提示的变更通知
3. **模块结构**：保持清晰的模块导入和依赖关系
4. **错误处理**：提供详细的错误信息和调试支持

## 项目结构
```
quarkdown-mcp/
├── src/quarkdown_mcp/
│   ├── server.py              # 主服务器实现
│   ├── core/
│   │   └── config.py          # 配置管理
│   └── tools/                 # 工具实现
│       ├── compile.py         # 文档编译工具
│       ├── create_project.py  # 项目创建工具
│       ├── validate.py        # Markdown 验证工具
│       ├── preview.py         # 预览服务器工具
│       └── batch.py           # 批量转换工具
├── test/                      # 测试文件目录
├── config.example.json        # 配置示例
├── test_server_config.py      # 服务器配置测试脚本
└── quarkdown/build/libs/quarkdown.jar  # Quarkdown JAR 文件
```

## 下一步计划
1. 完善单元测试覆盖
2. 添加集成测试
3. 优化错误处理和日志记录
4. 完善文档和使用指南

## 开发环境
- Python 3.12.0
- MCP SDK 1.0+
- macOS 开发环境
- 使用 pyenv 进行 Python 版本管理