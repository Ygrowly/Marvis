# -*- coding: utf-8 -*-
"""Marvis 构建器 v2

md 工作台 → 按格式选 adapter → 三类视图（P1 已实现母题页）

用法：
    python site/build.py

产物：
    site/_data/decks.json   多牌组数据（训练台用）
    site/_data/decks.js     同上，file:// 版本（fetch 本地 json 会被 CORS 拦）
    site/topics/*.html      母题页

md 里的约定：
    母题卡  —— 按 templates/母题卡模板.md 的字段写，自动成卡，无需任何额外标记
    补充卡  —— ::card id=x tag=y / Q: / A: / ::end
    图      —— ::figure 文件名.svg | 标题 | 说明（文件放 site/figures/）
"""
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
OUT_DATA = SITE / "_data"
OUT_TOPICS = SITE / "topics"
OUT_REVIEWS = SITE / "reviews"
OUT_MODULES = SITE / "modules"
FIGURES = SITE / "figures"

TOPIC_DIRS = ["wiki/topics"]          # 母题卡
REVIEW_DIRS = ["wiki/interview"]      # 面试复盘（诊断页）
MODULE_DIRS = ["wiki/topics"]         # 模块深挖卡（学习页）
CARD_DIRS = ["site/cards", "output/算法", "study", "wiki/interview", "wiki/thinking", "projects"]

CARD_RE = re.compile(r"^::card\s+id=(?P<id>\S+)(?:\s+tag=(?P<tag>\S+))?\s*$")
FIGURE_RE = re.compile(r"^::figure\s+(?P<file>\S+)\s*(?:\|(?P<rest>.*))?$")


# ---------------------------------------------------------------- 工具

def split_front(text):
    """拆 frontmatter，返回 (dict, body)"""
    meta = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            return meta, parts[2]
    return meta, text


def grab(text, name):
    """抽 `**字段**：值`，到下一个 ** / > / --- / 空行 为止"""
    pat = (r"\*\*" + re.escape(name) + r"\*\*\s*[：:]\s*(.+?)"
           r"(?=\n\s*\n|\n\s*\*\*|\n\s*>|\n\s*---|\Z)")
    m = re.search(pat, text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def grab_block(text, name):
    """抽 `**字段**：` 之后的整块内容（保留换行，可含代码块）"""
    pat = (r"\*\*" + re.escape(name) + r"\*\*\s*[：:]\s*\n?"
           r"(.*?)(?=\n\s*\*\*|\n\s*##|\n\s*---|\Z)")
    m = re.search(pat, text, re.S)
    return m.group(1).strip() if m else ""


def grab_list(text, name):
    """抽 `**字段**` 之后的 `- ` 列表项"""
    idx = text.find("**" + name + "**")
    if idx < 0:
        return []
    tail = text[idx + len("**" + name + "**"):]
    stop = re.search(r"\n\s*(?:\*\*|##)", tail)
    block = tail[: stop.start()] if stop else tail
    return [re.sub(r"^\s*[-*]\s+", "", ln).strip()
            for ln in block.splitlines() if re.match(r"^\s*[-*]\s+\S", ln)]


def grab_numbered(text, name):
    """抽 `**字段**` 之后的 `1. ` 编号列表，返回 [(问, 答)]"""
    idx = text.find("**" + name + "**")
    if idx < 0:
        return []
    tail = text[idx + len("**" + name + "**"):]
    out = []
    for ln in tail.splitlines():
        if re.match(r"^\s*##", ln):
            break
        m = re.match(r"^\s*\d+[.、]\s*(.+)$", ln)
        if not m:
            continue
        parts = re.split(r"\s*——\s*|\s*—\s*", m.group(1).strip(), maxsplit=1)
        out.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    return out


# ---------------------------------------------------------------- md → html（轻量）

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r'<code class="mv-md-code">\1</code>', s)
    return s


