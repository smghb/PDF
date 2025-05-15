#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片转换器
将PDF转换为PNG或JPG格式的图片
"""

import os
from typing import List, Optional, Tuple
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from ..converter import BaseConverter


class ImageConverter(BaseConverter):
    """图片转换器类"""
    
    def __init__(self, format_type: str = 'png'):
        """
        初始化转换器
        
        Args:
            format_type: 输出图片格式，'png'或'jpg'
        """
        super().__init__()
        self.format_type = format_type.lower()
        if self.format_type not in ['png', 'jpg', 'jpeg']:
            raise ValueError("不支持的图片格式，只支持'png'或'jpg'")
            
        # 标准化格式名称
        if self.format_type == 'jpeg':
            self.format_type = 'jpg'
            
        self.supported_formats = ['png', 'jpg']
        
    @property
    def output_extension(self) -> str:
        """获取输出文件扩展名"""
        return self.format_type
        
    def convert(self, input_path: str, output_path: str, **kwargs) -> bool:
        """
        将PDF转换为图片文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出图片文件路径（如果有多页，会自动添加页码）
            **kwargs: 其他转换参数
                - dpi: 图像DPI，默认为200
                - first_page: 开始页码（从1开始），默认为1
                - last_page: 结束页码，默认为最后一页
                - single_file: 是否合并为单个文件（仅适用于多页PDF），默认为False
                - quality: JPG质量（1-100），默认为90
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 提取参数
            dpi = kwargs.get('dpi', 200)
            first_page = kwargs.get('first_page', 1)
            last_page = kwargs.get('last_page')
            single_file = kwargs.get('single_file', False)
            quality = kwargs.get('quality', 90)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 转换PDF为图片
            images = convert_from_path(
                input_path,
                dpi=dpi,
                first_page=first_page,
                last_page=last_page
            )
            
            if not images:
                print("未能从PDF提取任何图片")
                return False
                
            if single_file and len(images) > 1:
                # 合并为单个文件
                return self._save_as_single_file(images, output_path, quality)
            else:
                # 保存为多个文件
                return self._save_as_multiple_files(images, output_path, quality)
                
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
            
    def _save_as_single_file(self, images: List[Image.Image], output_path: str, quality: int) -> bool:
        """
        将多个图片保存为单个文件（垂直拼接）
        
        Args:
            images: 图片列表
            output_path: 输出文件路径
            quality: JPG质量
            
        Returns:
            bool: 是否成功
        """
        try:
            # 计算合并后的图片尺寸
            width = max(img.width for img in images)
            height = sum(img.height for img in images)
            
            # 创建新图片
            merged_image = Image.new('RGB', (width, height), (255, 255, 255))
            
            # 拼接图片
            y_offset = 0
            for img in images:
                merged_image.paste(img, (0, y_offset))
                y_offset += img.height
                
            # 保存图片
            if self.format_type == 'png':
                merged_image.save(output_path, format='PNG')
            else:
                merged_image.save(output_path, format='JPEG', quality=quality)
                
            return True
            
        except Exception as e:
            print(f"保存合并图片失败: {str(e)}")
            return False
            
    def _save_as_multiple_files(self, images: List[Image.Image], output_path: str, quality: int) -> bool:
        """
        将多个图片保存为多个文件
        
        Args:
            images: 图片列表
            output_path: 输出文件路径模板
            quality: JPG质量
            
        Returns:
            bool: 是否成功
        """
        try:
            # 解析输出路径
            output_dir = os.path.dirname(output_path)
            filename = Path(output_path).stem
            
            # 保存每一页
            for i, img in enumerate(images):
                page_path = os.path.join(output_dir, f"{filename}_page_{i+1}.{self.format_type}")
                
                if self.format_type == 'png':
                    img.save(page_path, format='PNG')
                else:
                    img.save(page_path, format='JPEG', quality=quality)
                    
            return True
            
        except Exception as e:
            print(f"保存多个图片失败: {str(e)}")
            return False
            
    def get_pdf_dimensions(self, input_path: str) -> List[Tuple[int, int]]:
        """
        获取PDF各页面的尺寸
        
        Args:
            input_path: 输入PDF文件路径
            
        Returns:
            List[Tuple[int, int]]: 各页面的尺寸列表 (宽, 高)
        """
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(input_path)
            dimensions = []
            
            for page in doc:
                rect = page.rect
                dimensions.append((int(rect.width), int(rect.height)))
                
            doc.close()
            return dimensions
            
        except Exception as e:
            print(f"获取PDF尺寸失败: {str(e)}")
            return []