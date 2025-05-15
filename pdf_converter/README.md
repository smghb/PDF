# PDF多功能转换工具

一个功能全面的PDF转换工具，支持将PDF转换为多种格式，并提供图形用户界面。

## 功能特点

### 格式转换
- PDF → TXT (纯文本提取)
- PDF → DOCX (Word文档)
- PDF → PNG/JPG (图片格式)
- PDF → HTML (网页格式)
- PDF → Markdown (标记语言)
- PDF → XLSX (Excel表格，适用于包含表格的PDF)

### 增强功能
- OCR识别功能 (处理扫描版PDF)
- 批量转换功能
- 保留原PDF格式 (包括字体、表格、图片等)
- 转换进度显示
- 转换结果预览

## 安装说明

### 从源码安装

1. 克隆仓库
```
git clone https://github.com/yourusername/pdf-converter.git
cd pdf-converter
```

2. 安装依赖
```
pip install -r requirements.txt
```

3. 运行程序
```
python main.py
```

### 使用独立应用程序

1. 从[发布页面](https://github.com/yourusername/pdf-converter/releases)下载最新版本
2. 解压缩下载的文件
3. 运行可执行文件 `pdf_converter.exe` (Windows) 或 `pdf_converter` (macOS/Linux)

## 使用说明

1. 启动应用程序
2. 通过"打开文件"按钮或拖放方式添加PDF文件
3. 选择目标转换格式
4. 配置转换选项
5. 点击"转换"按钮开始转换
6. 转换完成后，可以在指定位置找到转换后的文件

## 系统要求

- Windows 7/8/10/11
- macOS 10.13 或更高版本
- Linux (主流发行版)

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎贡献代码、报告问题或提出改进建议。请查看 [贡献指南](CONTRIBUTING.md) 了解更多信息。