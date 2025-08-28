#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB转PDF工具
将source_book目录下的所有EPUB文件转换为PDF格式并保存到output_book目录
"""

import os
import sys
from pathlib import Path
import logging
import base64
import tempfile
import shutil
import re
from typing import List, Optional, Dict

# 设置递归限制，防止递归过深
sys.setrecursionlimit(3000)

try:
    import ebooklib
    from ebooklib import epub
    import weasyprint
    from weasyprint import HTML, CSS
except ImportError as e:
    print(f"缺少必要的依赖包: {e}")
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)


class EPUBtoPDFConverter:
    """EPUB转PDF转换器"""
    
    def __init__(self, source_dir: str = "source_book", output_dir: str = "output_book"):
        """
        初始化转换器
        
        Args:
            source_dir: EPUB文件源目录
            output_dir: PDF文件输出目录
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        # 确保输出目录存在
        self.output_dir.mkdir(exist_ok=True)
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def find_epub_files(self) -> List[Path]:
        """
        查找源目录下的所有EPUB文件
        
        Returns:
            EPUB文件路径列表
        """
        if not self.source_dir.exists():
            self.logger.error(f"源目录不存在: {self.source_dir}")
            return []
        
        epub_files = list(self.source_dir.glob("**/*.epub"))
        self.logger.info(f"找到 {len(epub_files)} 个EPUB文件")
        return epub_files
    
    def get_output_path(self, epub_path: Path) -> Path:
        """
        根据EPUB文件路径生成对应的PDF输出路径
        
        Args:
            epub_path: EPUB文件路径
            
        Returns:
            PDF文件输出路径
        """
        # 保持相对目录结构
        relative_path = epub_path.relative_to(self.source_dir)
        pdf_path = self.output_dir / relative_path.with_suffix('.pdf')
        
        # 确保输出目录存在
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        return pdf_path
    
    def is_already_converted(self, epub_path: Path) -> bool:
        """
        检查EPUB文件是否已经转换过
        
        Args:
            epub_path: EPUB文件路径
            
        Returns:
            如果已转换返回True，否则返回False
        """
        pdf_path = self.get_output_path(epub_path)
        if pdf_path.exists():
            # 比较文件修改时间，如果PDF比EPUB新，则认为已转换
            epub_mtime = epub_path.stat().st_mtime
            pdf_mtime = pdf_path.stat().st_mtime
            return pdf_mtime >= epub_mtime
        return False
    
    def extract_epub_content(self, epub_path: Path) -> Optional[str]:
        """
        从EPUB文件中提取HTML内容
        
        Args:
            epub_path: EPUB文件路径
            
        Returns:
            提取的HTML内容，失败时返回None
        """
        try:
            book = epub.read_epub(str(epub_path))
            
            # 获取书籍信息
            title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else epub_path.stem
            author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "未知作者"
            
            self.logger.info(f"处理书籍: {title} - {author}")
            
            # 提取图片资源
            images = self.extract_images_from_epub(book)
            
            # 构建HTML内容
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{title}</title>
                <style>
                    body {{
                        font-family: "SimSun", "宋体", serif;
                        font-size: 12pt;
                        line-height: 1.6;
                        margin: 2cm;
                        text-align: justify;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        font-weight: bold;
                        margin-top: 1em;
                        margin-bottom: 0.5em;
                    }}
                    h1 {{ font-size: 18pt; }}
                    h2 {{ font-size: 16pt; }}
                    h3 {{ font-size: 14pt; }}
                    p {{ margin: 0.5em 0; }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 1em auto;
                    }}
                    .title-page {{
                        text-align: center;
                        margin-bottom: 2em;
                    }}
                    .title {{ font-size: 24pt; font-weight: bold; }}
                    .author {{ font-size: 16pt; margin-top: 1em; }}
                    @page {{
                        margin: 2cm;
                        @bottom-center {{
                            content: counter(page);
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="title-page">
                    <div class="title">{title}</div>
                    <div class="author">{author}</div>
                </div>
            """
            
            # 获取所有文档类型的内容
            documents = []
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    documents.append(item)
            
            # 按spine顺序排序文档（如果有spine的话）
            if hasattr(book, 'spine') and book.spine:
                spine_order = {}
                for index, (item_id, linear) in enumerate(book.spine):
                    spine_order[item_id] = index
                
                # 按spine顺序排序
                documents.sort(key=lambda doc: spine_order.get(doc.get_id(), 999))
            
            # 添加所有文档内容
            for item in documents:
                try:
                    content = item.get_content().decode('utf-8', errors='ignore')
                    # 简单的HTML清理和格式化，并替换图片引用
                    cleaned_content = self._clean_html_content(content)
                    content_with_images = self._replace_image_references(cleaned_content, images)
                    html_content += content_with_images
                except Exception as e:
                    self.logger.warning(f"跳过章节 {item.get_id()}: {e}")
                    continue
            
            html_content += """
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"读取EPUB文件失败 {epub_path}: {e}")
            return None
    
    def _clean_html_content(self, content: str) -> str:
        """
        清理和格式化HTML内容
        
        Args:
            content: 原始HTML内容
            
        Returns:
            清理后的HTML内容
        """
        # 移除XML声明和DOCTYPE
        content = re.sub(r'<\?xml[^>]*\?>', '', content)
        content = re.sub(r'<!DOCTYPE[^>]*>', '', content)
        
        # 提取body内容
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
        if body_match:
            content = body_match.group(1)
        else:
            # 如果没有body标签，移除html和head标签
            content = re.sub(r'<html[^>]*>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'</html>', '', content, flags=re.IGNORECASE)
            content = re.sub(r'<head[^>]*>.*?</head>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        return content
    
    def _replace_image_references(self, content: str, images: Dict[str, str]) -> str:
        """
        替换HTML内容中的图片引用为base64编码的data URL
        
        Args:
            content: HTML内容
            images: 图片映射字典
            
        Returns:
            替换后的HTML内容
        """
        if not images:
            return content
            
        # 匹配所有img标签的src属性
        img_pattern = r'<img[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>'
        
        def replace_img_src(match):
            try:
                full_tag = match.group(0)
                src = match.group(1)
                
                # 避免处理已经是data URL的图片
                if src.startswith('data:'):
                    return full_tag
                
                # 预定义的图片路径变换（避免动态扩展导致的问题）
                possible_keys = [
                    src,  # 原始路径
                    src.split('/')[-1],  # 只要文件名
                    src.replace('../', ''),  # 移除相对路径前缀
                    src.replace('./', ''),  # 移除当前目录前缀
                    src.lstrip('/'),  # 移除开头的斜杠
                    src.replace('images/', ''),  # 移除images目录前缀
                    src.replace('Images/', ''),  # 移除Images目录前缀（大写）
                    src.replace('IMAGES/', ''),  # 移除IMAGES目录前缀（全大写）
                ]
                
                # 添加仅文件名的变体（限制数量以避免过度扩展）
                base_filename = src.split('/')[-1]
                if base_filename not in possible_keys:
                    possible_keys.append(base_filename)
                
                # 去重并限制数量
                possible_keys = list(dict.fromkeys(possible_keys))[:10]  # 最多尝试10种变体
                
                # 尝试查找匹配的图片
                for key in possible_keys:
                    if key and key in images:
                        # 替换src属性，使用更安全的方式
                        escaped_image_data = images[key].replace('"', '&quot;')
                        new_tag = re.sub(
                            r'src\s*=\s*["\'][^"\']+["\']', 
                            f'src="{escaped_image_data}"', 
                            full_tag, 
                            count=1  # 只替换第一个匹配项
                        )
                        return new_tag
                
                # 如果没找到匹配的图片，返回原标签但移除src以避免错误
                self.logger.debug(f"未找到图片: {src}")
                return re.sub(r'src\s*=\s*["\'][^"\']+["\']', 'src="#"', full_tag, count=1)
                
            except Exception as e:
                self.logger.warning(f"处理图片标签时出错: {e}")
                return match.group(0)  # 返回原始标签
        
        try:
            # 执行替换，限制替换次数以避免递归过深
            content = re.sub(img_pattern, replace_img_src, content, flags=re.IGNORECASE)
            return content
        except RecursionError as e:
            self.logger.error(f"图片替换时递归过深: {e}")
            # 如果递归过深，返回移除所有图片src的版本
            return re.sub(r'<img[^>]*src\s*=\s*["\'][^"\']+["\']', '<img src="#"', content, flags=re.IGNORECASE)
    
    def extract_images_from_epub(self, book) -> Dict[str, str]:
        """
        从EPUB中提取图片资源并转换为base64编码
        
        Args:
            book: EPUB book对象
            
        Returns:
            图片文件映射字典 {文件名: base64_data_url}
        """
        images = {}
        processed_count = 0
        max_images = 500  # 限制最大图片数量，防止内存问题
        max_size = 5 * 1024 * 1024  # 单个图片最大5MB
        
        try:
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE:
                    if processed_count >= max_images:
                        self.logger.warning(f"图片数量超过限制({max_images})，跳过剩余图片")
                        break
                        
                    try:
                        # 获取图片内容和MIME类型
                        content = item.get_content()
                        filename = item.get_name()
                        
                        # 检查图片大小
                        if len(content) > max_size:
                            self.logger.warning(f"图片 {filename} 太大({len(content)} bytes)，跳过")
                            continue
                        
                        # 根据文件扩展名确定MIME类型
                        mime_type = self._get_image_mime_type(filename)
                        
                        # 转换为base64编码的data URL
                        base64_content = base64.b64encode(content).decode('utf-8')
                        data_url = f"data:{mime_type};base64,{base64_content}"
                        
                        # 使用有限的路径格式作为键，避免过度扩展
                        base_name = filename.split('/')[-1]
                        images[filename] = data_url
                        if base_name != filename:
                            images[base_name] = data_url
                        
                        processed_count += 1
                        
                    except Exception as e:
                        self.logger.warning(f"处理图片 {item.get_name()} 失败: {e}")
                        continue
                    
            unique_images = len(set(images.values()))
            self.logger.info(f"提取了 {unique_images} 个图片资源 (总计 {processed_count} 个引用)")
        except Exception as e:
            self.logger.warning(f"提取图片失败: {e}")
        return images
    
    def _get_image_mime_type(self, filename: str) -> str:
        """根据文件扩展名获取MIME类型"""
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'svg': 'image/svg+xml',
            'webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')
    
    def convert_epub_to_pdf(self, epub_path: Path) -> bool:
        """
        将单个EPUB文件转换为PDF
        
        Args:
            epub_path: EPUB文件路径
            
        Returns:
            转换成功返回True，失败返回False
        """
        try:
            # 检查是否已转换
            if self.is_already_converted(epub_path):
                self.logger.info(f"跳过已转换的文件: {epub_path.name}")
                return True
            
            self.logger.info(f"开始转换: {epub_path.name}")
            
            # 提取EPUB内容
            html_content = self.extract_epub_content(epub_path)
            if not html_content:
                return False
            
            # 生成PDF
            pdf_path = self.get_output_path(epub_path)
            
            # 配置weasyprint，忽略外部资源加载错误
            import logging as wp_logging
            wp_logger = wp_logging.getLogger('weasyprint')
            original_level = wp_logger.level
            wp_logger.setLevel(wp_logging.CRITICAL)  # 只显示严重错误
            
            try:
                # 使用weasyprint转换HTML为PDF
                html_doc = HTML(string=html_content, base_url=str(epub_path.parent))
                html_doc.write_pdf(str(pdf_path))
                
                self.logger.info(f"转换完成: {epub_path.name} -> {pdf_path.name}")
                return True
                
            finally:
                # 恢复原始日志级别
                wp_logger.setLevel(original_level)
            
        except Exception as e:
            self.logger.error(f"转换失败 {epub_path.name}: {e}")
            return False
    
    def convert_all(self) -> dict:
        """
        转换所有EPUB文件
        
        Returns:
            转换结果统计
        """
        epub_files = self.find_epub_files()
        
        if not epub_files:
            self.logger.warning("未找到EPUB文件")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        
        results = {"total": len(epub_files), "success": 0, "failed": 0, "skipped": 0}
        
        for epub_path in epub_files:
            if self.is_already_converted(epub_path):
                results["skipped"] += 1
                self.logger.info(f"跳过已转换的文件: {epub_path.name}")
            elif self.convert_epub_to_pdf(epub_path):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        # 输出转换结果
        self.logger.info(f"转换完成！总计: {results['total']}, "
                        f"成功: {results['success']}, "
                        f"失败: {results['failed']}, "
                        f"跳过: {results['skipped']}")
        
        return results


def main():
    """主函数"""
    converter = EPUBtoPDFConverter()
    results = converter.convert_all()
    
    # 根据转换结果设置退出代码
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
