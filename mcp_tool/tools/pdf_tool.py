import os
import tempfile
import shutil
import PyPDF2
from pdf2image import convert_from_path
from PIL import Image
import pymupdf4llm
import mcp.types as types
from . import BaseTool, ToolRegistry

@ToolRegistry.register
class PdfTool(BaseTool):
    """PDF解析工具，用于解析PDF文件并提取文本和图片"""
    name = "file"
    description = "解析PDF文件并提取文本和图片内容"
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
    
    async def execute(self, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """解析PDF文件并提取文本和图片"""
        if "file_path" not in arguments:
            return [types.TextContent(
                type="text",
                text="Error: Missing required argument 'file_path'"
            )]
            
        file_path = arguments["file_path"]
        results = []
        
        # 添加初始状态提示
        results.append(types.TextContent(
            type="text",
            text="开始处理PDF文件，请稍候..."
        ))
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"错误: 文件不存在: {file_path}\n请检查路径是否正确，并确保文件可访问。"
            )]
        
        try:
            # 创建临时目录用于存储图片
            temp_dir = tempfile.mkdtemp()
            image_path = os.path.join(temp_dir, "images")
            os.makedirs(image_path, exist_ok=True)
            
            # 添加文件大小信息
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            results.append(types.TextContent(
                type="text",
                text=f"文件大小: {file_size_mb:.2f} MB"
            ))
            
            # 对大文件提供警告
            if file_size_mb > 10:
                results.append(types.TextContent(
                    type="text",
                    text=f"警告: 文件较大 ({file_size_mb:.2f} MB)，处理可能需要较长时间。"
                ))
            
            # 使用PymuPDF4llm提取PDF内容（包括文本和图像）
            try:
                # 获取PDF页数
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    num_pages = len(reader.pages)
                
                # 限制处理的页数
                max_pages = min(num_pages, 30)
                pages_to_process = list(range(max_pages))
                
                # 使用PymuPDF4llm提取内容
                md_content = pymupdf4llm.to_markdown(
                    doc=file_path,
                    pages=pages_to_process,
                    page_chunks=True,
                    write_images=True,
                    image_path=image_path,
                    image_format="jpg",
                    dpi=150
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
                
                # 处理提取的图像
                image_files = []
                for root, dirs, files in os.walk(image_path):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_files.append(os.path.join(root, file))
                
                # 添加图像信息
                if image_files:
                    image_info = "\n## 提取的图像信息\n\n"
                    image_info += f"共提取了 {len(image_files)} 张图像。\n\n"
                    
                    for i, img_file in enumerate(image_files):
                        try:
                            with Image.open(img_file) as img:
                                width, height = img.size
                                format_name = img.format
                                
                                image_info += f"### 图像 {i+1}\n\n"
                                image_info += f"- 文件名: {os.path.basename(img_file)}\n"
                                image_info += f"- 尺寸: {width}x{height} 像素\n"
                                image_info += f"- 格式: {format_name}\n\n"
                                image_info += "---\n\n"
                        except Exception as e:
                            image_info += f"### 图像 {i+1}\n\n"
                            image_info += f"- 文件名: {os.path.basename(img_file)}\n"
                            image_info += f"- 错误: 无法读取图像信息: {str(e)}\n\n"
                            image_info += "---\n\n"
                    
                    results.append(types.TextContent(
                        type="text",
                        text=image_info
                    ))
                else:
                    results.append(types.TextContent(
                        type="text",
                        text="\n## 图像信息\n\n未从PDF中提取到任何图像。"
                    ))
                    
            except Exception as extract_error:
                # 如果PymuPDF4llm提取失败，回退到原来的方法
                results.append(types.TextContent(
                    type="text",
                    text=f"警告: 使用PymuPDF4llm提取内容失败: {str(extract_error)}\n正在尝试使用备用方法..."
                ))
                
                # 使用PyPDF2提取文本
                text_content = ""
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    num_pages = len(reader.pages)
                    
                    # 添加PDF元数据
                    text_content += f"# PDF文档信息\n\n"
                    text_content += f"- 页数: {num_pages}\n"
                    if reader.metadata:
                        for key, value in reader.metadata.items():
                            if key.startswith('/'):
                                key = key[1:]  # 移除前导斜杠
                            if value and str(value).strip():
                                text_content += f"- {key}: {value}\n"
                    
                    # 提取文本 - 限制页数以提高性能
                    max_pages_to_process = min(num_pages, 30)  # 限制处理的最大页数
                    if max_pages_to_process < num_pages:
                        text_content += f"\n> 注意: 由于文件较大，仅处理前 {max_pages_to_process} 页内容。\n"
                    
                    text_content += "\n## 内容摘要\n\n"
                    
                    # 逐页提取文本
                    for page_num in range(max_pages_to_process):
                        # 添加进度提示
                        if page_num % 5 == 0 and page_num > 0:
                            progress_msg = f"已处理 {page_num}/{max_pages_to_process} 页..."
                            results.append(types.TextContent(type="text", text=progress_msg))
                        
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n### 第 {page_num + 1} 页\n\n"
                            text_content += page_text + "\n"
                
                # 添加文本内容到结果
                results.append(types.TextContent(type="text", text=text_content))
                
                # 尝试使用pdf2image提取图片
                try:
                    # 限制处理的页数以提高性能
                    max_img_pages = min(num_pages, 10)  # 限制处理图片的最大页数
                    
                    results.append(types.TextContent(
                        type="text",
                        text=f"正在提取图片，这可能需要一些时间..."
                    ))
                    
                    # 转换PDF页面为图片并保存
                    images = convert_from_path(
                        file_path, 
                        dpi=150, 
                        fmt="jpg", 
                        first_page=1, 
                        last_page=max_img_pages,
                        thread_count=2  # 使用多线程加速
                    )
                    
                    # 处理每个页面图片
                    image_markdown = "\n## 图片内容\n\n"
                    for i, img in enumerate(images):
                        # 保存图片到临时目录
                        img_path = os.path.join(temp_dir, f"page_{i+1}.jpg")
                        img.save(img_path, "JPEG", quality=80)
                        
                        # 获取图片尺寸
                        width, height = img.size
                        
                        # 添加图片信息到Markdown
                        image_markdown += f"### 第 {i+1} 页图片\n\n"
                        image_markdown += f"- 尺寸: {width}x{height} 像素\n"
                        image_markdown += f"- 格式: JPEG\n"
                        image_markdown += f"- DPI: 150\n\n"
                        
                        # 添加分隔线
                        image_markdown += "---\n\n"
                    
                    # 添加图片信息到结果
                    results.append(types.TextContent(
                        type="text",
                        text=image_markdown
                    ))
                except Exception as img_error:
                    # 如果图片提取失败，添加错误信息但继续
                    results.append(types.TextContent(
                        type="text",
                        text=f"警告: 无法提取图片: {str(img_error)}\n"
                             f"这可能是由于PDF文件结构复杂或缺少必要的系统依赖（如poppler-utils）。"
                    ))
            
            # 清理临时目录
            shutil.rmtree(temp_dir)
            
            # 添加处理完成的提示
            results.append(types.TextContent(
                type="text",
                text="PDF处理完成！"
            ))
            
            return results
        except Exception as e:
            # 确保清理临时目录
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                
            import traceback
            error_details = traceback.format_exc()
            return [
                types.TextContent(
                    type="text",
                    text=f"错误: 解析PDF文件失败: {str(e)}\n"
                         f"可能的原因:\n"
                         f"1. 文件格式不兼容\n"
                         f"2. 文件已加密或受密码保护\n"
                         f"3. 系统缺少必要的依赖（如poppler-utils）\n"
                         f"4. 文件太大，处理超时\n\n"
                         f"详细错误信息: {error_details}"
                )
            ] 