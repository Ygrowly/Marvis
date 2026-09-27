# -*- coding: utf-8 -*-
"""mermaid 代码块 → 内联 SVG（构建期离线渲染）

为什么不在页面里跑 mermaid.js：
    站点原则是「零依赖、离线可用、双击可开」。构建期把图渲成 SVG 内联进页面，
    页面既不引 JS 也不依赖 CDN，和已有的 90 张手绘 SVG 走同一条路。

怎么渲：
    把所有待渲的图块拼进一个临时 HTML → 本机 msedge 无头 `--dump-dom`
    拿到渲染后的 DOM → 抠出每块里的 <svg> → 按内容 hash 存缓存。
    `mermaid.min.js`（3.3MB，v10.9.1 UMD）已就地固化在本目录，只参与构建。

缓存：
    cache/<sha1(源码)[:16]>.svg —— md 里那段没改就不重渲。
    删掉 cache/ 目录 = 全部重渲。

用法：
    python site/_build/mermaid/mmd.py --scan      # 试渲活跃目录全部图块，报失败清单
    python site/_build/mermaid/mmd.py --clear     # 清缓存
"""

import hashlib
import html
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "mermaid.min.js"
CACHE = HERE / "cache"
TMP = HERE / "_tmp"

# 本机无头浏览器（Windows 上 Edge 一定有；Chrome 兜底）
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

INIT_JS = """
  mermaid.initialize({
    startOnLoad: true, theme: 'neutral', securityLevel: 'loose',
    fontFamily: '"Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif',
    flowchart: { useMaxWidth: false },
    sequence: { useMaxWidth: false },
    gantt: { useMaxWidth: false },
    'class': { useMaxWidth: false },
    state: { useMaxWidth: false },
    er: { useMaxWidth: false },
    journey: { useMaxWidth: false },
    pie: { useMaxWidth: false }
  });
"""

FENCE_RE = re.compile(r"^```mermaid[ \t]*\r?\n(.*?)^```[ \t]*$",
                      re.S | re.M)
MARK = '<div class="mmdwrap" data-k="%s">'


def key(code):
    return hashlib.sha1(code.encode("utf-8")).hexdigest()[:16]


def blocks_of(md_text):
    """抽出一段 markdown 里全部 ```mermaid 块（去掉首尾空行）"""
    return [m.group(1).strip("\r\n").rstrip() for m in FENCE_RE.finditer(md_text)]


def _browser():
    env = os.environ.get("MARVIS_EDGE")
    for p in ([env] if env else []) + EDGE_CANDIDATES:
        if p and Path(p).exists():
            return p
    return None


def _balanced_svg(chunk):
    """从一段 DOM 里抠出第一个完整的 <svg>…</svg>（按标签配平，不靠非贪婪正则）"""
    i = chunk.find("<svg")
    if i < 0:
        return None
    depth, j = 0, i
    for m in re.finditer(r"<svg\b|</svg>", chunk[i:]):
        depth += 1 if m.group(0) == "<svg" else -1
        if depth == 0:
            j = i + m.end()
            break
    else:
        return None
    return chunk[i:j]


def _prefix_ids(svg, pfx):
    """把图内所有 id ／ 引用统一加前缀。

    mermaid 内部除了根 id（带时间戳）还有 `actor1` / `root-0` / `L-A-B-0`
    这类按内容生成的短 id——同一页两张图完全可能撞名，所以不是只改根 id。
    顺序：先处理 `id="X"`，再处理 `#X`（覆盖 <style> 里的选择器和 url(#X)），
    最后处理属性值里的裸 `"X"`（aria-labelledby 之类）；长名先换，避免短名截胡。
    """
    for name in sorted(set(re.findall(r'id="([^"]+)"', svg)), key=len, reverse=True):
        new = "%s-%s" % (pfx, name)
        svg = svg.replace('id="%s"' % name, 'id="%s"' % new)
        svg = svg.replace("#%s" % name, "#" + new)
        svg = svg.replace('"%s"' % name, '"%s"' % new)
    return svg


def _normalize(svg):
    """统一成「按原始像素宽呈现」：页面用 overflow-x 横向滚动，不缩成一团糊字。

    useMaxWidth:false 时 mermaid 已经给出 px 宽高；两处兜底——① 个别图
    （mindmap）只给 width 不给 height，缺高度会被浏览器当成 100% 撑满；
    ② 万一还带 100%/max-width 就按 viewBox 还原。
    """
    vb = re.search(r'viewBox="([-\d.eE ]+)"', svg)
    nums = vb.group(1).split() if vb else []
    if len(nums) == 4:
        w, h = round(float(nums[2]), 1), round(float(nums[3]), 1)
        if 'width="100%"' in svg:
            svg = svg.replace('width="100%"', 'width="%s"' % w)
        root = re.search(r"<svg\b[^>]*>", svg)
        if root and "height=" not in root.group(0):
            svg = svg.replace(root.group(0), root.group(0)[:-1] + ' height="%s">' % h, 1)
    svg = re.sub(r'\s*style="max-width:[^"]*"', "", svg)
    return svg


