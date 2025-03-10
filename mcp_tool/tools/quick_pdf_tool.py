"""
PDF快速预览工具，仅提取文本内容，适用于大型PDF文件
"""

import os
import fitz  # PyMuPDF
import PyPDF2
import pymupdf4llm
import traceback
from typing import Dict, List, Any
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class QuickPdfTool(BaseTool):
    """
    用于快速预览PDF文件的工具，仅提取文本内容，不处理图片
    """
    
    name = "quick_pdf"
    description = "快速预览PDF文档内容（仅提取文本，不包含图片）"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "PDF文件的本地路径，例如'/path/to/document.pdf'",
            }
        },
    }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        快速预览PDF文档
        
        Args:
            arguments: 参数字典，必须包含'file_path'键
            
        Returns:
            PDF文本内容列表
        """
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="错误: 缺少必要参数 'file_path'"
            )]
        
        return await self._quick_preview_pdf(arguments["file_path"])
    
    async def _quick_preview_pdf(self, file_path: str) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        快速预览PDF文件内容，不包含图片处理
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            PDF文本内容列表
        """
        results = []
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不存在: {file_path}\n请检查路径是否正确，并确保文件可访问。"
            )]
        
        try:
            # 添加文件信息
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            results.append(types.TextContent(
                type="text",
                text=f"# 快速预览模式 - 仅提取文本内容\n\n文件大小: {file_size_mb:.2f} MB"
            ))
            
            # 获取PDF页数
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
            
            # 限制处理的页数
            max_pages = min(num_pages, 50)  # 快速模式可以处理更多页
            pages_to_process = list(range(max_pages))
            
            try:
                # 尝试使用PyMuPDF提取文本（通常比PyPDF2更快更准确）
                pdf_document = fitz.open(file_path)
                
                # 提取文本内容
                text_content = ""
                
                # 添加PDF元数据
                text_content += f"## PDF文档信息\n\n"
                text_content += f"- 页数: {num_pages}\n"
                
                # 从PyMuPDF获取元数据
                metadata = pdf_document.metadata
                if metadata:
                    for key, value in metadata.items():
                        if value and str(value).strip():
                            text_content += f"- {key}: {value}\n"
                
                # 如果处理的页数少于总页数，添加提示
                if max_pages < num_pages:
                    text_content += f"\n> 注意: 由于文件较大，仅处理前 {max_pages} 页内容。\n"
                
                text_content += "\n## 内容摘要\n\n"
                
                # 逐页提取文本
                for page_num in range(max_pages):
                    page = pdf_document[page_num]
                    page_text = page.get_text()
                    
                    if page_text.strip():
                        text_content += f"\n### 第 {page_num + 1} 页\n\n"
                        text_content += page_text.strip() + "\n"
                
                pdf_document.close()
                
                # 添加提取的内容到结果
                results.append(types.TextContent(
                    type="text",
                    text=text_content
                ))
                
            except Exception as pymupdf_error:
                # 如果PyMuPDF提取失败，回退到PymuPDF4llm
                results.append(types.TextContent(
                    type="text",
                    text=f"警告: 使用PyMuPDF提取内容失败: {str(pymupdf_error)}\n正在尝试使用备用方法..."
                ))
                
                try:
                    # 使用PymuPDF4llm提取内容，但不提取图像
                    md_content = pymupdf4llm.to_markdown(
                        doc=file_path,
                        pages=pages_to_process,
                        page_chunks=True,
                        write_images=False  # 不提取图像
                    )
                    
                    # 如果处理的页数少于总页数，添加提示
                    if max_pages < num_pages:
                        md_content = f"# PDF文档内容（前{max_pages}页）\n\n> 注意: 由于文件较大，仅处理前 {max_pages} 页内容。\n\n{md_content}"
                    else:
                        md_content = f"# PDF文档内容\n\n{md_content}"
                    
                    # 添加提取的内容到结果
                    results.append(types.TextContent(
                        type="text",
                        text=md_content
                    ))
                except Exception as extract_error:
                    # 如果PymuPDF4llm提取失败，回退到原来的方法
                    results.append(types.TextContent(
                        type="text",
                        text=f"警告: 使用PymuPDF4llm提取内容失败: {str(extract_error)}\n正在尝试使用最后的备用方法..."
                    ))
                    
                    # 使用PyPDF2提取文本
                    text_content = ""
                    with open(file_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        
                        # 添加PDF元数据
                        text_content += f"## PDF文档信息\n\n"
                        text_content += f"- 页数: {num_pages}\n"
                        if reader.metadata:
                            for key, value in reader.metadata.items():
                                if key.startswith('/'):
                                    key = key[1:]
                                if value and str(value).strip():
                                    text_content += f"- {key}: {value}\n"
                        
                        # 限制处理的页数
                        if max_pages < num_pages:
                            text_content += f"\n> 注意: 由于文件较大，仅处理前 {max_pages} 页内容。\n"
                        
                        text_content += "\n## 内容摘要\n\n"
                        
                        # 逐页提取文本
                        for page_num in range(max_pages):
                            page = reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text:
                                text_content += f"\n### 第 {page_num + 1} 页\n\n"
                                text_content += page_text + "\n"
                    
                    # 添加文本内容到结果
                    results.append(types.TextContent(type="text", text=text_content))
            
            # 添加提示信息
            results.append(types.TextContent(
                type="text",
                text="\n## 注意\n\n快速预览完成！如需查看图片内容，请使用完整的PDF解析工具。"
            ))
            
            return results
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 快速预览PDF失败: {str(e)}\n详细错误信息: {error_details}"
            )] 