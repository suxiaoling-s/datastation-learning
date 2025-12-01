# Data Station Web API 技术栈学习笔记

基于 FastAPI + Celery + Redis + PostgreSQL 的现代化 Web API 框架完整技术解析。

## 📖 内容

这份学习笔记详细介绍了 Data Station Web API 项目中使用的核心技术栈，包括：

- FastAPI 框架
- SQLAlchemy ORM 与数据库设计
- Redis 缓存与连接池管理
- Celery 异步任务处理
- JWT 认证与安全机制
- 项目架构设计模式
- 云服务集成
- 测试与部署
- 最佳实践总结

## 📄 文件说明

- `学习笔记.md` - Markdown 格式的学习笔记
- `学习笔记.html` - HTML 格式的学习笔记（可直接在浏览器中打开）

## 🌐 在线查看

- [Markdown 版本](学习笔记.md) - GitHub 会自动渲染 Markdown
- [HTML 版本](学习笔记.html) - 可直接下载并在浏览器中打开

## 🔧 本地查看 HTML

1. 直接双击 `学习笔记.html` 文件在浏览器中打开
2. 或者使用 Python 内置服务器：
   ```bash
   python3 -m http.server 8000
   ```
   然后在浏览器中访问 `http://localhost:8000/学习笔记.html`

## 📝 更新 HTML

如果修改了 Markdown 文件，可以运行以下命令重新生成 HTML：

```bash
python3 convert_to_html.py
```