def _is_error(svg):
    return 'class="error-icon"' in svg or "Syntax error in text" in svg


def render(codes, timeout=180):
    """一批图块 → {hash: svg}；渲不出来的（语法错、超时）不出现在结果里"""
    codes = [c for c in dict.fromkeys(codes) if c and c.strip()]
    if not codes:
        return {}
    exe = _browser()
    if not exe or not VENDOR.exists():
        return {}

    CACHE.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    parts = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">',
             '<style>body{margin:0;background:#FAFAF8}</style></head><body>']
    for c in codes:
        parts.append(MARK % key(c))
        parts.append('<pre class="mermaid">%s</pre></div>' % html.escape(c))
    parts.append('<script src="./mermaid.min.js"></script>')
    parts.append("<script>%s</script></body></html>" % INIT_JS)
    page = TMP / "batch.html"
    # 临时页里 vendor 用相对路径，保证 file:// 下能加载
    vendor_local = TMP / "mermaid.min.js"
    if (not vendor_local.exists()) or vendor_local.stat().st_size != VENDOR.stat().st_size:
        vendor_local.write_bytes(VENDOR.read_bytes())
    page.write_text("".join(parts), encoding="utf-8")

    cmd = [exe, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--user-data-dir=%s" % (TMP / "ud"),
           "--virtual-time-budget=30000",
           "--dump-dom", page.as_uri()]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except Exception as e:                                   # noqa: BLE001
        print("  [mermaid] 无头浏览器调用失败：%s" % e)
        return {}
    dom = r.stdout.decode("utf-8", "replace")
    if "<svg" not in dom:
        print("  [mermaid] 无头浏览器没有产出 DOM（%d 字节）" % len(dom))
        return {}

    out, bad = {}, []
    by_key = {key(c): c for c in codes}
    chunks = re.split(r'<div class="mmdwrap" data-k="([0-9a-f]{16})">', dom)
    for i in range(1, len(chunks) - 1, 2):
        k, body = chunks[i], chunks[i + 1]
        svg = _balanced_svg(body)
        if not svg or _is_error(svg):
            bad.append(k)
            continue
        svg = _normalize(_prefix_ids(svg, "mmd" + k[:8]))
        (CACHE / ("%s.svg" % k)).write_text(svg, encoding="utf-8")
        out[k] = svg
    for k in bad:
        src = by_key.get(k, "")
        print("  [mermaid] 渲染失败，退回代码块：%s" % src.strip().splitlines()[0][:60])
    return out


def ensure(codes, verbose=False):
    """补齐缓存：返回 {hash: svg}（含本次新渲的）"""
    want = [c for c in dict.fromkeys(codes) if c and c.strip()]
    have, todo = {}, []
    for c in want:
        f = CACHE / ("%s.svg" % key(c))
        if f.exists():
            have[key(c)] = f.read_text(encoding="utf-8")
        else:
            todo.append(c)
    if todo:
        if verbose:
            print("  [mermaid] 新渲 %d 张（缓存命中 %d 张）" % (len(todo), len(have)))
        have.update(render(todo))
    return have


def get(code_text, cache=None):
    """取单块 SVG；调用方拿不到就退回 <pre> 代码块"""
    if cache is not None and key(code_text) in cache:
        return cache[key(code_text)]
    f = CACHE / ("%s.svg" % key(code_text))
    if f.exists():
        return f.read_text(encoding="utf-8")
    return None


# ------------------------------------------------------------------ CLI
def _scan_roots(root):
    for base in ("wiki", "projects", "study", "raw"):
        d = root / base
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.md")):
            if ".workbuddy" in p.parts:
                continue
            yield p


def main():
    root = HERE.parent.parent.parent          # site/_build/mermaid → 库根
    args = sys.argv[1:]
    if "--clear" in args:
        n = 0
        for f in CACHE.glob("*.svg") if CACHE.exists() else []:
            f.unlink()
            n += 1
        print("已清缓存 %d 张" % n)
        return
    if "--scan" in args:
        total, bad = 0, []
        all_codes = []
        for p in _scan_roots(root):
            b = blocks_of(p.read_text(encoding="utf-8"))
            if b:
                total += len(b)
                all_codes += b
        print("活跃目录共 %d 张 mermaid 图" % total)
        got = ensure(all_codes, verbose=True)
        miss = [c for c in dict.fromkeys(all_codes) if key(c) not in got]
        print("成功 %d / 去重后 %d；失败 %d" % (len(got), len(set(key(c) for c in all_codes)), len(miss)))
        for m in miss:
            print("  ✗", m.strip().splitlines()[0][:70])
        return
    print(__doc__)


if __name__ == "__main__":
    main()
