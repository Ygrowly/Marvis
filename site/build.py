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
import os
import re
import datetime
from urllib.parse import quote
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
OUT_PROJECTS = SITE / "projects"
FIGURES = SITE / "figures"

# mermaid：双轨渲染，默认走轨二（最简单：一条 python site/build.py 就完事，不碰浏览器）。
#   轨二（默认·浏览器）：图源码留在 <div class="mermaid">，页面加载自带的 mermaid.min.js
#                      （取不到再走 CDN）现场渲染。改完 md 直接看，不用等构建。
#   轨一（可选·构建期）：MARVIS_MMD_PRERENDER=1 时启用——用无头 Edge 把图渲成内联 SVG 存进
#                      site/_build/mermaid/cache/，之后页面零依赖、离线也能看、打开更快。
#                      预热缓存：python site/_build/mermaid/mmd.py --scan
sys.path.insert(0, str(SITE / "_build" / "mermaid"))
try:
    import mmd as _mmd
except Exception:                                        # noqa: BLE001
    _mmd = None
MMD_POOL = {}
LIVE_MMD = [0]                 # 本次构建里走浏览器渲染的图块数
MMD_CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"

TOPIC_DIRS = ["wiki/topics"]          # 母题卡
REVIEW_DIRS = ["wiki/interview"]      # 面试复盘（诊断页）
MODULE_DIRS = ["wiki/topics"]         # 模块深挖卡（学习页）
CARD_DIRS = ["site/cards", "output/算法", "study", "wiki/interview", "wiki/thinking", "projects"]
LEDGER_SRC = ROOT / "questions.md"    # 问题台账（唯一加工驱动源）→ _data/ledger.js

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
                    # frontmatter 值里剥掉行内注释（`#` 之后），否则整串会被当值用
                    v = re.sub(r"\s+#.*$", "", v)
                    meta[k.strip()] = v.strip()
            return meta, parts[2]
    return meta, text


def grab(text, name):
    """抽 `**字段**：值`，到下一个 ** / > / --- / 空行 为止"""
    pat = (r"\*\*" + re.escape(name) + r"\*\*\s*[：:]\s*(.+?)"
           r"(?=\n\s*\n|\n\s*\*\*|\n\s*>|\n\s*---|\Z)")
    m = re.search(pat, text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def grab_titled(text, name):
    """抽 `**字段**：值` 或 `**字段（任意说明）**：值`。

    2026-09-13 新增：`方言差异` 这一段的括号说明在库里有多达 13 种写法
    （「面试安全底线」「跨中间件对照」「与 RAG 簇的分工」…），
    grab() 的精确匹配只认裸名字，结果 47 张卡的这一段几乎全被静默丢掉。
    """
    pat = (r"\*\*" + re.escape(name) + r"(?:（[^）]*）)?\*\*\s*[：:]\s*(.+?)"
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


def grab_items(text, *names):
    """抽 `**字段**` 之后的条目，`- ` 与 `1. ` 都认，返回去掉标记的整行文本。

    2026-09-12 新增：旧体例的母题卡（MySQL M5–M7/M13–M17、PostgreSQL 全部）用的是
    `**追问链**` / `**类似题**` 两个标签、且追问是 `- 追问一层：…` 的**无序**列表，
    原先 grab_numbered/grab_list 抓不到 → 这 27 张卡的页面静默丢掉追问与变体两节。
    本函数按「先给的名字先试，抓到就返回」工作，对已正常的卡零影响。
    """
    for name in names:
        idx = text.find("**" + name + "**")
        if idx < 0:
            continue
        tail = text[idx + len("**" + name + "**"):]
        stop = re.search(r"\n\s*(?:\*\*|##)", tail)
        block = tail[: stop.start()] if stop else tail
        out = [re.sub(r"^\s*(?:[-*]|\d+[.、])\s+", "", ln).strip()
               for ln in block.splitlines()
               if re.match(r"^\s*(?:[-*]|\d+[.、])\s+\S", ln)]
        if out:
            return out
    return []


def to_pairs(items):
    """把 `追问一层：**「问」**——答` 这类整行，切成 [(问, 答)]"""
    out = []
    for s in items:
        s = re.sub(r"^追问[一二三四五六七八九十]+层\s*[：:]\s*", "", s)
        parts = re.split(r"\s*——\s*|\s*—\s*", s, maxsplit=1)
        out.append((parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""))
    return out


# ---------------------------------------------------------------- md → html（轻量）

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def split_kw(s):
    """把「恢复关键词」那一行切成条目。

    2026-09-13 修：原先 `re.split(r"[/｜|·]", ...)` 有两个错——
      ① 括号里的 `/` 也被切：`（状态没变 / 重复同参数调用）` 被撕成两个碎片
      ② `·` 根本不是顶层分隔符，是【条目内部】的子列表标记：
         `分页 · 范围 · 过滤 · 截断 + 合理默认值`、`Resume · Replay · Retry · Fork 四分工`
         按它切会切出一堆无意义的单字芯片
    实测：33/93 张卡受影响，而这些词正是「卡住时重建整条链」用的。
    顶层真正的分隔符只有 `/`（`｜`/`|` 保留兜底，实测顶层从未出现）。
    """
    out, buf, depth = [], [], 0
    for ch in s:
        if ch in "（(":
            depth += 1
        elif ch in "）)":
            depth = max(0, depth - 1)
        if ch in "/｜|" and depth == 0:
            out.append("".join(buf)); buf = []
        else:
            buf.append(ch)
    out.append("".join(buf))
    return [x.strip() for x in out if x.strip()]


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r'<code class="mv-md-code">\1</code>', s)
    return s


def plain(s):
    """flip-card 只接受纯文本属性，去掉 markdown 标记"""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s or "")
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return s.strip()


def mmd_svg(code_text):
    """取 mermaid 源码对应的内联 SVG。

    只有显式 MARVIS_MMD_PRERENDER=1 才走构建期渲染；其余一律交给浏览器端。
    """
    if not _mmd or not os.environ.get("MARVIS_MMD_PRERENDER"):
        return None
    if code_text in MMD_POOL:
        return MMD_POOL[code_text]
    svg = _mmd.get(code_text)
    MMD_POOL[code_text] = svg
    return svg


def code_block_html(body, lang=""):
    """围栏代码块 → html。

    mermaid 双轨（2026-09-25）：
      1) 构建期渲染器有缓存 → 内联 SVG（离线可读，零依赖）；
      2) 没有缓存（新写的图 / 没跑过渲染器）→ 留 <div class="mermaid"> 源码，
         由页面在浏览器里渲染（本地 mermaid.min.js，取不到再走 CDN）。
    两条路都不静默丢内容：渲不出来时页面上仍是可读的图源码。
    """
    if lang == "mermaid":
        svg = mmd_svg(body)
        if svg:
            m = re.search(r'<svg\b[^>]*\bwidth="([\d.]+)"', svg)
            wide = bool(m) and float(m.group(1)) > 880      # 正文栏 54rem=864px
            hint = '<p class="mv-mmd-hint">图较宽，可左右拖动看全</p>' if wide else ''
            return hint + '<div class="mv-mmd">%s</div>' % svg
        LIVE_MMD[0] += 1
        return '<div class="mermaid">%s</div>' % esc(body)
    return '<pre class="mv-md-pre">' + esc(body) + "</pre>"


def warm_mermaid():
    """构建前把这次会渲染到的 md 里的 mermaid 块一次性补齐（一个浏览器进程渲完全部）"""
    if not _mmd or not os.environ.get("MARVIS_MMD_PRERENDER"):
        return 0
    codes = []
    for d in sorted(set(TOPIC_DIRS + MODULE_DIRS + REVIEW_DIRS + CARD_DIRS)):
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            try:
                codes += _mmd.blocks_of(p.read_text(encoding="utf-8"))
            except Exception:                            # noqa: BLE001
                continue
    if not codes:
        return 0
    MMD_POOL.update(_mmd.ensure(codes))
    print("  [mermaid] 图块 %d 处／去重 %d 张，已就绪"
          % (len(codes), len(set(_mmd.key(c) for c in codes))))
    return len(codes)


def mmd_boot(prefix):
    """浏览器端 mermaid 启动脚本：先取站点自带的 mermaid.min.js，取不到再走 CDN。"""
    return """/* 由 site/build.py 生成，别手改 —— 改 build.py 里的 mmd_boot() 再重跑。
   浏览器端 mermaid 渲染：优先站点自带的 mermaid.min.js，取不到再走 CDN。 */
(function () {
  var CDN = "%(_c)s";
  /* 本脚本放在 _data/ 下，用它自己的 src 反推站点根，各层目录的页面都能拿到对的路径 */
  var me = document.currentScript;
  var LOCAL = ((me && me.src) ? me.src.replace(/_data\\/mmd-boot\\.js.*$/, "") : "%(_p)s")
    + "_build/mermaid/mermaid.min.js";
  /* mermaid 要量文字尺寸：图若躺在折叠面板（display:none）里，量出来是 0，
     只会渲一个 16×16 的空图。渲染前把隐藏的祖先临时搬到屏幕外「显形」，渲完原样还原。 */
  function reveal(el) {
    var out = [], p = el.parentElement;
    while (p && p !== document.documentElement) {
      var cs = getComputedStyle(p);
      if (cs.display === "none" || cs.visibility === "hidden") {
        out.push([p, p.getAttribute("style") || ""]);
        p.style.cssText = "display:block !important; visibility:hidden !important;" +
          "position:absolute !important; left:-99999px !important; top:0 !important;" +
          "width:1600px !important;";
      }
      p = p.parentElement;
    }
    return out;
  }
  function restore(chain) {
    chain.forEach(function (x) {
      if (x[1]) x[0].setAttribute("style", x[1]); else x[0].removeAttribute("style");
    });
  }
  function boot() {
    if (!window.mermaid) return;
    window.mermaid.initialize({
      startOnLoad: false, theme: "neutral", securityLevel: "loose",
      fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
      flowchart: { useMaxWidth: false }, sequence: { useMaxWidth: false },
      gantt: { useMaxWidth: false }, class: { useMaxWidth: false },
      state: { useMaxWidth: false }, er: { useMaxWidth: false },
      journey: { useMaxWidth: false }, pie: { useMaxWidth: false }
    });
    var nodes = [].slice.call(document.querySelectorAll(".mermaid"));
    var chains = nodes.map(reveal);
    /* 宽图会被容器裁掉右边——跟构建期内联那条路一样，给一句「可左右拖动」的提示 */
    function hint() {
      nodes.forEach(function (d) {
        var svg = d.querySelector("svg");
        if (!svg) return;
        var w = parseFloat(svg.getAttribute("width")) || 0;
        if (w <= 880) return;
        var prev = d.previousElementSibling;
        if (prev && prev.className === "mv-mmd-hint") return;
        var p = document.createElement("p");
        p.className = "mv-mmd-hint";
        p.textContent = "图较宽，可左右拖动看全";
        d.parentNode.insertBefore(p, d);
      });
    }
    var fin = function () { chains.forEach(restore); hint(); };
    try {
      var r = window.mermaid.run({ querySelector: ".mermaid" });
      if (r && r.then) r.then(fin, fin); else fin();
    } catch (e) { fin(); console.error("[mermaid]", e); }
  }
  function go(url, next) {
    var s = document.createElement("script");
    s.src = url;
    s.onload = function () { boot(); };
    s.onerror = function () {
      if (s.parentNode) s.parentNode.removeChild(s);
      if (next) go(next, null);
      else console.warn("[mermaid] 本地与 CDN 都没取到，图保留源码");
    };
    document.head.appendChild(s);
  }
  go(LOCAL, CDN);
})();
""" % {"_p": prefix, "_c": MMD_CDN}


