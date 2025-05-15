#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件工具函数
包含文件操作的辅助函数
"""

import os
from pathlib import Path
from typing import Optional


def get_output_path(input_path: str, output_dir: str, extension: str) -> str:
    """
    根据输入路径和输出目录生成输出路径
    
    Args:
        input_path: 输入文件路径
        output_dir: 输出目录
        extension: 输出文件扩展名（不包含点号）
        
    Returns:
        str: 输出文件路径
    """
    filename = Path(input_path).stem
    return os.path.join(output_dir, f"{filename}.{extension}")


def ensure_dir_exists(directory: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        bool: 目录是否存在或创建成功
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {str(e)}")
        return False


def get_safe_filename(filename: str) -> str:
    """
    获取安全的文件名，移除不允许的字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    # 移除不允许的字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_unique_path(path: str) -> str:
    """
    获取唯一的文件路径，如果文件已存在则添加数字后缀
    
    Args:
        path: 原始文件路径
        
    Returns:
        str: 唯一的文件路径
    """
    if not os.path.exists(path):
        return path
        
    directory = os.path.dirname(path)
    filename = Path(path).stem
    extension = Path(path).suffix
    
    counter = 1
    while True:
        new_path = os.path.join(directory, f"{filename}_{counter}{extension}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def is_pdf_file(file_path: str) -> bool:
    """
    检查文件是否为PDF文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否为PDF文件
    """
    return file_path.lower().endswith('.pdf') and os.path.isfile(file_path)