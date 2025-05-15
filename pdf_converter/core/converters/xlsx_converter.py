#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
XLSX转换器
将PDF中的表格转换为Excel格式
"""

import os
import tempfile
from typing import List, Dict, Optional, Tuple, Union
import pandas as pd
import tabula
from ..converter import BaseConverter
from ..ocr.ocr_processor import OCRProcessor


class XlsxConverter(BaseConverter):
    """XLSX转换器类"""
    
    def __init__(self):
        """初始化转换器"""
        super().__init__()
        self.supported_formats = ['xlsx', 'xls']
        self._ocr_processor = None
        
    @property
    def output_extension(self) -> str:
        """获取输出文件扩展名"""
        return 'xlsx'
        
    def convert(self, input_path: str, output_path: str, use_ocr: bool = False, **kwargs) -> bool:
        """
        将PDF中的表格转换为Excel文件
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出Excel文件路径
            use_ocr: 是否使用OCR（对于扫描版PDF）
            **kwargs: 其他转换参数
                - pages: 页码列表或范围，例如"1-3,5,7-10"或[1,2,3,5,7,8,9,10]
                - area: 提取区域，格式为[top, left, bottom, right]，单位为点
                - multiple_tables: 是否提取多个表格，默认为True
                - lattice: 是否使用格子模式（适用于有表格线的PDF），默认为True
                - stream: 是否使用流模式（适用于没有表格线的PDF），默认为False
                - guess: 是否猜测表格结构，默认为True
                - spreadsheet: 是否将所有表格放在一个工作表中，默认为False
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 提取参数
            pages = kwargs.get('pages', 'all')
            area = kwargs.get('area')
            multiple_tables = kwargs.get('multiple_tables', True)
            lattice = kwargs.get('lattice', True)
            stream = kwargs.get('stream', False)
            guess = kwargs.get('guess', True)
            spreadsheet = kwargs.get('spreadsheet', False)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if use_ocr:
                # 使用OCR处理扫描版PDF
                return self._convert_with_ocr(
                    input_path, 
                    output_path, 
                    pages, 
                    area, 
                    multiple_tables
                )
            else:
                # 使用tabula直接提取表格
                tables = tabula.read_pdf(
                    input_path,
                    pages=pages,
                    area=area,
                    multiple_tables=multiple_tables,
                    lattice=lattice,
                    stream=stream,
                    guess=guess
                )
                
                if not tables:
                    print("未能从PDF提取任何表格")
                    return False
                    
                # 保存为Excel
                if spreadsheet:
                    # 所有表格放在一个工作表中
                    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                        for i, table in enumerate(tables):
                            table.to_excel(
                                writer, 
                                sheet_name=f'Sheet1', 
                                startrow=i * (len(table) + 2), 
                                index=False
                            )
                else:
                    # 每个表格一个工作表
                    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                        for i, table in enumerate(tables):
                            sheet_name = f'Table_{i+1}'
                            if i == 0:
                                sheet_name = 'Sheet1'
                            table.to_excel(writer, sheet_name=sheet_name, index=False)
                
                return True
                
        except Exception as e:
            print(f"转换失败: {str(e)}")
            return False
            
    def _convert_with_ocr(
        self, 
        input_path: str, 
        output_path: str, 
        pages: Union[str, List[int]], 
        area: Optional[List[float]], 
        multiple_tables: bool
    ) -> bool:
        """
        使用OCR处理扫描版PDF并提取表格
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出Excel文件路径
            pages: 页码列表或范围
            area: 提取区域
            multiple_tables: 是否提取多个表格
            
        Returns:
            bool: 转换是否成功
        """
        try:
            import fitz  # PyMuPDF
            import cv2
            import numpy as np
            
            # 初始化OCR处理器
            if self._ocr_processor is None:
                self._ocr_processor = OCRProcessor()
                
            # 打开PDF文档
            doc = fitz.open(input_path)
            
            # 确定处理的页面
            if pages == 'all':
                page_numbers = list(range(doc.page_count))
            elif isinstance(pages, str):
                # 解析页码范围，例如"1-3,5,7-10"
                page_numbers = []
                for part in pages.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        page_numbers.extend(range(start-1, end))
                    else:
                        page_numbers.append(int(part) - 1)
            else:
                # 页码列表
                page_numbers = [p-1 for p in pages]
                
            # 提取表格
            all_tables = []
            
            for page_num in page_numbers:
                if page_num >= doc.page_count:
                    continue
                    
                page = doc[page_num]
                
                # 将页面转换为图像
                pix = page.get_pixmap()
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, pix.n)
                
                # 转换为灰度图
                if pix.n == 4:  # RGBA
                    gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
                elif pix.n == 3:  # RGB
                    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                else:
                    gray = img
                    
                # 二值化处理
                _, binary = cv2.threshold(
                    gray, 150, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                # 检测表格线
                horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
                vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
                
                horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
                vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
                
                # 合并水平和垂直线
                table_mask = cv2.add(horizontal_lines, vertical_lines)
                
                # 查找轮廓
                contours, _ = cv2.findContours(
                    table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # 提取表格区域
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 过滤掉太小的区域
                    if w < 100 or h < 100:
                        continue
                        
                    # 提取表格区域图像
                    table_img = img[y:y+h, x:x+w]
                    
                    # 保存为临时图像文件
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        temp_path = tmp.name
                        cv2.imwrite(temp_path, table_img)
                        
                    # OCR处理表格图像
                    try:
                        # 使用pytesseract的表格识别功能
                        import pytesseract
                        
                        # 提取表格数据
                        table_data = pytesseract.image_to_data(
                            table_img, output_type=pytesseract.Output.DATAFRAME)
                        
                        # 处理表格数据
                        if not table_data.empty:
                            # 过滤掉空行和无效数据
                            table_data = table_data[table_data['conf'] > 0]
                            table_data = table_data[table_data['text'].str.strip() != '']
                            
                            # 根据位置信息重建表格结构
                            if not table_data.empty:
                                # 简化：按行分组
                                table_data['line_num'] = table_data['top'] // 10
                                
                                # 创建DataFrame
                                rows = []
                                for line_num, group in table_data.groupby('line_num'):
                                    # 按列排序
                                    group = group.sort_values('left')
                                    row = ' '.join(group['text'].tolist())
                                    rows.append(row)
                                    
                                # 创建简单的DataFrame
                                df = pd.DataFrame({'Content': rows})
                                all_tables.append(df)
                    except Exception as e:
                        print(f"表格OCR处理失败: {str(e)}")
                    
                    # 删除临时文件
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            
            # 保存为Excel
            if all_tables:
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    for i, table in enumerate(all_tables):
                        sheet_name = f'Table_{i+1}'
                        if i == 0:
                            sheet_name = 'Sheet1'
                        table.to_excel(writer, sheet_name=sheet_name, index=False)
                return True
            else:
                print("未能从PDF提取任何表格")
                return False
                
        except Exception as e:
            print(f"OCR表格提取失败: {str(e)}")
            return False
            
    def detect_tables(self, input_path: str, pages: Union[str, List[int]] = 'all') -> List[Dict]:
        """
        检测PDF中的表格
        
        Args:
            input_path: 输入PDF文件路径
            pages: 页码列表或范围
            
        Returns:
            List[Dict]: 检测到的表格信息列表
        """
        try:
            # 使用tabula检测表格
            tables_info = []
            
            # 读取表格
            tables = tabula.read_pdf(
                input_path,
                pages=pages,
                multiple_tables=True,
                lattice=True,
                stream=True,
                guess=True
            )
            
            # 获取表格信息
            for i, table in enumerate(tables):
                info = {
                    'index': i,
                    'rows': len(table),
                    'columns': len(table.columns),
                    'empty_cells': table.isna().sum().sum(),
                    'sample': table.head(3).to_dict()
                }
                tables_info.append(info)
                
            return tables_info
            
        except Exception as e:
            print(f"检测表格失败: {str(e)}")
            return []
            
    def preview_table(self, input_path: str, page: int, table_index: int = 0) -> Optional[pd.DataFrame]:
        """
        预览指定页面的表格
        
        Args:
            input_path: 输入PDF文件路径
            page: 页码（从1开始）
            table_index: 表格索引（如果一页有多个表格）
            
        Returns:
            Optional[pd.DataFrame]: 表格数据，如果失败则返回None
        """
        try:
            # 读取指定页面的表格
            tables = tabula.read_pdf(
                input_path,
                pages=page,
                multiple_tables=True,
                lattice=True,
                stream=True,
                guess=True
            )
            
            if not tables or table_index >= len(tables):
                return None
                
            return tables[table_index]
            
        except Exception as e:
            print(f"预览表格失败: {str(e)}")
            return None