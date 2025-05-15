# 应用程序资源文件

此目录用于存放应用程序的资源文件，如图标、图片等。

## 图标文件

应用程序需要以下图标文件：

1. `icon.png` - 主应用程序图标（PNG格式，建议尺寸：256x256像素）
2. `icon.ico` - Windows应用程序图标（ICO格式，包含多种尺寸）

### 创建图标文件

您可以使用以下工具创建图标文件：

- [GIMP](https://www.gimp.org/) - 免费的图像编辑软件
- [Inkscape](https://inkscape.org/) - 免费的矢量图形编辑软件
- [Photoshop](https://www.adobe.com/products/photoshop.html) - 专业图像编辑软件
- [Online ICO Converter](https://www.icoconverter.com/) - 在线ICO转换工具

### 图标设计建议

- 使用简单、清晰的设计
- 确保在小尺寸下仍然可识别
- 使用与应用程序功能相关的图像元素
- 考虑使用PDF相关的视觉元素，如文档图标、转换箭头等

### 示例图标描述

PDF转换工具的图标可以设计为：

- 一个PDF文档图标
- 带有转换箭头指向多种格式图标（如TXT、DOCX、图片等）
- 使用蓝色和红色作为主色调（PDF的传统颜色）
- 简洁的几何形状设计

将创建好的图标文件放置在此目录中，并确保在`setup.py`中正确引用它们。