# MCP开发框架

一个强大的MCP（Model Context Protocol）开发框架，用于创建与大语言模型交互的自定义工具。该框架提供了一套完整的工具集，可以轻松地扩展Cursor IDE的功能，实现网页内容获取、PDF文档处理和Word文档解析等高级功能。

## 主要功能

本框架提供了以下核心功能：

### 1. 网页内容获取

使用`url`工具可以获取任何网页的内容，支持完整的HTTP错误处理和超时管理。

- **用法**: `url https://example.com`
- **参数**: `url` - 要获取内容的网站URL
- **返回**: 网页的文本内容

### 2. PDF文档处理

框架提供了两种PDF处理工具，满足不同场景的需求：

#### 完整PDF解析 (file)

- **用法**: `file /path/to/document.pdf`
- **功能**: 解析PDF文档并提取文本和图片内容
- **参数**: `file_path` - PDF文件的本地路径
- **返回**: 文档的文本内容（Markdown格式）和图片信息
- **特点**: 使用PymuPDF4llm库提供高质量的文本提取和图像处理

#### 快速PDF预览 (quick_pdf)

- **用法**: `quick_pdf /path/to/document.pdf`
- **功能**: 快速预览PDF文档内容（仅提取文本）
- **参数**: `file_path` - PDF文件的本地路径
- **返回**: 文档的文本内容（Markdown格式）
- **适用场景**: 大型PDF文件或只需要文本内容时

### 3. Word文档解析

使用`word`工具可以解析Word文档（.docx和.doc格式），提取文本内容、表格和图片信息。

- **用法**: `word /path/to/document.docx`
- **功能**: 解析Word文档并提取文本内容、表格和图片信息
- **参数**: `file_path` - Word文档的本地路径
- **返回**: 文档的文本内容（Markdown格式）、表格和图片信息
- **特点**: 使用python-docx库提供高质量的文本和表格提取

## 文档处理技术特点

本框架使用了多种技术来优化文档处理性能：

### PDF处理

1. **多层次处理策略**:
   - 首先尝试使用PyMuPDF（fitz）提取内容（速度快、准确度高）
   - 如果失败，回退到PymuPDF4llm（专为大语言模型优化）
   - 最后尝试PyPDF2作为最终备用方案

2. **性能优化**:
   - 限制处理的最大页数（完整模式: 30页，快速模式: 50页）
   - 图片处理优化（DPI调整、大小限制）
   - 多线程处理加速

3. **错误处理**:
   - 详细的错误信息和提示
   - 备用处理方法，确保服务稳定性
   - 超时保护机制（5分钟超时设置）

### Word文档处理

1. **文档结构解析**:
   - 提取文档属性（标题、作者、创建时间等）
   - 段落内容提取，保留原始格式
   - 表格转换为Markdown格式

2. **图片信息**:
   - 提供文档中图片的数量信息
   - 图片引用关系识别

## 模块化工具框架

本框架采用模块化设计，便于扩展和维护：

```
mcp_simple_tool/
├── tools/
│   ├── __init__.py        # 定义工具基类和注册器
│   ├── loader.py          # 工具加载器，自动加载所有工具
│   ├── url_tool.py        # URL工具实现
│   ├── pdf_tool.py        # PDF解析工具实现
│   ├── quick_pdf_tool.py  # 快速PDF预览工具实现
│   └── word_tool.py       # Word文档解析工具实现
├── __init__.py
├── __main__.py
└── server.py              # MCP服务器实现
```

### 框架特点

1. **自动工具发现**:
   - 工具加载器自动发现和加载所有工具
   - 无需手动注册，只需创建新工具文件

2. **统一接口**:
   - 所有工具继承自`BaseTool`基类
   - 标准化的输入和输出格式

3. **简单扩展**:
   - 只需创建新的工具类并使用`@ToolRegistry.register`装饰器
   - 框架自动处理工具的注册和调用

## 如何开发新工具

