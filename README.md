# MCP开发框架
[![Verified on MseeP](https://mseep.ai/badge.svg)](https://mseep.ai/app/34780cde-ee17-4a7b-b9ee-356f41fc9e77) [![smithery badge](https://smithery.ai/badge/@aigo666/mcp-framework)](https://smithery.ai/server/@aigo666/mcp-framework)

一个强大的MCP（Model Context Protocol）开发框架，用于创建与大语言模型交互的自定义工具。该框架提供了一套完整的工具集，可以轻松地扩展Cursor IDE的功能，实现网页内容获取、文件处理（PDF、Word、Excel、CSV、Markdown）以及AI对话等高级功能。它具有强大的MCP工具扩展能力，使开发者能够快速构建和集成各种自定义工具。

<a href="https://glama.ai/mcp/servers/@aigo666/mcp-framework">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@aigo666/mcp-framework/badge" />
</a>

<details>
<summary>🔥 最新特性：文档图片内容显示与理解</summary>

最新版本现在支持在PDF和Word文档处理中，直接返回原始图片内容并进行OCR识别，使大语言模型能够同时理解文档中的文本和图像内容：

- **图片内容直接显示**：文档中的图表、图像等可以直接在对话中显示，无需额外工具
- **OCR文本识别**：自动提取图片中的文字内容，支持中英文多语言
- **图片内容理解**：大模型可以"看到"文档中的图片，并基于图片内容进行分析和回答
- **完整文档内容返回**：真正实现文档的全内容理解，包括文本、表格和图像

这使得AI模型能够更全面地理解和分析文档内容，特别是对于包含图表、表单、流程图或其他可视化信息的文档尤为有价值。
</details>

## 主要功能

<details>
<summary>点击展开查看框架提供的核心功能</summary>

本框架提供了以下核心功能：

### 1. 综合文件处理

使用`parse_file`工具可以自动识别文件类型并选择合适的处理方式，支持PDF、Word、Excel、CSV和Markdown文件。

- **用法**: `parse_file /path/to/document`
- **支持格式**: 
  - PDF文件 (.pdf)
  - Word文档 (.doc, .docx)
  - Excel文件 (.xls, .xlsx, .xlsm)
  - CSV文件 (.csv)
  - Markdown文件 (.md)
- **参数**: `file_path` - 文件的本地路径
- **返回**: 根据文件类型返回相应的处理结果

### 2. PDF文档处理

使用`parse_pdf`工具可以处理PDF文档，支持两种处理模式：

- **用法**: `parse_pdf /path/to/document.pdf [mode]`
- **参数**: 
  - `file_path` - PDF文件的本地路径
  - `mode` - 处理模式（可选）：
    - `quick` - 快速预览模式，仅提取文本内容
    - `full` - 完整解析模式，提取文本、图片内容和OCR文本（默认）
- **返回**: 
  - 快速预览模式：文档的文本内容
  - 完整解析模式：文档的文本内容、原始图片和OCR识别结果

### 3. Word文档解析

使用`parse_word`工具可以解析Word文档，提取文本、表格和图片信息。

- **用法**: `parse_word /path/to/document.docx`
- **功能**: 解析Word文档并提取文本内容、表格和图片
- **参数**: `file_path` - Word文档的本地路径
- **返回**: 文档的文本内容、表格和原始图片
- **特点**: 同时提供文档内嵌图像的显示和分析功能

### 4. Excel文件处理

使用`parse_excel`工具可以解析Excel文件，提供完整的表格数据和结构信息。

- **用法**: `parse_excel /path/to/spreadsheet.xlsx`
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

### 5. CSV文件处理

使用`parse_csv`工具可以解析CSV文件，提供完整的数据分析和预览功能。

- **用法**: `parse_csv /path/to/data.csv`
- **功能**: 解析CSV文件并提供数据分析
- **参数**: 
  - `file_path` - CSV文件的本地路径
  - `encoding` - 文件编码格式（可选，默认自动检测）
- **返回**: 
  - 文件基本信息（文件名、行数、列数）
  - 列名列表
  - 数据预览（前5行）
  - 描述性统计信息
- **特点**: 
  - 自动编码检测
  - 支持多种编码格式（UTF-8、GBK等）
  - 提供数据统计分析
  - 智能数据类型处理

### 6. Markdown文件解析

使用`parse_markdown`工具可以解析Markdown文件，提取文本内容、标题结构和列表等信息。

- **用法**: `parse_markdown /path/to/document.md`
- **功能**: 解析Markdown文件并提取标题结构、列表和文本内容
- **参数**: `file_path` - Markdown文件的本地路径
- **返回**: 
  - 文件基本信息（文件名、大小、修改时间等）
  - 标题结构层级展示
  - 内容元素统计（代码块、列表、链接、图片、表格等）
  - 原始Markdown内容
- **特点**: 
  - 自动识别各级标题和结构
  - 智能统计内容元素
  - 完整的标题层级展示

### 7. 网页内容获取

使用`url`工具可以获取任何网页的内容。

- **用法**: `url https://example.com`
- **参数**: `url` - 要获取内容的网站URL
- **返回**: 网页的文本内容
- **特点**: 
  - 完整的HTTP错误处理
  - 超时管理
  - 自动编码处理

### 8. MaxKB AI对话

使用`maxkb`工具可以与MaxKB API进行交互，实现智能对话功能。

- **用法**: `maxkb "您的问题或指令"`
- **功能**: 发送消息到MaxKB API并获取AI回复
- **参数**: 
  - `message` - 要发送的消息内容（必需）
  - `re_chat` - 是否重新开始对话（可选，默认false）
  - `stream` - 是否使用流式响应（可选，默认true）
- **返回**: AI的回复内容
- **特点**: 
  - 支持流式响应
  - 自动重试机制
  - 完整的错误处理
  - 60秒超时保护
  - 保持连接配置优化

</details>

## 技术特点

本框架采用了多种技术来优化文件处理性能：

1. **智能文件类型识别**
   - 自动根据文件扩展名选择合适的处理工具
   - 提供统一的文件处理接口

2. **高效的文档处理**
   - PDF处理：支持快速预览和完整解析两种模式
   - Word处理：精确提取文本、表格和图片
   - Excel处理：高效处理大型表格数据

3. **强大的MCP工具扩展能力**
   - 插件化架构设计，易于扩展
   - 统一的工具注册和调用接口
   - 支持同步和异步工具开发
   - 丰富的工具开发API和辅助函数

4. **内存优化**
   - 使用临时文件管理大型文件
   - 自动清理临时资源
   - 分块处理大型文档

5. **错误处理**
   - 完整的异常捕获和处理
   - 详细的错误信息反馈
   - 优雅的失败处理机制

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
│   ├── csv_tool.py        # CSV文件处理工具
│   ├── markdown_tool.py   # Markdown文件解析工具
│   ├── url_tool.py        # URL工具实现
│   └── maxkb_tool.py      # MaxKB AI对话工具
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

在`.env`文件中配置以下环境变量：

```bash
# Server Configuration
MCP_SERVER_PORT=8000        # 服务器端口
MCP_SERVER_HOST=0.0.0.0     # 服务器主机

# 鉴权配置
MCP_AUTH_URL=http://170.106.105.206:4000/users  # 鉴权服务地址

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

### Docker部署（推荐）

1. 初始设置：
```bash
# 克隆仓库
git clone https://github.com/aigo666/mcp-framework.git
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
- URL: `http://localhost:8000/sse?token=<your-token>` (替换 `<your-token>` 为您的 JWT Token)

## 鉴权配置

<details>
<summary>点击展开查看详细的鉴权配置信息</summary>

SSE 服务现在支持 API 鉴权机制，每个请求都需要携带有效的认证信息：

1. 配置鉴权服务地址：
   - 在 `.env` 文件中设置 `MCP_AUTH_URL` 环境变量（默认为 `http://170.106.105.206:4000/users` 该鉴权地址仅供测试，不保证长期稳定，建议使用以下项目自行部署）

2. 客户端配置：
   - 在 Cursor 插件中配置时，需要在 URL 中添加 `token` 查询参数
   - 格式为 `http://your-server:8000/sse?token=<your-token>`
   - 服务器会自动将 token 转换为 `Bearer <your-token>` 格式发送到鉴权服务

3. 鉴权流程：
   - 当 SSE 服务收到请求时，会从 URL 中提取 token 参数
   - 然后向配置的鉴权地址发送请求，并传递 `Authorization: Bearer <your-token>` 头
   - 只有鉴权成功（返回 200 状态码）的请求才会被处理
   - 鉴权失败的请求会收到 401 Unauthorized 响应

4. 推荐JWT鉴权服务：
   - 我们推荐使用Jason Watmore的Node.js JWT鉴权服务作为参考实现
   - 详细文档和示例代码：https://jasonwatmore.com/nodejs-jwt-authentication-tutorial-with-example-api
   - 该实现提供了完整的用户注册、登录、令牌生成和验证功能
   - 可以无缝集成到本框架的鉴权流程中

</details>

## 部署方式

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