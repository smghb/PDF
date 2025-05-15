#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML转换器
将PDF转换为HTML格式
"""

import os
import re
import base64
import tempfile
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from ..converter import BaseConverter
from ..ocr.ocr_processor import OCRProcessor


class HtmlConverter(BaseConverter):
    """HTML转换器类"""
    
    def __init__(self):
        """初始化转换器"""
        super().__init__()
        self.supported_formats = ['html']
        self._ocr_processor = None
        
    @property
    def output_extension(self) -> str:
        """获取输出文件扩展名"""
        return 'html'
        
    def convert(self, input_path: str, output_path: str, use_ocr: bool = False, **kwargs) -> bool:
        """
        将PDF转换为HTML文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出HTML文件路径
            use_ocr: 是否使用OCR（对于扫描版PDF）
            **kwargs: 其他转换参数
                - extract_images: 是否提取图片，默认为True
                - image_quality: 图片质量（1-100），默认为80
                - embed_images: 是否将图片嵌入HTML，默认为True
                - image_dir: 图片保存目录，如果embed_images为False则必须提供
                - css_file: 自定义CSS文件路径
                - page_range: 页面范围，格式为(start, end)
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 提取参数
            extract_images = kwargs.get('extract_images', True)
            image_quality = kwargs.get('image_quality', 80)
            embed_images = kwargs.get('embed_images', True)
            image_dir = kwargs.get('image_dir')
            css_file = kwargs.get('css_file')
            page_range = kwargs.get('page_range')
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 如果不嵌入图片，确保图片目录存在
            if extract_images and not embed_images:
                if not image_dir:
                    image_dir = os.path.join(os.path.dirname(output_path), 'images')
                os.makedirs(image_dir, exist_ok=True)
                
            # 打开PDF文档
            doc = fitz.open(input_path)
            
            # 确定处理的页面范围
            start_page = 0
            end_page = doc.page_count - 1
            
            if page_range:
                start_page = max(0, page_range[0])
                end_page = min(doc.page_count - 1, page_range[1])
                
            # 生成HTML内容
            html_content = self._generate_html_content(
                doc, 
                start_page, 
                end_page, 
                extract_images, 
                embed_images, 
                image_dir, 
                image_quality,
                use_ocr,
                css_file
            )
            
            # 写入HTML文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            doc.close()
            return True
            
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
            
    def _generate_html_content(
        self, 
        doc, 
        start_page: int, 
        end_page: int, 
        extract_images: bool, 
        embed_images: bool, 
        image_dir: Optional[str], 
        image_quality: int,
        use_ocr: bool,
        css_file: Optional[str]
    ) -> str:
        """
        生成HTML内容
        
        Args:
            doc: PDF文档对象
            start_page: 开始页码
            end_page: 结束页码
            extract_images: 是否提取图片
            embed_images: 是否嵌入图片
            image_dir: 图片保存目录
            image_quality: 图片质量
            use_ocr: 是否使用OCR
            css_file: 自定义CSS文件路径
            
        Returns:
            str: HTML内容
        """
        # 准备HTML头部
        html = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '<meta charset="UTF-8">',
            f'<title>{os.path.basename(doc.name)}</title>',
            self._get_css(css_file),
            '</head>',
            '<body>'
        ]
        
        # 处理每一页
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            
            # 添加页面分隔符
            if page_num > start_page:
                html.append('<div class="page-break"></div>')
                
            html.append(f'<div class="page" id="page-{page_num + 1}">')
            
            if use_ocr:
                # 使用OCR处理页面
                if self._ocr_processor is None:
                    self._ocr_processor = OCRProcessor()
                    
                # 将页面转换为图像
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # OCR处理
                text = self._ocr_processor.image_to_text(img)
                
                # 将文本添加到HTML
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        html.append(f'<p>{para.strip()}</p>')
            else:
                # 直接提取文本和布局
                text_blocks = page.get_text("blocks")
                
                # 按垂直位置排序
                text_blocks.sort(key=lambda b: b[1])  # 按y0坐标排序
                
                for block in text_blocks:
                    if block[6] == 0:  # 文本块
                        text = block[4]
                        text = text.replace('\n', '<br>')
                        html.append(f'<p>{text}</p>')
            
            # 提取图片
            if extract_images:
                image_list = self._extract_images_from_page(
                    page, 
                    page_num, 
                    embed_images, 
                    image_dir, 
                    image_quality
                )
                
                # 添加图片到HTML
                for img_info in image_list:
                    if embed_images:
                        html.append(
                            f'<div class="image-container"><img src="data:image/png;base64,{img_info["data"]}" '
                            f'alt="Image {img_info["index"]}" class="pdf-image"></div>'
                        )
                    else:
                        rel_path = os.path.relpath(img_info["path"], os.path.dirname(doc.name))
                        html.append(
                            f'<div class="image-container"><img src="{rel_path}" '
                            f'alt="Image {img_info["index"]}" class="pdf-image"></div>'
                        )
                        
            html.append('</div>')  # 结束页面div
            
        # 添加HTML尾部
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)
        
    def _extract_images_from_page(
        self, 
        page, 
        page_num: int, 
        embed_images: bool, 
        image_dir: Optional[str], 
        image_quality: int
    ) -> List[Dict]:
        """
        从页面提取图片
        
        Args:
            page: PDF页面对象
            page_num: 页码
            embed_images: 是否嵌入图片
            image_dir: 图片保存目录
            image_quality: 图片质量
            
        Returns:
            List[Dict]: 图片信息列表
        """
        image_list = []
        img_index = 0
        
        # 获取页面上的图像
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]
            
            # 提取图像
            base_image = self._extract_image(page.parent, xref)
            if base_image is None:
                continue
                
            if embed_images:
                # 转换为base64
                buffered = BytesIO()
                base_image.save(buffered, format="PNG")
                img_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                image_list.append({
                    "index": img_index,
                    "data": img_data
                })
            else:
                # 保存为文件
                img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                img_path = os.path.join(image_dir, img_filename)
                base_image.save(img_path, format="PNG")
                
                image_list.append({
                    "index": img_index,
                    "path": img_path
                })
                
        return image_list
        
    def _extract_image(self, doc, xref: int) -> Optional[Image.Image]:
        """
        从文档中提取图像
        
        Args:
            doc: PDF文档对象
            xref: 图像引用
            
        Returns:
            Optional[Image.Image]: 图像对象，如果失败则返回None
        """
        try:
            pix = fitz.Pixmap(doc, xref)
            
            # 转换为RGB（如果需要）
            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                
            # 转换为PIL图像
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return img
            
        except Exception as e:
            print(f"提取图像失败: {str(e)}")
            return None
            
    def _get_css(self, css_file: Optional[str]) -> str:
        """
        获取CSS样式
        
        Args:
            css_file: 自定义CSS文件路径
            
        Returns:
            str: CSS样式标签
        """
        default_css = """
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f9f9f9;
            }
            .page {
                background-color: white;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
                padding: 40px;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }
            .page-break {
                page-break-after: always;
                height: 20px;
            }
            p {
                margin-bottom: 10px;
            }
            .image-container {
                margin: 20px 0;
                text-align: center;
            }
            .pdf-image {
                max-width: 100%;
                height: auto;
            }
            @media print {
                body {
                    background-color: white;
                    padding: 0;
                }
                .page {
                    box-shadow: none;
                    padding: 0;
                    margin: 0;
                }
                .page-break {
                    height: 0;
                }
            }
        </style>
        """
        
        if css_file and os.path.exists(css_file):
            try:
                with open(css_file, 'r', encoding='utf-8') as f:
                    custom_css = f.read()
                return f'<style>{custom_css}</style>'
            except Exception as e:
                print(f"读取CSS文件失败: {str(e)}")
                
        return default_css