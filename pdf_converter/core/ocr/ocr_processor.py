#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OCR处理器
负责处理OCR相关功能
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class OCRProcessor:
    """OCR处理器类"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = 'chi_sim+eng'):
        """
        初始化OCR处理器
        
        Args:
            tesseract_cmd: Tesseract可执行文件路径，如果为None则使用默认路径
            lang: OCR语言，默认为中文简体+英文
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.lang = lang
        
    def process_pdf(self, pdf_path: str, dpi: int = 300) -> str:
        """
        处理PDF文件，提取文本
        
        Args:
            pdf_path: PDF文件路径
            dpi: 图像DPI，影响OCR质量
            
        Returns:
            str: 提取的文本
        """
        # 将PDF转换为图像
        images = self.pdf_to_images(pdf_path, dpi)
        
        # 对每个图像进行OCR处理
        text_parts = []
        for img in images:
            text = self.image_to_text(img)
            text_parts.append(text)
            
        # 合并文本
        return '\n\n'.join(text_parts)
        
    def pdf_to_images(self, pdf_path: str, dpi: int = 300) -> List[Image.Image]:
        """
        将PDF转换为图像
        
        Args:
            pdf_path: PDF文件路径
            dpi: 图像DPI
            
        Returns:
            List[Image.Image]: 图像列表
        """
        return convert_from_path(pdf_path, dpi=dpi)
        
    def image_to_text(self, image: Image.Image) -> str:
        """
        从图像中提取文本
        
        Args:
            image: 图像对象
            
        Returns:
            str: 提取的文本
        """
        return pytesseract.image_to_string(image, lang=self.lang)
        
    def enhance_image(self, image: Image.Image) -> Image.Image:
        """
        增强图像以提高OCR准确率
        
        Args:
            image: 原始图像
            
        Returns:
            Image.Image: 增强后的图像
        """
        # 转换为灰度图
        gray = image.convert('L')
        
        # 二值化处理
        threshold = 150
        binary = gray.point(lambda x: 0 if x < threshold else 255, '1')
        
        return binary
        
    def process_image_with_enhancement(self, image: Image.Image) -> str:
        """
        处理图像并应用增强，提取文本
        
        Args:
            image: 图像对象
            
        Returns:
            str: 提取的文本
        """
        enhanced = self.enhance_image(image)
        return self.image_to_text(enhanced)
        
    def process_pdf_with_enhancement(self, pdf_path: str, dpi: int = 300) -> str:
        """
        处理PDF文件并应用图像增强，提取文本
        
        Args:
            pdf_path: PDF文件路径
            dpi: 图像DPI
            
        Returns:
            str: 提取的文本
        """
        # 将PDF转换为图像
        images = self.pdf_to_images(pdf_path, dpi)
        
        # 对每个图像进行增强和OCR处理
        text_parts = []
        for img in images:
            text = self.process_image_with_enhancement(img)
            text_parts.append(text)
            
        # 合并文本
        return '\n\n'.join(text_parts)