
# LLM 文本渲染器（Markdown + LaTeX）

这是一个用 **Python + Flask** 搭建的极简网站，用来安全地渲染由大模型生成的文本，支持 Markdown 与 LaTeX 数学公式（通过 MathJax 在浏览器端渲染）。

## 功能
- 左侧编辑器输入/粘贴文本，右侧预览渲染结果
- 服务器端使用 `Markdown` 将 Markdown 转为 HTML
- 使用 `bleach` 白名单清理，降低 XSS 风险
- 使用 `MathJax v3` 在前端渲染 `$...$`（行内）与 `$$...$$`（块级）数学公式
- 提供 `POST /api/render` JSON 接口，便于和你的 LLM 服务集成

## 本地运行

```bash
# python -m venv .venv
# source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```


访问：<http://127.0.0.1:5000/>

## 运行实例

![运行示例](img/explore.png)

## 与你的后端对接（可选）

如果你有一个生成 LLM 输出的后端，可以将模型返回的原始文本提交到：

```
POST /api/render
Content-Type: application/json

{"text": "由模型生成的 Markdown/LaTeX 文本 ..."}
```

响应：

```json
{"html": "<p> ... 清洗后的安全 HTML ... </p>"}
```

你可以把这个 `html` 直接放到你的页面中（例如 `<div>`），MathJax 会自动进行数学公式渲染。

## 安全说明

- 本例使用 `bleach` 做 HTML 白名单清理，以减少 XSS 风险；根据你的业务场景可调整 `ALLOWED_TAGS` 与 `ALLOWED_ATTRS`。
- MathJax 只处理文本中的数学定界符（如 `$...$`、`$$...$$`），不会执行脚本。
- 若允许外链图片或数据 URL，请确认来源可信。

## 部署建议

- Docker 化部署（示例）
- 反向代理（Nginx/Caddy），开启 HTTPS
- 关闭 Flask `debug=True`，改为生产模式（如 gunicorn/uwsgi）

### 简易 Dockerfile（可选）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["python", "app.py"]
```

---

欢迎按需扩展：如加入用户鉴权、历史记录保存、文件上传、服务端持久化存储等。
