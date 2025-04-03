"""
CSV文件处理工具
"""

import os
import pandas as pd
import traceback
from typing import Dict, List, Any
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class CsvTool(BaseTool):
    """
    CSV文件处理工具，用于解析CSV文件内容
    """
    
    name = "parse_csv"
    description = "解析CSV文件内容，支持各种编码格式"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "CSV文件的本地路径，例如'/path/to/data.csv'",
            },
            "encoding": {
                "type": "string",
                "description": "文件编码格式，例如'utf-8'、'gbk'等，默认自动检测",
            }
        },
    }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """
        解析CSV文件内容
        
        Args:
            arguments: 参数字典，必须包含'file_path'键，可选'encoding'键
        
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
        
        try:
            # 尝试自动检测编码
            encoding = arguments.get("encoding", None)
            if encoding is None:
                try:
                    import chardet
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        encoding = chardet.detect(raw_data)['encoding']
                except ImportError:
                    encoding = 'utf-8'  # 如果没有chardet，默认使用utf-8
            
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 获取基本信息
            info = {
                "文件名": os.path.basename(file_path),
                "行数": len(df),
                "列数": len(df.columns),
                "列名": list(df.columns),
                "数据预览": df.head().to_string()
            }
            
            # 生成描述性统计
            stats = df.describe().to_string()
            
            # 组合结果
            result = (
                f"CSV文件解析结果:\n\n"
                f"基本信息:\n"
                f"- 文件名: {info['文件名']}\n"
                f"- 行数: {info['行数']}\n"
                f"- 列数: {info['列数']}\n"
                f"- 列名: {', '.join(info['列名'])}\n\n"
                f"数据预览:\n{info['数据预览']}\n\n"
                f"描述性统计:\n{stats}"
            )
            
            return [types.TextContent(
                type="text",
                text=result
            )]
            
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 处理CSV文件时发生错误: {str(e)}\n{error_details}"
            )] 