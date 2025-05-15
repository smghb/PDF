#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DOCX转换器
将PDF转换为Word文档格式
"""

import os
from typing import Optional, Dict, Any
from pdf2docx import Converter
from ..converter import BaseConverter
from ..ocr.ocr_processor import OCRProcessor


class DocxConverter(BaseConverter):
    """DOCX转换器类"""
    
    def __init__(self):
        """初始化转换器"""
        super().__init__()
        self.supported_formats = ['docx']
        self._ocr_processor = None
        
    @property
    def output_extension(self) -> str:
        """获取输出文件扩展名"""
        return 'docx'
        
    def convert(self, input_path: str, output_path: str, use_ocr: bool = False, **kwargs) -> bool:
        """
        将PDF转换为DOCX文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出DOCX文件路径
            use_ocr: 是否使用OCR（对于扫描版PDF）
            **kwargs: 其他转换参数
                - start_page: 开始页码（从0开始）
                - end_page: 结束页码
                - pages: 指定页码列表
            
        Returns:
            bool: 转换是否成功
        """
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 提取转换参数
            start_page = kwargs.get('start_page', 0)
            end_page = kwargs.get('end_page')
            pages = kwargs.get('pages')
            
            if use_ocr:
                # 使用OCR处理扫描版PDF
                return self._convert_with_ocr(input_path, output_path, **kwargs)
            else:
                # 使用pdf2docx直接转换
                cv = Converter(input_path)
                
                if pages:
                    # 转换指定页面
                    cv.convert(output_path, pages=pages)
                else:
                    # 转换页面范围
                    cv.convert(output_path, start=start_page, end=end_page)
                    
                cv.close()
                return True
                
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
            
    def _convert_with_ocr(self, input_path: str, output_path: str, **kwargs) -> bool:
        """
        使用OCR处理扫描版PDF并转换为DOCX
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出DOCX文件路径
            **kwargs: 其他转换参数
            
        Returns:
            bool: 转换是否成功
        """
        try:
            from docx import Document
            from docx.shared import Pt
            
            # 初始化OCR处理器
            if self._ocr_processor is None:
                self._ocr_processor = OCRProcessor()
                
            # 使用OCR提取文本
            text = self._ocr_processor.process_pdf(input_path)
            
            # 创建Word文档
            doc = Document()
            
            # 设置默认字体
            style = doc.styles['Normal']
            style.font.name = 'Arial'
            style.font.size = Pt(11)
            
            # 添加文本
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    doc.add_paragraph(para.strip())
                    
            # 保存文档
            doc.save(output_path)
            
            return True
            
        except Exception as e:
            print(f"OCR转换失败: {str(e)}")
            return False
            
    def get_document_info(self, input_path: str) -> Dict[str, Any]:
        """
        获取PDF文档信息
        
        Args:
            input_path: 输入PDF文件路径
            
        Returns:
            Dict[str, Any]: 文档信息
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(input_path)
            info = {
                'page_count': doc.page_count,
                'metadata': doc.metadata,
                'is_encrypted': doc.is_encrypted,
                'has_text': any(page.get_text() for page in doc)
            }
            doc.close()
            
            return info
            
        except Exception as e:
            print(f"获取文档信息失败: {str(e)}")
            return {}