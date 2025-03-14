# MCP开发框架
[![smithery badge](https://smithery.ai/badge/@aigo666/mcp-framework)](https://smithery.ai/server/@aigo666/mcp-framework)

一个强大的MCP（Model Context Protocol）开发框架，用于创建与大语言模型交互的自定义工具。该框架提供了一套完整的工具集，可以轻松地扩展Cursor IDE的功能，实现网页内容获取、文件处理（PDF、Word、Excel）以及AI对话等高级功能。

## 主要功能

本框架提供了以下核心功能：

### 1. 综合文件处理

使用`file`工具可以自动识别文件类型并选择合适的处理方式，支持PDF、Word和Excel文件。

- **用法**: `file /path/to/document`
- **支持格式**: 
  - PDF文件 (.pdf)
  - Word文档 (.doc, .docx)
  - Excel文件 (.xls, .xlsx, .xlsm)
- **参数**: `file_path` - 文件的本地路径
- **返回**: 根据文件类型返回相应的处理结果

### 3. PDF文档处理

使用`pdf`工具可以处理PDF文档，支持两种处理模式：

- **用法**: `pdf /path/to/document.pdf [mode]`
- **参数**: 
  - `file_path` - PDF文件的本地路径
  - `mode` - 处理模式（可选）：
    - `quick` - 快速预览模式，仅提取文本内容
    - `full` - 完整解析模式，提取文本和图片内容（默认）
- **返回**: 
  - 快速预览模式：文档的文本内容
  - 完整解析模式：文档的文本内容和图片
- **特点**: 
  - 使用PyMuPDF提供高质量的文本提取和图像处理
  - 自动处理大型文件
  - 支持图片提取和保存

### 4. Word文档解析

使用`word`工具可以解析Word文档，提取文本、表格和图片信息。

- **用法**: `word /path/to/document.docx`
- **功能**: 解析Word文档并提取文本内容、表格和图片信息
- **参数**: `file_path` - Word文档的本地路径
- **返回**: 文档的文本内容、表格和图片信息
- **特点**: 使用python-docx库提供高质量的文本和表格提取

### 5. Excel文件处理

使用`excel`工具可以解析Excel文件，提供完整的表格数据和结构信息。

- **用法**: `excel /path/to/spreadsheet.xlsx`
- **功能**: 解析Excel文件的所有工作表
- **参数**: `file_path` - Excel文件的本地路径
- **返回**: 
  - 文件基本信息（文件名、工作表数量）
  - 每个工作表的详细信息：
    - 行数和列数
    - 列名列表
    - 完整的表格数据
- **特点**: 
  - 使用pandas和openpyxl提供高质量的表格数据处理
  - 支持多工作表处理
  - 自动处理数据类型转换

### 6. 网页内容获取

使用`url`工具可以获取任何网页的内容。

- **用法**: `url https://example.com`
- **参数**: `url` - 要获取内容的网站URL
- **返回**: 网页的文本内容
- **特点**: 
  - 完整的HTTP错误处理
  - 超时管理
  - 自动编码处理

## 技术特点

本框架采用了多种技术来优化文件处理性能：

1. **智能文件类型识别**
   - 自动根据文件扩展名选择合适的处理工具
   - 提供统一的文件处理接口

2. **高效的文档处理**
   - PDF处理：支持快速预览和完整解析两种模式
   - Word处理：精确提取文本、表格和图片
   - Excel处理：高效处理大型表格数据

3. **内存优化**
   - 使用临时文件管理大型文件
   - 自动清理临时资源
   - 分块处理大型文档

4. **错误处理**
   - 完整的异常捕获和处理
   - 详细的错误信息反馈
   - 优雅的失败处理机制

## 文档处理技术细节

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

## 项目结构

本框架采用模块化设计，便于扩展和维护：

```
mcp_tool/
├── tools/
│   ├── __init__.py        # 定义工具基类和注册器
│   ├── loader.py          # 工具加载器，自动加载所有工具
│   ├── file_tool.py       # 综合文件处理工具
│   ├── pdf_tool.py        # PDF解析工具
│   ├── word_tool.py       # Word文档解析工具
│   ├── excel_tool.py      # Excel文件处理工具
│   └── url_tool.py        # URL工具实现
├── __init__.py
├── __main__.py
└── server.py              # MCP服务器实现
```

## 开发指南

### 如何开发新工具

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

## 部署指南

### 环境变量配置

在开始部署之前，请确保配置以下环境变量：

1. **MaxKB工具配置**:
   - `MAXKB_HOST` - MaxKB API的主机地址
   - `MAXKB_CHAT_ID` - 对话ID
   - `MAXKB_APPLICATION_ID` - 应用ID
   - `MAXKB_AUTHORIZATION` - 授权令牌

2. **其他配置**（可选）:
   - `HTTPCORE_TIMEOUT` - HTTP请求超时时间（默认60秒）
   - `HTTPX_TIMEOUT` - HTTPX客户端超时时间（默认60秒）

### Docker部署（推荐）

1. 初始设置：
```bash
# 克隆仓库
git clone https://github.com/your-username/mcp-framework.git
cd mcp-framework

# 创建环境文件
cp .env.example .env
```

2. 使用Docker Compose：
```bash
# 构建并启动
docker compose up --build -d

# 查看日志
docker compose logs -f

# 管理容器
docker compose ps
docker compose pause
docker compose unpause
docker compose down
```

3. 访问服务：
   - SSE端点: http://localhost:8000/sse

4. Cursor IDE配置：
- 设置 → 功能 → 添加MCP服务器
- 类型: "sse"
- URL: `http://localhost:8000/sse`

### 传统Python部署

1. 安装系统依赖：
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install poppler tesseract tesseract-lang

# Windows
# 1. 下载并安装Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# 2. 将Tesseract添加到系统PATH
```

2. 安装Python依赖：
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

3. 启动服务：
```bash
python -m mcp_tool
```

## 配置说明

### 环境变量配置

在`.env`文件中配置以下环境变量：

```bash
# Server Configuration
MCP_SERVER_PORT=8000        # 服务器端口
MCP_SERVER_HOST=0.0.0.0     # 服务器主机

# MaxKB配置
MAXKB_HOST=http://host.docker.internal:8080  # MaxKB API主机地址
MAXKB_CHAT_ID=your_chat_id_here              # MaxKB聊天ID
MAXKB_APPLICATION_ID=your_application_id_here # MaxKB应用ID
MAXKB_AUTHORIZATION=your_authorization_key    # MaxKB授权密钥

# 调试模式
DEBUG=false                 # 是否启用调试模式

# 用户代理
MCP_USER_AGENT="MCP Test Server (github.com/modelcontextprotocol/python-sdk)"

# 本地目录挂载配置
HOST_MOUNT_SOURCE=/path/to/your/local/directory  # 本地目录路径
HOST_MOUNT_TARGET=/host_files                    # 容器内挂载路径
```

### 本地目录挂载

框架支持将本地目录挂载到容器中，以便工具可以访问本地文件。配置方法：

1. 在`.env`文件中设置`HOST_MOUNT_SOURCE`和`HOST_MOUNT_TARGET`环境变量
2. `HOST_MOUNT_SOURCE`是你本地机器上的目录路径
3. `HOST_MOUNT_TARGET`是容器内的挂载路径（默认为`/host_files`）

使用工具时，可以直接引用本地文件路径，框架会自动将其转换为容器内的路径。例如：

```
# 使用PDF工具处理本地文件
pdf "/Users/username/Documents/example.pdf"

# 框架会自动将路径转换为容器内路径
# 例如："/host_files/example.pdf"
```

这样，你就可以在不修改工具代码的情况下，轻松访问本地文件。

## 依赖项

主要依赖：
- `mcp`: Model Context Protocol实现
- `PyMuPDF`: PDF文档处理
- `python-docx`: Word文档处理
- `pandas`和`openpyxl`: Excel文件处理
- `httpx`: 异步HTTP客户端
- `anyio`: 异步I/O支持
- `click`: 命令行接口

## 贡献指南

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。

