"""
PDF解析工具，用于解析PDF文件内容，支持快速预览和完整解析两种模式
"""

import os
import tempfile
import shutil
import fitz  # PyMuPDF
import PyPDF2
import pymupdf4llm
import traceback
from typing import Dict, List, Any
import mcp.types as types
from . import BaseTool, ToolRegistry
from PIL import Image
import io
import pytesseract

@ToolRegistry.register
class PdfTool(BaseTool):
    """
    PDF解析工具，支持两种模式：
    1. 快速预览模式：仅提取文本内容，适用于大型PDF文件
    2. 完整解析模式：提取文本和图片内容，提供更详细的文档分析
    """
    
    name = "pdf"
    description = "解析PDF文件内容，支持快速预览和完整解析两种模式"
    input_schema = {
        "type": "object",
        "required": ["file_path"],
        "properties": {
            "file_path": {
                "type": "string",
                "description": "PDF文件的本地路径，例如'/path/to/document.pdf'",
            },
            "mode": {
                "type": "string",
                "description": "解析模式：'quick'（仅文本）或'full'（文本和图片），默认为'full'",
                "enum": ["quick", "full"],
                "default": "full"
            }
        },
    }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        解析PDF文件
        
        Args:
            arguments: 参数字典，必须包含'file_path'键，可选'mode'键
            
        Returns:
            PDF内容列表
        """
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="错误: 缺少必要参数 'file_path'"
            )]
        
        file_path = arguments["file_path"]
        mode = arguments.get("mode", "full")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不存在: {file_path}"
            )]
            
        # 检查文件扩展名
        if not file_path.lower().endswith('.pdf'):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不是PDF格式: {file_path}"
            )]
        
        try:
            if mode == "quick":
                return await self._quick_preview_pdf(file_path)
            else:
                return await self._full_parse_pdf(file_path)
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 处理PDF文件时发生错误: {str(e)}\n{error_details}"
            )]
    
    async def _quick_preview_pdf(self, file_path: str) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        快速预览PDF文件，仅提取文本内容
        """
        try:
            # 使用PyMuPDF提取文本
            doc = fitz.open(file_path)
            text_content = []
            
            # 添加文件信息
            text_content.append(f"文件名: {os.path.basename(file_path)}")
            text_content.append(f"页数: {doc.page_count}")
            text_content.append("---")
            
            # 提取每页文本
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_content.append(f"第{page_num + 1}页:")
                    text_content.append(text)
                    text_content.append("---")
            
            doc.close()
            
            return [types.TextContent(
                type="text",
                text="\n".join(text_content)
            )]
            
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 快速预览PDF时发生错误: {str(e)}\n{error_details}"
            )]
    
    async def _analyze_image(self, image_bytes: bytes, lang: str = 'chi_sim+eng') -> str:
        """
        分析图片内容，识别文字和场景

        Args:
            image_bytes: 图片的二进制数据
            lang: OCR语言，默认中文简体+英文

        Returns:
            str: 图片分析结果
        """
        try:
            # 将二进制数据转换为PIL Image对象
            image = Image.open(io.BytesIO(image_bytes))
            
            # 进行OCR文字识别
            text = pytesseract.image_to_string(image, lang=lang)
            
            # 如果识别出文字，返回结果
            if text.strip():
                return f"图片中识别出的文字：\n{text.strip()}"
            else:
                return "未在图片中识别出文字"
                
        except Exception as e:
            return f"图片分析失败: {str(e)}"

    async def _full_parse_pdf(self, file_path: str) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """
        完整解析PDF文件，提取文本和图片内容
        """
        results = []
        temp_dir = None
        
        try:
            # 创建临时目录存储图片
            temp_dir = tempfile.mkdtemp()
            
            # 使用PyMuPDF提取文本和图片
            doc = fitz.open(file_path)
            
            # 添加文件信息
            results.append(types.TextContent(
                type="text",
                text=f"文件名: {os.path.basename(file_path)}\n页数: {doc.page_count}\n---"
            ))
            
            # 处理每一页
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # 提取文本
                text = page.get_text()
                if text.strip():
                    results.append(types.TextContent(
                        type="text",
                        text=f"第{page_num + 1}页:\n{text}\n---"
                    ))
                
                # 提取图片
                image_list = page.get_images()
                for img_idx, img_info in enumerate(image_list):
                    try:
                        xref = img_info[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        # 保存图片到临时文件
                        img_temp_path = os.path.join(temp_dir, f"page_{page_num + 1}_img_{img_idx + 1}.png")
                        with open(img_temp_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # 分析图片内容
                        image_analysis = await self._analyze_image(image_bytes)
                        
                        # 添加图片和分析结果到结果列表
                        results.append(types.ImageContent(
                            type="image",
                            title=f"第{page_num + 1}页 图片{img_idx + 1}",
                            image_data=image_bytes
                        ))
                        results.append(types.TextContent(
                            type="text",
                            text=f"第{page_num + 1}页 图片{img_idx + 1}分析结果：\n{image_analysis}\n---"
                        ))
                    except Exception as img_error:
                        results.append(types.TextContent(
                            type="text",
                            text=f"警告: 提取第{page_num + 1}页图片{img_idx + 1}时出错: {str(img_error)}"
                        ))
            
            doc.close()
            return results
            
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 完整解析PDF时发生错误: {str(e)}\n{error_details}"
            )]
            
        finally:
            # 清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir) 