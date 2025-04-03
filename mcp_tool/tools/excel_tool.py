import os
import pandas as pd
import json
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class ExcelTool(BaseTool):
    """Excel解析工具，用于解析Excel文件内容"""
    name = "parse_excel"
    description = "Parses an Excel file and returns its content including all sheets"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the Excel file to parse",
            }
        },
    }
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """解析Excel文件并返回内容"""
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="Error: Missing required argument 'file_path'"
            )]
        
        file_path = arguments["file_path"]
        # 处理文件路径，支持挂载目录的转换
        file_path = self.process_file_path(file_path)
        
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"Error: File not found at path: {file_path}"
            )]
        
        if not file_path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
            return [types.TextContent(
                type="text",
                text=f"Error: File is not an Excel file: {file_path}"
            )]
        
        try:
            # 读取Excel文件中的所有sheet
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            result = {
                "file_name": os.path.basename(file_path),
                "sheet_count": len(sheet_names),
                "sheets": {}
            }
            
            # 解析每个sheet
            for sheet_name in sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # 将DataFrame转换为字典
                sheet_data = df.to_dict(orient='records')
                
                # 获取列名
                columns = df.columns.tolist()
                
                # 获取行数和列数
                row_count = len(df)
                column_count = len(columns)
                
                result["sheets"][sheet_name] = {
                    "row_count": row_count,
                    "column_count": column_count,
                    "columns": columns,
                    "data": sheet_data
                }
            
            # 将结果转换为JSON字符串，并格式化输出
            result_json = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            
            return [types.TextContent(
                type="text",
                text=result_json
            )]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error: Failed to parse Excel file: {str(e)}"
            )] 