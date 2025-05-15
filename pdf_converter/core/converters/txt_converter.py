#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TXT转换器
将PDF转换为纯文本格式
"""

import os
from typing import Optional
from pdfminer.high_level import extract_text
from ..converter import BaseConverter
from ..ocr.ocr_processor import OCRProcessor


class TxtConverter(BaseConverter):
    """TXT转换器类"""
    
    def __init__(self):
        """初始化转换器"""
        super().__init__()
        self.supported_formats = ['txt']
        self._ocr_processor = None
        
    @property
    def output_extension(self) -> str:
        """获取输出文件扩展名"""
        return 'txt'
        
    def convert(self, input_path: str, output_path: str, use_ocr: bool = False, **kwargs) -> bool:
        """
        将PDF转换为TXT文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出TXT文件路径
            use_ocr: 是否使用OCR
            **kwargs: 其他转换参数
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if use_ocr:
                # 使用OCR处理
                if self._ocr_processor is None:
                    self._ocr_processor = OCRProcessor()
                text = self._ocr_processor.process_pdf(input_path)
            else:
                # 使用pdfminer直接提取文本
                text = extract_text(input_path)
            
            # 写入文本文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
                
            return True
            
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
            
    def extract_text_from_page(self, input_path: str, page_number: int) -> Optional[str]:
        """
        从指定页面提取文本
        
        Args:
            input_path: 输入PDF文件路径
            page_number: 页码（从0开始）
            
        Returns:
            Optional[str]: 提取的文本，如果失败则返回None
        """
        try:
            # 使用pdfminer提取指定页面的文本
            text = extract_text(input_path, page_numbers=[page_number])
            return text
        except Exception as e:
            print(f"提取文本失败: {str(e)}")
            return None
            
    def extract_text_with_ocr(self, input_path: str, dpi: int = 300) -> Optional[str]:
        """
        使用OCR从PDF提取文本
        
        Args:
            input_path: 输入PDF文件路径
            dpi: OCR处理的DPI
            
        Returns:
            Optional[str]: 提取的文本，如果失败则返回None
        """
        try:
            if self._ocr_processor is None:
                self._ocr_processor = OCRProcessor()
            return self._ocr_processor.process_pdf(input_path, dpi)
        except Exception as e:
            print(f"OCR处理失败: {str(e)}")
            return None