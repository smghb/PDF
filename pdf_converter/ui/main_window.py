#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口类
包含应用程序的主要GUI界面
"""

import os
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QComboBox, QLabel, QFileDialog,
    QProgressBar, QListWidget, QMessageBox, QGroupBox,
    QApplication, QStatusBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon

# 导入自定义模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.conversion_manager import ConversionManager

class ConversionThread(QThread):
    """转换处理线程"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, conversion_manager, parent=None):
        super().__init__(parent)
        self.conversion_manager = conversion_manager
        
    def run(self):
        """执行转换任务"""
        try:
            # 执行所有转换任务
            self.conversion_manager.execute_all_tasks(
                progress_callback=self.update_progress
            )
            self.finished.emit(True, "转换完成")
        except Exception as e:
            self.finished.emit(False, str(e))
            
    def update_progress(self, value):
        """更新进度"""
        self.progress.emit(value)


from core.conversion_manager import ConversionManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.conversion_manager = ConversionManager()
        self.output_dir = None
        self.output_format = None
        self.init_ui()
        
        # 连接信号
        self.conversion_manager.task_started.connect(self.on_task_started)
        self.conversion_manager.task_progress.connect(self.on_task_progress)
        self.conversion_manager.task_completed.connect(self.on_task_completed)
        self.conversion_manager.all_tasks_completed.connect(self.on_all_tasks_completed)
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PDF多功能转换工具")
        self.setMinimumSize(800, 600)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 添加文件列表区域
        self.create_file_list_group(main_layout)
        
        # 添加转换选项区域
        self.create_conversion_options_group(main_layout)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # 添加底部按钮区域
        self.create_bottom_buttons(main_layout)
        
        # 设置窗口接受拖放
        self.setAcceptDrops(True)
        
    def create_file_list_group(self, parent_layout):
        """创建文件列表组"""
        group = QGroupBox("文件列表")
        layout = QVBoxLayout()
        
        # 文件列表
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # 文件操作按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加文件")
        add_btn.clicked.connect(self.add_files)
        remove_btn = QPushButton("移除选中")
        remove_btn.clicked.connect(self.remove_selected_files)
        clear_btn = QPushButton("清空列表")
        clear_btn.clicked.connect(self.file_list.clear)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def create_conversion_options_group(self, parent_layout):
        """创建转换选项组"""
        group = QGroupBox("转换选项")
        layout = QVBoxLayout()
        
        # 格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("目标格式:"))
        self.format_combo = QComboBox()
        
        # 从转换管理器获取格式信息
        format_info = self.conversion_manager.get_format_info()
        for fmt in format_info:
            self.format_combo.addItem(f"{fmt['name']} ({fmt['ext']})", fmt['id'])
            
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # 设置按钮
        settings_layout = QHBoxLayout()
        self.settings_btn = QPushButton("转换设置")
        self.settings_btn.clicked.connect(self.show_conversion_settings)
        settings_layout.addWidget(self.settings_btn)
        
        # OCR选项
        self.ocr_checkbox = QPushButton("启用OCR")
        self.ocr_checkbox.setCheckable(True)
        self.ocr_checkbox.toggled.connect(self.on_ocr_toggled)
        settings_layout.addWidget(self.ocr_checkbox)
        
        layout.addLayout(settings_layout)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
        # 初始化输出格式
        self.output_format = self.format_combo.currentData()
        
    def create_bottom_buttons(self, parent_layout):
        """创建底部按钮区域"""
        layout = QHBoxLayout()
        
        self.output_dir_btn = QPushButton("选择输出目录")
        self.output_dir_btn.clicked.connect(self.select_output_directory)
        
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        
        layout.addWidget(self.output_dir_btn)
        layout.addWidget(self.convert_btn)
        
        parent_layout.addLayout(layout)
        
    def add_files(self):
        """添加文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择PDF文件",
            "",
            "PDF文件 (*.pdf)"
        )
        for file in files:
            if file not in [self.file_list.item(i).text() 
                          for i in range(self.file_list.count())]:
                self.file_list.addItem(file)
                
    def remove_selected_files(self):
        """移除选中的文件"""
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))
            
    def select_output_directory(self):
        """选择输出目录"""
        self.output_dir = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            ""
        )
        if self.output_dir:
            self.output_dir_btn.setText(f"输出目录: {os.path.basename(self.output_dir)}")
            
    def start_conversion(self):
        """开始转换"""
        if self.file_list.count() == 0:
            QMessageBox.warning(self, "警告", "请先添加要转换的PDF文件！")
            return
            
        if not self.output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录！")
            return
            
        # 获取文件列表
        files = [self.file_list.item(i).text() 
                for i in range(self.file_list.count())]
        
        # 获取选择的格式
        self.output_format = self.format_combo.currentData()
        
        # 清除之前的任务
        self.conversion_manager.clear_tasks()
        
        # 创建转换设置
        settings = self.get_conversion_settings()
        
        # 创建转换任务
        for input_path in files:
            # 生成输出路径
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(
                self.output_dir, 
                f"{filename}.{self.conversion_manager.get_converter(self.output_format).output_extension}"
            )
            
            # 创建任务
            self.conversion_manager.create_task(
                input_path, output_path, self.output_format, settings
            )
        
        # 禁用界面
        self.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # 创建并启动转换线程
        self.conversion_thread = ConversionThread(self.conversion_manager)
        self.conversion_thread.progress.connect(self.progress_bar.setValue)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.start()
        
    def conversion_finished(self, success, message):
        """转换完成的回调函数"""
        self.setEnabled(True)
        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.critical(self, "错误", f"转换失败：{message}")
            
    def on_task_started(self, input_path):
        """任务开始的回调函数"""
        self.statusBar().showMessage(f"正在转换: {os.path.basename(input_path)}...")
        
    def on_task_progress(self, input_path, progress):
        """任务进度的回调函数"""
        self.progress_bar.setValue(progress)
        
    def on_task_completed(self, input_path, success, error_message):
        """任务完成的回调函数"""
        filename = os.path.basename(input_path)
        if success:
            self.statusBar().showMessage(f"{filename} 转换成功")
        else:
            self.statusBar().showMessage(f"{filename} 转换失败: {error_message}")
            
    def on_all_tasks_completed(self):
        """所有任务完成的回调函数"""
        self.statusBar().showMessage("所有转换任务已完成")
        
    def on_format_changed(self, index):
        """格式改变的回调函数"""
        self.output_format = self.format_combo.currentData()
        
    def on_ocr_toggled(self, checked):
        """OCR选项切换的回调函数"""
        if checked:
            self.statusBar().showMessage("OCR功能已启用，将尝试识别扫描版PDF中的文本")
        else:
            self.statusBar().showMessage("OCR功能已禁用")
            
    def show_conversion_settings(self):
        """显示转换设置对话框"""
        from ui.components.conversion_settings_dialog import ConversionSettingsDialog
        
        format_text = self.format_combo.currentText()
        dialog = ConversionSettingsDialog(format_text, self)
        
        if dialog.exec_():
            self.conversion_settings = dialog.get_settings()
            self.statusBar().showMessage("转换设置已更新")
            
    def get_conversion_settings(self):
        """获取转换设置"""
        if not hasattr(self, 'conversion_settings'):
            # 默认设置
            self.conversion_settings = {
                "general": {
                    "overwrite": False,
                    "open_after": True
                },
                "pages": {"type": "all"},
                "ocr": {
                    "use_ocr": self.ocr_checkbox.isChecked(),
                    "language": "中文简体+英文",
                    "dpi": 300
                }
            }
            
        # 确保OCR设置与复选框状态一致
        self.conversion_settings["ocr"]["use_ocr"] = self.ocr_checkbox.isChecked()
        
        return self.conversion_settings
            
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        files = [url.toLocalFile() for url in event.mimeData().urls()
                if url.toLocalFile().lower().endswith('.pdf')]
        for file in files:
            if file not in [self.file_list.item(i).text() 
                          for i in range(self.file_list.count())]:
                self.file_list.addItem(file)