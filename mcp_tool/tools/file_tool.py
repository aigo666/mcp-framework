"""
综合文件处理工具，根据文件类型自动选择合适的处理方式
"""

import os
import traceback
from typing import Dict, List, Any
import mcp.types as types
from . import BaseTool, ToolRegistry
from .pdf_tool import PdfTool
from .word_tool import WordTool
from .excel_tool import ExcelTool

@ToolRegistry.register
class FileTool(BaseTool):
    """
    综合文件处理工具，根据文件扩展名自动选择合适的处理方式
    支持的文件类型：
    - PDF文件 (.pdf)
    - Word文档 (.doc, .docx)
    - Excel文件 (.xls, .xlsx, .xlsm)
    """
    
    name = "file"
    description = "解析文件内容，支持PDF、Word和Excel格式"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文件的本地路径，例如'/path/to/document.pdf'",
            }
        },
    }
    
    def __init__(self):
        """初始化各种文件处理工具"""
        super().__init__()
        self.pdf_tool = PdfTool()
        self.word_tool = WordTool()
        self.excel_tool = ExcelTool()
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        根据文件类型选择合适的处理工具
        
        Args:
            arguments: 参数字典，必须包含'file_path'键
            
        Returns:
            文件内容列表
        """
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="错误: 缺少必要参数 'file_path'"
            )]
        
        file_path = arguments["file_path"]
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不存在: {file_path}"
            )]
        
        # 获取文件扩展名（转换为小写）
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # 根据文件扩展名选择处理工具
            if file_ext == '.pdf':
                return await self.pdf_tool.execute(arguments)
            elif file_ext in ['.doc', '.docx']:
                return await self.word_tool.execute(arguments)
            elif file_ext in ['.xls', '.xlsx', '.xlsm']:
                return await self.excel_tool.execute(arguments)
            else:
                return [types.TextContent(
                    type="text",
                    text=f"错误: 不支持的文件类型: {file_ext}"
                )]
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 处理文件时发生错误: {str(e)}\n{error_details}"
            )] 