1. 在`tools`目录下创建一个新的Python文件，如`your_tool.py`
2. 导入必要的依赖和基类
3. 创建一个继承自`BaseTool`的工具类
4. 使用`@ToolRegistry.register`装饰器注册工具
5. 实现工具的`execute`方法

### 工具模板示例

```python
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class YourTool(BaseTool):
    """您的工具描述"""
    name = "your_tool_name"  # 工具的唯一标识符
    description = "您的工具描述"  # 工具的描述信息，将显示给用户
    input_schema = {
        "type": "object",
        "required": ["param1"],  # 必需的参数
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数1的描述",
            },
            "param2": {
                "type": "integer",
                "description": "参数2的描述（可选）",
            }
        },
    }
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """执行工具逻辑"""
        # 参数验证
        if "param1" not in arguments:
            return [types.TextContent(
                type="text",
                text="Error: Missing required argument 'param1'"
            )]
            
        # 获取参数
        param1 = arguments["param1"]
        param2 = arguments.get("param2", 0)  # 获取可选参数，提供默认值
        
        # 执行工具逻辑
        result = f"处理参数: {param1}, {param2}"
        
        # 返回结果
        return [types.TextContent(
            type="text",
            text=result
        )]
```

## 部署方式

您可以通过以下方式部署和使用本框架：

### Docker部署（推荐）

该项目包括Docker支持，便于部署：

1. 初始设置：
```bash
# 克隆仓库
git clone https://github.com/your-username/mcp-development-framework.git
cd mcp-development-framework

# 创建环境文件
cp .env.example .env
```

2. 使用Docker Compose构建并运行：
```bash
# 构建并启动服务器
docker compose up --build -d

# 查看日志
docker compose logs -f

# 检查服务器状态
docker compose ps

# 暂停容器（不删除）
docker compose pause

# 恢复已暂停的容器
docker compose unpause

# 停止服务器
docker compose down
```

3. 服务器将可以在以下地址访问：
   - SSE端点: http://localhost:8000/sse

4. 连接到Cursor IDE：
   - 打开Cursor设置 → 功能
   - 添加新的MCP服务器
   - 类型: 选择"sse"
   - URL: 输入`http://localhost:8000/sse`

5. 访问本地文件：
   - 默认情况下，Docker容器无法访问主机（您的电脑）上的文件
   - 在`docker-compose.yml`文件中配置卷挂载，将本地目录挂载到容器内
   - 例如，如果挂载了`/Users/username/Documents`到`/host_docs`，则使用`/host_docs/file.pdf`访问文件

### 传统Python部署

首先，安装uv包管理器和系统依赖：

```bash
# 安装uv
pip install uv

# 安装PDF处理的系统依赖
# 在Ubuntu/Debian上
sudo apt-get install poppler-utils
# 在macOS上
brew install poppler
# 在Windows上
# 从http://blog.alivate.com.au/poppler-windows/下载并安装poppler
# 并将bin目录添加到您的PATH中
```

然后安装和运行服务器：

```bash
# 安装开发依赖的包
uv pip install -e ".[dev]"

# 使用stdio传输（默认）
uv run mcp-simple-tool

# 使用自定义端口的SSE传输
uv run mcp-simple-tool --transport sse --port 8000

# 运行测试
uv run pytest -v
```

## 环境变量配置

可用的环境变量（可以在`.env`中设置）：

- `MCP_SERVER_PORT`（默认: 8000） - 服务器运行的端口
- `MCP_SERVER_HOST`（默认: 0.0.0.0） - 绑定服务器的主机
- `DEBUG`（默认: false） - 启用调试模式
- `MCP_USER_AGENT` - 网站抓取的自定义User-Agent

## 依赖项

本项目使用以下主要依赖：

- `mcp` - Model Context Protocol实现
- `PyPDF2` - PDF文档处理
- `PyMuPDF` - 高性能PDF文档处理
- `pymupdf4llm` - 为大语言模型优化的PDF处理
- `pdf2image` - PDF转图像处理
- `python-docx` - Word文档处理
- `httpx` - 异步HTTP客户端
- `anyio` - 异步I/O支持
- `click` - 命令行接口

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。

