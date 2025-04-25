# MCP开发框架
[![smithery badge](https://smithery.ai/badge/@aigo666/mcp-framework)](https://smithery.ai/server/@aigo666/mcp-framework)

一个强大的MCP（Model Context Protocol）开发框架，用于创建与大语言模型交互的自定义工具。该框架提供了一套完整的工具集，可以轻松地扩展Cursor IDE的功能，实现网页内容获取、文件处理（PDF、Word、Excel、CSV、Markdown）以及AI对话等高级功能。它具有强大的MCP工具扩展能力，使开发者能够快速构建和集成各种自定义工具。

<a href="https://glama.ai/mcp/servers/@aigo666/mcp-framework">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@aigo666/mcp-framework/badge" />
</a>

## 🔥 最新更新

- **图片处理增强**: 现在PDF和Word文档处理工具支持直接返回文档中的图片内容，不仅返回OCR文本，还通过MCP协议的ImageContent类型直接展示原始图片，实现真正的全文内容返回。
- **Docker部署支持**: 提供了完整的Docker部署方案，方便本地或服务器快速部署MCP服务。

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
    - `full` - 完整解析模式，提取文本和图片内容（默认）
- **返回**: 
  - 快速预览模式：文档的文本内容
  - 完整解析模式：文档的文本内容和**原始图片**（不仅是OCR文本）
- **特点**:
  - 支持图片直接显示：通过MCP的ImageContent类型返回图片
  - OCR文本识别：自动识别图片中的文字内容
  - 多语言支持：支持中英文等多语言OCR识别

### 3. Word文档解析

使用`parse_word`工具可以解析Word文档，提取文本、表格和图片信息。

- **用法**: `parse_word /path/to/document.docx`
- **功能**: 解析Word文档并提取文本内容、表格和图片信息
- **参数**: `file_path` - Word文档的本地路径
- **返回**: 文档的文本内容、表格和**原始图片**
- **特点**: 
  - 使用python-docx库提供高质量的文本和表格提取
  - 支持图片直接显示：完整提取并以ImageContent形式返回文档中的图片
  - 高质量表格格式化：将Word表格转换为易读的格式

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
   - PDF处理：支持快速预览和完整解析两种模式，**支持图片直接返回**
   - Word处理：精确提取文本、表格和图片，**支持文档内图片直接显示**
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

6. **容器化部署**
   - 提供Docker部署方案
   - 支持环境变量配置
   - 文件系统挂载简化部署

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

## 部署指南

本框架提供了两种部署方式：

### 方式一：本地Python部署

1. 克隆仓库
```bash
git clone https://github.com/yourusername/mcp-framework.git
cd mcp-framework
```

2. 安装依赖
```bash
pip install -e .
```

3. 运行服务
```bash
python -m mcp_tool --transport sse --port 8000
```

### 方式二：Docker部署

1. 克隆仓库
```bash
git clone https://github.com/yourusername/mcp-framework.git
cd mcp-framework
```

2. 使用部署脚本
```bash
chmod +x deploy.sh
./deploy.sh
```

3. 配置部署环境
在`.env`文件中配置挂载目录等设置：
```
HOST_MOUNT_SOURCE=/path/to/your/documents
HOST_MOUNT_TARGET=/documents
```

更多详细部署指南请参考[DEPLOY.md](DEPLOY.md)。

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
      
        # 返回结果 - 支持文本和图片混合返回
        return [types.TextContent(
            type="text",
            text=result
        )]
```

### 图片处理示例

如果您需要在工具中返回图片，可以使用以下代码片段：

```python
import base64
import imghdr

def get_image_mime_type(image_bytes: bytes) -> str:
    """获取图片的MIME类型"""
    image_type = imghdr.what(None, image_bytes)
    if image_type:
        return f"image/{image_type}"
    return "image/png"  # 默认返回PNG类型

def encode_image_base64(image_bytes: bytes) -> str:
    """将图片编码为base64格式"""
    return base64.b64encode(image_bytes).decode('utf-8')

# 在执行方法中返回图片
image_bytes = get_image_data()  # 获取图片数据
mime_type = get_image_mime_type(image_bytes)
image_base64 = encode_image_base64(image_bytes)

return [
    types.TextContent(type="text", text="图片说明文本"),
    types.ImageContent(
        type="image",
        data=image_base64,
        mimeType=mime_type
    )
]
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