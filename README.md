# EPUB转PDF工具

[English](README_EN.md) | 中文

一个简单易用的Python工具，用于批量将EPUB格式的电子书转换为PDF格式。

## 功能特点

- 🔄 批量转换：自动处理`source_book`目录下的所有EPUB文件
- 📁 保持目录结构：转换后的PDF文件在`output_book`目录中保持原有的目录结构
- ⚡ 智能跳过：自动检测已转换的文件，避免重复转换
- 🖼️ 图片支持：自动提取EPUB中的图片并完整嵌入PDF
- 📖 保留格式：尽可能保持原书的格式和布局
- 📄 页码支持：自动添加页码
- 🎨 中文优化：针对中文显示进行优化

## 使用方法

> **💡 提示**: 启动脚本会自动处理所有依赖安装，无需手动安装！

### 方法一：使用启动脚本（推荐）

**macOS/Linux:**
```bash
./run.sh
```

启动脚本会自动：
- 检查和安装Python依赖
- 创建和激活虚拟环境
- 创建必要的目录结构
- 运行转换程序

> **⚠️ Windows用户注意**: 需要先安装GTK+ for Windows: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer，然后使用方法二手动运行

### 方法二：手动运行（仅适用于高级用户）

<details>
<summary>点击展开手动安装步骤</summary>

1. **创建虚拟环境：**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate.bat
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行转换：**
   ```bash
   python epub2pdf.py
   ```

</details>

### 准备EPUB文件

将需要转换的EPUB文件放置到`source_book`目录中。支持子目录结构，例如：

```
source_book/
├── 小说/
│   ├── 三体.epub
│   └── 流浪地球.epub
├── 技术书籍/
│   ├── Python编程.epub
│   └── 算法导论.epub
└── 其他/
    └── 历史书.epub
```

### 查看结果

转换完成后，PDF文件将保存在`output_book`目录中，保持与源目录相同的结构：

```
output_book/
├── 小说/
│   ├── 三体.pdf
│   └── 流浪地球.pdf
├── 技术书籍/
│   ├── Python编程.pdf
│   └── 算法导论.pdf
└── 其他/
    └── 历史书.pdf
```

## 进阶使用

### 自定义源目录和输出目录

```python
from epub2pdf import EPUBtoPDFConverter

# 自定义目录
converter = EPUBtoPDFConverter(
    source_dir="my_epub_books",
    output_dir="my_pdf_books"
)
converter.convert_all()
```

### 转换单个文件

```python
from pathlib import Path
from epub2pdf import EPUBtoPDFConverter

converter = EPUBtoPDFConverter()
epub_file = Path("source_book/example.epub")
converter.convert_epub_to_pdf(epub_file)
```

## 技术说明

### 依赖库说明

- **ebooklib**: 用于读取和解析EPUB文件
- **weasyprint**: 用于将HTML转换为PDF
- **Pillow**: 图像处理支持
- **lxml**: XML解析支持

### 转换流程

1. 扫描源目录中的所有EPUB文件
2. 检查目标PDF是否已存在且为最新版本
3. 解析EPUB文件，提取章节内容和图片资源
4. 将图片转换为base64编码并嵌入HTML
5. 生成格式化的HTML内容
6. 使用WeasyPrint将HTML转换为PDF
7. 保存PDF到输出目录

### PDF格式特点

- 使用宋体字体，适合中文阅读
- 12pt字体大小，1.6倍行距
- 2cm页边距
- 自动页码
- 保留原书标题和作者信息
- 图片自动适配页面宽度，居中显示
- 完整保留EPUB中的所有图片内容

## 常见问题

### Q: 转换速度较慢怎么办？
A: EPUB转PDF是一个计算密集型操作，特别是包含大量图片的书籍。这是正常现象。

### Q: 依赖安装失败怎么办？
A: 如果`run.sh`脚本安装依赖失败，可能的原因和解决方案：
- **macOS**: 可能需要先安装系统依赖 `brew install cairo pango gdk-pixbuf libffi`
- **Ubuntu/Debian**: 需要安装 `sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
- **Windows**: 需要先安装GTK+ for Windows

### Q: 某些EPUB文件转换失败怎么办？
A: 检查日志输出中的错误信息。常见原因包括：
- EPUB文件损坏
- 包含不支持的格式
- 缺少必要的字体

### Q: 如何调整PDF的格式？
A: 修改`epub2pdf.py`中的CSS样式部分，可以调整字体、字号、行距等。

### Q: 支持哪些EPUB版本？
A: 支持EPUB 2.0和EPUB 3.0格式。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
