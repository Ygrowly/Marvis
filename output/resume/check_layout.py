#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简历版面校验：导出的 PDF 有没有溢出被裁。

用法（在 output/resume/ 下）：
    python check_layout.py                              # 量默认版（AI 应用开发）
    python check_layout.py --name 刘宇广-AI交付工程师-2027届
    python check_layout.py --all                        # 遍历目录里全部「刘宇广-*.html」
    python check_layout.py --all --export               # 先逐个重导 PDF 再量
    python check_layout.py --list                       # 只看有哪些成品、PDF 齐不齐
    python check_layout.py --export                     # 默认版：先重导 PDF 再量

为什么要它：简历是固定 A4 + `overflow: hidden`——**溢出会被静默裁掉，页面看起来完全正常**。
只有渲染后的 PDF 才能证明有没有裁。这根尺子把「量一次」变成一条命令。

**两道尺子（2026-09-20 加第二道）**：
1. 底部余量——量最后一行的底边离页底还有多少。**它抓不到被裁的内容**（被裁的字根本不在 PDF 文本层里）。
2. 文本完整性——把 HTML 的可见文本与 PDF 抽出的文本做差集，报出「哪些片段没进 PDF」。
   2026-09-20 的事故：第三行技能整行被裁（含 CET-6），第 1 道尺子报「✓ 未溢出 +2.3pt」，
   第 2 道尺子才把它抓出来。**只要改过 HTML，两道都必须看。**

依赖：pymupdf（`import pymupdf`）。渲染引擎见 BROWSERS。
      本机 pymupdf 只装在隔离 venv 里，**直接用 `python check_layout.py` 也行**——
      脚本发现当前解释器没有它会自动切到 venv 再跑（见 VENV_PY）。
