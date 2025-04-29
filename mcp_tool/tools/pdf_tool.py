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
import base64
import imghdr

@ToolRegistry.register
class PdfTool(BaseTool):
    """
    PDF解析工具，支持两种模式：
    1. 快速预览模式：仅提取文本内容，适用于大型PDF文件
    2. 完整解析模式：提取文本和图片内容，提供更详细的文档分析
    """
    
    name = "parse_pdf"
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
        
        if not file_path.lower().endswith('.pdf'):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不是PDF格式: {file_path}"
            )]
        
        mode = arguments.get("mode", "full")
        
        if mode == "quick":
            return await self._quick_preview_pdf(file_path)
        else:
            return await self._full_parse_pdf(file_path)
    
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
    
    def _get_image_mime_type(self, image_bytes: bytes) -> str:
        """
        获取图片的MIME类型
        """
        image_type = imghdr.what(None, image_bytes)
        if image_type:
            return f"image/{image_type}"
        return "image/png"  # 默认返回PNG类型

    def _encode_image_base64(self, image_bytes: bytes) -> str:
        """
        将图片编码为base64格式
        """
        return base64.b64encode(image_bytes).decode('utf-8')

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
        
        try:
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
                if image_list:
                    results.append(types.TextContent(
                        type="text",
                        text=f"第{page_num + 1}页包含{len(image_list)}张图片"
                    ))
                    
                    # 处理各页的图片
                    skipped_images = 0
                    successful_images = 0
                    
                    for img_idx, img_info in enumerate(image_list):
                        try:
                            xref = img_info[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # 获取图片MIME类型并检查是否支持
                            mime_type = self._get_image_mime_type(image_bytes)
                            supported_mime_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
                            
                            # 如果格式不受支持，则跳过该图片
                            if mime_type not in supported_mime_types:
                                skipped_images += 1
                                continue
                            
                            # 添加图片OCR识别结果
                            image_analysis = await self._analyze_image(image_bytes)
                            results.append(types.TextContent(
                                type="text",
                                text=f"第{page_num + 1}页 图片{successful_images + 1}分析结果：\n{image_analysis}\n---"
                            ))
                            
                            # 添加图片内容，直接返回图片而非只返回OCR文本
                            image_base64 = self._encode_image_base64(image_bytes)
                            results.append(types.ImageContent(
                                type="image",
                                data=image_base64,
                                mimeType=mime_type
                            ))
                            
                            successful_images += 1
                        except Exception:
                            # 捕获所有异常，但不中断处理流程
                            skipped_images += 1
                    
                    # 如果有跳过的图片，添加简单提示
                    if skipped_images > 0:
                        results.append(types.TextContent(
                            type="text",
                            text=f"注意: 第{page_num + 1}页有 {skipped_images} 张图片因格式问题已跳过处理。"
                        ))
            
            doc.close()
            return results
            
        except Exception as e:
            error_details = traceback.format_exc()
            return [types.TextContent(
                type="text",
                text=f"错误: 完整解析PDF时发生错误: {str(e)}\n{error_details}"
            )] 