def inject_mermaid_runtime():
    """给含未渲染 mermaid 块的页面挂上启动脚本（按目录深度算相对路径）"""
    n = 0
    boot = mmd_boot("")
    for d in [SITE, OUT_TOPICS, OUT_MODULES, OUT_PROJECTS]:
        if not d.exists():
            continue
        for p in sorted(d.glob("*.html")):
            try:
                s = p.read_text(encoding="utf-8")
            except Exception:                            # noqa: BLE001
                continue
            if 'class="mermaid"' not in s or "</body>" not in s:
                continue
            depth = len(p.relative_to(SITE).parts) - 1
            tag = '<script src="%s_data/mmd-boot.js"></script>' % ("../" * depth)
            if tag in s:
                continue
            p.write_text(s.replace("</body>", tag + "</body>"), encoding="utf-8")
            n += 1
    if n:
        OUT_DATA.mkdir(parents=True, exist_ok=True)
        (OUT_DATA / "mmd-boot.js").write_text(boot, encoding="utf-8")
        print("  [mermaid] 浏览器端渲染 %d 处图块／%d 个页面（本地 mermaid.min.js → CDN 兜底）"
              % (LIVE_MMD[0], n))
    return n


def md_to_html(md, figmap=None, used=None):
    """markdown 转 html。figmap 非空时，正文里的 ::figure 行会就地渲染成图。"""
    figmap = figmap or {}
    out, para, lst, code, in_code, lang = [], [], [], [], False, ""

    def flush_para():
        if para:
            out.append('<p class="mv-md-p">' + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        if lst:
            out.append('<ul class="mv-md-ul">' +
                       "".join("<li>" + inline(x) + "</li>" for x in lst) + "</ul>")
            lst.clear()

    lines = md.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        i += 1
        # 表格：连续以 | 开头的行
        if raw.strip().startswith("|") and raw.strip().count("|") >= 2:
            block = [raw.strip()]
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            flush_para(); flush_list()
            rows = parse_md_table(block)
            if rows:
                out.append("<table class=\"mv-table\"><thead><tr>" +
                           "".join("<th>%s</th>" % inline(c) for c in rows[0]) +
                           "</tr></thead><tbody>" +
                           "".join("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) +
                                   "</tr>" for r in rows[1:]) +
                           "</tbody></table>")
            continue
        fm = FIGURE_RE.match(raw.strip())
        if fm:
            flush_para(); flush_list()
            _name = fm.group("file")
            _f = figmap.get(_name)
            if _f:
                if used is not None:
                    used.add(_name)
                out.append('<figure-box num="%s" title="%s" note="%s">%s</figure-box>'
                           % (attrs(_f["title"]), "", attrs(_f["note"]),
                              prefix_svg_ids(_f["svg"],
                                             "fig" + re.sub(r"\W+", "-", _name))))
            continue
        if raw.startswith("```"):
            if not in_code:
                flush_para(); flush_list()
                code, in_code, lang = [], True, raw[3:].strip().lower()
            else:
                flush_para(); flush_list()
                out.append(code_block_html("\n".join(code), lang))
                in_code, lang = False, ""
            continue
        if in_code:
            code.append(raw)
            continue
        if not raw.strip():
            flush_para(); flush_list()
            continue
        if re.fullmatch(r"[-*_]{3,}", raw.strip()):
            flush_para(); flush_list()
            out.append('<hr class="mv-md-hr">')
            continue
        m = re.match(r"^(#{2,5})\s+(.+)$", raw)
        if m:
            flush_para(); flush_list()
            _lv = len(m.group(1))
            _tag = "h3" if _lv <= 3 else "h4"
            out.append('<%s class="mv-md-h mv-md-h%d">%s</%s>'
                       % (_tag, _lv, inline(m.group(2)), _tag))
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
        out.append(code_block_html("\n".join(code), lang))
    return "\n".join(out)


# ---------------------------------------------------------------- adapter：母题卡

def answer_panel(speak, points=""):
    """完整回答块：口述稿 + 分层要点。

    字数/秒数是构建时真数出来的（去空白后计字符），秒数按 4 字/秒折算并标明是估算——
    不写死「60 秒」：那会让不同长度的稿子都挂同一个假数字。
    """
    n = len(re.sub(r"\s", "", plain(speak)))
    sec = int(round(n / 4.0))
    inner = ('<p class="mv-note" style="margin:0 0 .625rem">实测 %d 字 · 按 4 字/秒折算约 %d 秒'
             '（秒数是估算，字数才是实测）</p>' % (n, sec))
    inner += md_to_html(speak)
    if points:
        inner += ('<p class="mv-md-h mv-md-h4" style="margin-top:1rem">分层要点'
                  '<span class="mv-topic-meta">追问深挖时用</span></p>' + md_to_html(points))
    return ('<collapse-panel title="完整回答 · 口述稿（先自己答，再看）">%s</collapse-panel>'
            % inner)

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

    figures, figmap, used_figs = [], {}, set()
    for line in body.splitlines():
        fm = FIGURE_RE.match(line.strip())
        if not fm:
            continue
        fpath = FIGURES / fm.group("file")
        if not fpath.exists():
            print("  [warn] 图不存在，已跳过：%s (%s)" % (fm.group("file"), path.name))
            continue
        rest = [x.strip() for x in (fm.group("rest") or "").split("|")]
        _rec = {
            "file": fm.group("file"),
            "svg": fpath.read_text(encoding="utf-8"),
            "title": rest[0] if len(rest) > 0 else "",
            "note": rest[1] if len(rest) > 1 else "",
        }
        figmap[fm.group("file")] = _rec
        figures.append(_rec)
        continue
        figures.append({
            "svg": fpath.read_text(encoding="utf-8"),
            "title": rest[0] if len(rest) > 0 else "",
            "note": rest[1] if len(rest) > 1 else "",
        })

    lesson_md = section_by_title(body, "一、教材") or section_by_title(body, "教材")
    quiz_md = section_by_title(body, "二、自测") or section_by_title(body, "自测")

    mbody = ""
    mb = re.search(r"\n---\s*\n(.*?)(?=\n##\s*二、|\Z)", body, re.S)
    if mb and not lesson_md:
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
        "keywords": split_kw(grab(body, "恢复关键词")),
        "invariant": grab(body, "核心不变量 / 主线") or grab(body, "核心不变量"),
        "skeleton": grab(body, "完整回答骨架"),
        # 2026-09-26 新增：真正能照着讲的一段答案 + 分层要点。
        # 原来只有「一句话结论 + 骨架」，讲的时候没有可对照的完整答案。
        "answer": grab_block(body, "完整回答（口述稿）"),
        "points": grab_block(body, "分层要点"),
        "followups": (grab_numbered(body, "追问") or grab_numbered(body, "两层追问")
                      or to_pairs(grab_items(body, "追问链", "追问"))),
        "variants": grab_list(body, "同类变体") or grab_items(body, "类似题"),
        "related": grab(body, "关联母题"),
        "contrast": grab_titled(body, "方言差异"),
        "transfer": grab(body, "可迁移场景"),
        "breakpoint": grab(body, "本次断点"),
        "evidence": grab(body, "通过证据"),
        "guide": grab(body, "导读"),
        "interactive": meta.get("interactive", ""),
        "lesson_html": md_to_html(lesson_md, figmap, used_figs) if lesson_md else "",
        "quiz": parse_quiz(quiz_md),
        "figures": [f for f in figures if f["file"] not in used_figs],
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
  %%MODULE_BACK%%%%INTERACTIVE%%

  <div class="mv-topic-head">
    <span class="mv-topic-module">%%MODULE%%</span>
    <h1 class="mv-topic-title">%%TITLE%%</h1>
    <p class="mv-topic-meta">%%META%%</p>
  </div>
%%GUIDE%%
  <nav class="mv-toc" aria-label="本页大纲">
    <a href="#s-problem">题目</a>
    <a href="#s-lesson">教材</a>
    <a href="#s-quiz">自测</a>
    <a href="#s-output">面试输出</a>
    <a href="#s-conclusion">一句话结论</a>
    <a href="#s-extra">展开</a>
    <a href="#s-recycle">复训</a>
  </nav>
%%PROBLEM%%
%%LESSON%%
%%QUIZ%%
  <div class="mv-section" id="s-output">
    <h2 class="mv-section-title">三 · 面试输出 <span class="mv-topic-meta">闭卷口述 60 秒，再看结论</span></h2>
    <div class="mv-ask">
      <p class="mv-ask-q">%%Q%%</p>
      <textarea class="mv-ask-in" rows="3" placeholder="先闭卷把答案说一遍（或写下关键词），再往下看…"></textarea>
    </div>
    <flip-card gradable card-id="%%KEY%%" tag="%%MODULE%%" q="%%Q%%" a="%%A%%"></flip-card>
    <p class="mv-note" id="mv-grade-tip" style="margin-top:8px">翻面对照自测，评分会进训练台的复训调度。</p>
    %%IMPORTANCE%%
  </div>
  <div class="mv-section" id="s-conclusion">
    <h2 class="mv-section-title">一句话结论 <span class="mv-topic-meta">全卡唯一要背的锚点</span></h2>
    <div class="mv-conclusion">%%CONCLUSION%%</div>
    %%KEYWORDS%%
  </div>
%%FIGURES%%%%EXPAND%%%%BODY%%
  <div class="mv-section" id="s-recycle">
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


def parse_quiz(md):
    """自测段格式：**Q1（计算）**：题干  接着 **A1**：答案

    **题干和答案都允许多行**——选项 ①②③、引用段落都算题干。
    分割点是 **An** 那一行本身，不是题干的第一行。
    （曾经的 bug：把 A 标记之前的行都当成答案，于是选项和引用被翻到了卡背。）
    """
    items, cur, in_answer = [], None, False

    def clean(s):
        return re.sub(r"^>\s*", "", s).strip()

    for raw in md.splitlines():
        line = raw.strip()
        mq = re.match(r"^\*\*Q(\d+)\s*(?:[（(]([^）)]*)[）)])?\*\*\s*[：:]?\s*(.*)$", line)
        if mq:
            if cur:
                items.append(cur)
            cur = {"no": mq.group(1), "kind": (mq.group(2) or "").strip(),
                   "q": [clean(mq.group(3))], "a": []}
            in_answer = False
            continue
        if cur is None:
            continue
        ma = re.match(r"^\*\*A\d+\*\*\s*[：:]?\s*(.*)$", line)
        if ma:
            in_answer = True
            cur["a"].append(clean(ma.group(1)))
            continue
        if not line:
            continue
        (cur["a"] if in_answer else cur["q"]).append(clean(line))
    if cur:
        items.append(cur)
    for it in items:
        it["q"] = "\n".join(x for x in it["q"] if x).strip()
        it["a"] = "\n".join(x for x in it["a"] if x).strip()
    return [it for it in items if it["q"] and it["a"]]


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
        keywords = ('\n    <ul class="mv-kw" style="margin-top:1.25rem">%s</ul>\n'
                    '    <p class="mv-note">卡住时靠这几个词重建整条链。</p>\n'
                    % "".join("<li>%s</li>" % inline(k) for k in t["keywords"]))

    panels = []
    # 完整回答排第一：这是现在唯一能照着讲的一段话，比骨架更该先看到。
    # 字数与秒数都按构建时实测算，标清楚是估算，不写死「60 秒」。
    if t["answer"]:
        panels.append(answer_panel(t["answer"], t["points"]))
    # 方言差异排第一：卡里标的是「面试安全底线」，最容易说反的一段，
    # 2026-09-13 审查发现原先根本没被解析成字段、47 张卡全丢在 md 里没上页面。
    if t["contrast"]:
        panels.append('<collapse-panel title="方言差异（面试安全底线）">'
                      '<p class="mv-md-p">%s</p></collapse-panel>' % inline(t["contrast"]))
    if t["followups"]:
        items = ""
        for i, (fq, fa) in enumerate(t["followups"], 1):
            items += ('<p class="mv-md-p"><strong>%d. %s</strong></p>\n<p class="mv-md-p">%s</p>\n'
                      % (i, inline(fq),
                         inline(fa) if fa else '<span class="mv-topic-meta">答案见正文底稿</span>'))
        panels.append('<collapse-panel title="追问（先说后看）">%s</collapse-panel>' % items)
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
        expand = ('\n  <div class="mv-section" id="s-extra">\n'
                  '    <h2 class="mv-section-title">展开（先自答，再看 · 默认收起，不进复训调度）</h2>\n'
                  "    " + "\n    ".join(panels) + "\n  </div>\n")

    body = ""
    if t["body_html"]:
        body = ('\n  <div class="mv-section">\n    <h2 class="mv-section-title">讲解</h2>\n'
                '    <collapse-panel title="展开推导 / 代码 / 原始素材">\n%s\n    </collapse-panel>\n  </div>\n'
                % t["body_html"])

    bits = []
    if t["related"]:
        bits.append("关联 %s" % t["related"])
    bits.append("正本 %s" % t["src"])
    meta = esc(" ｜ ".join(bits)).replace("[[", "").replace("]]", "")

    imp = ('<p class="mv-note" style="margin-top:10px">为什么重要：%s</p>' % inline(t["importance"])
           if t["importance"] else "")

    mi = TOPIC_MODULE_INDEX.get(t["module"])
    module_back = ('<a class="mv-back mv-back-2" href="../modules/%s.html">← %s 模块概览</a>'
                   % (esc(safe_fname(mi)), esc(t["module"]))) if mi else ""

    # 交互版（archify 产出的自包含 HTML，放在 site/interactive/）——frontmatter: interactive: xxx.html
    # 自带前导换行，空值时就什么也不留（否则每张卡都会多一行空白）
    inter = ('\n  <a class="mv-back mv-back-2" href="../interactive/%s">交互版 →</a>'
             % esc(t["interactive"])) if t.get("interactive") else ""

    problem = ""
    if t["problem"]:
        problem = ('\n  <div class="mv-section" id="s-problem">\n    <h2 class="mv-section-title">题目</h2>\n'
                   '    <div class="mv-problem">%s</div>\n  </div>\n' % md_to_html(t["problem"]))

    guide = ('<p class="mv-guide">%s</p>' % inline(t["guide"])) if t.get("guide") else ""

    lesson = ""
    if t.get("lesson_html"):
        lesson = ('<div class="mv-section" id="s-lesson">'
                  '<h2 class="mv-section-title">一 · 教材 '
                  '<span class="mv-topic-meta">从前提推到结论，不需要先会</span></h2>'
                  '<div class="mv-lesson">%s</div></div>' % t["lesson_html"])

    quiz = ""
    if t.get("quiz"):
        _cards = ""
        for it in t["quiz"]:
            _cards += ('<div class="mv-qitem"><div class="mv-qhead">'
                       '<span class="mv-qid">Q%s</span>'
                       '<span class="mv-chip ghost">%s</span></div>'
                       '<flip-card card-id="%s-q%s" tag="%s" q="%s" a="%s"></flip-card></div>'
                       % (esc(it["no"]), esc(it["kind"] or "自测"),
                          attrs(t["key"]), attrs(it["no"]), esc(t["module"]),
                          attrs(card_text(it["q"])), attrs(card_text(it["a"]))))
        quiz = ('<div class="mv-section" id="s-quiz">'
                '<h2 class="mv-section-title">二 · 自测 '
                '<span class="mv-topic-meta">先自己想，再翻面看答案 · 做错说明没懂</span></h2>'
                '%s</div>' % _cards)

    out = PAGE
    for k, v in (
        ("%%GUIDE%%", guide),
        ("%%LESSON%%", lesson),
        ("%%QUIZ%%", quiz),
        ("%%PROBLEM%%", problem),
        ("%%TITLE%%", esc(t["title"])),
        ("%%MODULE%%", esc(t["module"])),
        ("%%META%%", meta),
        ("%%KEY%%", attrs(t["key"])),
        ("%%Q%%", attrs(plain(t["question"]))),
        ("%%A%%", attrs(plain(t["conclusion"]))),
        ("%%CONCLUSION%%", inline(t["conclusion"])),
        ("%%IMPORTANCE%%", imp),
        ("%%FIGURES%%", figures),
        ("%%KEYWORDS%%", keywords),
        ("%%EXPAND%%", expand),
        ("%%BODY%%", body),
        ("%%MODULE_BACK%%", module_back),
        ("%%INTERACTIVE%%", inter),
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


def section_by_title(body, title):
    """按二级标题里的关键词取一节。

    用标题找而不是硬编码「第 N 节」——章节顺序调整时不会静默取空。
    """
    m = re.search(r"^##\s*[^\n]*%s[^\n]*$\n(.*?)(?=^##\s|\Z)"
                  % re.escape(title), body, re.S | re.M)
    return m.group(1) if m else ""


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

    panels, heat_groups, weak_all = [], [], []
    for rnd, mod in gorder:
        arr = groups[(rnd, mod)]
        scored = [x for x in arr if x["total"] is not None]
        avg = (sum(x["total"] for x in scored) / len(scored)) if scored else 0
        heat_groups.append(("%s · %s" % (rnd, mod_label(mod)), arr, avg))
        weak_all.extend(scored)

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
            answer_panel = ('<collapse-panel title="标准答案 / 口述稿（先自己答，再看）">%s</collapse-panel>'
                            % abody)
            inner += (
                '<div class="mv-qitem" id="q-%s">'
                '<div class="mv-qhead"><span class="mv-qid">%s</span>'
                '<span class="mv-qtime">%s</span>%s</div>'
                '<div class="mv-qtext">%s</div>'
                '%s'
                '</div>'
                % (esc(it["id"]), esc(it["id"]), esc(it["time"]), chips,
                   inline(it["q"]), answer_panel)
            )
        panels.append('<collapse-panel title="%s · %s · 平均 %.1f（%d 题）" open>%s</collapse-panel>'
                      % (esc(rnd), esc(mod), avg, len(arr), inner))

    # 低分题 Top：总分 ≤12 的题按分升序取前 5，前置到最显眼的位置
    weak = sorted([x for x in weak_all if x["total"] <= 12], key=lambda x: x["total"])[:5]
    weak_html = ""
    if weak:
        rows = ""
        for it in weak:
            rows += ('<a class="mv-weak-row" href="#q-%s">'
                     '<span class="mv-qid">%s</span>'
                     '<span class="mv-chip">%g/25</span>'
                     '<span class="mv-weak-q">%s</span>'
                     '<span class="mv-chip warn">%s</span>'
                     '<span class="mv-weak-go">跳到该题 →</span></a>'
                     % (esc(it["id"]), esc(it["id"]), it["total"],
                        esc(it["q"]), esc(it["cause"] or "—")))
        weak_html = ('\n  <div class="mv-section">\n'
                     '    <h2 class="mv-section-title">先改这些 · 低分题 Top <span class="mv-topic-meta">点题号跳到对应题的答案</span></h2>\n'
                     '    %s\n  </div>\n' % rows)

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
        ("%%WEAK%%", weak_html),
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
%%WEAK%%
  <div class="mv-section">
    <h2 class="mv-section-title">分数分布 <span class="mv-topic-meta">共 %%TOTAL%% 题 · 颜色越深分越高 · 悬停看题号与归因</span></h2>
    <figure-box num="1" title="各模块逐题得分与平均分（满分 25）">%%HEAT%%</figure-box>
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title">逐题（按模块）<span class="mv-topic-meta">题干直接可见 · 答案先自答再展开</span></h2>
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
    for cells in parse_md_table(section_by_title(body, "主线拆解").splitlines()):
        if len(cells) < 3 or not re.fullmatch(r"[一二三四五六七八九十]+", cells[0].strip()):
            continue
        lines_.append({
            "no": cells[0].strip(), "name": cells[1].strip(),
            "tradeoff": cells[2].strip(),
            "count": cells[3].strip() if len(cells) > 3 else "",
        })

    topics = []
    for cells in parse_md_table(section_by_title(body, "母题清单").splitlines()):
        if len(cells) < 4 or not re.fullmatch(r"[A-Z]\d+", cells[0].strip()):
            continue
        topics.append({"id": cells[0].strip(), "name": cells[1].strip(),
                       "line": cells[2].strip(), "status": cells[3].strip()})

    questions = []
    for cells in parse_md_table(section_by_title(body, "题单").splitlines()):
        if len(cells) < 4 or not re.fullmatch(r"\d+", cells[0].strip()):
            continue
        # 列：# ｜ 题目 ｜ 归属主线 ｜ [母题] ｜ 优先级 ｜ 状态 ｜ 首验
        if len(cells) >= 7:
            topic, pri = cells[3].strip(), cells[4].strip()
        else:
            topic, pri = "", cells[3].strip()
        questions.append({"no": cells[0].strip(), "q": cells[1].strip(),
                          "line": cells[2].strip(), "topic": topic, "pri": pri})

    bridge = []
    for cells in parse_md_table(section_by_title(body, "方言桥").splitlines()):
        if len(cells) < 4 or "面试官问的" in cells[0]:
            continue
        bridge.append(cells[:4])

    gate = [re.sub(r"^\s*-\s*\[[ xX]\]\s*", "", ln).strip()
            for ln in section_by_title(body, "验收门").splitlines()
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
        # 2026-09-26：「题级答案」——题单是题面，答案要能直接说出口。
        # 原来翻转卡背面是用 q_answer() 从母题凑的（结论 + 骨架），97% 的题与同母题其它题共用一段话。
        "qanswers": parse_qanswers(body),
        "projects": parse_projects(body),
        "bridge": bridge,
        "gate": gate,
        "cards": cards,
        "page": "modules/%s.html" % safe_fname(module),
    }


CN_INDEX = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

# 运行时登记（main 里填充）：母题 key -> 母题页路径；模块名 -> 模块概览页
TOPIC_PAGES = {}
TOPIC_MODULE_INDEX = {}


def safe_fname(s):
    r"""文件名清洗：Windows 禁止 < > : " / \ | ? *，且不能以空格或点结尾。

    2026-09-13 新增：模块卡的主线名会进文件名，一个 ASCII 双引号就让 write_text
    抛 OSError、整个 build 静默中断（后面的主线页全不生成，模块页里留下死链）。
    """
    s = re.sub(r'[<>:"/\\|?*]', "", s).strip().rstrip(".")
    return s or "untitled"


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
    return "modules/%s-%02d-%s.html" % (
        safe_fname(md["module"]), idx,
        safe_fname(line_short(
            next((l["name"] for l in md["lines"] if l["no"] == no), no))))


def module_line_file(md, no):
    """主线页文件名——模块页之间是同目录引用，不能再带 modules/ 前缀"""
    return module_line_page(md, no).split("/")[-1]


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
    # 2026-09-25：状态机退场——「能不能练」不再由 md 的 status 决定。
    # 全库 87 张母题卡全是 candidate（AI 产出上限），按 integrated 过滤的结果是
    # 复训牌组里只剩 9 张算法卡。新判据：这张卡有没有可供复述的骨架——
    # 讲没讲过由进度页的本机数据说话，不由 md 的 status 说话。
    return ("live" if (tc.get("skeleton") or tc.get("conclusion")) else "draft"), tc


def parse_qanswers(body):
    """第 8 节「题级答案」→ {题号: 答案文字}。

    格式：`### <题号> （必背|理解|了解）` 后面跟正文，直到下一个 ### 或 ##。
    """
    sec = section_by_title(body, "题级答案")
    if not sec:
        return {}
    out = {}
    for m in re.finditer(r"^###\s*(\d+)\b[^\n]*\n([\s\S]*?)(?=^###\s|^##\s|\Z)",
                         sec, re.M):
        txt = m.group(2).strip()
        if txt:
            out[m.group(1)] = txt
    return out


def q_answer(md, topic_field, no=None):
    """题卡背面。

    2026-09-26：优先用「题级答案」（md 第 8 节）。原来只有从母题凑的
    「【母题号】一句话结论 + 展开：骨架」——题比母题细（平均 3.7 题共用一张母题），
    97% 的题翻出来是跟别的题同一段话，而且骨架是记忆路线图、不是能说出口的答案。
    还没写题级答案的模块退回母题口径，但把「这是顶上的」写清楚，别假装是答案。
    """
    qa = (md.get("qanswers") or {}).get(str(no)) if no is not None else None
    if qa:
        return qa
    ids = re.findall(r"[A-Z]\d+", topic_field or "")
    if not ids:
        return ("这道题目前没有母题覆盖。\n\n"
                "这正是「覆盖度校验」要暴露的：要么给它补一个母题，"
                "要么明确降级为「了解」并写下理由。")
    parts = ["【这道题还没写题级答案 · 下面是用母题结论顶上的】"]
    for i in ids:
        st, tc = _topic_state(md, i)
        if not tc:
            parts.append("【%s】讲解待提炼 —— 先回主线区把这道母题补上。" % i)
            continue
        parts.append("【%s】%s" % (i, plain(tc["conclusion"])))
        detail = tc["skeleton"] or tc["invariant"]
        if detail:
            parts.append("展开：%s" % plain(detail))
        if st != "live":
            parts.append("（这道母题还是草稿，尚未通过验收）")
    return "\n\n".join(parts)


def q_more(md, tid):
    """翻转卡背面下半段：所属母题的完整回答（折叠）+ 单卡入口。

    这一段是「深挖」，不替代题级答案——题级答案在上半段。
    """
    ids = re.findall(r"[A-Z]\d+", tid or "")
    if not ids:
        return ''
    out = []
    for i in ids:
        _st, tc = _topic_state(md, i)
        src_mod, cross = md["module"], False
        if not tc:
            # 跨模块引用：题单里挂的是别的模块的母题（如 Redis Q19 → 并发与锁 L3）
            gp = TOPIC_CARD_BY_ID.get(i.upper())
            if gp:
                tc, src_mod, cross = parse_topic(gp), gp.parent.name, True
        if not tc:
            continue
        nm = next((t["name"] for t in md["topics"] if t["id"] == i), "")
        if not nm and tc.get("title"):
            nm = re.sub(r"^母题\s*\S+\s*·\s*", "", tc["title"])
        head = ('<p class="mv-fc-sub">这道题属于母题 %s%s%s · 下面挂它的完整回答（学的时候看）</p>'
                % (esc(i), ("（%s 模块）" % esc(src_mod)) if cross else "",
                   (" · " + esc(plain(nm))) if nm else ""))
        if tc.get("answer"):
            body = answer_panel(tc["answer"], tc["points"])
        else:
            body = ('<p class="mv-md-p"><strong>一句话结论</strong>：%s</p>'
                    % inline(tc["conclusion"]))
        cp = md["cards"].get(i) or TOPIC_CARD_BY_ID.get(i.upper())
        pg = TOPIC_PAGES.get("%s/%s" % (src_mod, cp.stem)) if cp else ""
        link = ('<p class="mv-md-p"><a class="mv-mt-link" href="../%s">'
                '打开单卡 %s →</a></p>' % (esc(pg), esc(i))) if pg else ''
        out.append(head + body + link)
    return '<div class="mv-fc-more">%s</div>' % "".join(out) if out else ''


def parse_projects(body):
    """第 5 节项目映射：每个 ### 小标题一块，收集「锚点」与项目符号条目"""
    sec = section_by_title(body, "项目映射")
    blocks, cur, item = [], None, None
    for raw in sec.splitlines():
        ln = raw.rstrip()
        m = re.match(r"^###\s*(.+)$", ln.strip())
        if m:
            name = re.sub(r"^\d+(\.\d+)*\s*", "", m.group(1)).strip()
            cur = {"name": name, "anchor": "", "items": []}
            blocks.append(cur)
            item = None
            continue
        if cur is None:
            continue
        t = ln.strip()
        if not t or t.startswith(">"):
            continue
        m3 = re.match(r"^\*\*锚点\*\*[：:]\s*(.*)$", t)
        if m3:
            cur["anchor"] = m3.group(1).strip()
            item = None
            continue
        m2 = re.match(r"^[-*]\s+\*\*(.+?)\*\*[：:]\s*(.*)$", t)
        if m2:
            item = {"label": m2.group(1).strip(), "text": m2.group(2).strip()}
            cur["items"].append(item)
            continue
        if item is not None:      # 续行（含代码块）
            item["text"] = "\n".join(
                x.strip() for x in (item["text"] + "\n" + ln).splitlines())
    return [b for b in blocks if b["items"] or b["anchor"]]


def render_projects(md):
    blocks = md.get("projects") or []
    if not blocks:
        return '<p class="mv-note">正本第 5 节还没有填项目映射。</p>'
    out = []
    for b in blocks:
        inner = ""
        if b["anchor"]:
            inner += '<p class="mv-pj-anchor">锚点：%s</p>' % inline(b["anchor"])
        for it in b["items"]:
            inner += ('<div class="mv-pj-item"><b>%s</b>%s</div>'
                      % (esc(it["label"]), md_to_html(it["text"])))
        out.append('<collapse-panel title="%s">%s</collapse-panel>'
                   % (esc(b["name"]), inner))
    return "".join(out)


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
            % (esc(module_line_file(md, ln["no"])), esc(ln["no"]),
               esc(line_short(ln["name"])), esc(line_question(ln["name"])),
               len(arr), len(qs), pct)
        )

    # 总纲题：不属于任何一条主线，放在概览页（2026-09-27）
    gen = orphan_questions(md)
    gsec = ""
    if gen:
        gsec = ('<div class="mv-section">'
                '<h2 class="mv-section-title">本模块的题 · 总纲 '
                '<span class="mv-topic-meta">%d 道 · 不属于某一条主线，先说后翻</span></h2>'
                '%s</div>' % (len(gen), "".join(q_card(md, q) for q in gen)))

    out = MODULE_INDEX_PAGE
    for k, v in (
        ("%%GENERAL%%", gsec),
        ("%%TITLE%%", esc(md["title"])),
        ("%%MODULE%%", esc(md["module"])),
        ("%%SUMMARY%%", esc(md["summary"]) if md["summary"]
            else '<span class="mv-topic-meta">一句话结论待填（闭卷后自己写 20 秒版）</span>'),
        ("%%REASON%%", inline(md["reason"])),
        ("%%INCLUDE%%", inline(md["include"])),
        ("%%EXCLUDE%%", inline(md["exclude"])),
        ("%%NLINE%%", str(len(md["lines"]))),
        ("%%NTOPIC%%", str(len(md["topics"]))),
        ("%%NQ%%", str(n_q)),
        ("%%NMUST%%", str(n_must)),
        ("%%NLIVE%%", str(n_live)),
        ("%%NDRAFT%%", str(n_draft)),
        ("%%ROWS%%", rows or '<p class="mv-note">还没有主线。</p>'),
        ("%%PROJECTS%%", render_projects(md)),
        ("%%SRC%%", esc(md["key"])),
    ):
        out = out.replace(k, v)
    return out


TOPIC_CARD_BY_ID = {}          # 母题 id -> path（跨模块兜底，2026-09-27）


def index_topic_cards():
    """全库母题卡按 id 建索引。

    题单里会引用别的模块的母题（Redis Q19 → [[母题-L3-分布式锁与fencing-token]]），
    模块内查不到就查全局。全库母题 id 无重名（审查已确认），所以这张表是安全的。
    """
    for p in sorted((ROOT / "wiki" / "topics").glob("*/母题-*.md")):
        m = re.match(r"母题-([A-Za-z]?\d+)", p.stem)
        if m:
            TOPIC_CARD_BY_ID.setdefault(m.group(1).upper(), p)


def orphan_questions(md):
    """归属主线不是行号的题（md 里写的是「全」「前提」「——」）。

    _by_line 按行号分组，这些题归不到任何主线页，2026-09-27 审查发现
    它们一直没露面——而恰好都是总纲题（如何评测一个 Agent、设计一个生产级 RAG…）。
    放在模块概览页，别让它们继续消失。
    """
    nos = {ln["no"] for ln in md["lines"]}
    return [q for q in md["questions"] if q["line"] not in nos]


def q_card(md, q):
    """一道题 = 一张翻转卡：正面题面，背面题级答案 + 所属母题的完整回答。"""
    tid = q.get("topic") or ""
    chip = ('<span class="mv-chip ghost">%s</span>' % esc(q["pri"])) if q["pri"] else ""
    if tid:
        chip += '<span class="mv-chip ghost">%s</span>' % esc(tid)
    return ('<div class="mv-qitem"><div class="mv-qhead">'
            '<span class="mv-qid">%s</span>%s'
            '<button class="mv-qdone" data-k="%s-q%s" type="button">未掌握</button>'
            "</div>"
            '<flip-card card-id="%s-q%s" tag="%s" q="%s" a="%s">%s</flip-card></div>'
            % (esc(q["no"]), chip, esc(md["module"]), esc(q["no"]),
               attrs(md["module"]), attrs(q["no"]), attrs(md["module"]),
               attrs(plain(q["q"])), attrs(q_answer(md, tid, q["no"])),
               q_more(md, tid)))


def render_module_line(md, ln, prev_ln, next_ln):
    """主线页：先出题 → 自己答 → 展开对照 → 记断点；本主线的题在页内"""
    tbl, qbl = _by_line(md["topics"]), _by_line(md["questions"])
    arr, qs = tbl.get(ln["no"], []), qbl.get(ln["no"], [])

    blocks = ""
    for t in arr:
        st, tc = _topic_state(md, t["id"])
        # 状态机退场：不再显示「已掌握 / 草稿待验收」——那是 md 的状态，
        # 不是你练没练过。这里只提示「这张卡能不能讲」。
        chip = {"live": '',
                "draft": '<span class="mv-chip warn">缺骨架</span>'}.get(
                    st, '<span class="mv-chip ghost">未提炼</span>')
        cp = md["cards"].get(t["id"])
        cpage = TOPIC_PAGES.get("%s/%s" % (md["module"], cp.stem)) if cp else ""
        card_link = ('<a class="mv-mt-link" href="../%s">单卡 →</a>' % esc(cpage)) if cpage else ""
        head = ('<div class="mv-mt-head"><span class="mv-mt-id">%s</span>'
                '<span class="mv-mt-name">%s</span>%s%s</div>'
                % (esc(t["id"]), esc(plain(t["name"])), chip, card_link))

        if not tc:
            ctx = ('<p class="mv-mt-empty">讲解待提炼。这道母题将覆盖的题：</p>'
                   '<ul class="mv-md-ul">%s</ul>'
                   % "".join("<li>%s</li>" % inline(q["q"]) for q in qs[:4]))
            blocks += '<div class="mv-mt">%s%s</div>' % (head, ctx)
            continue

        # 2026-09-13：原来这里再摆一次题目，但卡片头的 mv-mt-name 已经是同一句话
        #（例："默认 RC 还是 RR？…" vs "PG 默认是 RC 还是 RR？…?"），纯重复。
        # 头部那份才是可扫的索引，删掉这个灰框，每张卡省 ~44px。
        ctx = ""
        if tc["problem"]:
            ctx += '<collapse-panel title="题目背景">%s</collapse-panel>' % md_to_html(tc["problem"])

        ref = ['<p class="mv-md-p"><strong>一句话结论</strong>：%s</p>' % inline(tc["conclusion"])]
        if tc["keywords"]:
            ref.append('<ul class="mv-kw">%s</ul>' % "".join("<li>%s</li>" % inline(k)
                                                             for k in tc["keywords"]))
        if tc["invariant"]:
            ref.append('<p class="mv-md-p"><strong>主线</strong>：%s</p>' % inline(tc["invariant"]))
        if tc["body_html"]:
            ref.append(tc["body_html"])
        for i, f in enumerate(tc["figures"], 1):
            ref.append('<figure-box num="%s-%d" title="%s" note="%s">%s</figure-box>'
                       % (t["id"], i, attrs(f["title"]), attrs(f["note"]),
                          prefix_svg_ids(f["svg"], "m%s%d" % (t["id"], i))))
        # 完整答案排在对照讲解前面：学的时候先看这一段，再展开推导
        if tc["answer"]:
            ctx += answer_panel(tc["answer"], tc["points"])
        ctx += ('<collapse-panel title="对照讲解（先答完再看）">%s</collapse-panel>'
                % "".join(ref))

        if tc["followups"]:
            items = "".join(
                '<p class="mv-md-p"><strong>%d. %s</strong></p><p class="mv-md-p">%s</p>'
                % (i, inline(fq), inline(fa) or '<span class="mv-topic-meta">见讲解</span>')
                for i, (fq, fa) in enumerate(tc["followups"], 1))
            ctx += '<collapse-panel title="追问（先说后看）">%s</collapse-panel>' % items

        ctx += '<p class="mv-note">正本：%s</p>' % esc(tc["src"])

        blocks += '<div class="mv-mt">%s%s</div>' % (head, ctx)

    # 2026-09-25 新增：主线骨架节（复述用）。学的时候读「对照讲解」，
    # 讲的时候只看这一节——凭记忆按骨架讲，讲完再展开核对。
    skel, n_sk = "", 0
    for t in arr:
        st, tc = _topic_state(md, t["id"])
        head = ('<div class="mv-mt-head"><span class="mv-mt-id">%s</span>'
                '<span class="mv-mt-name">%s</span></div>'
                % (esc(t["id"]), esc(plain(t["name"]))))
        if not tc:
            skel += ('<div class="mv-mt">%s<p class="mv-mt-empty">讲解待提炼。</p></div>' % head)
            continue
        body = tc["skeleton"] or tc["invariant"] or ""
        inner = ""
        if body:
            n_sk += 1
            inner += '<p class="mv-md-p"><strong>骨架</strong>：%s</p>' % inline(body)
        else:
            inner += '<p class="mv-note">这张卡还没写「完整回答骨架」，先补正本。</p>'
        if tc["conclusion"]:
            inner += ('<p class="mv-md-p"><strong>一句话结论</strong>：%s</p>'
                      % inline(tc["conclusion"]))
        if tc["keywords"]:
            inner += ('<ul class="mv-kw">%s</ul>'
                      % "".join("<li>%s</li>" % inline(k) for k in tc["keywords"]))
        # 完整答案折叠在主线骨架旁边：讲完再展开对，不提前看答案
        ans = answer_panel(tc["answer"], tc["points"]) if tc["answer"] else (
            '<p class="mv-note">这张卡还没写「完整回答（口述稿）」，先补正本。</p>')
        skel += ('<div class="mv-mt">%s<collapse-panel title="讲完再对：骨架 · 结论 · 关键词">'
                 '%s</collapse-panel>%s</div>' % (head, inner, ans))

    drill = ""
    for q in qs:
        tid = q.get("topic") or ""
        chip = ('<span class="mv-chip ghost">%s</span>' % esc(q["pri"])) if q["pri"] else ""
        if tid:
            chip += '<span class="mv-chip ghost">%s</span>' % esc(tid)
        drill += q_card(md, q)
    if not drill:
        drill = '<p class="mv-note">这条主线还没有挂题。</p>'

    nav = '<a class="mv-line-nav" href="../index.html">训练台</a>'
    if prev_ln:
        nav += '<a class="mv-line-nav" href="%s">← %s · %s</a>' % (
            esc(module_line_file(md, prev_ln["no"])), esc(prev_ln["no"]),
            esc(line_short(prev_ln["name"])))
    if next_ln:
        nav += '<a class="mv-line-nav next" href="%s">%s · %s →</a>' % (
            esc(module_line_file(md, next_ln["no"])), esc(next_ln["no"]),
            esc(line_short(next_ln["name"])))

    out = MODULE_LINE_PAGE
    for k, v in (
        ("%%TITLE%%", esc(line_short(ln["name"]))),
        ("%%MODULE%%", esc(md["module"])),
        ("%%INDEX%%", esc("%s.html" % md["module"])),
        ("%%NO%%", esc(ln["no"])),
        ("%%LEAD%%", inline(line_question(ln["name"])) or "—"),
        ("%%TRADEOFF%%", inline(ln["tradeoff"]) if ln["tradeoff"] else ""),
        ("%%BLOCKS%%", blocks or '<p class="mv-note">这条主线还没有母题。</p>'),
        ("%%SKEL%%", skel or '<p class="mv-note">这条主线还没有母题。</p>'),
        ("%%NSK%%", str(n_sk)),
        ("%%NT%%", str(len(arr))),
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
    <span class="mv-stat-i ok"><b>%%NLIVE%%</b> 可讲</span>
    <span class="mv-stat-i warn"><b>%%NDRAFT%%</b> 缺骨架</span>
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

  %%GENERAL%%

  <div class="mv-section">
    <h2 class="mv-section-title">项目映射 <span class="mv-topic-meta">把这个模块挂到真实经历上</span></h2>
    %%PROJECTS%%
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

  <p class="mv-note" style="margin-bottom:22px">
    用法两段：<strong>先学</strong>——展开下面每个母题的「对照讲解」，把这条主线的教材读完；
    <strong>再讲</strong>——回到上面「本主线骨架」，凭记忆按骨架讲一遍，讲完再展开核对。
    讲得出 = 这条主线过关，进 1/3/7/14 天复训；卡壳 = 记断点、明天重讲；讲不出 = 回教材重读。
  </p>

  <div class="mv-section">
    <h2 class="mv-section-title">本主线骨架 <span class="mv-topic-meta">%%NSK%% / %%NT%% 张有骨架 · 凭记忆讲，讲完再对</span></h2>
    <p class="mv-note" style="margin-bottom:14px">
      一条主线一次过：按母题顺序，<strong>先不看内容讲一遍</strong> → 卡住时用「恢复关键词」接上 →
      讲完展开核对，漏掉的就是明天的断点。
    </p>
    %%SKEL%%
  </div>

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
document.querySelectorAll('.mv-qdone').forEach(function (b) {
  var k = 'mv.done.' + b.getAttribute('data-k');
  function paint() {
    var on = false;
    try { on = localStorage.getItem(k) === '1'; } catch (e) {}
    b.classList.toggle('on', on);
    b.textContent = on ? '已掌握' : '未掌握';
  }
  b.addEventListener('click', function (e) {
    e.preventDefault();
    try { localStorage.setItem(k, localStorage.getItem(k) === '1' ? '0' : '1'); } catch (e) {}
    paint();
  });
  paint();
});
</script>
</body>
</html>
"""



# ---------------------------------------------------------------- main

DIRTY_ATTR = re.compile(r'\s+data-page-[a-z-]+="[^"]*"')


PROJECT_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%%NAME%% · 项目口述</title>
<link rel="stylesheet" href="../_components/marvis.css">
</head>
<body class="mv-page">
<div class="mv-wrap">
  <a class="mv-back" href="../index.html">← 今日</a>

  <div class="mv-topic-head">
    <span class="mv-topic-module">项目口述 · 90 秒骨架 → 决策链</span>
    <h1 class="mv-topic-title">%%NAME%%</h1>
    <p class="mv-topic-meta">%%LEAD%%</p>
  </div>

  <p class="mv-note" style="margin-bottom:22px">
    <strong>先讲</strong>——不看内容，按 90 秒把项目讲一遍；<strong>再对</strong>——展开下面每一块逐个核对，
    漏掉的那句就是今天的断点。<br>
    决策链同理：<strong>先看问题自己答</strong>，再展开标答比对自己漏了哪一层。<br>
    正本在 md（<a href="%%OBS%%">用 Obsidian 打开</a>），本页是它的对照视图，内容由构建脚本抽取、不做改写。
  </p>

  <div class="mv-section">
    <h2 class="mv-section-title" id="skel">90 秒骨架 <span class="mv-topic-meta">%%NSKEL%% 块 · 先讲再对</span></h2>
    <p class="mv-note" style="margin-bottom:14px">
      三档长度各有用处：<b>20 秒</b>用在「简单介绍一下项目」；<b>90 秒</b>是主场开场；
      <b>5 分钟</b>是被追到系统层面时展开的骨架。练习的单位是这整块，不是里头的某一句。
    </p>
    %%SKEL%%
  </div>

  <div class="mv-section">
    <h2 class="mv-section-title" id="chain">决策链 <span class="mv-topic-meta">%%NCHAIN%% 问 · 先看题自答，再展开标答</span></h2>
    <p class="mv-note" style="margin-bottom:14px">
      骨架过关后才走这一节：每一问先闭卷答，答不出来的就是下次复训要带的断点。
    </p>
    %%CHAIN%%
  </div>
</div>
<script src="../_components/marvis.js"></script>
</body>
</html>
"""

# 项目口述：三个项目的口述稿分散在不同 md 里，这里只声明「从哪份正本的哪一节抽」，
# 抽取键一律用二级标题里的关键词（顺序调整不会静默取空），正文不在这里维护。
PROJECT_PITCH = [
    {
        "id": "energyops", "name": "EnergyOps",
        "lead": "园区能耗智能运营平台：把脏的累计读数做成可查询、可结算的业务事实，再让 Agent 安全地操作真实系统",
        "src": "EnergyOps/EnergyOps-快速学习掌握与面试实战.md",
        "skel": "三版项目表达", "chain": "最高频面试题与短答",
    },
    {
        "id": "shuyu", "name": "数驭穹图",
        "lead": "NL2BI：自然语言到可信业务结论，每一步都留证据",
        "src": "数驭穹图/16-项目表达与面试题库.md",
        "skel": "三层项目介绍", "chain": "高频问题与回答主线",
    },
    {
        "id": "rulearena", "name": "RuleArena",
        "lead": "规则资损对抗验证：干净重放 + 独立 Oracle，证明 Agent 没把钱搞错",
        "src": "RuleArena/01-project-mainline.md",
        "skel": "90 秒回答骨架", "chain": "高频问题与标答",
    },
]


def split_h3(md):
    """按三级标题切成 [(标题, 正文)]；没有三级标题就整段一块。"""
    parts = re.split(r"^###\s+(.*?)\s*$", md, flags=re.M)
    if len(parts) == 1:
        return [("", md.strip())]
    out = []
    head = parts[0].strip()
    if head:
        out.append(("", head))
    for i in range(1, len(parts), 2):
        out.append((parts[i].strip(), parts[i + 1].strip()))
    return out


def pitch_panels(md):
    """一块一折叠：标题看得见、内容收起来，讲完 / 答完才展开核对。"""
    blocks = split_h3(md)
    # 整节没有三级标题时（RuleArena 的骨架节就是「关键词 + 标答」一整段），
    # 按 md 自己的建议处理：关键词留在外面照着讲，标答折起来讲完再对。
    if len(blocks) == 1 and not blocks[0][0]:
        body = blocks[0][1]
        m = re.search(r"^标答[：:]", body, re.M)
        if m:
            head, tail = body[:m.start()].strip(), body[m.start():].strip()
            return (md_to_html(head) + "\n"
                    + '<collapse-panel title="标答（讲完再对）">'
                    + md_to_html(tail) + "</collapse-panel>")
        return ('<collapse-panel title="口述稿（先讲，讲完再对）">'
                + md_to_html(body) + "</collapse-panel>")
    out = []
    for title, body in blocks:
        html = md_to_html(body)
        if title:
            out.append('<collapse-panel title="%s">%s</collapse-panel>'
                       % (esc(title), html))
        else:
            out.append(html)
    return "\n".join(out)


def count_blocks(md):
    """面板计数：有三级标题数标题，整节一块（没有三级标题）也算 1。"""
    blocks = split_h3(md)
    n = len([1 for t, _ in blocks if t])
    if n == 0 and blocks and blocks[0][1].strip():
        n = 1
    return n


def render_project(p, body):
    skel = section_by_title(body, p["skel"])
    chain = section_by_title(body, p["chain"])
    if not skel.strip():
        print("  !! %s：没抽到骨架节「%s」——正本节名改了？" % (p["id"], p["skel"]))
    if not chain.strip():
        print("  !! %s：没抽到决策链节「%s」——正本节名改了？" % (p["id"], p["chain"]))
    n_skel = count_blocks(skel)
    n_chain = count_blocks(chain)
    obs = ("obsidian://open?vault=Marvis&file="
           + quote("projects/" + p["src"].replace(".md", "")))
    return (PROJECT_PAGE
            .replace("%%NAME%%", esc(p["name"]))
            .replace("%%LEAD%%", esc(p["lead"]))
            .replace("%%OBS%%", obs)
            .replace("%%NSKEL%%", str(n_skel))
            .replace("%%NCHAIN%%", str(n_chain))
            .replace("%%SKEL%%", pitch_panels(skel))
            .replace("%%CHAIN%%", pitch_panels(chain)))


def build_projects():
    """生成 site/projects/{id}.html：三个项目的口述对照页（正本仍是 md）。

    同时产出 _data/projects.js 给首页当入口——跟 modules.js 一个路子，
    页面清单不在首页写死，改名/增删不会两处失同步。
    """
    OUT_PROJECTS.mkdir(parents=True, exist_ok=True)
    pages = []
    for p in PROJECT_PITCH:
        path = ROOT / "projects" / p["src"]
        if not path.exists():
            print("  !! 找不到项目正本：%s" % path)
            continue
        body = split_front(path.read_text(encoding="utf-8"))[1]
        (OUT_PROJECTS / ("%s.html" % p["id"])).write_text(
            render_project(p, body), encoding="utf-8")
        pages.append({"id": p["id"], "name": p["name"], "lead": p["lead"],
                      "href": "projects/%s.html" % p["id"]})
    gone = prune_dir(OUT_PROJECTS, {"%s.html" % p["id"] for p in PROJECT_PITCH})
    if gone:
        print("  [清理陈旧页面] projects ×%d" % len(gone))
    (OUT_DATA / "projects.js").write_text(
        "window.MARVIS_PROJECTS = " + json.dumps(pages, ensure_ascii=False,
                                                 indent=2) + ";\n",
        encoding="utf-8")
    return [x["id"] for x in pages]


def prune_dir(d, expected):
    """删掉上一轮构建留下的陈旧页面（页面/主线改名或内容下线时产生）"""
    if not d.exists():
        return []
    gone = []
    for p in d.glob("*.html"):
        if p.name not in expected:
            p.unlink()
            gone.append(p.name)
    return gone


def cleanup_html():
    """清掉预览面板写回源文件的注入属性（否则会污染提交）

    site/interactive/ 是 archify 产出的自包含 HTML，属于「外部产物」不是本站生成的
    页面——它的 data-* 是它自己的运行时状态，扫过去改掉会静默改坏交互图。
    """
    n = 0
    for p in SITE.rglob("*.html"):
        if p.parent.name == "interactive":
            continue
        txt = p.read_text(encoding="utf-8")
        new = DIRTY_ATTR.sub("", txt)
        if new != txt:
            p.write_text(new, encoding="utf-8")
            n += 1
    return n


# ---------------------------------------------------------------- 面经手册 → 牌组

INTERVIEW_MANUAL = "wiki/interview/面经-字节AI-Agent.md"


def _subsec(sec, title):
    """取三级小节：### <title>... 到下一个 ### 之间"""
    m = re.search(r"^###\s*[^\n]*%s[^\n]*$\n(.*?)(?=^###\s|^##\s|\Z)"
                  % re.escape(title), sec, re.S | re.M)
    return m.group(1).strip() if m else ""


def card_text(md):
    """卡片背面用：去引用号/列表号/标题号；表格行折成「a · b」；不留 markdown 标记。

    注意列表号必须要求后跟空白（`[-*+]\\s+`）——写成字符类会把 `**加粗**` 的首个星号吃掉。
    """
    lines = []
    for ln in (md or "").splitlines():
        s = ln.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            cells = [c for c in cells if c and not re.fullmatch(r":?-{2,}:?", c)]
            if cells:
                lines.append(" · ".join(cells))
            continue
        s = re.sub(r"^>\s*", "", s)
        s = re.sub(r"^[-*+]\s+", "", s)
        s = re.sub(r"^#{1,6}\s*", "", s)
        lines.append(s)
    return plain("\n".join(lines)).strip()


def parse_interview_manual():
    """把面试手册拆成可练的牌组。

    来源格式：
      ## N. 母题 XX：<问题>  → 取「15 秒」「60 秒标准回答」做主卡
      ## 20. 三个项目的定向回答卡 → 取每个 ### 小节做项目口述卡
    小节缺失就跳过，不报错——不因为格式不全卡住整条流水线。
    """
    p = ROOT / INTERVIEW_MANUAL
    if not p.exists():
        return []
    body = split_front(p.read_text(encoding="utf-8"))[1]
    parts = re.split(r"^##\s+\d+\.\s+([^\n]+)$", body, flags=re.M)

    topics, projects = [], []
    for i in range(1, len(parts) - 1, 2):
        title, sec = parts[i].strip(), parts[i + 1]
        if "母题" in title and "：" in title:
            no, name = title.split("：", 1)
            num = re.search(r"\d+", no)
            long_ = _subsec(sec, "60 秒标准回答") or _subsec(sec, "60 秒版本")
            if not long_:
                continue
            short = _subsec(sec, "15 秒")
            back = card_text(long_)
            if short:
                back = card_text(short) + "\n\n" + back
            topics.append({
                "id": "ai-%s" % (num.group(0) if num else len(topics) + 1),
                "q": plain(name), "a": back, "tag": "AI/Agent",
                "src": INTERVIEW_MANUAL,
            })
        elif "项目" in title and "定向" in title:
            for m in re.finditer(r"^###\s+([^\n]+)$", sec, re.M):
                head = m.group(1).strip()
                if "：" not in head:
                    continue
                proj, variant = head.split("：", 1)
                proj = re.sub(r"^\d+(\.\d+)*\s*", "", proj).strip()
                chunk = sec[m.end():]
                nxt = re.search(r"^###\s", chunk, re.M)
                if nxt:
                    chunk = chunk[:nxt.start()]
                projects.append({
                    "id": "proj-%s" % proj.lower(),
                    "q": "讲一遍 %s（%s）" % (proj, variant.strip()),
                    "a": card_text(chunk), "tag": "项目口述",
                    "src": INTERVIEW_MANUAL,
                })

    decks = []
    if topics:
        decks.append({"id": "ai", "name": "AI 母题", "cards": topics})
    if projects:
        decks.append({"id": "project", "name": "项目口述", "cards": projects})
    return decks


# ── 读厚卡片层（2026-10-03）：wiki/cards/ 正本 → _data/cards.js + site/cards.html ────
# 两型卡（第二大脑重构，方案见 site/PLAN.md）：
#   原则卡（kind: principle）——书/准则的读厚产物，核心字段是「情境 → 标准动作」，
#     进派单簇 card/*（每日 1 条，由 progress.html 派）；掌握度存 mv.progress.v1。
#   地基包（kind: ground）——技术模块的先修资料，核心是「必会清单 + 学习路径」，
#     只做导航不进派单（模块本身的推进仍走主线）。
# 正本一文件一来源，这里只抽取不改写；卡片 id（adler-1 这种）发布后不改——派单等级挂在上面。
# 正文里的 [@模块-行号] 会替换成主线页链接（解析不到的保留原文，不丢内容）。

CARDS_DIR = ROOT / "wiki" / "cards"
BRAIN_CARD_SEC_RE = re.compile(r"^##\s+(card|ground)\s+([\w-]+)\s*·\s*(.+?)\s*$", re.M)
LINE_REF_RE = re.compile(r"\[@(.+?)-([一二三四五六七八九十\d]+)\]")


def _cn_line(no):
    """主线号统一成中文数字（模块卡主线表用 一二三…；卡片里写 1 2 3 也认）"""
    no = str(no).strip()
    if no in CN_INDEX:
        return no
    d = {"1": "一", "2": "二", "3": "三", "4": "四", "5": "五",
         "6": "六", "7": "七", "8": "八", "9": "九", "10": "十"}
    return d.get(no, no)


def parse_brain_cards_file(path):
    meta, body = split_front(path.read_text(encoding="utf-8"))
    kind = (meta.get("kind") or "").strip()
    if kind not in ("principle", "ground"):
        return None
    out = {
        "kind": kind,
        "source": (meta.get("source") or path.stem).strip(),
        "author": (meta.get("author") or "").strip(),
        "source_href": (meta.get("source_href") or "").strip(),
        "status": (meta.get("status") or "candidate").strip(),
        "human_reviewed": (meta.get("human_reviewed") or "").strip().lower() == "true",
        "module": (meta.get("module") or "").strip(),
        "src": path.relative_to(ROOT).as_posix(),
        "cards": [], "grounds": [],
    }
    parts = BRAIN_CARD_SEC_RE.split(body)
    for i in range(1, len(parts) - 3, 4):
        typ, cid, name, sec = parts[i], parts[i + 1], parts[i + 2].strip(), parts[i + 3]
        if typ == "card":
            out["cards"].append({
                "id": cid, "name": name,
                "one": grab(sec, "一句话"),
                "scene": grab_block(sec, "情境"),
                "action": grab_block(sec, "标准动作"),
                "triggers": grab_list(sec, "触发器"),
                "trap": grab_block(sec, "易错"),
                "links": grab_list(sec, "关联"),
            })
        else:
            out["grounds"].append({
                "id": cid, "name": name,
                "module": out["module"] or name.replace(" 地基包", "").strip(),
                "positioning": grab(sec, "定位"),
                "model": grab_block(sec, "心智模型"),
                "must": grab_list(sec, "必会清单"),
                "path": grab_list(sec, "学习路径"),
                "gate": grab_list(sec, "验收门"),
            })
    return out


def link_line_refs(html, line_href):
    """把正文里的 [@模块-行号] 换成主线页链接（在 md_to_html 之后跑，避免被转义）"""
    def sub(m):
        href = line_href.get((m.group(1), CN_INDEX.get(_cn_line(m.group(2)), 0)))
        if not href:
            return m.group(0)
        return ' <a class="mv-cref" href="%s" title="跳到这条主线">@%s-%s</a>' % (
            esc(href), esc(m.group(1)), m.group(2))
    return LINE_REF_RE.sub(sub, html)


def _ref_list(items, line_href):
    return "".join("<li>%s</li>" % link_line_refs(inline(x), line_href) for x in items)


CARDS_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>内化馆 · 读厚卡片</title>
<link rel="stylesheet" href="_components/marvis.css">
<style>
  .crd, .gnd { border: 1px solid rgba(0,0,0,.12); border-radius: 12px; background: #fff;
    padding: 14px 16px; margin: 12px 0; scroll-margin-top: 20px; }
  .sum-row { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0 6px; }
  .sum-row div { border: 1px solid rgba(0,0,0,.1); border-radius: 10px; padding: 8px 12px; background: #fff; }
  .sum-row small { display: block; color: #5F5E5A; font-size: 11px; }
  .sum-row strong { font-size: 17px; font-weight: 500; }
  .crd.hl, .gnd.hl { border-color: #D85A30; box-shadow: 0 0 0 3px rgba(216,90,48,.14); }
  .crd-h, .gnd-h { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
  .crd-n { font-size: 12px; color: #888780; font-variant-numeric: tabular-nums; }
  .crd-t { font-size: 15px; font-weight: 500; }
  .crd-tag { font-size: 11px; padding: 1px 7px; border-radius: 20px; background: #FBE9E1; color: #993C1D; }
  .crd-lv { font-size: 11px; padding: 1px 7px; border-radius: 20px; background: #EEEDFE; color: #534AB7; }
  .crd-src { font-size: 11px; color: #888780; margin-left: auto; }
  .crd-one { font-size: 14px; line-height: 1.65; margin: 0 0 10px; color: #2C2C2A; }
  .crd-one b { font-weight: 500; color: #993C1D; }
  .crd-scene { font-size: 14px; line-height: 1.65; color: #2C2C2A;
    background: #fbfaf7; border-left: 3px solid #F3C1AC; border-radius: 0 8px 8px 0;
    padding: 10px 12px; margin: 0 0 10px; }
  .crd-scene b { font-weight: 500; color: #993C1D; }
  details.crd-d, details.gnd-d { border-top: 1px dashed rgba(0,0,0,.12); padding-top: 8px; }
  details.crd-d summary, details.gnd-d summary { cursor: pointer; font-size: 13px; color: #993C1D;
    list-style: none; user-select: none; }
  details.crd-d summary::-webkit-details-marker, details.gnd-d summary::-webkit-details-marker { display: none; }
  details.crd-d summary::before, details.gnd-d summary::before { content: '▸ '; }
  details.crd-d[open] summary::before, details.gnd-d[open] summary::before { content: '▾ '; }
  .crd-sec { font-size: 14px; line-height: 1.7; margin: 8px 0 0; color: #2C2C2A; }
  .crd-sec b { font-weight: 500; color: #5F5E5A; }
  .crd-f { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 10px; }
  .crd-use { font-size: 12px; color: #5F5E5A; }
  .gnd .crd-sec ul, .gnd .crd-sec ol { margin: 6px 0 0; padding-left: 20px; }
  .gnd .crd-sec li { margin: 4px 0; }
  a.mv-cref { color: #185FA5; text-decoration: none; border-bottom: 1px dotted rgba(24,95,165,.5); }
  .src-h { margin: 26px 0 4px; font-size: 16px; font-weight: 500; }
  .src-h small { font-weight: 400; color: #5F5E5A; font-size: 12px; margin-left: 8px; }
</style>
</head>
<body class="mv-page">
<div class="mv-wrap">

  <div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap">
    <h1 class="mv-h1" style="margin:0">内化馆 · 读厚卡片</h1>
    <div style="display:flex;gap:8px;align-items:center">
      <a class="mv-btn" href="index.html" style="text-decoration:none">回今日</a>
      <a class="mv-btn" href="brain.html" style="text-decoration:none">第二大脑</a>
      <a class="mv-btn mv-btn-primary" href="progress.html" style="text-decoration:none">进度与作业</a>
    </div>
  </div>
  <p class="mv-sub" style="margin-bottom:4px">
    读过的书在这里被「读厚」：每张卡只回答一件事——<b>遇到这个情境，具体怎么做</b>。
    概念记住不算数，真实用过一次记一笔 ⚡；等级仍只由进度页的闭卷自评推进。
  </p>
  <div class="sum-row" id="sum"></div>

  <h2 class="mv-h2" style="margin-top:10px">原则卡 <small>书 → 情境 → 动作 · 已接进每日派单</small></h2>
  %%PRINCIPLES%%

  <h2 class="mv-h2" style="margin-top:26px">地基包 <small>先记住打底，再去主线页添砖加瓦 · 不进派单</small></h2>
  %%GROUNDS%%

  <p class="mv-note" style="margin-top:20px">
    正本在 <code>wiki/cards/</code>（一文件一来源），本页与 <code>_data/cards.js</code> 由 <code>build.py</code> 生成，不手改。
    以后读完一本书：写一份「原则-{书名}.md」正本 → 跑 build → 卡片自动进星系和派单。模板在 <code>templates/</code>。
  </p>

</div>

<script src="_data/cards.js"></script>
<script src="_components/marvis.js"></script>
<script>
(function () {
  'use strict';
  var KEY = 'mv.progress.v1', BKEY = 'mv.brain.v1';
  var S = {}, B = {};
  try { S = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
  try { B = JSON.parse(localStorage.getItem(BKEY) || '{}'); } catch (e) {}
  if (!S.lv) S.lv = {};
  if (!B.uses) B.uses = {};
  function lvOf(id) { return (S.lv['card/' + id] && S.lv['card/' + id].l) || 0; }
  function lvRec(id) { return S.lv['card/' + id] || {}; }
  var LVW = ['未练', '会了', '常练'];

  function paint() {
    document.querySelectorAll('[data-lv]').forEach(function (el) {
      var id = el.getAttribute('data-lv'), r = lvRec(id);
      var t = LVW[lvOf(id)];
      if (r.hit || r.miss) t += ' · 讲得出 ' + (r.hit || 0) + ' / 卡壳 ' + (r.miss || 0);
      el.textContent = t;
    });
    document.querySelectorAll('[data-use]').forEach(function (el) {
      var u = B.uses[el.getAttribute('data-use')] || [];
      el.textContent = u.length ? '已真实用过 ' + u.length + ' 次' + (u.length ? ' · 最近 ' + u[u.length - 1].d : '') : '还没真实用过——读到 ≠ 用到';
    });
    var trained = 0, tot = 0;
    document.querySelectorAll('[data-lv]').forEach(function (el) {
      tot++; if (lvOf(el.getAttribute('data-lv')) >= 1) trained++;
    });
    var sum = document.getElementById('sum');
    var cards = (window.MARVIS_CARDS && window.MARVIS_CARDS.principles) || [];
    var grounds = (window.MARVIS_CARDS && window.MARVIS_CARDS.grounds) || [];
    var srcs = {};
    cards.forEach(function (c) { srcs[c.source] = 1; });
    if (sum) sum.innerHTML =
      '<div><small>原则卡</small><strong>' + cards.length + '</strong></div>' +
      '<div><small>来源</small><strong>' + Object.keys(srcs).length + '</strong></div>' +
      '<div><small>地基包</small><strong>' + grounds.length + '</strong></div>' +
      '<div><small>已内化（到「会了」）</small><strong>' + trained + ' / ' + tot + '</strong></div>';
  }

  window.cardUse = function (id) {
    var note = prompt('在哪用上的？（一句话，可留空）', '');
    if (note === null) return;
    var d = new Date();
    var ds = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    B.uses[id] = B.uses[id] || [];
    B.uses[id].push({ d: ds, note: (note || '').trim() });
    try { localStorage.setItem(BKEY, JSON.stringify(B)); } catch (e) {}
    paint();
  };

  paint();

  if (location.hash) {
    var el = document.getElementById(location.hash.slice(1));
    if (el) {
      el.classList.add('hl');
      var dd = el.querySelector('details');
      if (dd) dd.open = true;
    }
  }
})();
</script>
</body>
</html>
"""


def render_cards_page(payload, line_href):
    def principle_html(c):
        details = ['<details class="crd-d"><summary>先想：这个情境你会怎么做，再展开对</summary>']
        details.append('<div class="crd-sec"><b>标准动作</b>%s</div>'
                       % link_line_refs(md_to_html(c["action"]), line_href) if c["action"] else "")
        if c["triggers"]:
            details.append('<div class="crd-sec"><b>触发器</b><ul class="mv-md-ul">%s</ul></div>'
                           % _ref_list(c["triggers"], line_href))
        if c["trap"]:
            details.append('<div class="crd-sec"><b>易错</b>%s</div>'
                           % link_line_refs(md_to_html(c["trap"]), line_href))
        if c["links"]:
            details.append('<div class="crd-sec"><b>关联</b> %s</div>'
                           % "　".join(esc(x.replace("[[", "").replace("]]", "")) for x in c["links"]))
        details.append("</details>")
        return (
            '<div class="crd" id="card-%s">'
            '<div class="crd-h"><span class="crd-n">%s</span>'
            '<span class="crd-t">%s</span>'
            '<span class="crd-lv" data-lv="%s">未练</span>'
            '<span class="crd-src">正本 %s</span></div>'
            '<p class="crd-one"><b>一句话</b>　%s</p>'
            '<p class="crd-scene"><b>情境</b>　%s</p>'
            '%s'
            '<div class="crd-f">'
            '<button class="mv-btn" type="button" onclick="cardUse(\'%s\')">⚡ 记一笔：真实用上了一次</button>'
            '<span class="crd-use" data-use="%s"></span>'
            "</div></div>"
            % (esc(c["id"]), esc(c["id"]), esc(c["name"]), attrs(c["id"]), esc(c["src"]),
               link_line_refs(inline(c["one"]), line_href),
               link_line_refs(md_to_html(c["scene"]), line_href) if c["scene"] else "—",
               "".join(details), esc(c["id"]), esc(c["id"]))
        )

    psec = ""
    by_src, order = {}, []
    for c in payload["principles"]:
        if c["source"] not in by_src:
            by_src[c["source"]] = []
            order.append(c)
        by_src[c["source"]].append(c)
    for first in order:
        src = first["source"]
        head = '<div class="src-h">%s<small>%s</small>' % (esc(src), esc(first["author"]))
        if first["source_href"]:
            head += (' <a href="obsidian://open?vault=Marvis&amp;file=%s" style="font-size:12px;color:#185FA5;text-decoration:none">打开阅读闭环 →</a>'
                     % quote(first["source_href"].replace(".md", "")))
        head += ('　<small>%s</small></div>'
                 % ("人已复核" if first["human_reviewed"] else "AI 读厚产出 · 待本人验证（status %s）" % first["status"]))
        psec += head + "".join(principle_html(c) for c in by_src[src])

    gsec = ""
    for g in payload["grounds"]:
        mod_page = "modules/%s.html" % safe_fname(g["module"])
        inner = ['<div class="crd-sec"><b>定位</b>%s</div>'
                 % link_line_refs(inline(g["positioning"]), line_href) if g["positioning"] else ""]
        if g["model"]:
            inner.append('<div class="crd-sec"><b>心智模型</b>%s</div>'
                         % link_line_refs(md_to_html(g["model"]), line_href))
        if g["must"]:
            inner.append('<div class="crd-sec"><b>必会清单</b><ul>%s</ul></div>'
                         % _ref_list(g["must"], line_href))
        if g["path"]:
            inner.append('<div class="crd-sec"><b>学习路径</b><ol>%s</ol></div>'
                         % _ref_list(g["path"], line_href))
        if g["gate"]:
            inner.append('<details class="gnd-d"><summary>验收门（做完地基再过）</summary>'
                         '<div class="crd-sec"><ul>%s</ul></div></details>'
                         % _ref_list(g["gate"], line_href))
        gsec += (
            '<div class="gnd" id="%s">'
            '<div class="gnd-h"><span class="crd-t">%s</span>'
            '<span class="crd-tag">%s</span>'
            '<a class="mv-btn" style="margin-left:auto;text-decoration:none" href="%s">%s 模块概览 →</a></div>'
            "%s</div>"
            % (esc(g["id"]), esc(g["name"]), esc(g["module"]), esc(mod_page), esc(g["module"]),
               "".join(inner))
        )
    return CARDS_PAGE.replace("%%PRINCIPLES%%", psec or '<p class="mv-note">还没有原则卡。</p>') \
                     .replace("%%GROUNDS%%", gsec or '<p class="mv-note">还没有地基包。</p>')


def write_cards(modules):
    """wiki/cards/*.md → _data/cards.js（含派单簇 MARVIS_CARD_CLUSTER）+ site/cards.html"""
    if not CARDS_DIR.exists():
        return None
    line_href = {}
    for md in modules:
        for ln in md["lines"]:
            line_href[(md["module"], CN_INDEX.get(_cn_line(ln["no"]), 0))] = module_line_page(md, ln["no"])

    principles, grounds, seen = [], [], set()
    for p in sorted(CARDS_DIR.glob("*.md")):
        f = parse_brain_cards_file(p)
        if not f:
            continue
        for c in f["cards"]:
            if c["id"] in seen:
                print("  [warn] 原则卡 id 重复，丢弃后者：%s (%s)" % (c["id"], p.name))
                continue
            seen.add(c["id"])
            c.update(source=f["source"], author=f["author"], source_href=f["source_href"],
                     status=f["status"], human_reviewed=f["human_reviewed"], src=f["src"])
            principles.append(c)
        for g in f["grounds"]:
            if g["id"] in seen:
                print("  [warn] 地基包 id 重复，丢弃后者：%s (%s)" % (g["id"], p.name))
                continue
            seen.add(g["id"])
            g.update(src=f["src"], status=f["status"], human_reviewed=f["human_reviewed"])
            grounds.append(g)

    payload = {"generated": datetime.date.today().isoformat(),
               "principles": principles, "grounds": grounds}
    cluster = {"id": "card", "name": "原则卡 · 读厚", "zone": "准则",
               "topics": [{"id": c["id"], "name": c["name"], "href": "cards.html#card-" + c["id"]}
                          for c in principles]}
    (OUT_DATA / "cards.js").write_text(
        "window.MARVIS_CARDS = " + json.dumps(payload, ensure_ascii=False) + ";\n"
        "window.MARVIS_CARD_CLUSTER = " + json.dumps(cluster, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    (SITE / "cards.html").write_text(render_cards_page(payload, line_href), encoding="utf-8")
    n_use = sum(len((g.get("must") or [])) for g in grounds)
    print("读厚卡片：原则卡 %d 张（%d 个来源）+ 地基包 %d 份（必会 %d 条）→ cards.js + cards.html"
          % (len(principles), len({c["source"] for c in principles}), len(grounds), n_use))
    return payload


# ── 问题台账（questions.md → _data/ledger.js，进度页「问题台账」抽屉用）────────────
# 版式（2026-10-02 卡片版）：### Q-YYYY-NNN · 标题 [active|parked]，字段行
#   - 为什么现在： / - 下一步： / - 落点： / - 重启条件： / - 触碰：YYYY-MM-DD ｜ 创建：YYYY-MM-DD
# 已闭环节一行一条：- YYYY-MM-DD · Q-YYYY-NNN · 说明。
# 纯函数拆出来是给 _tests/test_ledger.py 喂固定文本用的；解析不了的字段一律空串，不报错。
def parse_questions_text(text, today=None):
    today = today or datetime.date.today()
    out = {"active": [], "parked": [], "closed": [],
           "weekStart": (today - datetime.timedelta(days=today.weekday())).isoformat()}
    section, cur, last_key = None, None, None
    for raw in text.splitlines():
        line = raw.rstrip()
        if re.match(r"^##\s", line):
            sec = line.lstrip("# ").strip()
            section = ("active" if ("当前战役" in sec or "活跃" in sec)
                       else "parked" if "冷却" in sec
                       else "closed" if "已闭环" in sec else None)
            cur, last_key = None, None
            continue
        mh = re.match(r"^###\s+(Q-\d{4}-\d{3})\s*·\s*(.+?)\s*(?:\[(active|parked)\])?\s*$", line)
        if mh and section in ("active", "parked"):
            # 状态标记缺省时跟随所在节——宁可默认也不让字段串进上一条问题
            cur = {"id": mh.group(1), "title": mh.group(2),
                   "status": mh.group(3) or section,
                   "why": "", "next": "", "target": "", "restart": "",
                   "touched": "", "created": ""}
            out[section].append(cur)
            last_key = None
            continue
        if cur is None:
            ml = re.match(r"^-\s+(\d{4}-\d{2}-\d{2})\s*·\s*(Q-\d{4}-\d{3})\s*·?\s*(.*)$", line)
            if section == "closed" and ml:
                out["closed"].append(
                    {"date": ml.group(1), "id": ml.group(2), "note": ml.group(3)})
            continue
        mf = re.match(r"^-\s*(为什么现在|下一步|落点|重启条件)\s*[：:]\s*(.*)$", line)
        if mf:
            key = {"为什么现在": "why", "下一步": "next", "落点": "target",
                   "重启条件": "restart"}[mf.group(1)]
            cur[key] = mf.group(2).strip()
            last_key = key
            continue
        mt = re.match(r"^-\s*触碰\s*[：:]\s*(\d{4}-\d{2}-\d{2})?", line)
        if mt:
            cur["touched"] = mt.group(1) or ""
            mc = re.search(r"创建\s*[：:]\s*(\d{4}-\d{2}-\d{2})", line)
            cur["created"] = mc.group(1) if mc else ""
            last_key = None
            continue
        if line.strip() and last_key:                    # 字段折行并回上一个字段
            cur[last_key] += " " + line.strip()
    return out


def write_ledger():
    """questions.md → _data/ledger.js。文件不存在就跳过，不卡构建。"""
    if not LEDGER_SRC.exists():
        return
    led = parse_questions_text(LEDGER_SRC.read_text(encoding="utf-8"))
    week_closed = sum(1 for c in led["closed"] if c["date"] >= led["weekStart"])
    stale_line = (datetime.date.today()
                  - datetime.timedelta(days=14)).isoformat()
    stale = [q["id"] for q in led["active"]
             if not q["touched"] or q["touched"] <= stale_line]
    payload = {
        "generated": datetime.date.today().isoformat(),
        "weekStart": led["weekStart"],
        "weekTarget": 1,
        "weekClosed": week_closed,
        "active": led["active"],
        "parked": led["parked"],
        "closed": led["closed"][-20:],
    }
    (OUT_DATA / "ledger.js").write_text(
        "window.MARVIS_LEDGER = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print("台账 %d 活跃 / %d 冷却 / 已闭环 %d · 本周 %d/%d · 超 14 天未触碰：%s"
          % (len(led["active"]), len(led["parked"]), len(led["closed"]),
             week_closed, payload["weekTarget"], " ".join(stale) or "无"))


def main():
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_TOPICS.mkdir(parents=True, exist_ok=True)
    warm_mermaid()

    # 有模块卡的模块名（母题页要据此回链模块概览，必须早于母题页渲染）
    for d in MODULE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            head = p.read_text(encoding="utf-8")[:600]
            if "type: study-module" not in head:
                continue
            mm = re.search(r"^module:[ ]*(.+)$", head, re.M)
            if mm:
                nm = mm.group(1).split("/")[0].strip()
                TOPIC_MODULE_INDEX[nm] = nm

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

    TOPIC_PAGES.update({t["key"]: t["page"] for t in topics})
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
    index_topic_cards()          # 跨模块母题兜底（Redis Q19 → 并发与锁 L3）
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

    projects = build_projects()

    # 读厚卡片层：wiki/cards 正本 → cards.js（派单簇）+ cards.html 内化馆
    write_cards(modules)

    # 复训牌组：2026-09-25 起不再按 md 的 integrated 过滤（状态机退场）。
    # 判据改为「这张卡有可供复述的骨架或结论」——讲没讲过由进度页的本机数据决定。
    def _speakable(t):
        return bool(t.get("conclusion") or t.get("skeleton"))
    live = [t for t in topics if _speakable(t)]
    drafts = [t for t in topics if not _speakable(t)]

    decks = []
    if live:
        decks.append({
            "id": "topics", "name": "母题",
            "cards": [{"id": t["key"], "q": t["question"], "a": t["conclusion"],
                       "tag": t["module"], "href": t["page"], "src": t["src"]}
                      for t in live],
        })
    decks.extend(parse_interview_manual())
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

    # 断点回流：进度页要按「上次断点」派复训、按断点抽检，所以母题卡里的
    # 断点 / 证据 / 关键词 / 结论要出成数据，不能只埋在 html 里。
    # 键 = 母题页路径，与 clusters.js 里的 href 精确对应（同一套 module-stem 命名）。
    # 模板占位符（「【待填 —— …】」）一律当空值，否则进度页会把模板文字当断点摊出来。
    def _real(s):
        s = (s or "").strip()
        if not s or re.match(r"^【.*】$", s) or "待填" in s or "待写" in s:
            return ""
        return s

    breaks = {}
    for t in topics:
        bp, con = _real(t["breakpoint"]), _real(t["conclusion"])
        if not (bp or con):
            continue
        # 只出进度页真正会渲染的字段：断点原文、一句话结论、恢复关键词、两条追问。
        # 通过证据 / 完整骨架这些是学习当时的验收标准，复训时用不上，不进数据。
        fu = []
        for f in t["followups"][:2]:
            if isinstance(f, (list, tuple)) and len(f) >= 2:
                fu.append({"q": f[0], "a": f[1]})
        breaks[t["page"]] = {"con": con, "kw": t["keywords"], "bp": bp, "fu": fu}
    (OUT_DATA / "breaks.js").write_text(
        "window.MARVIS_BREAKS = " + json.dumps(breaks, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    _nbp = sum(1 for v in breaks.values() if v["bp"])
    print("断点回流 %d 张卡（其中 %d 张有真断点原文）" % (len(breaks), _nbp))

    write_ledger()

    inject_mermaid_runtime()

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
        # 覆盖率：还有多少母题只有「一句话结论 + 骨架」而没有完整答案（2026-09-26）
        ans_n = sum(1 for t in md["topics"]
                    if (_topic_state(md, t["id"])[1] or {}).get("answer"))
        qa = md.get("qanswers") or {}
        qa_n = sum(1 for q in md["questions"] if q["no"] in qa)
        print("  == %s（%d 主线 / %d 母题，已提炼 %d，必背题 %d，完整答案 %d，题级答案 %d/%d）"
              % (md["page"], len(md["lines"]), len(md["topics"]), ready,
                 sum(1 for q in md["questions"] if "必背" in (q["pri"] or "")), ans_n,
                 qa_n, len(md["questions"])))

    # 清理陈旧页面：主线/母题改名后，上一轮生成的 html 会残留成死链
    exp_topics = {"%s-%s.html" % (t["module"], t["stem"]) for t in topics}
    exp_reviews = {rv["stem"] + ".html" for rv in reviews}
    exp_modules = set()
    for md in modules:
        exp_modules.add("%s.html" % md["module"])
        for ln in md["lines"]:
            exp_modules.add(module_line_page(md, ln["no"]).split("/")[-1])
    for _d, _exp in ((OUT_TOPICS, exp_topics), (OUT_REVIEWS, exp_reviews),
                     (OUT_MODULES, exp_modules)):
        _gone = prune_dir(_d, _exp)
        if _gone:
            print("  [清理陈旧页面] %s ×%d" % (_d.name, len(_gone)))

    for pid in projects:
        print("  ## projects/%s.html（项目口述 · 骨架 + 决策链）" % pid)

    cleaned = cleanup_html()
    if cleaned:
        print("清理预览注入属性：%d 个 html 文件" % cleaned)


if __name__ == "__main__":
    main()
