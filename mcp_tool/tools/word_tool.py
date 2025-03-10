"""
Word文档解析工具，用于解析Word文档内容
"""

import os
import traceback
from typing import Dict, List, Any
import docx
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class WordTool(BaseTool):
    """
    用于解析Word文档的工具，提取文本内容、表格和图片信息
    """
    
    name = "word"
    description = "解析Word文档内容，提取文本、表格和图片信息"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Word文档的本地路径，例如'/path/to/document.docx'",
            }
        },
    }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        解析Word文档
        
        Args:
            arguments: 参数字典，必须包含'file_path'键
            
        Returns:
            Word文档内容列表
        """
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="错误: 缺少必要参数 'file_path'"
            )]
        
        return await self._parse_word_document(arguments["file_path"])
    
    async def _parse_word_document(self, file_path: str) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        解析Word文档内容
        
        Args:
            file_path: Word文档路径
            
        Returns:
            Word文档内容列表
        """
        results = []
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不存在: {file_path}\n请检查路径是否正确，并确保文件可访问。"
            )]
        
        # 检查文件扩展名
        if not file_path.lower().endswith(('.docx', '.doc')):
            return [types.TextContent(
                type="text",
                text=f"错误: 不支持的文件格式: {file_path}\n仅支持.docx和.doc格式的Word文档。"
            )]
        
        try:
            # 添加文件信息
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            results.append(types.TextContent(
                type="text",
                text=f"# Word文档解析\n\n文件大小: {file_size_mb:.2f} MB"
            ))
            
            # 打开Word文档
            doc = docx.Document(file_path)
            
            # 提取文档属性
            properties = {}
            if hasattr(doc.core_properties, 'title') and doc.core_properties.title:
                properties['标题'] = doc.core_properties.title
            if hasattr(doc.core_properties, 'author') and doc.core_properties.author:
                properties['作者'] = doc.core_properties.author
            if hasattr(doc.core_properties, 'created') and doc.core_properties.created:
                properties['创建时间'] = str(doc.core_properties.created)
            if hasattr(doc.core_properties, 'modified') and doc.core_properties.modified:
                properties['修改时间'] = str(doc.core_properties.modified)
            if hasattr(doc.core_properties, 'comments') and doc.core_properties.comments:
                properties['备注'] = doc.core_properties.comments
            
            # 添加文档属性信息
            if properties:
                properties_text = "## 文档属性\n\n"
                for key, value in properties.items():
                    properties_text += f"- {key}: {value}\n"
                results.append(types.TextContent(
                    type="text",
                    text=properties_text
                ))
            
            # 提取文档内容
            content_text = "## 文档内容\n\n"
            
            # 处理段落
            paragraphs_count = len(doc.paragraphs)
            content_text += f"### 段落 (共{paragraphs_count}个)\n\n"
            
            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():  # 只处理非空段落
                    content_text += f"{para.text}\n\n"
            
            # 处理表格
            tables_count = len(doc.tables)
            if tables_count > 0:
                content_text += f"### 表格 (共{tables_count}个)\n\n"
                
                for i, table in enumerate(doc.tables):
                    content_text += f"#### 表格 {i+1}\n\n"
                    
                    # 创建Markdown表格
                    rows = []
                    for row in table.rows:
                        cells = [cell.text.replace('\n', ' ').strip() for cell in row.cells]
                        rows.append(cells)
                    
                    if rows:
                        # 表头
                        content_text += "| " + " | ".join(rows[0]) + " |\n"
                        # 分隔线
                        content_text += "| " + " | ".join(["---"] * len(rows[0])) + " |\n"
                        # 表格内容
                        for row in rows[1:]:
                            content_text += "| " + " | ".join(row) + " |\n"
                        
                        content_text += "\n"
            
            # 添加文档内容
            results.append(types.TextContent(
                type="text",
                text=content_text
            ))
            
            # 提取图片信息
            try:
                # 计算文档中的图片数量
                image_count = 0
                for rel in doc.part.rels.values():
                    if "image" in rel.target_ref:
                        image_count += 1
                
                if image_count > 0:
                    image_info = f"## 图片信息\n\n文档中包含 {image_count} 张图片。\n\n"
                    image_info += "注意：当前仅提供图片数量信息，不提取图片内容。如需查看图片，请直接打开原始文档。\n"
                    
                    results.append(types.TextContent(
                        type="text",
                        text=image_info
                    ))
            except Exception as img_error:
                results.append(types.TextContent(
                    type="text",
                    text=f"警告: 提取图片信息时出错: {str(img_error)}"
                ))
            
            # 添加处理完成的提示
            results.append(types.TextContent(
                type="text",
                text="Word文档处理完成！"
            ))
            
            return results
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 解析Word文档失败: {str(e)}\n"
                     f"可能的原因:\n"
                     f"1. 文件格式不兼容或已损坏\n"
                     f"2. 文件受密码保护\n"
                     f"3. 文件包含不支持的内容\n\n"
                     f"详细错误信息: {error_details}"
            )] 