#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Markdown转换器
将PDF转换为Markdown格式
"""

import os
import re
from typing import List, Dict, Optional, Tuple
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import base64
from ..converter import BaseConverter
from ..ocr.ocr_processor import OCRProcessor


class MarkdownConverter(BaseConverter):
    """Markdown转换器类"""
    
    def __init__(self):
        """初始化转换器"""
        super().__init__()
        self.supported_formats = ['md', 'markdown']
        self._ocr_processor = None
        
    @property
    def output_extension(self) -> str:
        """获取输出文件扩展名"""
        return 'md'
        
    def convert(self, input_path: str, output_path: str, use_ocr: bool = False, **kwargs) -> bool:
        """
        将PDF转换为Markdown文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出Markdown文件路径
            use_ocr: 是否使用OCR（对于扫描版PDF）
            **kwargs: 其他转换参数
                - extract_images: 是否提取图片，默认为True
                - image_quality: 图片质量（1-100），默认为80
                - embed_images: 是否将图片嵌入Markdown，默认为False
                - image_dir: 图片保存目录，默认为与输出文件同名的目录
                - page_range: 页面范围，格式为(start, end)
                - include_toc: 是否包含目录，默认为True
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 提取参数
            extract_images = kwargs.get('extract_images', True)
            image_quality = kwargs.get('image_quality', 80)
            embed_images = kwargs.get('embed_images', False)
            image_dir = kwargs.get('image_dir')
            page_range = kwargs.get('page_range')
            include_toc = kwargs.get('include_toc', True)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 如果不嵌入图片，确保图片目录存在
            if extract_images and not embed_images:
                if not image_dir:
                    # 创建与输出文件同名的目录
                    output_stem = os.path.splitext(output_path)[0]
                    image_dir = f"{output_stem}_images"
                os.makedirs(image_dir, exist_ok=True)
                
            # 打开PDF文档
            doc = fitz.open(input_path)
            
            # 确定处理的页面范围
            start_page = 0
            end_page = doc.page_count - 1
            
            if page_range:
                start_page = max(0, page_range[0])
                end_page = min(doc.page_count - 1, page_range[1])
                
            # 生成Markdown内容
            md_content = self._generate_markdown_content(
                doc, 
                start_page, 
                end_page, 
                extract_images, 
                embed_images, 
                image_dir, 
                image_quality,
                use_ocr,
                include_toc
            )
            
            # 写入Markdown文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            doc.close()
            return True
            
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
            
    def _generate_markdown_content(
        self, 
        doc, 
        start_page: int, 
        end_page: int, 
        extract_images: bool, 
        embed_images: bool, 
        image_dir: Optional[str], 
        image_quality: int,
        use_ocr: bool,
        include_toc: bool
    ) -> str:
        """
        生成Markdown内容
        
        Args:
            doc: PDF文档对象
            start_page: 开始页码
            end_page: 结束页码
            extract_images: 是否提取图片
            embed_images: 是否嵌入图片
            image_dir: 图片保存目录
            image_quality: 图片质量
            use_ocr: 是否使用OCR
            include_toc: 是否包含目录
            
        Returns:
            str: Markdown内容
        """
        md_lines = []
        
        # 添加标题
        title = os.path.splitext(os.path.basename(doc.name))[0]
        md_lines.append(f"# {title}\n")
        
        # 提取目录结构
        toc = []
        if include_toc:
            toc = self._extract_toc(doc)
            
            if toc:
                md_lines.append("## 目录\n")
                for level, title, page in toc:
                    indent = "  " * (level - 1)
                    md_lines.append(f"{indent}- [{title}](#{self._slugify(title)})\n")
                md_lines.append("\n")
        
        # 处理每一页
        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            
            # 添加页码标记
            md_lines.append(f"\n<!-- 第 {page_num + 1} 页 -->\n")
            
            if use_ocr:
                # 使用OCR处理页面
                if self._ocr_processor is None:
                    self._ocr_processor = OCRProcessor()
                    
                # 将页面转换为图像
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # OCR处理
                text = self._ocr_processor.image_to_text(img)
                
                # 将文本添加到Markdown
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        md_lines.append(f"{para.strip()}\n\n")
            else:
                # 直接提取文本和布局
                text_blocks = page.get_text("blocks")
                
                # 按垂直位置排序
                text_blocks.sort(key=lambda b: b[1])  # 按y0坐标排序
                
                for block in text_blocks:
                    if block[6] == 0:  # 文本块
                        text = block[4]
                        # 检查是否为标题
                        if self._is_heading(text, toc):
                            heading_level = self._get_heading_level(text, toc)
                            md_lines.append(f"\n{'#' * heading_level} {text.strip()}\n\n")
                        else:
                            md_lines.append(f"{text.strip()}\n\n")
            
            # 提取图片
            if extract_images:
                image_list = self._extract_images_from_page(
                    page, 
                    page_num, 
                    embed_images, 
                    image_dir, 
                    image_quality
                )
                
                # 添加图片到Markdown
                for img_info in image_list:
                    if embed_images:
                        md_lines.append(
                            f"\n![Image {img_info['index']}](data:image/png;base64,{img_info['data']})\n\n"
                        )
                    else:
                        # 使用相对路径
                        rel_path = os.path.relpath(
                            img_info["path"], 
                            os.path.dirname(doc.name)
                        ).replace('\\', '/')
                        md_lines.append(
                            f"\n![Image {img_info['index']}]({rel_path})\n\n"
                        )
        
        return ''.join(md_lines)
        
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
        
        # 获取页面上的图像
        images = page.get_images(full=True)
        
        for img_index, img in enumerate(images):
            xref = img[0]
            
            # 提取图像
            pix = fitz.Pixmap(page.parent, xref)
            
            # 转换为RGB（如果需要）
            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
                
            if embed_images:
                # 转换为base64
                img_data = base64.b64encode(pix.tobytes()).decode('utf-8')
                
                image_list.append({
                    "index": img_index,
                    "data": img_data
                })
            else:
                # 保存为文件
                img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                img_path = os.path.join(image_dir, img_filename)
                pix.save(img_path)
                
                image_list.append({
                    "index": img_index,
                    "path": img_path
                })
                
        return image_list
        
    def _extract_toc(self, doc) -> List[Tuple[int, str, int]]:
        """
        提取文档的目录结构
        
        Args:
            doc: PDF文档对象
            
        Returns:
            List[Tuple[int, str, int]]: 目录项列表，每项为(级别, 标题, 页码)
        """
        try:
            toc = doc.get_toc()
            return toc
        except Exception as e:
            print(f"提取目录失败: {str(e)}")
            return []
            
    def _is_heading(self, text: str, toc: List[Tuple[int, str, int]]) -> bool:
        """
        判断文本是否为标题
        
        Args:
            text: 文本
            toc: 目录项列表
            
        Returns:
            bool: 是否为标题
        """
        text = text.strip()
        for _, title, _ in toc:
            if text == title:
                return True
        return False
        
    def _get_heading_level(self, text: str, toc: List[Tuple[int, str, int]]) -> int:
        """
        获取标题级别
        
        Args:
            text: 文本
            toc: 目录项列表
            
        Returns:
            int: 标题级别
        """
        text = text.strip()
        for level, title, _ in toc:
            if text == title:
                return level
        return 2  # 默认为二级标题
        
    def _slugify(self, text: str) -> str:
        """
        将文本转换为slug格式（用于锚点链接）
        
        Args:
            text: 文本
            
        Returns:
            str: slug格式的文本
        """
        # 移除非字母数字字符
        text = re.sub(r'[^\w\s-]', '', text.lower())
        # 将空格替换为连字符
        text = re.sub(r'[\s]+', '-', text)
        return text