"""
from __future__ import annotations

import argparse
import io
import os
import pathlib
import subprocess
import sys

# Windows 控制台默认 GBK，直接 print 中文/符号会崩
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# 渲染引擎：按顺序试，谁写出 PDF 用谁。
# 2026-09-28 实测：本机 80+ 个 msedge 进程常驻时，Edge headless 连 --dump-dom 都空输出、
# 导出静默失败；同一份 HTML 用 Chrome 一次就成。所以 Chrome 必须留在列表里兜底。
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]
VENV_PY = pathlib.Path(
    r"C:\Users\Lenovo\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
)
DEFAULT = "刘宇广-AI应用开发-2027届"   # 默认版（AI 应用 / Agent）
PATTERN = "刘宇广-*.html"             # 遍历用；改名了只动这两行
LINE_PT = 11.25                       # 正文行高（9pt × 1.25）——省一行的最小单位
HERE = pathlib.Path(__file__).parent.resolve()


def _ensure_pymupdf() -> None:
    """pymupdf 只装在隔离 venv 里。当前解释器没有就自动切过去重跑，省掉记路径。"""
    try:
        import pymupdf  # noqa: F401, PLC0415
        return
    except ImportError:
        pass
    if os.environ.get("_MV_REEXEC") == "1" or not VENV_PY.exists():
        sys.exit(f"[FAIL] 当前解释器没有 pymupdf。用这个跑：\n  \"{VENV_PY}\" check_layout.py")
    print(f"[i] 当前解释器没有 pymupdf，自动切到隔离环境重跑")
    sys.stdout.flush()
    r = subprocess.run([str(VENV_PY), str(pathlib.Path(__file__).resolve()), *sys.argv[1:]],
                       env={**os.environ, "_MV_REEXEC": "1"})
    raise SystemExit(r.returncode)


def list_pairs() -> list[tuple[str, pathlib.Path, pathlib.Path | None]]:
    """目录里所有成品：返回 (基名, html, pdf 或 None)。"""
    out = []
    for html in sorted(HERE.glob(PATTERN)):
        pdf = html.with_suffix(".pdf")
        out.append((html.stem, html, pdf if pdf.exists() else None))
    return out


def export(html: pathlib.Path, pdf: pathlib.Path) -> None:
    """HTML → PDF。两个坑（都是本机实测，别再踩回去）：

    1. **中文路径**会让 Edge 报「拒绝访问」，所以先写 ASCII 名再 rename。
    2. **本机开着 Edge 时 headless 会抢不到默认用户目录**，静默不产出 PDF
       （实测本机 80+ 个 msedge 进程，导出直接失败）。必须给一个独占的
       --user-data-dir，否则只能靠「手动关掉 Edge 再跑」这种脆弱操作。
    """
    import tempfile  # noqa: PLC0415

    tmp = HERE / f"_layout_tmp_{abs(hash(html.stem)) % 10 ** 8}.pdf"
    for exe in BROWSERS:
        if not pathlib.Path(exe).exists():
            continue
        subprocess.run(
            [exe, "--headless", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
             f"--user-data-dir={tempfile.mkdtemp(prefix='_mv_pdf_')}",
             "--no-pdf-header-footer", f"--print-to-pdf={tmp}", str(html)],
            capture_output=True, timeout=180, check=False,
        )
        if tmp.exists():
            pdf.unlink(missing_ok=True)
            tmp.rename(pdf)
            return
    sys.exit("[FAIL] 导出失败：BROWSERS 里的浏览器都没写出文件"
             "（都已安装？是否被别的浏览器进程挡住？）")


BLOCK_TAGS = (r"(?i)</?(?:div|p|li|ul|ol|h[1-6]|section|article|header|footer"
              r"|tr|table|br)\b[^>]*>")


def visible_units(path: pathlib.Path) -> list[str]:
    """抽 HTML 的可见文本，**按块拆开**（块级标签当作分隔符）。

    必须按块拆：PDF 的抽取顺序不等于阅读顺序，整篇当一条流比对会在块与块的接缝处
    产生假阳性（实测 7 处）。按块各自比对才既无假阳性、又能抓出被裁的整块。"""
    import html as htmllib  # noqa: PLC0415
    import re  # noqa: PLC0415

    s = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?is)<body[^>]*>(.*)</body>", s)
    if m:
        s = m.group(1)
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?s)<!--.*?-->", " ", s)
    s = re.sub(BLOCK_TAGS, "\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = htmllib.unescape(s)
    return [u for u in (x.strip() for x in s.split("\n")) if u]


def missing_runs(units: list[str], pdf_text: str, win: int = 8) -> list[str]:
    """哪些块（或块内片段）没进 PDF 文本层——「被裁掉」的唯一直接证据。

    逐块去掉全部空白后按 win 字窗口做成员判定（与抽取顺序无关）。"""
    import re  # noqa: PLC0415

    b = re.sub(r"\s+", "", pdf_text)
    if len(b) < win:
        return []
    grams = {b[i:i + win] for i in range(len(b) - win + 1)}
    out: list[str] = []
    for unit in units:
        a = re.sub(r"\s+", "", unit)
        if not a:
            continue
        if len(a) < win:
            if a not in b:
                out.append(a)
            continue
        runs: list[str] = []
        start: int | None = None
        for i in range(len(a) - win + 1):
            if a[i:i + win] not in grams:
                if start is None:
                    start = i
            elif start is not None:
                runs.append(a[start:i + win - 1])
                start = None
        if start is not None:
            runs.append(a[start:])
        out.extend(runs)
    return out


def measure(pdf: pathlib.Path, html: pathlib.Path | None = None,
            text_check: bool = True) -> int:
    """量一张 PDF。返回 0 没问题 / 1 有问题。"""
    try:
        import pymupdf as fitz  # noqa: PLC0415
    except ImportError:  # 老版本只暴露 fitz
        import fitz  # type: ignore  # noqa: PLC0415

    doc = fitz.open(pdf)
    page = doc[0]
    height = page.rect.height

    lines = [
        (l["bbox"][1], l["bbox"][3],
         "".join(sp["text"] for sp in l["spans"]).strip(),
         l["bbox"][2] - l["bbox"][0])
        for b in page.get_text("dict")["blocks"]
        for l in b.get("lines", [])
        if "".join(sp["text"] for sp in l["spans"]).strip()
    ]
    if not lines:
        sys.exit(f"[FAIL] {pdf.name} 里没抽到文字")

    lines.sort(key=lambda x: x[1])
    bottom = lines[-1][1]
    margin = height - bottom
    top = lines[0][0]

    print(f"  页数      {doc.page_count}")
    print(f"  页高      {height:.1f} pt")
    print(f"  正文起    {top:.1f} pt")
    print(f"  末行底    {bottom:.1f} pt")
    print(f"  余量      {margin:+.1f} pt", "← 溢出被裁！" if margin < 0 else "")
    print(f"  末行内容  {lines[-1][2][:58]}")

    if doc.page_count > 1:
        print("  ⚠ 多于 1 页——初筛以单页为优，检查是不是内容真的放不下")

    bad = margin < 0
    if bad:
        print(f"  ✗ 溢出 {abs(margin):.1f}pt（约 {abs(margin) / LINE_PT:.1f} 行）")
    else:
        print(f"  ✓ 底部未溢出（余量 {margin:.1f}pt ≈ {margin / LINE_PT:.1f} 行）")

    if html is not None and text_check:
        pdf_text = "\n".join(p.get_text() for p in doc)
        runs = missing_runs(visible_units(html), pdf_text)
        if runs:
            print(f"  ✗ 有 {len(runs)} 处文字没进 PDF（被 overflow:hidden 裁掉，"
                  f"共 {sum(len(r) for r in runs)} 字）——底部余量量不出来：")
            for r in runs[:3]:
                print(f"      「{r[:56]}{'…' if len(r) > 56 else ''}」")
            bad = True
        else:
            print("  ✓ 文本完整：HTML 可见文字全部进了 PDF")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="量简历 PDF 有没有溢出被裁")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--name", help="成品基名（不含扩展名），如 刘宇广-AI交付工程师-2027届")
    g.add_argument("--all", action="store_true", help="遍历目录里全部成品")
    g.add_argument("--list", action="store_true", help="只列出成品与 PDF 状态")
    ap.add_argument("--html", help="直接指定 HTML（覆盖 --name 推导）")
    ap.add_argument("--pdf", help="直接指定 PDF（覆盖 --name 推导）")
    ap.add_argument("--export", action="store_true", help="先从 HTML 重导 PDF 再量")
    ap.add_argument("--no-text", dest="text", action="store_false",
                    help="跳过「HTML 可见文字是否全进 PDF」的完整性校验")
    args = ap.parse_args()
    if not args.list:
        _ensure_pymupdf()   # --list 只看文件，不必为此切解释器

    if args.list:
        pairs = list_pairs()
        if not pairs:
            print(f"没找到 {PATTERN}")
            return 1
        for stem, html, pdf in pairs:
            print(f"  {'✓' if pdf else '✗'} {stem}" + ("" if pdf else "   ← 缺 PDF（加 --export 生成）"))
        return 0

    if args.all:
        pairs = list_pairs()
        if not pairs:
            print(f"没找到 {PATTERN}")
            return 1
        bad, missing = [], []
        for stem, html, pdf in pairs:
            print(f"\n=== {stem} ===")
            target = html.with_suffix(".pdf")     # 新成品还没有 PDF，不能拿 pdf 的 None 去导出
            if args.export:
                export(html, target)
            elif pdf is None:
                print("  ✗ 缺 PDF —— 加 --export 生成")
                missing.append(stem)
                continue
            if measure(target, html, text_check=args.text):
                bad.append(stem)
        print(f"\n{'=' * 40}\n共 {len(pairs)} 份：{len(pairs) - len(bad) - len(missing)} 通过"
              f" / {len(bad)} 溢出 / {len(missing)} 缺 PDF")
        if bad:
            print("  溢出：" + "、".join(bad))
        if missing:
            print("  缺 PDF：" + "、".join(missing))
        return 1 if (bad or missing) else 0

    # 单份模式
    name = args.name or DEFAULT
    html = pathlib.Path(args.html) if args.html else HERE / f"{name}.html"
    pdf = pathlib.Path(args.pdf) if args.pdf else HERE / f"{name}.pdf"

    if not html.exists():
        sys.exit(f"[FAIL] 找不到 HTML：{html.name}（可用 --list 看现有成品）")
    if args.export:
        export(html, pdf)
    elif not pdf.exists():
        sys.exit(f"[FAIL] 找不到 PDF：{pdf.name} —— 加 --export 生成，或核对 --name")

    print(f"=== {html.stem} ===")
    return measure(pdf, html, text_check=args.text)


if __name__ == "__main__":
    raise SystemExit(main())
