#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 Markdown 文件转换为 HTML，支持目录跳转
"""
import re
from markdown import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc
from markdown.extensions.toc import slugify


def slugify_chinese(text, separator='-'):
    """处理中文标题的锚点生成"""
    # 先使用默认的 slugify
    slug = slugify(text, separator)
    # 如果结果是空的（中文情况），使用 Unicode 编码
    if not slug:
        # 将中文转换为拼音或使用 Unicode 编码
        import unicodedata
        slug = ''.join(
            unicodedata.name(char, char).lower().replace(' ', '-')
            if ord(char) > 127 else char
            for char in text
        )
        slug = re.sub(r'[^\w\-]', '', slug)
    return slug


def add_anchor_ids(html_content):
    """为所有标题添加 id 属性"""
    # 匹配所有标题标签
    def add_id(match):
        tag = match.group(1)  # h1, h2, h3, etc.
        content = match.group(2)  # 标题内容
        # 生成锚点 ID
        anchor_id = slugify_chinese(content)
        return f'<{tag} id="{anchor_id}">{content}</{tag}>'
    
    # 匹配 <h1>到<h6>标签
    pattern = r'<h([1-6])>(.*?)</h[1-6]>'
    html_content = re.sub(pattern, add_id, html_content)
    return html_content


def fix_toc_links(html_content):
    """修复目录链接，确保指向正确的锚点"""
    # 匹配目录中的链接
    def fix_link(match):
        link_text = match.group(1)
        # 生成正确的锚点
        anchor = slugify_chinese(link_text)
        return f'<a href="#{anchor}">{link_text}</a>'
    
    # 匹配目录中的链接（在 <div class="toc"> 内的链接）
    # 先找到目录区域
    toc_pattern = r'(<div class="toc">.*?</div>)'
    
    def process_toc(match):
        toc_content = match.group(1)
        # 修复目录中的链接
        link_pattern = r'<a href="[^"]*">(.*?)</a>'
        toc_content = re.sub(link_pattern, fix_link, toc_content)
        return toc_content
    
    html_content = re.sub(toc_pattern, process_toc, html_content, flags=re.DOTALL)
    
    # 也处理手动编写的目录链接（Markdown 格式的链接）
    manual_link_pattern = r'<a href="(#.*?)">(.*?)</a>'
    def fix_manual_link(match):
        href = match.group(1)
        text = match.group(2)
        # 如果已经是 # 开头，重新生成锚点
        if href.startswith('#'):
            anchor = slugify_chinese(text)
            return f'<a href="#{anchor}">{text}</a>'
        return match.group(0)
    
    html_content = re.sub(manual_link_pattern, fix_manual_link, html_content)
    
    return html_content


def convert_markdown_to_html(md_file: str, html_file: str):
    """将 Markdown 文件转换为 HTML"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 配置 Markdown 扩展
    extensions = [
        'codehilite',
        'fenced_code',
        'tables',
        'toc',
        'nl2br',
    ]
    
    # 自定义 slugify 函数处理中文
    toc_config = {
        'permalink': False,  # 不在标题旁显示链接图标
        'slugify': slugify_chinese,
        'toc_depth': 3,  # 目录深度
    }
    
    # 转换为 HTML
    html_body = markdown(
        md_content,
        extensions=extensions,
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
            },
            'toc': toc_config
        }
    )
    
    # 为所有标题添加 id
    html_body = add_anchor_ids(html_body)
    
    # 修复目录链接
    html_body = fix_toc_links(html_body)
    
    # 创建完整的 HTML 文档
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Station Web API 技术栈学习笔记</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
            scroll-margin-top: 20px;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
            scroll-margin-top: 20px;
        }}
        
        h3 {{
            color: #555;
            margin-top: 30px;
            margin-bottom: 15px;
            scroll-margin-top: 20px;
        }}
        
        h4, h5, h6 {{
            color: #666;
            margin-top: 20px;
            margin-bottom: 10px;
            scroll-margin-top: 20px;
        }}
        
        p {{
            margin-bottom: 15px;
        }}
        
        ul, ol {{
            margin-left: 30px;
            margin-bottom: 15px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            color: inherit;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        a {{
            color: #3498db;
            text-decoration: none;
            transition: color 0.2s;
        }}
        
        a:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}
        
        a:visited {{
            color: #8e44ad;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 40px 0;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 40px;
            border-left: 4px solid #3498db;
        }}
        
        .toc h2 {{
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: none;
        }}
        
        .toc ul {{
            list-style-type: none;
            margin-left: 0;
        }}
        
        .toc li {{
            margin-bottom: 8px;
            line-height: 1.8;
        }}
        
        .toc a {{
            color: #2c3e50;
            font-weight: 500;
        }}
        
        .toc a:hover {{
            color: #3498db;
            text-decoration: underline;
        }}
        
        .toc ul ul {{
            margin-left: 20px;
            margin-top: 5px;
        }}
        
        .toc ul ul ul {{
            margin-left: 20px;
        }}
        
        /* 标题锚点样式 */
        h1[id], h2[id], h3[id], h4[id], h5[id], h6[id] {{
            position: relative;
        }}
        
        h1[id]:hover::before, h2[id]:hover::before, h3[id]:hover::before,
        h4[id]:hover::before, h5[id]:hover::before, h6[id]:hover::before {{
            content: "🔗";
            position: absolute;
            left: -30px;
            font-size: 0.8em;
            opacity: 0.5;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            body {{
                padding: 10px;
            }}
            
            .toc {{
                padding: 15px;
            }}
        }}
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script>
        hljs.highlightAll();
        
        // 平滑滚动增强
        document.addEventListener('DOMContentLoaded', function() {{
            // 为所有锚点链接添加平滑滚动
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    const href = this.getAttribute('href');
                    if (href !== '#' && href.length > 1) {{
                        const target = document.querySelector(href);
                        if (target) {{
                            e.preventDefault();
                            const offset = 80; // 偏移量，避免被固定导航栏遮挡
                            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                            window.scrollTo({{
                                top: targetPosition,
                                behavior: 'smooth'
                            }});
                        }}
                    }}
                }});
            }});
        }});
    </script>
</head>
<body>
    <div class="container">
        {html_body}
    </div>
</body>
</html>"""
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ 成功将 {md_file} 转换为 {html_file}")

if __name__ == '__main__':
    convert_markdown_to_html('学习笔记.md', '学习笔记.html')