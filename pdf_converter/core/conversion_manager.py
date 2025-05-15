#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
转换任务管理器
协调各种转换器和处理转换任务
"""

import os
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from PyQt5.QtCore import QObject, pyqtSignal

from .converters import (
    TxtConverter,
    DocxConverter,
    ImageConverter,
    HtmlConverter,
    MarkdownConverter,
    XlsxConverter
)
from .ocr.ocr_processor import OCRProcessor


class ConversionTask:
    """转换任务类"""
    
    def __init__(
        self, 
        input_path: str, 
        output_path: str, 
        format_type: str,
        settings: Dict[str, Any]
    ):
        """
        初始化转换任务
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            format_type: 转换格式类型
            settings: 转换设置
        """
        self.input_path = input_path
        self.output_path = output_path
        self.format_type = format_type
        self.settings = settings
        self.start_time = None
        self.end_time = None
        self.success = None
        self.error_message = None
        
    @property
    def duration(self) -> Optional[float]:
        """获取任务持续时间（秒）"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
        
    def start(self):
        """开始任务"""
        self.start_time = time.time()
        
    def complete(self, success: bool, error_message: Optional[str] = None):
        """
        完成任务
        
        Args:
            success: 是否成功
            error_message: 错误信息
        """
        self.end_time = time.time()
        self.success = success
        self.error_message = error_message
        
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 任务信息字典
        """
        return {
            "input_path": self.input_path,
            "output_path": self.output_path,
            "format_type": self.format_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "error_message": self.error_message
        }


class ConversionManager(QObject):
    """转换任务管理器类"""
    
    # 信号定义
    task_started = pyqtSignal(str)  # 任务开始信号，参数为输入文件路径
    task_progress = pyqtSignal(str, int)  # 任务进度信号，参数为输入文件路径和进度值
    task_completed = pyqtSignal(str, bool, str)  # 任务完成信号，参数为输入文件路径、是否成功和错误信息
    all_tasks_completed = pyqtSignal()  # 所有任务完成信号
    
    def __init__(self):
        """初始化转换任务管理器"""
        super().__init__()
        self.converters = {}
        self.ocr_processor = None
        self.tasks = []
        self.current_task = None
        self.initialize_converters()
        
    def initialize_converters(self):
        """初始化转换器"""
        self.converters = {
            "txt": TxtConverter(),
            "docx": DocxConverter(),
            "png": ImageConverter(format_type="png"),
            "jpg": ImageConverter(format_type="jpg"),
            "html": HtmlConverter(),
            "md": MarkdownConverter(),
            "xlsx": XlsxConverter()
        }
        
    def get_converter(self, format_type: str):
        """
        获取指定格式的转换器
        
        Args:
            format_type: 格式类型
            
        Returns:
            转换器实例
        """
        format_type = format_type.lower()
        if format_type in self.converters:
            return self.converters[format_type]
        raise ValueError(f"不支持的格式类型: {format_type}")
        
    def create_task(
        self, 
        input_path: str, 
        output_path: str, 
        format_type: str,
        settings: Dict[str, Any]
    ) -> ConversionTask:
        """
        创建转换任务
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            format_type: 转换格式类型
            settings: 转换设置
            
        Returns:
            ConversionTask: 转换任务实例
        """
        task = ConversionTask(input_path, output_path, format_type, settings)
        self.tasks.append(task)
        return task
        
    def add_tasks(self, tasks: List[ConversionTask]):
        """
        添加多个转换任务
        
        Args:
            tasks: 转换任务列表
        """
        self.tasks.extend(tasks)
        
    def clear_tasks(self):
        """清除所有任务"""
        self.tasks = []
        
    def execute_task(self, task: ConversionTask) -> bool:
        """
        执行单个转换任务
        
        Args:
            task: 转换任务
            
        Returns:
            bool: 是否成功
        """
        try:
            self.current_task = task
            task.start()
            self.task_started.emit(task.input_path)
            
            # 获取转换器
            converter = self.get_converter(task.format_type)
            
            # 准备转换参数
            kwargs = self.prepare_conversion_args(task)
            
            # 执行转换
            success = converter.convert(task.input_path, task.output_path, **kwargs)
            
            if not success:
                task.complete(False, "转换失败")
                self.task_completed.emit(task.input_path, False, "转换失败")
                return False
                
            task.complete(True)
            self.task_completed.emit(task.input_path, True, "")
            return True
            
        except Exception as e:
            error_message = str(e)
            task.complete(False, error_message)
            self.task_completed.emit(task.input_path, False, error_message)
            return False
            
    def execute_all_tasks(self, progress_callback: Optional[Callable[[int], None]] = None):
        """
        执行所有转换任务
        
        Args:
            progress_callback: 进度回调函数
        """
        total_tasks = len(self.tasks)
        completed_tasks = 0
        
        for task in self.tasks:
            self.execute_task(task)
            completed_tasks += 1
            
            if progress_callback:
                progress = int(completed_tasks / total_tasks * 100)
                progress_callback(progress)
                
        self.all_tasks_completed.emit()
        
    def prepare_conversion_args(self, task: ConversionTask) -> Dict[str, Any]:
        """
        准备转换参数
        
        Args:
            task: 转换任务
            
        Returns:
            Dict[str, Any]: 转换参数
        """
        kwargs = {}
        
        # 提取OCR设置
        ocr_settings = task.settings.get("ocr", {})
        kwargs["use_ocr"] = ocr_settings.get("use_ocr", False)
        
        # 如果启用OCR，初始化OCR处理器
        if kwargs["use_ocr"]:
            if self.ocr_processor is None:
                tesseract_path = ocr_settings.get("tesseract_path")
                lang_map = {
                    "中文简体+英文": "chi_sim+eng",
                    "中文繁体+英文": "chi_tra+eng",
                    "英文": "eng",
                    "日文": "jpn",
                    "韩文": "kor",
                    "法文": "fra",
                    "德文": "deu",
                    "西班牙文": "spa"
                }
                lang = lang_map.get(ocr_settings.get("language"), "chi_sim+eng")
                self.ocr_processor = OCRProcessor(tesseract_path, lang)
                
            # 添加OCR相关参数
            kwargs["ocr_dpi"] = ocr_settings.get("dpi", 300)
            kwargs["ocr_preprocess"] = ocr_settings.get("preprocess", False)
            
        # 提取页面设置
        page_settings = task.settings.get("pages", {"type": "all"})
        page_type = page_settings.get("type", "all")
        
        if page_type == "range":
            kwargs["start_page"] = page_settings.get("from", 1)
            kwargs["end_page"] = page_settings.get("to")
        elif page_type == "custom":
            kwargs["pages"] = page_settings.get("pages", "all")
            
        # 根据格式类型添加特定参数
        format_type = task.format_type.lower()
        
        if format_type == "txt":
            txt_settings = task.settings.get("txt", {})
            kwargs["encoding"] = txt_settings.get("encoding", "UTF-8")
            kwargs["line_ending"] = txt_settings.get("line_ending", "系统默认")
            
        elif format_type == "docx":
            docx_settings = task.settings.get("docx", {})
            kwargs["preserve_format"] = docx_settings.get("preserve_format", True)
            kwargs["extract_images"] = docx_settings.get("extract_images", True)
            kwargs["detect_tables"] = docx_settings.get("detect_tables", True)
            
        elif format_type in ["png", "jpg"]:
            image_settings = task.settings.get("image", {})
            kwargs["dpi"] = image_settings.get("dpi", 200)
            kwargs["quality"] = image_settings.get("quality", 90)
            kwargs["single_file"] = image_settings.get("single_file", False)
            
        elif format_type == "html":
            html_settings = task.settings.get("html", {})
            kwargs["extract_images"] = html_settings.get("extract_images", True)
            kwargs["embed_images"] = html_settings.get("embed_images", False)
            kwargs["image_quality"] = html_settings.get("image_quality", 80)
            kwargs["css_file"] = html_settings.get("css_file")
            
        elif format_type == "md":
            md_settings = task.settings.get("markdown", {})
            kwargs["extract_images"] = md_settings.get("extract_images", True)
            kwargs["embed_images"] = md_settings.get("embed_images", False)
            kwargs["include_toc"] = md_settings.get("include_toc", True)
            
        elif format_type == "xlsx":
            xlsx_settings = task.settings.get("xlsx", {})
            kwargs["multiple_tables"] = xlsx_settings.get("multiple_tables", True)
            kwargs["lattice"] = xlsx_settings.get("lattice", True)
            kwargs["stream"] = xlsx_settings.get("stream", False)
            kwargs["guess"] = xlsx_settings.get("guess", True)
            kwargs["spreadsheet"] = xlsx_settings.get("spreadsheet", False)
            
        return kwargs
        
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的格式列表
        
        Returns:
            List[str]: 支持的格式列表
        """
        return list(self.converters.keys())
        
    def get_format_info(self) -> List[Dict[str, str]]:
        """
        获取格式信息列表
        
        Returns:
            List[Dict[str, str]]: 格式信息列表
        """
        format_info = [
            {"id": "txt", "name": "文本文件", "ext": "TXT"},
            {"id": "docx", "name": "Word文档", "ext": "DOCX"},
            {"id": "png", "name": "PNG图片", "ext": "PNG"},
            {"id": "jpg", "name": "JPG图片", "ext": "JPG"},
            {"id": "html", "name": "网页文件", "ext": "HTML"},
            {"id": "md", "name": "Markdown文件", "ext": "MD"},
            {"id": "xlsx", "name": "Excel表格", "ext": "XLSX"}
        ]
        return format_info