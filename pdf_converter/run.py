#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF转换工具启动脚本
用于在开发环境中运行应用程序
"""

import os
import sys

# 确保当前工作目录正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 将当前目录添加到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主模块并运行
from main import main

if __name__ == "__main__":
    main()