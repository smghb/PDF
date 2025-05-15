#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF转换工具打包配置
使用PyInstaller将项目打包为独立可执行文件
"""

import sys
from cx_Freeze import setup, Executable

# 依赖项
build_exe_options = {
    "packages": [
        "PyQt5",
        "PyPDF2",
        "fitz",  # PyMuPDF
        "pdfminer",
        "pdf2docx",
        "pdf2image",
        "Pillow",
        "tabula",
        "pytesseract",
        "numpy",
        "pandas",
        "openpyxl"
    ],
    "excludes": [],
    "include_files": [
        ("assets/", "assets/"),  # 复制资源文件
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE")
    ],
    "include_msvcr": True,  # 包含Visual C++ 运行时
}

# 基本信息
setup(
    name="PDF转换工具",
    version="1.0.0",
    description="功能全面的PDF转换工具",
    author="Your Name",
    options={
        "build_exe": build_exe_options
    },
    executables=[
        Executable(
            "main.py",
            base="Win32GUI" if sys.platform == "win32" else None,
            icon="assets/icon.ico",
            target_name="pdf_converter.exe",
            shortcut_name="PDF转换工具",
            shortcut_dir="DesktopFolder",
            copyright="Copyright (C) 2024",
        )
    ]
)

"""
打包说明：

1. 安装打包工具：
   pip install cx_Freeze

2. 创建可执行文件：
   python setup.py build

3. 创建安装程序（可选）：
   python setup.py bdist_msi  # Windows
   python setup.py bdist_dmg  # macOS
   python setup.py bdist_rpm  # Linux

注意事项：
1. 确保所有依赖项都已正确安装
2. 确保assets目录中包含必要的资源文件
3. 根据需要修改build_exe_options中的配置
4. 测试打包后的程序是否能正常运行
5. 检查是否包含所有必要的DLL和运行时文件
"""