#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
转换器基类
定义所有转换器共有的接口和方法
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

class BaseConverter(ABC):
    """转换器抽象基类"""
    
    def __init__(self):
        self.supported_formats = []
        
    @abstractmethod
    def convert(self, input_path: str, output_path: str, **kwargs) -> bool:
        """
        执行转换操作
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出文件路径
            **kwargs: 其他转换参数
            
        Returns:
            bool: 转换是否成功
        """
        pass
        
    def batch_convert(self, input_paths: List[str], output_dir: str, **kwargs) -> List[str]:
        """
        批量转换多个PDF文件
        
        Args:
            input_paths: 输入PDF文件路径列表
            output_dir: 输出目录
            **kwargs: 其他转换参数
            
        Returns:
            List[str]: 成功转换的文件路径列表
        """
        success_files = []
        for input_path in input_paths:
            try:
                filename = Path(input_path).stem
                output_path = os.path.join(output_dir, f"{filename}.{self.output_extension}")
                if self.convert(input_path, output_path, **kwargs):
                    success_files.append(output_path)
            except Exception as e:
                print(f"转换 {input_path} 失败: {str(e)}")
        return success_files
        
    @property
    @abstractmethod
    def output_extension(self) -> str:
        """获取输出文件的扩展名"""
        pass
        
    def get_output_path(self, input_path: str, output_dir: str) -> str:
        """
        根据输入路径和输出目录生成输出路径
        
        Args:
            input_path: 输入文件路径
            output_dir: 输出目录
            
        Returns:
            str: 输出文件路径
        """
        filename = Path(input_path).stem
        return os.path.join(output_dir, f"{filename}.{self.output_extension}")
        
    def ensure_output_dir(self, output_dir: str) -> bool:
        """
        确保输出目录存在
        
        Args:
            output_dir: 输出目录路径
            
        Returns:
            bool: 目录是否存在或创建成功
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建输出目录失败: {str(e)}")
            return False