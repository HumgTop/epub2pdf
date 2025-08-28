#!/bin/bash

# EPUB转PDF工具启动脚本

echo "🚀 启动EPUB转PDF工具..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! python -c "import ebooklib, weasyprint, PIL, lxml" 2>/dev/null; then
    echo "📥 安装依赖包..."
    pip install -r requirements.txt
    
    # 验证安装是否成功
    if ! python -c "import ebooklib, weasyprint, PIL, lxml" 2>/dev/null; then
        echo "❌ 依赖安装失败，请检查错误信息"
        exit 1
    else
        echo "✅ 依赖安装成功"
    fi
fi

# 运行转换器
echo "🔄 开始转换..."
python epub2pdf.py

echo "✅ 转换完成！"