def md_to_html(md):
    out, para, lst, code, in_code = [], [], [], [], False

    def flush_para():
        if para:
            out.append('<p class="mv-md-p">' + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        if lst:
            out.append('<ul class="mv-md-ul">' +
                       "".join("<li>" + inline(x) + "</li>" for x in lst) + "</ul>")
            lst.clear()

    for line in md.splitlines():
        raw = line.rstrip()
        if raw.startswith("```"):
            if not in_code:
                flush_para(); flush_list(); code, in_code = [], True
            else:
                out.append('<pre class="mv-md-pre">' + esc("\n".join(code)) + "</pre>")
                in_code = False
            continue
        if in_code:
            code.append(raw)
            continue
        if not raw.strip():
            flush_para(); flush_list()
            continue
        if raw.strip() in ("---", "***"):
            flush_para(); flush_list()
            out.append('<hr class="mv-md-hr">')
            continue
        m = re.match(r"^#{2,4}\s+(.+)$", raw)
        if m:
            flush_para(); flush_list()
            out.append('<h3 class="mv-md-h">' + inline(m.group(1)) + "</h3>")
            continue
        if re.match(r"^\s*[-*]\s+\S", raw):
            flush_para()
            lst.append(re.sub(r"^\s*[-*]\s+", "", raw).strip())
            continue
        if re.match(r"^\s*>\s?", raw):
            flush_para(); flush_list()
            out.append('<p class="mv-md-p mv-md-quote">' +
                       inline(re.sub(r"^\s*>\s?", "", raw)) + "</p>")
            continue
        para.append(raw.strip())

    flush_para(); flush_list()
    if in_code and code:
        out.append('<pre class="mv-md-pre">' + esc("\n".join(code)) + "</pre>")
    return "\n".join(out)


# ---------------------------------------------------------------- adapter：母题卡

def parse_topic(path):
    meta, body = split_front(path.read_text(encoding="utf-8"))
    if "**母题**" not in body:
        return None

    title = ""
    m = re.search(r"^#\s+(.+)$", body, re.M)
    if m:
        title = m.group(1).strip()

    module = meta.get("topic") or path.parent.name
    stem = path.stem

    q = grab(body, "母题")
    a = grab(body, "一句话结论")
    if not q or not a:
        return None

    figures = []
    for line in body.splitlines():
        fm = FIGURE_RE.match(line.strip())
        if not fm:
            continue
        fpath = FIGURES / fm.group("file")
        if not fpath.exists():
            print("  [warn] 图不存在，已跳过：%s (%s)" % (fm.group("file"), path.name))
            continue
        rest = [x.strip() for x in (fm.group("rest") or "").split("|")]
        figures.append({
            "svg": fpath.read_text(encoding="utf-8"),
            "title": rest[0] if len(rest) > 0 else "",
            "note": rest[1] if len(rest) > 1 else "",
        })

    mbody = ""
    mb = re.search(r"\n---\s*\n(.*?)(?=\n##\s*二、|\Z)", body, re.S)
    if mb:
        mbody = mb.group(1).strip()

    return {
        "key": "%s/%s" % (module, stem),
        "module": module,
        "stem": stem,
        "title": title,
        "status": meta.get("status", ""),
        "src": path.relative_to(ROOT).as_posix(),
        "question": q,
        "conclusion": a,
        "problem": grab_block(body, "题目"),
        "importance": grab(body, "为什么重要"),
        "keywords": [x.strip() for x in re.split(r"[/｜|·]", grab(body, "恢复关键词")) if x.strip()],
        "invariant": grab(body, "核心不变量 / 主线") or grab(body, "核心不变量"),
        "skeleton": grab(body, "完整回答骨架"),
        "followups": grab_numbered(body, "两层追问"),
        "variants": grab_list(body, "同类变体"),
        "related": grab(body, "关联母题"),
        "transfer": grab(body, "可迁移场景"),
        "breakpoint": grab(body, "本次断点"),
        "evidence": grab(body, "通过证据"),
        "figures": figures,
        "body_html": md_to_html(mbody) if mbody else "",
        "page": "topics/%s-%s.html" % (module, stem),
    }


# ---------------------------------------------------------------- adapter：::card

def parse_cards(path):
    cards, cur, field = [], None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = CARD_RE.match(line)
        if m:
            if cur:
                cards.append(cur)
            cur = {"id": m.group("id"), "tag": m.group("tag") or "补充",
                   "q": "", "a": "", "src": path.relative_to(ROOT).as_posix()}
            field = None
            continue
        if line.strip() == "::end":
            if cur:
                cards.append(cur)
            cur, field = None, None
            continue
        if cur is None:
            continue
        if line.startswith("Q:"):
            field = "q"; cur["q"] += line[2:].lstrip()
        elif line.startswith("A:"):
            field = "a"; cur["a"] += line[2:].lstrip()
        elif field:
            cur[field] += "\n" + line.strip()
    if cur:
        cards.append(cur)
    return cards


# ---------------------------------------------------------------- 渲染母题页

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%TITLE%%</title>
<link rel="stylesheet" href="../_components/marvis.css">
</head>
<body class="mv-page">
<div class="mv-wrap">
  <a class="mv-back" href="../index.html">← 返回训练台</a>

  <div class="mv-topic-head">
    <span class="mv-topic-module">%%MODULE%%</span>
    <h1 class="mv-topic-title">%%TITLE%%</h1>
    <p class="mv-topic-meta">%%META%%</p>
  </div>
%%PROBLEM%%
  <div class="mv-section">
    <h2 class="mv-section-title">主卡</h2>
    <flip-card gradable card-id="%%KEY%%" tag="%%MODULE%%" q="%%Q%%" a="%%A%%"></flip-card>
    <p class="mv-note" id="mv-grade-tip" style="margin-top:8px">在这里练也可以，评分会进训练台的复训调度。</p>
    %%IMPORTANCE%%
  </div>
%%FIGURES%%%%KEYWORDS%%%%EXPAND%%%%BODY%%
  <div class="mv-section">
    <h2 class="mv-section-title">复训</h2>
    <div class="mv-ladder">
      <span class="mv-ladder-step">D1</span>
      <span class="mv-ladder-step">D3</span>
      <span class="mv-ladder-step">D7</span>
      <span class="mv-ladder-step">D14</span>
      <span class="mv-ladder-step">D30</span>
      <span class="mv-topic-meta" style="margin-left:6px">进度在训练台统一调度</span>
    </div>
  </div>
</div>
<script src="../_components/marvis.js"></script>
<script>
document.addEventListener('mv-grade', function (e) {
  var s = window.Marvis && Marvis.gradeCard(e.detail.id, e.detail.ok);
  var t = document.getElementById('mv-grade-tip');
  if (t && s) t.textContent = (e.detail.ok ? '已记录 · 下次复训 ' : '已归零 · 明天重来 ') + s.next;
});
</script>
</body>
</html>
"""


def prefix_svg_ids(svg, prefix):
    """同一页面可能出现多张图，给内部 id / url(#…) 加前缀避免冲突"""
    for name in sorted(set(re.findall(r'id="([^"]+)"', svg)), key=len, reverse=True):
        svg = svg.replace('id="%s"' % name, 'id="%s-%s"' % (prefix, name))
        svg = svg.replace('url(#%s)' % name, 'url(#%s-%s)' % (prefix, name))
    return svg


def attrs(s):
    """放进 HTML 属性：转义引号与换行"""
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("\n", "&#10;"))


def render_topic(t):
    figures = ""
    for i, f in enumerate(t["figures"], 1):
        figures += (
            '\n  <div class="mv-section">\n    <h2 class="mv-section-title">图</h2>\n'
            '    <figure-box num="%d" title="%s" note="%s">\n%s\n    </figure-box>\n  </div>\n'
            % (i, attrs(f["title"]), attrs(f["note"]), prefix_svg_ids(f["svg"], "fig%d" % i))
        )

    keywords = ""
    if t["keywords"]:
        keywords = ('\n  <div class="mv-section">\n    <h2 class="mv-section-title">恢复关键词</h2>\n'
                    '    <ul class="mv-kw">%s</ul>\n'
                    '    <p class="mv-note">卡住时靠这几个词重建整条链。</p>\n  </div>\n'
                    % "".join("<li>%s</li>" % esc(k) for k in t["keywords"]))

    panels = []
    if t["followups"]:
        items = ""
        for i, (fq, fa) in enumerate(t["followups"], 1):
            items += ('<p class="mv-md-p"><strong>%d. %s</strong></p>\n<p class="mv-md-p">%s</p>\n'
                      % (i, inline(fq),
                         inline(fa) if fa else '<span class="mv-topic-meta">答案见正文底稿</span>'))
        panels.append('<collapse-panel title="两层追问（能答完才算出师）">%s</collapse-panel>' % items)
    if t["variants"]:
        panels.append('<collapse-panel title="同类变体"><ul class="mv-md-ul">%s</ul></collapse-panel>'
                      % "".join("<li>%s</li>" % inline(v) for v in t["variants"]))
    if t["transfer"]:
        panels.append('<collapse-panel title="可迁移场景"><p class="mv-md-p">%s</p></collapse-panel>'
                      % inline(t["transfer"]))
    if t["skeleton"]:
        panels.append('<collapse-panel title="完整回答骨架"><p class="mv-md-p">%s</p></collapse-panel>'
                      % inline(t["skeleton"]))
    if t["invariant"]:
        panels.append('<collapse-panel title="核心不变量 / 主线"><p class="mv-md-p">%s</p></collapse-panel>'
                      % inline(t["invariant"]))
    if t["breakpoint"] or t["evidence"]:
        inner = ""
        if t["breakpoint"]:
            inner += '<p class="mv-md-p"><strong>本次断点</strong>：%s</p>' % inline(t["breakpoint"])
        if t["evidence"]:
            inner += '<p class="mv-md-p"><strong>通过证据</strong>：%s</p>' % inline(t["evidence"])
        panels.append('<collapse-panel title="本次断点与通过证据">%s</collapse-panel>' % inner)

    expand = ""
    if panels:
        expand = ('\n  <div class="mv-section">\n'
                  '    <h2 class="mv-section-title">展开（默认收起，不进复训调度）</h2>\n'
                  "    " + "\n    ".join(panels) + "\n  </div>\n")

    body = ""
    if t["body_html"]:
        body = ('\n  <div class="mv-section">\n    <h2 class="mv-section-title">正文底稿</h2>\n'
                '    <collapse-panel title="展开推导 / 代码 / 原始素材">\n%s\n    </collapse-panel>\n  </div>\n'
                % t["body_html"])

    bits = []
    if t["related"]:
        bits.append("关联 %s" % t["related"])
    bits.append("正本 %s" % t["src"])
    meta = esc(" ｜ ".join(bits)).replace("[[", "").replace("]]", "")

    imp = ('<p class="mv-note" style="margin-top:10px">为什么重要：%s</p>' % esc(t["importance"])
           if t["importance"] else "")

    problem = ""
    if t["problem"]:
        problem = ('\n  <div class="mv-section">\n    <h2 class="mv-section-title">题目</h2>\n'
                   '    <div class="mv-problem">%s</div>\n  </div>\n' % md_to_html(t["problem"]))

    out = PAGE
    for k, v in (
        ("%%PROBLEM%%", problem),
        ("%%TITLE%%", esc(t["title"])),
        ("%%MODULE%%", esc(t["module"])),
        ("%%META%%", meta),
        ("%%KEY%%", attrs(t["key"])),
        ("%%Q%%", attrs(t["question"])),
        ("%%A%%", attrs(t["conclusion"])),
        ("%%IMPORTANCE%%", imp),
        ("%%FIGURES%%", figures),
        ("%%KEYWORDS%%", keywords),
        ("%%EXPAND%%", expand),
        ("%%BODY%%", body),
    ):
        out = out.replace(k, v)
    return out


# ---------------------------------------------------------------- adapter：面试复盘（诊断页）

def parse_md_table(lines):
    rows = []
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c.strip()):
            continue
        rows.append(cells)
    return rows


