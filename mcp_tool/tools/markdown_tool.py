"""
Markdown文件解析工具，用于解析和提取Markdown文件内容
"""

import os
import traceback
from typing import Dict, List, Any
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class MarkdownTool(BaseTool):
    """
    用于解析Markdown文件的工具，提取文本内容、标题结构和列表等信息
    """
    
    name = "parse_markdown"
    description = "解析Markdown文件内容，提取标题结构、列表和文本内容"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Markdown文件的本地路径，例如'/path/to/document.md'",
            }
        },
    }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        解析Markdown文件
        
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
        
        # 处理文件路径，支持挂载目录的转换
        file_path = self.process_file_path(arguments["file_path"])
        
        return await self._parse_markdown_file(file_path)
    
    async def _parse_markdown_file(self, file_path: str) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        解析Markdown文件内容
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            Markdown文件内容解析结果列表
        """
        results = []
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不存在: {file_path}\n请检查路径是否正确，并确保文件可访问。"
            )]
        
        # 检查文件扩展名
        if not file_path.lower().endswith('.md'):
            return [types.TextContent(
                type="text",
                text=f"错误: 不支持的文件格式: {file_path}\n仅支持.md格式的Markdown文件。"
            )]
        
        try:
            # 添加文件信息
            file_size_kb = os.path.getsize(file_path) / 1024
            results.append(types.TextContent(
                type="text",
                text=f"# Markdown文件解析\n\n文件大小: {file_size_kb:.2f} KB"
            ))
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 基本文件信息
            file_info = f"## 文件基本信息\n\n"
            file_info += f"- 文件名: {os.path.basename(file_path)}\n"
            file_info += f"- 路径: {file_path}\n"
            file_info += f"- 大小: {file_size_kb:.2f} KB\n"
            file_info += f"- 最后修改时间: {os.path.getmtime(file_path)}\n"
            
            results.append(types.TextContent(
                type="text",
                text=file_info
            ))
            
            # 解析Markdown内容结构
            structure = self._analyze_markdown_structure(content)
            results.append(types.TextContent(
                type="text",
                text=structure
            ))
            
            # 添加原始内容
            results.append(types.TextContent(
                type="text",
                text=f"## 原始Markdown内容\n\n```markdown\n{content}\n```"
            ))
            
            # 添加处理完成的提示
            results.append(types.TextContent(
                type="text",
                text="Markdown文件处理完成！"
            ))
            
            return results
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 解析Markdown文件失败: {str(e)}\n"
                     f"可能的原因:\n"
                     f"1. 文件编码不兼容\n"
                     f"2. 文件已损坏\n"
                     f"3. 文件内容格式异常\n\n"
                     f"详细错误信息: {error_details}"
            )]
    
    def _analyze_markdown_structure(self, content: str) -> str:
        """
        分析Markdown文件结构
        
        Args:
            content: Markdown文件内容
            
        Returns:
            结构分析结果
        """
        lines = content.split('\n')
        
        # 分析标题
        headings = {
            "h1": [],
            "h2": [],
            "h3": [],
            "h4": [],
            "h5": [],
            "h6": []
        }
        
        # 计数
        code_blocks = 0
        lists = 0
        links = 0
        images = 0
        tables = 0
        
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            
            # 检测代码块
            if line.startswith('```'):
                in_code_block = not in_code_block
                if not in_code_block:
                    code_blocks += 1
                continue
                
            if in_code_block:
                continue
                
            # 检测标题
            if line.startswith('# '):
                headings["h1"].append(line[2:])
            elif line.startswith('## '):
                headings["h2"].append(line[3:])
            elif line.startswith('### '):
                headings["h3"].append(line[4:])
            elif line.startswith('#### '):
                headings["h4"].append(line[5:])
            elif line.startswith('##### '):
                headings["h5"].append(line[6:])
            elif line.startswith('###### '):
                headings["h6"].append(line[7:])
                
            # 检测列表
            if line.startswith('- ') or line.startswith('* ') or line.startswith('+ ') or \
               (line and line[0].isdigit() and '.' in line[:3]):
                lists += 1
                
            # 检测链接和图片
            if '](' in line:
                if line.count('![') > 0:
                    images += line.count('![')
                links += line.count('](') - line.count('![')
                
            # 检测表格
            if line.startswith('|') and line.endswith('|'):
                tables += 1
                
        # 生成结构报告
        structure = "## Markdown结构分析\n\n"
        
        # 标题结构
        structure += "### 标题结构\n\n"
        has_headings = False
        for level, titles in headings.items():
            if titles:
                has_headings = True
                indent = "  " * (int(level[1]) - 1)
                for title in titles:
                    structure += f"{indent}- {title}\n"
                    
        if not has_headings:
            structure += "文档中未检测到标题结构\n"
            
        # 内容元素统计
        structure += "\n### 内容元素统计\n\n"
        structure += f"- 代码块: {code_blocks} 个\n"
        structure += f"- 列表项: {lists} 个\n"
        structure += f"- 链接: {links} 个\n"
        structure += f"- 图片: {images} 个\n"
        structure += f"- 表格行: {tables} 行\n"
        
        return structure 