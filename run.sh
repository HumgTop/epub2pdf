#!/bin/bash

# EPUB转PDF工具启动脚本

echo "🚀 启动EPUB转PDF工具..."

# 检查Python是否存在
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查requirements.txt是否存在
if [ ! -f "requirements.txt" ]; then
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️ 升级pip到最新版本..."
pip install --upgrade pip -q

# 检查依赖是否需要安装或更新
echo "🔍 检查依赖包..."
NEED_INSTALL=false

# 检查每个依赖包
if ! python -c "import ebooklib" 2>/dev/null; then
    echo "   - ebooklib: 未安装"
    NEED_INSTALL=true
fi

if ! python -c "import weasyprint" 2>/dev/null; then
    echo "   - weasyprint: 未安装"
    NEED_INSTALL=true
fi

if ! python -c "import PIL" 2>/dev/null; then
    echo "   - Pillow: 未安装"
    NEED_INSTALL=true
fi

if ! python -c "import lxml" 2>/dev/null; then
    echo "   - lxml: 未安装"
    NEED_INSTALL=true
fi

# 如果需要安装依赖
if [ "$NEED_INSTALL" = true ]; then
    echo "📥 安装依赖包..."
    pip install -r requirements.txt
    
    # 验证安装是否成功
    echo "🔍 验证依赖安装..."
    if ! python -c "import ebooklib, weasyprint, PIL, lxml" 2>/dev/null; then
        echo "❌ 依赖安装失败，请检查错误信息"
        echo "💡 提示：可能需要先安装系统依赖，请参考README.md"
        exit 1
    else
        echo "✅ 所有依赖安装成功"
    fi
else
    echo "✅ 所有依赖已正确安装"
fi

# 检查源文件目录
if [ ! -d "source_book" ]; then
    echo "📁 创建source_book目录..."
    mkdir -p source_book
fi

# 检查输出目录
if [ ! -d "output_book" ]; then
    echo "📁 创建output_book目录..."
    mkdir -p output_book
fi

# 检查是否有EPUB文件
EPUB_COUNT=$(find source_book -name "*.epub" -type f | wc -l)
if [ $EPUB_COUNT -eq 0 ]; then
    echo "⚠️  source_book目录中没有找到EPUB文件"
    echo "💡 请将EPUB文件放入source_book目录后重新运行"
    exit 0
fi

echo "📚 找到 $EPUB_COUNT 个EPUB文件"

# 运行转换器
echo "🔄 开始转换..."
python epub2pdf.py

echo "✅ 转换完成！"
