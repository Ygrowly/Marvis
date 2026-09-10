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
FIGURES = SITE / "figures"

TOPIC_DIRS = ["wiki/topics"]          # 母题卡
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
        "src": path.relative_to(ROOT).as_posix(),
        "question": q,
        "conclusion": a,
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

    out = PAGE
    for k, v in (
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


# ---------------------------------------------------------------- main

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

    decks = []
    if topics:
        decks.append({
            "id": "topics", "name": "母题",
            "cards": [{"id": t["key"], "q": t["question"], "a": t["conclusion"],
                       "tag": t["module"], "href": t["page"], "src": t["src"]}
                      for t in topics],
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

    n = sum(len(d["cards"]) for d in decks)
    print("母题页 %d | 牌组 %d | 卡片合计 %d" % (len(topics), len(decks), n))
    for d in decks:
        print("  [%s] %d 个" % (d["name"], len(d["cards"])))
    for t in topics:
        print("  -> %s（%s，追问 %d，变体 %d）"
              % (t["page"], "有图" if t["figures"] else "无图",
                 len(t["followups"]), len(t["variants"])))


if __name__ == "__main__":
    main()
