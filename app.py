
from flask import Flask, render_template, request, jsonify
import markdown as md
import bleach

app = Flask(__name__)

# Markdown configuration
MD_EXTENSIONS = [
    "extra",           # tables, fenced code, etc.
    "admonition",
    "sane_lists",
    "toc",
    "nl2br",           # preserve newlines
]

# Bleach (HTML sanitizer) configuration
ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    "p","pre","code","span","div","br","hr",
    "h1","h2","h3","h4","h5","h6",
    "ul","ol","li",
    "em","strong","blockquote","tt","kbd","s","sub","sup",
    "table","thead","tbody","tr","th","td",
    "img","a"
})
ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href","title","name","target","rel"],
    "img": ["src","alt","title","width","height"],
    "*": ["class", "id", "aria-label", "role"]
}
ALLOWED_PROTOCOLS = bleach.sanitizer.ALLOWED_PROTOCOLS.union({"data"})

from bleach.linkifier import Linker
from bleach.callbacks import nofollow, target_blank

TOKENS = {
    r"\(": "%%MJX_LP%%",
    r"\)": "%%MJX_RP%%",
    r"\[": "%%MJX_LB%%",
    r"\]": "%%MJX_RB%%",
}

def _protect_tex_delimiters(text: str) -> str:
    for k, v in TOKENS.items():
        text = text.replace(k, v)
    return text

def _restore_tex_delimiters(html: str) -> str:
    # 把占位符还原为原定界符
    rev = {v: k for k, v in TOKENS.items()}
    for k, v in rev.items():
        html = html.replace(k, v)
    return html

def render_markdown_to_html(text: str) -> str:
    # 1) 保护数学定界符（防止 Markdown 吃掉反斜杠）
    protected = _protect_tex_delimiters(text)

    # 2) Markdown -> HTML
    html = md.markdown(protected, extensions=MD_EXTENSIONS, output_format="html5")

    # 3) 还原数学定界符
    html = _restore_tex_delimiters(html)

    # 4) 清洗 HTML
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=False
    )

    linker = Linker(callbacks=[nofollow, target_blank])
    clean_html = linker.linkify(clean_html)   # ← 注意这里调用 .linkify()
    return clean_html


@app.route("/", methods=["GET", "POST"])
def index():
    sample = r"""# 欢迎使用 LLM 文本渲染器

你可以在左侧粘贴/输入由大模型生成的文本（Markdown + LaTeX）。
例如：

- **行内数学**：$E=mc^2$
- **块级数学**：
  $$
  \int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}
  $$

- **矩阵**：
  $$
  A = \begin{bmatrix}
  1 & 2 \\
  3 & 4
  \end{bmatrix}
  $$

- **求和与极限**：
  $$
  \sum_{k=1}^n k = \frac{n(n+1)}{2},\quad \lim_{x\to 0} \frac{\sin x}{x} = 1
  $$

- 
The system of equations is:
\[
y = h(x), \quad x = k(y).
\]
Substituting \(y = h(x)\) into the second equation gives \(x = k(h(x))\). Thus, solving \(x = k(h(x))\) for \(x\) in \([0, 1)\) gives the \(x\)-coordinates of the intersection points, and corresponding \(y\) are given by \(y = h(x)\).
"""
    rendered = ""
    raw = sample
    if request.method == "POST":
        raw = request.form.get("text", "")
        rendered = render_markdown_to_html(raw)
    return render_template("index.html", raw=raw, rendered=rendered)

@app.post("/api/render")
def api_render():
    """
    POST JSON: {"text": "..."} -> {"html": "<p>...</p>"}
    Useful if you want to call it from another service.
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    html = render_markdown_to_html(text)
    return jsonify({"html": html})

if __name__ == "__main__":
    # For local dev: python app.py
    app.run(host="0.0.0.0", port=8989, debug=True)
    
