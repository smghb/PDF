#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF多功能转换工具
主程序入口
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    """主函数，程序入口点"""
    # 确保当前工作目录正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("PDF多功能转换工具")
    
    # 设置应用程序图标
    icon_path = os.path.join("assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()