def slice_section(body, start_re, end_re=None):
    m = re.search(start_re, body, re.M)
    if not m:
        return ""
    rest = body[m.end():]
    if end_re:
        m2 = re.search(end_re, rest, re.M)
        if m2:
            rest = rest[:m2.start()]
    return rest


def short_round(s):
    """「一面（61 分钟）」→「一面」"""
    m = re.match(r"^(一面|二面|三面|四面|终面|HR 面|HR面)", (s or "").strip())
    return m.group(1) if m else (s or "").strip()[:4]


CN_NUM = "一二三四五六七八九十"


def mod_label(name):
    """「模块 A · 开场与动机」→「一、开场与动机」"""
    m = re.match(r"模块\s*([A-Za-z])\s*[·•]\s*(.+)$", (name or "").strip())
    if not m:
        return name or ""
    i = ord(m.group(1).upper()) - ord("A")
    num = CN_NUM[i] if 0 <= i < len(CN_NUM) else m.group(1)
    title = re.sub(r"（[^）]*）", "", m.group(2)).strip()
    return "%s、%s" % (num, title)


def _num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s or "")
    return float(m.group(0)) if m else None


def parse_review(path):
    meta, body = split_front(path.read_text(encoding="utf-8"))
    if "面试官问题全清单" not in body:
        return None

    m = re.search(r"^#\s+(.+)$", body, re.M)
    title = m.group(1).strip() if m else path.stem

    head_meta = [(mm.group(1), mm.group(2))
                 for mm in re.finditer(r"^\*\*(.+?)\*\*[：:]\s*(.+)$",
                                       body[:body.find("## 0.")], re.M)]

    # §1 问题清单（同时跟踪「轮次」与「模块」行）
    items, order = {}, []
    cur_mod, cur_round = "未分组", ""
    for ln in slice_section(body, r"^##\s*1\.", r"^##\s*2\.").splitlines():
        h = re.match(r"^###\s+\d+\.\d+\s*(.*)$", ln.strip())
        if h:
            cur_round = h.group(1).strip()
            continue
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c.strip()):
            continue
        first = cells[0] if cells else ""
        if first.startswith("**") and "模块" in first:
            cur_mod = first.strip("*").strip()
            continue
        if not re.fullmatch(r"[AB]\d+", first):
            continue
        items[first] = {
            "id": first, "module": cur_mod, "round": short_round(cur_round),
            "time": cells[1] if len(cells) > 1 else "",
            "q": cells[2] if len(cells) > 2 else "",
            "type": cells[3] if len(cells) > 3 else "",
            "want": cells[4] if len(cells) > 4 else "",
            "total": None, "cause": "", "radar": {}, "answer": "",
        }
        order.append(first)

    # §2 五维评分
    for cells in parse_md_table(slice_section(body, r"^##\s*2\.", r"^##\s*3\.").splitlines()):
        sid = cells[0] if cells else ""
        if sid not in items:
            continue
        for i, k in enumerate(["结构", "论据", "完整", "清晰", "针对"]):
            if len(cells) > 2 + i:
                items[sid]["radar"][k] = _num(cells[2 + i])
        if len(cells) > 7:
            items[sid]["total"] = _num(cells[7])
        if len(cells) > 8:
            items[sid]["cause"] = cells[8].strip()

    # §3 标准回答（按 ### / #### 切分，标题里找题号）
    sec3 = slice_section(body, r"^##\s*3\.", r"^##\s*4\.")
    for part in re.split(r"^#{3,4}\s+", sec3, flags=re.M)[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        mm = re.search(r"([AB]\d+(?:\s*/\s*[AB]\d+)*)\s*[·•]\s*(.+)$", lines[0].strip())
        if not mm:
            continue
        html = md_to_html("\n".join(lines[1:]).strip())
        for sid in re.findall(r"[AB]\d+", mm.group(1)):
            if sid in items and not items[sid]["answer"]:
                items[sid]["answer"] = html

    # §4 缺失知识模块
    missing = []
    for cells in parse_md_table(slice_section(body, r"^##\s*4\.", r"^##\s*5\.").splitlines()):
        if not cells or not re.match(r"\**M\d+", cells[0]):
            continue
        missing.append({
            "id": cells[0].strip("*").strip(),
            "name": cells[1].strip("*").strip() if len(cells) > 1 else "",
            "why": cells[2] if len(cells) > 2 else "",
            "target": cells[3] if len(cells) > 3 else "",
            "ref": cells[4] if len(cells) > 4 else "",
        })

    # §5 下次准备清单
    plan = []
    sec5 = slice_section(body, r"^##\s*5\.", r"^##\s*6\.")
    for part in re.split(r"^###\s+", sec5, flags=re.M)[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        todos = [re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", ln).strip()
                 for ln in lines if re.match(r"^\s*-\s*\[[ xX]\]\s*\S", ln)]
        if todos:
            plan.append({"section": lines[0].strip(), "todos": todos})

    return {
        "key": path.relative_to(ROOT).as_posix(),
        "stem": path.stem,
        "title": title,
        "head_meta": head_meta,
        "summary": md_to_html(slice_section(body, r"^##\s*0\.", r"^##\s*1\.")),
        "items": [items[i] for i in order],
        "missing": missing,
        "plan": plan,
        "page": "reviews/%s.html" % path.stem,
    }


# ---------------------------------------------------------------- 渲染诊断页

def score_color(v):
    if v is None:
        return "#D3D1C7"
    if v <= 11:
        return "#E24B4A"
    if v <= 15:
        return "#EF9F27"
    if v <= 20:
        return "#639922"
    return "#3B6D11"


def heat_svg(mod_groups):
    """每模块一行：模块名（中文序号 + 标题）｜逐题方块｜该模块平均分"""
    cell, gap, label_w, avg_w = 30, 6, 232, 74
    step, rowh = cell + gap, cell + gap + 10
    maxn = max((len(arr) for _, arr, _ in mod_groups), default=1) or 1
    W = label_w + maxn * step + avg_w
    H = len(mod_groups) * rowh
    out = ['<svg viewBox="0 0 %d %d" width="100%%" role="img" xmlns="http://www.w3.org/2000/svg">' % (W, H),
           '<title>各模块逐题得分与平均分</title>',
           '<desc>每行一个面试模块，方块是该模块每道题的得分（颜色越深分越高），行末是模块平均分。</desc>']

    for r, (label, arr, avg) in enumerate(mod_groups):
        y = r * rowh
        # 行标签：一面 · 一、开场与动机
        out.append('<text x="%d" y="%d" text-anchor="end" dominant-baseline="central" '
                   'font-family="system-ui,sans-serif" font-size="11" fill="#2C2C2A">%s</text>'
                   % (label_w - 14, y + cell // 2, esc(label)))
        for c, it in enumerate(arr):
            v = it["total"]
            x = label_w + c * step
            out.append('<g><title>%s · %s —— %s%s</title>'
                       % (it["id"], esc(it["q"][:30]),
                          ("%g 分" % v) if v is not None else "未评分",
                          ("（%s）" % it["cause"]) if it["cause"] else ""))
            out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="%s"/>'
                       % (x, y, cell, cell, score_color(v)))
            out.append('<text x="%d" y="%d" text-anchor="middle" dominant-baseline="central" '
                       'font-family="ui-monospace,monospace" font-size="11" fill="#FFFFFF">%s</text>'
                       % (x + cell // 2, y + cell // 2 + 1, "%g" % v if v is not None else "—"))
            out.append('</g>')
        # 行末平均分
        ax = label_w + maxn * step + 10
        out.append('<text x="%d" y="%d" dominant-baseline="central" '
                   'font-family="ui-monospace,monospace" font-size="12" font-weight="500" '
                   'fill="%s">%.1f</text>' % (ax, y + cell // 2, score_color(avg), avg))
    out.append('</svg>')
    return "".join(out)


def render_review(rv):
    groups, gorder = {}, []
    for it in rv["items"]:
        k = (it["round"], it["module"])
        if k not in groups:
            groups[k] = []
            gorder.append(k)
        groups[k].append(it)

    panels, heat_groups = [], []
    for rnd, mod in gorder:
        arr = groups[(rnd, mod)]
        scored = [x for x in arr if x["total"] is not None]
        avg = (sum(x["total"] for x in scored) / len(scored)) if scored else 0
        heat_groups.append(("%s · %s" % (rnd, mod_label(mod)), arr, avg))

        inner = ""
        for it in arr:
            chips = ""
            if it["total"] is not None:
                chips += '<span class="mv-chip">%g/25</span>' % it["total"]
            if it["cause"]:
                chips += '<span class="mv-chip warn">%s</span>' % esc(it["cause"])
            if it["type"]:
                chips += '<span class="mv-chip ghost">%s</span>' % esc(it["type"])
            ans = it["answer"]
            if ans:
                abody = ans
            elif it["want"]:
                abody = '<p class="mv-md-p">面试官真正想听：%s</p>' % inline(it["want"])
            else:
                abody = '<p class="mv-md-p mv-topic-meta">本报告未附标准答案。</p>'
            inner += (
                '<div class="mv-qitem">'
                '<div class="mv-qhead"><span class="mv-qid">%s</span>'
                '<span class="mv-qtime">%s</span>%s</div>'
                '<flip-card card-id="review-%s" tag="%s" q="%s" a="%s"></flip-card>'
                '</div>'
                % (esc(it["id"]), esc(it["time"]), chips,
                   attrs(it["id"]) + "-" + attrs(rv["stem"])[:12],
                   attrs(it["type"] or "面试题"),
                   attrs(it["q"]), attrs(_strip_tags(abody)))
            )
        panels.append('<collapse-panel title="%s · %s · 平均 %.1f（%d 题）">%s</collapse-panel>'
                      % (esc(rnd), esc(mod), avg, len(arr), inner))

    missing = ""
    for mm in rv["missing"]:
        inner = ('<p class="mv-md-p"><strong>为什么是缺口</strong>：%s</p>'
                 '<p class="mv-md-p"><strong>补到什么程度</strong>：%s</p>'
                 '<p class="mv-md-p"><strong>挂靠</strong>：%s</p>'
                 % (inline(mm["why"]), inline(mm["target"]),
                    inline(mm["ref"]) or '<span class="mv-topic-meta">—</span>'))
        missing += ('<collapse-panel title="%s · %s">%s</collapse-panel>'
                    % (esc(mm["id"]), esc(mm["name"]), inner))

    plan = ""
    for blk in rv["plan"]:
        lis = "".join("<li>%s</li>" % inline(x) for x in blk["todos"])
        plan += ('<collapse-panel title="%s（%d 条）"%s>'
                 '<ul class="mv-md-ul">%s</ul></collapse-panel>'
                 % (esc(blk["section"]), len(blk["todos"]),
                    " open" if blk == rv["plan"][0] else "", lis))

    meta_line = esc(" ｜ ".join("%s %s" % (k, v) for k, v in rv["head_meta"][:4]))
    out = REVIEW_PAGE
    for k, v in (
        ("%%TITLE%%", esc(rv["title"])),
        ("%%META%%", meta_line),
        ("%%SUMMARY%%", rv["summary"]),
        ("%%HEAT%%", heat_svg(heat_groups)),
        ("%%TOTAL%%", str(len(rv["items"]))),
        ("%%PANELS%%", "".join(panels)),
        ("%%MISSING%%", missing or '<p class="mv-note">本报告未列缺失模块。</p>'),
        ("%%PLAN%%", plan or '<p class="mv-note">本报告未列下次清单。</p>'),
        ("%%SRC%%", esc(rv["key"])),
    ):
        out = out.replace(k, v)
    return out


def _strip_tags(html):
    """把答案 HTML 压成纯文本（flip-card 只接受文本属性）"""
    s = re.sub(r"<br\s*/?>", "\n", html)
    s = re.sub(r"</(p|li|h3|pre|div)>", "\n", s)
    s = re.sub(r"<li>", "· ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


REVIEW_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%TITLE%%</title>
<link rel="stylesheet" href="../_components/marvis.css">
</head>
<body class="mv-page">
<div class="mv-wrap">
  <a class="mv-back" href="../index.html">← 返回训练台</a>

  <div class="mv-topic-head">
    <span class="mv-topic-module">面试诊断</span>
    <h1 class="mv-topic-title">%%TITLE%%</h1>
    <p class="mv-topic-meta">%%META%%</p>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">总评</h2>
    <div class="mv-problem">%%SUMMARY%%</div>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">分数分布 <span class="mv-topic-meta">共 %%TOTAL%% 题 · 颜色越深分越高 · 悬停看题号与归因</span></h2>
    <figure-box num="1" title="各模块逐题得分与平均分（满分 25）">%%HEAT%%</figure-box>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">逐题（按模块）<span class="mv-topic-meta">先说后翻</span></h2>
    %%PANELS%%
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">缺失知识模块</h2>
    %%MISSING%%
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">下次准备清单</h2>
    %%PLAN%%
  </div>

  <p class="mv-note">正本：%%SRC%%　（改正本后重跑 build.py 即可刷新本页）</p>
</div>
<script src="../_components/marvis.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- adapter：模块深挖卡（学习页）

def bullet_field(text, label):
    """抽 `- **标签**（可选补充）：值`"""
    m = re.search(r"^\s*-\s*\*\*" + re.escape(label) + r"\*\*[^：:]*[：:]\s*(.+)$",
                  text, re.M)
    return m.group(1).strip() if m else ""


def parse_module_card(path):
    """解析模块深挖卡（按 templates/模块深挖卡模板.md 的结构）"""
    meta, body = split_front(path.read_text(encoding="utf-8"))
    if "主线拆解" not in body:
        return None

    m = re.search(r"^#\s+(.+)$", body, re.M)
    title = m.group(1).strip() if m else path.stem
    module = (meta.get("module") or path.parent.name).split("/")[0].strip()
    if module in ("topics", "wiki"):
        module = path.stem

    sec1 = slice_section(body, r"^##\s*1\.", r"^##\s*2\.")
    sm = re.search(r"^>\s*(.+)$", sec1, re.M)
    summary = sm.group(1).strip() if sm else ""
    if summary.startswith("【"):
        summary = ""

    lines_ = []
    for cells in parse_md_table(slice_section(body, r"^##\s*2\.", r"^##\s*3\.").splitlines()):
        if len(cells) < 3 or not re.fullmatch(r"[一二三四五六七八九十]+", cells[0].strip()):
            continue
        lines_.append({
            "no": cells[0].strip(), "name": cells[1].strip(),
            "tradeoff": cells[2].strip(),
            "count": cells[3].strip() if len(cells) > 3 else "",
        })

    topics = []
    for cells in parse_md_table(slice_section(body, r"^##\s*3\.", r"^##\s*4\.").splitlines()):
        if len(cells) < 4 or not re.fullmatch(r"M\d+", cells[0].strip()):
            continue
        topics.append({"id": cells[0].strip(), "name": cells[1].strip(),
                       "line": cells[2].strip(), "status": cells[3].strip()})

    questions = []
    for cells in parse_md_table(slice_section(body, r"^##\s*4\.", r"^##\s*5\.").splitlines()):
        if len(cells) < 4 or not re.fullmatch(r"\d+", cells[0].strip()):
            continue
        questions.append({"no": cells[0].strip(), "q": cells[1].strip(),
                          "line": cells[2].strip(), "pri": cells[3].strip()})

    bridge, seen_b = [], False
    for cells in parse_md_table(slice_section(body, r"^##\s*6\.", r"^##\s*7\.").splitlines()):
        if len(cells) < 4:
            continue
        if "面试官问的" in cells[0]:
            seen_b = True
            continue
        bridge.append(cells[:4])

    gate = [re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", ln).strip()
            for ln in slice_section(body, r"^##\s*7\.", r"^##\s*8\.").splitlines()
            if re.match(r"^\s*-\s*\[[ xX]\]\s*\S", ln)]

    # 同目录下的母题卡（内容来源）
    cards = {}
    for p in sorted(path.parent.glob("母题-*.md")):
        mm = re.match(r"母题-([A-Za-z]?\d+)", p.stem)
        if mm:
            cards[mm.group(1)] = p

    return {
        "key": path.relative_to(ROOT).as_posix(),
        "module": module,
        "stem": path.stem,
        "title": title,
        "summary": summary,
        "include": bullet_field(body, "包含"),
        "exclude": bullet_field(body, "明确不包含"),
        "reason": bullet_field(body, "为什么现在"),
        "lines": lines_,
        "topics": topics,
        "questions": questions,
        "bridge": bridge,
        "gate": gate,
        "cards": cards,
        "page": "modules/%s.html" % module,
    }


CN_INDEX = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def line_short(name):
    """「**索引**：怎么让查询不用扫全表」→「索引」"""
    return re.split(r"[：:]", re.sub(r"\*+", "", name or ""))[0].strip()


def line_question(name):
    """取冒号后的那半（这条线在回答什么问题）"""
    s = re.sub(r"\*+", "", name or "")
    parts = re.split(r"[：:]", s, 1)
    return parts[1].strip() if len(parts) > 1 else ""


def module_line_page(md, no):
    idx = CN_INDEX.get(no, 0)
    return "modules/%s-%02d-%s.html" % (md["module"], idx, line_short(
        next((l["name"] for l in md["lines"] if l["no"] == no), no)))


def _by_line(rows, key="line"):
    d = {}
    for r in rows:
        d.setdefault(r[key], []).append(r)
    return d


def _topic_state(md, tid):
    p = md["cards"].get(tid)
    if not p:
        return "none", None
    tc = parse_topic(p)
    if not tc:
        return "none", None
    return ("live" if tc.get("status") == "integrated" else "draft"), tc


def render_module_index(md):
    """模块概览页：几条主线、多少题、走到哪了"""
    tbl, qbl = _by_line(md["topics"]), _by_line(md["questions"])
    n_live = n_draft = 0
    for t in md["topics"]:
        st, _ = _topic_state(md, t["id"])
        n_live += st == "live"
        n_draft += st == "draft"
    n_q = len(md["questions"])
    n_must = sum(1 for q in md["questions"] if "必背" in (q["pri"] or ""))

    rows = ""
    for ln in md["lines"]:
        arr, qs = tbl.get(ln["no"], []), qbl.get(ln["no"], [])
        done = sum(1 for t in arr if _topic_state(md, t["id"])[0] != "none")
        pct = int(done * 100 / len(arr)) if arr else 0
        rows += (
            '<a class="mv-line-row" href="%s">'
            '<span class="mv-line-no">%s</span>'
            '<span class="mv-line-name">%s</span>'
            '<span class="mv-line-q">%s</span>'
            '<span class="mv-line-st">母题 %d · 题 %d</span>'
            '<span class="mv-line-bar"><i style="width:%d%%"></i></span>'
            "</a>"
            % (esc(module_line_page(md, ln["no"])), esc(ln["no"]),
               esc(line_short(ln["name"])), esc(line_question(ln["name"])),
               len(arr), len(qs), pct)
        )

    out = MODULE_INDEX_PAGE
    for k, v in (
        ("%%TITLE%%", esc(md["title"])),
        ("%%MODULE%%", esc(md["module"])),
        ("%%SUMMARY%%", esc(md["summary"]) if md["summary"]
            else '<span class="mv-topic-meta">一句话结论待填（闭卷后自己写 20 秒版）</span>'),
        ("%%REASON%%", esc(md["reason"])),
        ("%%INCLUDE%%", esc(md["include"])),
        ("%%EXCLUDE%%", esc(md["exclude"])),
        ("%%NLINE%%", str(len(md["lines"]))),
        ("%%NTOPIC%%", str(len(md["topics"]))),
        ("%%NQ%%", str(n_q)),
        ("%%NMUST%%", str(n_must)),
        ("%%NLIVE%%", str(n_live)),
        ("%%NDRAFT%%", str(n_draft)),
        ("%%ROWS%%", rows or '<p class="mv-note">还没有主线。</p>'),
        ("%%SRC%%", esc(md["key"])),
    ):
        out = out.replace(k, v)
    return out


def render_module_line(md, ln, prev_ln, next_ln):
    """主线页：先出题 → 自己答 → 展开对照 → 记断点；本主线的题在页内"""
    tbl, qbl = _by_line(md["topics"]), _by_line(md["questions"])
    arr, qs = tbl.get(ln["no"], []), qbl.get(ln["no"], [])

    blocks = ""
    for t in arr:
        st, tc = _topic_state(md, t["id"])
        chip = {"live": '<span class="mv-chip">已掌握</span>',
                "draft": '<span class="mv-chip warn">草稿 · 待验收</span>'}.get(
                    st, '<span class="mv-chip ghost">未提炼</span>')
        head = ('<div class="mv-mt-head"><span class="mv-mt-id">%s</span>'
                '<span class="mv-mt-name">%s</span>%s</div>'
                % (esc(t["id"]), esc(t["name"]), chip))

        if not tc:
            ctx = ('<p class="mv-mt-empty">讲解待提炼。这道母题将覆盖的题：</p>'
                   '<ul class="mv-md-ul">%s</ul>'
                   % "".join("<li>%s</li>" % inline(q["q"]) for q in qs[:4]))
            blocks += '<div class="mv-mt">%s%s</div>' % (head, ctx)
            continue

        ctx = ""
        if tc["problem"]:
            ctx += '<collapse-panel title="题目背景">%s</collapse-panel>' % md_to_html(tc["problem"])
        ctx += ('<div class="mv-ask"><p class="mv-ask-q">%s</p>'
                '<textarea class="mv-ask-in" data-k="ask-%s-%s" rows="3" '
                'placeholder="先自己答一遍（关键词就行），答完再展开对照"></textarea></div>'
                % (inline(tc["question"]), esc(md["module"]), esc(t["id"])))

        ref = ['<p class="mv-md-p"><strong>一句话结论</strong>：%s</p>' % inline(tc["conclusion"])]
        if tc["keywords"]:
            ref.append('<ul class="mv-kw">%s</ul>' % "".join("<li>%s</li>" % esc(k)
                                                             for k in tc["keywords"]))
        if tc["invariant"]:
            ref.append('<p class="mv-md-p"><strong>主线</strong>：%s</p>' % inline(tc["invariant"]))
        if tc["body_html"]:
            ref.append(tc["body_html"])
        for i, f in enumerate(tc["figures"], 1):
            ref.append('<figure-box num="%s-%d" title="%s" note="%s">%s</figure-box>'
                       % (t["id"], i, attrs(f["title"]), attrs(f["note"]),
                          prefix_svg_ids(f["svg"], "m%s%d" % (t["id"], i))))
        ctx += ('<collapse-panel title="对照讲解（先答完再看）">%s</collapse-panel>'
                % "".join(ref))

        if tc["followups"]:
            items = "".join(
                '<p class="mv-md-p"><strong>%d. %s</strong></p><p class="mv-md-p">%s</p>'
                % (i, inline(fq), inline(fa) or '<span class="mv-topic-meta">见讲解</span>')
                for i, (fq, fa) in enumerate(tc["followups"], 1))
            ctx += '<collapse-panel title="两层追问（先说后看）">%s</collapse-panel>' % items

        ctx += ('<collapse-panel title="断点与验收">'
                '<textarea class="mv-ask-in" data-k="bp-%s-%s" rows="2" '
                'placeholder="这次卡在哪（写成事实，不写评价）"></textarea>'
                '<p class="mv-note">正本：%s ｜ 闭卷过关后把 frontmatter 的 status 改成 '
                '<code class="mv-md-code">integrated</code>，它才会进复训牌组。</p>'
                "</collapse-panel>" % (esc(md["module"]), esc(t["id"]), esc(tc["src"])))

        blocks += '<div class="mv-mt">%s%s</div>' % (head, ctx)

    drill = ""
    for q in qs:
        drill += ('<div class="mv-qitem"><div class="mv-qhead">'
                  '<span class="mv-qid">%s</span><span class="mv-chip ghost">%s</span></div>'
                  '<flip-card card-id="%s-q%s" tag="%s" q="%s" a="%s"></flip-card></div>'
                  % (esc(q["no"]), esc(q["pri"]), attrs(md["module"]), attrs(q["no"]),
                     attrs(md["module"]), attrs(q["q"]),
                     attrs("先自己讲一遍，再回上面的母题区核对。")))
    if not drill:
        drill = '<p class="mv-note">这条主线还没有挂题。</p>'

    nav = ""
    if prev_ln:
        nav += '<a class="mv-line-nav" href="%s">← %s · %s</a>' % (
            esc(module_line_page(md, prev_ln["no"])), esc(prev_ln["no"]),
            esc(line_short(prev_ln["name"])))
    if next_ln:
        nav += '<a class="mv-line-nav next" href="%s">%s · %s →</a>' % (
            esc(module_line_page(md, next_ln["no"])), esc(next_ln["no"]),
            esc(line_short(next_ln["name"])))

    out = MODULE_LINE_PAGE
    for k, v in (
        ("%%TITLE%%", esc(line_short(ln["name"]))),
        ("%%MODULE%%", esc(md["module"])),
        ("%%INDEX%%", esc("modules/%s.html" % md["module"])),
        ("%%NO%%", esc(ln["no"])),
        ("%%LEAD%%", inline(line_question(ln["name"])) or "—"),
        ("%%TRADEOFF%%", inline(ln["tradeoff"]) if ln["tradeoff"] else ""),
        ("%%BLOCKS%%", blocks or '<p class="mv-note">这条主线还没有母题。</p>'),
        ("%%DRILL%%", drill),
        ("%%NQ%%", str(len(qs))),
        ("%%NAV%%", nav),
    ):
        out = out.replace(k, v)
    return out


MODULE_INDEX_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%TITLE%%</title>
<link rel="stylesheet" href="../_components/marvis.css">
</head>
<body class="mv-page">
<div class="mv-wrap">
  <a class="mv-back" href="../index.html">← 返回训练台</a>

  <div class="mv-topic-head">
    <span class="mv-topic-module">模块概览</span>
    <h1 class="mv-topic-title">%%TITLE%%</h1>
    <p class="mv-topic-meta">正本 %%SRC%%</p>
  </div>

  <div class="mv-stat">
    <span class="mv-stat-i"><b>%%NLINE%%</b> 条主线</span>
    <span class="mv-stat-i"><b>%%NTOPIC%%</b> 个母题</span>
    <span class="mv-stat-i"><b>%%NQ%%</b> 道题（<b>%%NMUST%%</b> 必背）</span>
    <span class="mv-stat-i ok"><b>%%NLIVE%%</b> 已掌握</span>
    <span class="mv-stat-i warn"><b>%%NDRAFT%%</b> 草稿待验收</span>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">一句话结论</h2>
    <div class="mv-problem"><p class="mv-md-p">%%SUMMARY%%</p></div>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">模块边界 <span class="mv-topic-meta">防无限扩张</span></h2>
    <div class="mv-bd">
      <p class="mv-md-p"><strong>包含</strong>：%%INCLUDE%%</p>
      <p class="mv-md-p"><strong>明确不包含</strong>：%%EXCLUDE%%</p>
      <p class="mv-md-p"><strong>为什么现在</strong>：%%REASON%%</p>
    </div>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">主线 <span class="mv-topic-meta">一次只开一条</span></h2>
    %%ROWS%%
  </div>
</div>
<script src="../_components/marvis.js"></script>
</body>
</html>
"""


MODULE_LINE_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%NO%% · %%TITLE%%</title>
<link rel="stylesheet" href="../_components/marvis.css">
</head>
<body class="mv-page">
<div class="mv-wrap">
  <a class="mv-back" href="%%INDEX%%">← %%MODULE%% 模块概览</a>

  <div class="mv-topic-head">
    <span class="mv-topic-module">%%MODULE%% · 主线 %%NO%%</span>
    <h1 class="mv-topic-title">%%TITLE%%</h1>
    <p class="mv-topic-meta">这条线在回答：%%LEAD%%</p>
  </div>
  <p class="mv-line-lead">%%TRADEOFF%%</p>

  <div class="mv-section">
    <h2 class="mv-section-title">母题 <span class="mv-topic-meta">先自己答，再展开对照</span></h2>
    %%BLOCKS%%
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">本主线的题 <span class="mv-topic-meta">%%NQ%% 道 · 先说后翻</span></h2>
    %%DRILL%%
  </div>

  <div class="mv-nav">%%NAV%%</div>
</div>
<script src="../_components/marvis.js"></script>
<script>
document.querySelectorAll('.mv-ask-in').forEach(function (t) {
  var k = 'mv.ask.' + t.getAttribute('data-k');
  try { var v = localStorage.getItem(k); if (v) t.value = v; } catch (e) {}
  t.addEventListener('input', function () {
    try { localStorage.setItem(k, t.value); } catch (e) {}
  });
});
</script>
</body>
</html>
"""



# ---------------------------------------------------------------- main

DIRTY_ATTR = re.compile(r'\s+data-page-[a-z-]+="[^"]*"')


def cleanup_html():
    """清掉预览面板写回源文件的注入属性（否则会污染提交）"""
    n = 0
    for p in SITE.rglob("*.html"):
        txt = p.read_text(encoding="utf-8")
        new = DIRTY_ATTR.sub("", txt)
        if new != txt:
            p.write_text(new, encoding="utf-8")
            n += 1
    return n


def main():
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_TOPICS.mkdir(parents=True, exist_ok=True)

    topics, seen_t = [], set()
    for d in TOPIC_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name.startswith("00-") or "母题池" in p.name or "母题组" in p.name:
                continue
            t = parse_topic(p)
            if not t:
                continue
            if t["key"] in seen_t:
                print("  [dup ] %s" % t["key"])
                continue
            seen_t.add(t["key"])
            topics.append(t)

    cards, seen_c = [], set()
    for d in CARD_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            if OUT_DATA in p.parents:
                continue
            for c in parse_cards(p):
                if not c["q"] or not c["a"] or c["id"] in seen_c:
                    continue
                seen_c.add(c["id"])
                cards.append(c)

    for t in topics:
        (OUT_TOPICS / ("%s-%s.html" % (t["module"], t["stem"]))).write_text(
            render_topic(t), encoding="utf-8")

    # 诊断页
    reviews, seen_r = [], set()
    for d in REVIEW_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            rv = parse_review(p)
            if not rv or rv["stem"] in seen_r:
                continue
            seen_r.add(rv["stem"])
            reviews.append(rv)
    OUT_REVIEWS.mkdir(parents=True, exist_ok=True)
    for rv in reviews:
        (OUT_REVIEWS / (rv["stem"] + ".html")).write_text(
            render_review(rv), encoding="utf-8")

    # 模块学习页
    modules, seen_m = [], set()
    for d in MODULE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            md = parse_module_card(p)
            if not md or md["module"] in seen_m:
                continue
            seen_m.add(md["module"])
            modules.append(md)
    OUT_MODULES.mkdir(parents=True, exist_ok=True)
    for md in modules:
        (OUT_MODULES / ("%s.html" % md["module"])).write_text(
            render_module_index(md), encoding="utf-8")
        for i, ln in enumerate(md["lines"]):
            fname = module_line_page(md, ln["no"]).split("/")[-1]
            (OUT_MODULES / fname).write_text(
                render_module_line(md, ln,
                                   md["lines"][i - 1] if i > 0 else None,
                                   md["lines"][i + 1] if i + 1 < len(md["lines"]) else None),
                encoding="utf-8")

    # 复训牌组只收已验收（integrated）的母题；草稿只读不练
    live = [t for t in topics if t.get("status") == "integrated"]
    drafts = [t for t in topics if t.get("status") != "integrated"]

    decks = []
    if live:
        decks.append({
            "id": "topics", "name": "母题",
            "cards": [{"id": t["key"], "q": t["question"], "a": t["conclusion"],
                       "tag": t["module"], "href": t["page"], "src": t["src"]}
                      for t in live],
        })
    if cards:
        decks.append({
            "id": "extra", "name": "补充卡",
            "cards": [{"id": c["id"], "q": c["q"], "a": c["a"],
                       "tag": c["tag"], "src": c["src"]} for c in cards],
        })

    (OUT_DATA / "decks.json").write_text(
        json.dumps(decks, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DATA / "decks.js").write_text(
        "window.MARVIS_DECKS = " + json.dumps(decks, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    review_index = [{"title": rv["title"], "href": rv["page"],
                     "items": len(rv["items"]), "missing": len(rv["missing"])}
                    for rv in reviews]
    (OUT_DATA / "reviews.js").write_text(
        "window.MARVIS_REVIEWS = " + json.dumps(review_index, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    mod_index = [{"module": md["module"], "title": md["title"], "href": md["page"],
                  "lines": len(md["lines"]), "topics": len(md["topics"]),
                  "ready": sum(1 for t in md["topics"] if t["id"] in md["cards"])}
                 for md in modules]
    (OUT_DATA / "modules.js").write_text(
        "window.MARVIS_MODULES = " + json.dumps(mod_index, ensure_ascii=False) + ";\n",
        encoding="utf-8")

    n = sum(len(d["cards"]) for d in decks)
    print("母题页 %d | 牌组 %d | 可练卡片 %d" % (len(topics), len(decks), n))
    if drafts:
        print("  草稿 %d 个（只读不练）：%s"
              % (len(drafts), " ".join(t["stem"] for t in drafts)))
    for d in decks:
        print("  [%s] %d 个" % (d["name"], len(d["cards"])))
    for t in topics:
        print("  -> %s（%s，追问 %d，变体 %d）"
              % (t["page"], "有图" if t["figures"] else "无图",
                 len(t["followups"]), len(t["variants"])))
    for rv in reviews:
        scored = [x for x in rv["items"] if x["total"] is not None]
        print("  => %s（%d 题，已评 %d，有标准答案 %d，缺失模块 %d，计划 %d 段）"
              % (rv["page"], len(rv["items"]), len(scored),
                 sum(1 for x in rv["items"] if x["answer"]),
                 len(rv["missing"]), len(rv["plan"])))
    for md in modules:
        ready = sum(1 for t in md["topics"] if t["id"] in md["cards"])
        print("  == %s（%d 主线 / %d 母题，已提炼 %d，必背题 %d）"
              % (md["page"], len(md["lines"]), len(md["topics"]), ready,
                 sum(1 for q in md["questions"] if "必背" in (q["pri"] or ""))))

    cleaned = cleanup_html()
    if cleaned:
        print("清理预览注入属性：%d 个 html 文件" % cleaned)


if __name__ == "__main__":
    main()
