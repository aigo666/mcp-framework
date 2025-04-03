'''
Author: 刘彦志 lyzgithub@163.com
Date: 2025-03-11 11:25:58
LastEditors: 刘彦志 lyzgithub@163.com
LastEditTime: 2025-04-01 17:54:16
FilePath: /mcp-framework/mcp_tool/tools/file_tool.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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
from .csv_tool import CsvTool
from .markdown_tool import MarkdownTool

@ToolRegistry.register
class FileTool(BaseTool):
    """
    综合文件处理工具，根据文件扩展名自动选择合适的处理方式
    支持的文件类型：
    - PDF文件 (.pdf)
    - Word文档 (.doc, .docx)
    - Excel文件 (.xls, .xlsx, .xlsm)
    - CSV文件 (.csv)
    - Markdown文件 (.md)
    """
    
    name = "parse_file"
    description = "解析文件内容，支持PDF、Word、Excel、CSV和Markdown格式"
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
        self.csv_tool = CsvTool()
        self.markdown_tool = MarkdownTool()
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        解析文件内容
        
        Args:
            arguments: 参数字典，必须包含'file_path'键
        
        Returns:
            解析结果列表
        """
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="错误: 缺少必要参数 'file_path'"
            )]
        
        file_path = arguments["file_path"]
        # 处理文件路径，支持挂载目录的转换
        file_path = self.process_file_path(file_path)
        
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
            elif file_ext == '.csv':
                return await self.csv_tool.execute(arguments)
            elif file_ext == '.md':
                return await self.markdown_tool.execute(arguments)
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