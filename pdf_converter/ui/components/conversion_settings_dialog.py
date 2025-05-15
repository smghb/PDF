#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
转换设置对话框
允许用户配置转换选项
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QCheckBox, QSpinBox,
    QDialogButtonBox, QGroupBox, QTabWidget,
    QLineEdit, QPushButton, QFileDialog
)
from PyQt5.QtCore import Qt, QSettings


class ConversionSettingsDialog(QDialog):
    """转换设置对话框类"""
    
    def __init__(self, format_type, parent=None):
        """
        初始化对话框
        
        Args:
            format_type: 转换格式类型
            parent: 父窗口
        """
        super().__init__(parent)
        self.format_type = format_type
        self.settings = QSettings("PDFConverter", "Settings")
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("转换设置")
        self.setMinimumWidth(400)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 创建通用设置选项卡
        general_tab = QWidget()
        tab_widget.addTab(general_tab, "通用设置")
        self.create_general_tab(general_tab)
        
        # 创建格式特定设置选项卡
        format_tab = QWidget()
        tab_widget.addTab(format_tab, f"{self.format_type}设置")
        self.create_format_tab(format_tab)
        
        # 创建OCR设置选项卡
        ocr_tab = QWidget()
        tab_widget.addTab(ocr_tab, "OCR设置")
        self.create_ocr_tab(ocr_tab)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def create_general_tab(self, tab):
        """创建通用设置选项卡"""
        layout = QVBoxLayout(tab)
        
        # 页面范围设置
        page_group = QGroupBox("页面范围")
        page_layout = QFormLayout()
        
        self.all_pages_radio = QCheckBox("所有页面")
        self.all_pages_radio.setChecked(True)
        page_layout.addRow(self.all_pages_radio)
        
        page_range_layout = QHBoxLayout()
        self.page_from_spin = QSpinBox()
        self.page_from_spin.setMinimum(1)
        self.page_from_spin.setMaximum(9999)
        self.page_to_spin = QSpinBox()
        self.page_to_spin.setMinimum(1)
        self.page_to_spin.setMaximum(9999)
        page_range_layout.addWidget(QLabel("从"))
        page_range_layout.addWidget(self.page_from_spin)
        page_range_layout.addWidget(QLabel("到"))
        page_range_layout.addWidget(self.page_to_spin)
        page_range_layout.addStretch()
        
        self.page_range_radio = QCheckBox("指定页面范围")
        page_layout.addRow(self.page_range_radio, page_range_layout)
        
        self.custom_pages_radio = QCheckBox("自定义页面")
        self.custom_pages_edit = QLineEdit()
        self.custom_pages_edit.setPlaceholderText("例如: 1,3,5-7")
        page_layout.addRow(self.custom_pages_radio, self.custom_pages_edit)
        
        page_group.setLayout(page_layout)
        layout.addWidget(page_group)
        
        # 连接信号
        self.all_pages_radio.toggled.connect(self.update_page_options)
        self.page_range_radio.toggled.connect(self.update_page_options)
        self.custom_pages_radio.toggled.connect(self.update_page_options)
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QFormLayout()
        
        self.overwrite_check = QCheckBox("覆盖现有文件")
        output_layout.addRow(self.overwrite_check)
        
        self.open_after_check = QCheckBox("转换后打开文件")
        output_layout.addRow(self.open_after_check)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # 添加伸展因子
        layout.addStretch()
        
    def create_format_tab(self, tab):
        """创建格式特定设置选项卡"""
        layout = QVBoxLayout(tab)
        
        if self.format_type in ["TXT", "文本文件"]:
            self.create_txt_settings(layout)
        elif self.format_type in ["DOCX", "Word文档"]:
            self.create_docx_settings(layout)
        elif self.format_type in ["PNG", "JPG", "图片文件"]:
            self.create_image_settings(layout)
        elif self.format_type in ["HTML", "网页文件"]:
            self.create_html_settings(layout)
        elif self.format_type in ["MD", "Markdown文件"]:
            self.create_markdown_settings(layout)
        elif self.format_type in ["XLSX", "Excel表格"]:
            self.create_xlsx_settings(layout)
        
        # 添加伸展因子
        layout.addStretch()
        
    def create_txt_settings(self, layout):
        """创建TXT设置"""
        encoding_group = QGroupBox("编码设置")
        encoding_layout = QFormLayout()
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["UTF-8", "GBK", "ASCII", "Latin-1"])
        encoding_layout.addRow("文件编码:", self.encoding_combo)
        
        self.line_ending_combo = QComboBox()
        self.line_ending_combo.addItems(["系统默认", "Windows (CRLF)", "Unix (LF)", "Mac (CR)"])
        encoding_layout.addRow("行尾符:", self.line_ending_combo)
        
        encoding_group.setLayout(encoding_layout)
        layout.addWidget(encoding_group)
        
    def create_docx_settings(self, layout):
        """创建DOCX设置"""
        docx_group = QGroupBox("Word文档设置")
        docx_layout = QFormLayout()
        
        self.preserve_format_check = QCheckBox("尽可能保留原始格式")
        self.preserve_format_check.setChecked(True)
        docx_layout.addRow(self.preserve_format_check)
        
        self.extract_images_check = QCheckBox("提取并包含图片")
        self.extract_images_check.setChecked(True)
        docx_layout.addRow(self.extract_images_check)
        
        self.detect_tables_check = QCheckBox("检测并转换表格")
        self.detect_tables_check.setChecked(True)
        docx_layout.addRow(self.detect_tables_check)
        
        docx_group.setLayout(docx_layout)
        layout.addWidget(docx_group)
        
    def create_image_settings(self, layout):
        """创建图片设置"""
        image_group = QGroupBox("图片设置")
        image_layout = QFormLayout()
        
        self.image_format_combo = QComboBox()
        self.image_format_combo.addItems(["PNG", "JPG"])
        image_layout.addRow("图片格式:", self.image_format_combo)
        
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setMinimum(72)
        self.dpi_spin.setMaximum(600)
        self.dpi_spin.setValue(200)
        image_layout.addRow("DPI:", self.dpi_spin)
        
        self.quality_spin = QSpinBox()
        self.quality_spin.setMinimum(1)
        self.quality_spin.setMaximum(100)
        self.quality_spin.setValue(90)
        image_layout.addRow("质量(JPG):", self.quality_spin)
        
        self.single_file_check = QCheckBox("合并为单个文件")
        image_layout.addRow(self.single_file_check)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
    def create_html_settings(self, layout):
        """创建HTML设置"""
        html_group = QGroupBox("HTML设置")
        html_layout = QFormLayout()
        
        self.extract_images_html_check = QCheckBox("提取图片")
        self.extract_images_html_check.setChecked(True)
        html_layout.addRow(self.extract_images_html_check)
        
        self.embed_images_check = QCheckBox("嵌入图片(Base64)")
        html_layout.addRow(self.embed_images_check)
        
        self.image_quality_html_spin = QSpinBox()
        self.image_quality_html_spin.setMinimum(1)
        self.image_quality_html_spin.setMaximum(100)
        self.image_quality_html_spin.setValue(80)
        html_layout.addRow("图片质量:", self.image_quality_html_spin)
        
        self.css_file_edit = QLineEdit()
        css_browse_btn = QPushButton("浏览...")
        css_browse_btn.clicked.connect(self.browse_css_file)
        css_layout = QHBoxLayout()
        css_layout.addWidget(self.css_file_edit)
        css_layout.addWidget(css_browse_btn)
        html_layout.addRow("自定义CSS:", css_layout)
        
        html_group.setLayout(html_layout)
        layout.addWidget(html_group)
        
    def create_markdown_settings(self, layout):
        """创建Markdown设置"""
        md_group = QGroupBox("Markdown设置")
        md_layout = QFormLayout()
        
        self.extract_images_md_check = QCheckBox("提取图片")
        self.extract_images_md_check.setChecked(True)
        md_layout.addRow(self.extract_images_md_check)
        
        self.embed_images_md_check = QCheckBox("嵌入图片(Base64)")
        md_layout.addRow(self.embed_images_md_check)
        
        self.include_toc_check = QCheckBox("包含目录")
        self.include_toc_check.setChecked(True)
        md_layout.addRow(self.include_toc_check)
        
        md_group.setLayout(md_layout)
        layout.addWidget(md_group)
        
    def create_xlsx_settings(self, layout):
        """创建Excel设置"""
        xlsx_group = QGroupBox("Excel设置")
        xlsx_layout = QFormLayout()
        
        self.multiple_tables_check = QCheckBox("提取多个表格")
        self.multiple_tables_check.setChecked(True)
        xlsx_layout.addRow(self.multiple_tables_check)
        
        self.lattice_check = QCheckBox("使用格子模式(适用于有表格线的PDF)")
        self.lattice_check.setChecked(True)
        xlsx_layout.addRow(self.lattice_check)
        
        self.stream_check = QCheckBox("使用流模式(适用于没有表格线的PDF)")
        xlsx_layout.addRow(self.stream_check)
        
        self.guess_check = QCheckBox("猜测表格结构")
        self.guess_check.setChecked(True)
        xlsx_layout.addRow(self.guess_check)
        
        self.spreadsheet_check = QCheckBox("所有表格放在一个工作表中")
        xlsx_layout.addRow(self.spreadsheet_check)
        
        xlsx_group.setLayout(xlsx_layout)
        layout.addWidget(xlsx_group)
        
    def create_ocr_tab(self, tab):
        """创建OCR设置选项卡"""
        layout = QVBoxLayout(tab)
        
        # OCR基本设置
        ocr_group = QGroupBox("OCR设置")
        ocr_layout = QFormLayout()
        
        self.use_ocr_check = QCheckBox("启用OCR(用于扫描版PDF)")
        ocr_layout.addRow(self.use_ocr_check)
        
        self.ocr_lang_combo = QComboBox()
        self.ocr_lang_combo.addItems(["中文简体+英文", "中文繁体+英文", "英文", "日文", "韩文", "法文", "德文", "西班牙文"])
        ocr_layout.addRow("OCR语言:", self.ocr_lang_combo)
        
        self.ocr_dpi_spin = QSpinBox()
        self.ocr_dpi_spin.setMinimum(72)
        self.ocr_dpi_spin.setMaximum(600)
        self.ocr_dpi_spin.setValue(300)
        ocr_layout.addRow("OCR DPI:", self.ocr_dpi_spin)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # Tesseract路径设置
        tesseract_group = QGroupBox("Tesseract设置")
        tesseract_layout = QFormLayout()
        
        self.tesseract_path_edit = QLineEdit()
        tesseract_browse_btn = QPushButton("浏览...")
        tesseract_browse_btn.clicked.connect(self.browse_tesseract_path)
        tesseract_layout_h = QHBoxLayout()
        tesseract_layout_h.addWidget(self.tesseract_path_edit)
        tesseract_layout_h.addWidget(tesseract_browse_btn)
        tesseract_layout.addRow("Tesseract路径:", tesseract_layout_h)
        
        tesseract_group.setLayout(tesseract_layout)
        layout.addWidget(tesseract_group)
        
        # 图像预处理设置
        preprocess_group = QGroupBox("图像预处理")
        preprocess_layout = QFormLayout()
        
        self.preprocess_check = QCheckBox("启用图像预处理")
        preprocess_layout.addRow(self.preprocess_check)
        
        self.denoise_check = QCheckBox("降噪")
        preprocess_layout.addRow(self.denoise_check)
        
        self.threshold_check = QCheckBox("二值化")
        preprocess_layout.addRow(self.threshold_check)
        
        preprocess_group.setLayout(preprocess_layout)
        layout.addWidget(preprocess_group)
        
        # 添加伸展因子
        layout.addStretch()
        
    def update_page_options(self):
        """更新页面选项状态"""
        self.page_from_spin.setEnabled(self.page_range_radio.isChecked())
        self.page_to_spin.setEnabled(self.page_range_radio.isChecked())
        self.custom_pages_edit.setEnabled(self.custom_pages_radio.isChecked())
        
    def browse_css_file(self):
        """浏览CSS文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CSS文件", "", "CSS文件 (*.css)")
        if file_path:
            self.css_file_edit.setText(file_path)
            
    def browse_tesseract_path(self):
        """浏览Tesseract可执行文件路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Tesseract可执行文件", "", 
            "可执行文件 (*.exe);;所有文件 (*.*)")
        if file_path:
            self.tesseract_path_edit.setText(file_path)
            
    def load_settings(self):
        """加载设置"""
        # 通用设置
        self.overwrite_check.setChecked(
            self.settings.value("general/overwrite", False, type=bool))
        self.open_after_check.setChecked(
            self.settings.value("general/open_after", True, type=bool))
        
        # OCR设置
        self.use_ocr_check.setChecked(
            self.settings.value("ocr/use_ocr", False, type=bool))
        
        ocr_lang_index = self.settings.value("ocr/language_index", 0, type=int)
        if 0 <= ocr_lang_index < self.ocr_lang_combo.count():
            self.ocr_lang_combo.setCurrentIndex(ocr_lang_index)
            
        self.ocr_dpi_spin.setValue(
            self.settings.value("ocr/dpi", 300, type=int))
        
        self.tesseract_path_edit.setText(
            self.settings.value("ocr/tesseract_path", ""))
        
        self.preprocess_check.setChecked(
            self.settings.value("ocr/preprocess", False, type=bool))
        self.denoise_check.setChecked(
            self.settings.value("ocr/denoise", False, type=bool))
        self.threshold_check.setChecked(
            self.settings.value("ocr/threshold", False, type=bool))
        
        # 格式特定设置
        if self.format_type in ["PNG", "JPG", "图片文件"]:
            self.dpi_spin.setValue(
                self.settings.value("image/dpi", 200, type=int))
            self.quality_spin.setValue(
                self.settings.value("image/quality", 90, type=int))
            
            format_index = 0
            if self.format_type == "JPG" or self.format_type == "图片文件" and \
               self.settings.value("image/format", "PNG") == "JPG":
                format_index = 1
            self.image_format_combo.setCurrentIndex(format_index)
            
    def save_settings(self):
        """保存设置"""
        # 通用设置
        self.settings.setValue("general/overwrite", self.overwrite_check.isChecked())
        self.settings.setValue("general/open_after", self.open_after_check.isChecked())
        
        # OCR设置
        self.settings.setValue("ocr/use_ocr", self.use_ocr_check.isChecked())
        self.settings.setValue("ocr/language_index", self.ocr_lang_combo.currentIndex())
        self.settings.setValue("ocr/dpi", self.ocr_dpi_spin.value())
        self.settings.setValue("ocr/tesseract_path", self.tesseract_path_edit.text())
        self.settings.setValue("ocr/preprocess", self.preprocess_check.isChecked())
        self.settings.setValue("ocr/denoise", self.denoise_check.isChecked())
        self.settings.setValue("ocr/threshold", self.threshold_check.isChecked())
        
        # 格式特定设置
        if self.format_type in ["PNG", "JPG", "图片文件"]:
            self.settings.setValue("image/dpi", self.dpi_spin.value())
            self.settings.setValue("image/quality", self.quality_spin.value())
            self.settings.setValue("image/format", self.image_format_combo.currentText())
            
    def accept(self):
        """确认对话框"""
        self.save_settings()
        super().accept()
        
    def get_settings(self):
        """获取设置"""
        settings = {
            "general": {
                "overwrite": self.overwrite_check.isChecked(),
                "open_after": self.open_after_check.isChecked()
            },
            "pages": self.get_page_settings(),
            "ocr": {
                "use_ocr": self.use_ocr_check.isChecked(),
                "language": self.ocr_lang_combo.currentText(),
                "dpi": self.ocr_dpi_spin.value(),
                "tesseract_path": self.tesseract_path_edit.text(),
                "preprocess": self.preprocess_check.isChecked(),
                "denoise": self.denoise_check.isChecked(),
                "threshold": self.threshold_check.isChecked()
            }
        }
        
        # 添加格式特定设置
        if self.format_type in ["TXT", "文本文件"]:
            settings["txt"] = {
                "encoding": self.encoding_combo.currentText(),
                "line_ending": self.line_ending_combo.currentText()
            }
        elif self.format_type in ["DOCX", "Word文档"]:
            settings["docx"] = {
                "preserve_format": self.preserve_format_check.isChecked(),
                "extract_images": self.extract_images_check.isChecked(),
                "detect_tables": self.detect_tables_check.isChecked()
            }
        elif self.format_type in ["PNG", "JPG", "图片文件"]:
            settings["image"] = {
                "format": self.image_format_combo.currentText(),
                "dpi": self.dpi_spin.value(),
                "quality": self.quality_spin.value(),
                "single_file": self.single_file_check.isChecked()
            }
        elif self.format_type in ["HTML", "网页文件"]:
            settings["html"] = {
                "extract_images": self.extract_images_html_check.isChecked(),
                "embed_images": self.embed_images_check.isChecked(),
                "image_quality": self.image_quality_html_spin.value(),
                "css_file": self.css_file_edit.text()
            }
        elif self.format_type in ["MD", "Markdown文件"]:
            settings["markdown"] = {
                "extract_images": self.extract_images_md_check.isChecked(),
                "embed_images": self.embed_images_md_check.isChecked(),
                "include_toc": self.include_toc_check.isChecked()
            }
        elif self.format_type in ["XLSX", "Excel表格"]:
            settings["xlsx"] = {
                "multiple_tables": self.multiple_tables_check.isChecked(),
                "lattice": self.lattice_check.isChecked(),
                "stream": self.stream_check.isChecked(),
                "guess": self.guess_check.isChecked(),
                "spreadsheet": self.spreadsheet_check.isChecked()
            }
            
        return settings
        
    def get_page_settings(self):
        """获取页面设置"""
        if self.all_pages_radio.isChecked():
            return {"type": "all"}
        elif self.page_range_radio.isChecked():
            return {
                "type": "range",
                "from": self.page_from_spin.value(),
                "to": self.page_to_spin.value()
            }
        elif self.custom_pages_radio.isChecked():
            return {
                "type": "custom",
                "pages": self.custom_pages_edit.text()
            }
        return {"type": "all"}