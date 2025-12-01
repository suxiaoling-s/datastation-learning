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
    # 如果结果是空的（中文情况），使用哈希值
    if not slug or len(slug) < 3:
        # 使用标题的哈希值作为锚点
        import hashlib
        # 移除 emoji 和特殊字符
        clean_text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        # 生成简短的哈希值
        hash_obj = hashlib.md5(clean_text.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:8]
        slug = f"section-{hash_hex}"
    
    # CSS 选择器不能以数字开头，如果以数字开头，添加前缀
    if slug and slug[0].isdigit():
        slug = f"section-{slug}"
    
    # 如果 slug 太长，截断
    if len(slug) > 50:
        slug = slug[:50]
    
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


def extract_heading_map(html_content):
    """提取所有标题及其 id，建立映射关系"""
    heading_map = {}
    # 匹配所有标题标签及其 id
    pattern = r'<h([1-6]) id="([^"]+)">(.*?)</h[1-6]>'
    
    for match in re.finditer(pattern, html_content):
        level = match.group(1)
        heading_id = match.group(2)
        heading_text = match.group(3)
        
        # 清理标题文本（移除 HTML 标签和 emoji）
        clean_text = re.sub(r'<[^>]+>', '', heading_text)  # 移除 HTML 标签
        clean_text = re.sub(r'[📚🔧🌐📝📖]', '', clean_text).strip()  # 移除 emoji
        clean_text = re.sub(r'^\d+\.\s*', '', clean_text)  # 移除开头的数字编号
        
        # 存储映射：文本 -> id
        heading_map[clean_text] = heading_id
        # 也存储原始文本的映射
        heading_map[heading_text] = heading_id
    
    return heading_map


def fix_toc_links(html_content):
    """修复目录链接，确保指向正确的锚点"""
    # 先提取所有标题的映射
    heading_map = extract_heading_map(html_content)
    
    # 修复目录中的链接
    def fix_toc_link(match):
        full_link = match.group(0)
        link_text = match.group(1)
        
        # 清理链接文本
        clean_text = re.sub(r'<[^>]+>', '', link_text)
        clean_text = re.sub(r'[📚🔧🌐📝📖]', '', clean_text).strip()
        clean_text = re.sub(r'^\d+\.\s*', '', clean_text)
        
        # 查找匹配的标题 id
        heading_id = None
        # 精确匹配
        if clean_text in heading_map:
            heading_id = heading_map[clean_text]
        else:
            # 模糊匹配：查找包含该文本的标题
            for heading_text, h_id in heading_map.items():
                if clean_text in heading_text or heading_text in clean_text:
                    heading_id = h_id
                    break
        
        # 如果找到了匹配的 id，使用它；否则使用生成的锚点
        if heading_id:
            return f'<a href="#{heading_id}">{link_text}</a>'
        else:
            # 回退：使用文本生成锚点
            anchor = slugify_chinese(clean_text)
            return f'<a href="#{anchor}">{link_text}</a>'
    
    # 匹配目录中的链接（在 <ol> 或 <ul> 内的链接，通常在目录区域）
    # 先找到目录区域（通常在 <h2>目录</h2> 之后的 <ol>）
    toc_pattern = r'(<h[1-6][^>]*>.*?目录.*?</h[1-6]>.*?<ol>.*?</ol>)'
    
    def process_toc(match):
        toc_content = match.group(1)
        # 修复目录中的链接
        link_pattern = r'<a href="[^"]*">(.*?)</a>'
        toc_content = re.sub(link_pattern, fix_toc_link, toc_content)
        return toc_content
    
    html_content = re.sub(toc_pattern, process_toc, html_content, flags=re.DOTALL)
    
    # 也处理其他手动编写的目录链接
    manual_link_pattern = r'<a href="(#.*?)">(.*?)</a>'
    def fix_manual_link(match):
        href = match.group(1)
        text = match.group(2)
        # 如果已经是 # 开头，尝试匹配标题
        if href.startswith('#'):
            clean_text = re.sub(r'<[^>]+>', '', text)
            clean_text = re.sub(r'[📚🔧🌐📝📖]', '', clean_text).strip()
            clean_text = re.sub(r'^\d+\.\s*', '', clean_text)
            
            if clean_text in heading_map:
                return f'<a href="#{heading_map[clean_text]}">{text}</a>'
            else:
                # 模糊匹配
                for heading_text, h_id in heading_map.items():
                    if clean_text in heading_text or heading_text in clean_text:
                        return f'<a href="#{h_id}">{text}</a>'
                # 回退
                anchor = slugify_chinese(clean_text)
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
                        e.preventDefault();
                        
                        // 尝试多种方式查找目标元素
                        let target = document.querySelector(href);
                        
                        // 如果直接查询失败，尝试解码 URL
                        if (!target) {{
                            try {{
                                const decodedHref = decodeURIComponent(href);
                                target = document.querySelector(decodedHref);
                            }} catch (e) {{
                                console.warn('Failed to decode href:', href);
                            }}
                        }}
                        
                        // 如果还是找不到，尝试通过 id 属性查找
                        if (!target) {{
                            const id = href.substring(1); // 移除 #
                            target = document.getElementById(id);
                        }}
                        
                        if (target) {{
                            const offset = 80; // 偏移量，避免被固定导航栏遮挡
                            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                            
                            window.scrollTo({{
                                top: Math.max(0, targetPosition),
                                behavior: 'smooth'
                            }});
                            
                            // 更新 URL（可选，保持浏览器历史记录）
                            if (history.pushState) {{
                                history.pushState(null, null, href);
                            }}
                        }} else {{
                            console.warn('Target not found for href:', href);
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