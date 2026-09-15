#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简历版面校验：导出的 PDF 有没有溢出被裁。

用法（在 output/resume/ 下）：
    python check_layout.py                       # 量当前 PDF
    python check_layout.py --export              # 先从 HTML 重导 PDF 再量

为什么要它：简历是固定 A4 + `overflow: hidden`——**溢出会被静默裁掉，页面看起来完全正常**。
只有渲染后的 PDF 才能证明有没有裁。这根尺子把「量一次」变成一条命令。

依赖：pymupdf（import fitz）。Edge 路径见 EDGE。
"""
from __future__ import annotations

import argparse
import pathlib
import io
import subprocess
import sys

# Windows 控制台默认 GBK，直接 print 中文/符号会崩
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTML = "刘宇广-AI应用开发-2027届.html"
PDF = "刘宇广-AI应用开发-2027届.pdf"
TMP = "_layout_tmp.pdf"          # Edge headless 写不进中文文件名，用 ASCII 中转
LINE_PT = 11.25                  # 正文行高（9pt × 1.25）——省一行的最小单位


def export() -> None:
    """HTML → PDF。中文路径会让 Edge 报「拒绝访问」，所以先写 ASCII 名再改名。"""
    here = pathlib.Path(__file__).parent.resolve()
    subprocess.run(
        [EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={here / TMP}", str(here / HTML)],
        capture_output=True, timeout=180, check=False,
    )
    tmp, out = here / TMP, here / PDF
    if not tmp.exists():
        sys.exit("[FAIL] 导出失败：Edge 没写出文件（检查 EDGE 路径）")
    out.unlink(missing_ok=True)
    tmp.rename(out)


def measure() -> int:
    import fitz  # noqa: PLC0415

    here = pathlib.Path(__file__).parent.resolve()
    doc = fitz.open(here / PDF)
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
        sys.exit("[FAIL] PDF 里没抽到文字")

    lines.sort(key=lambda x: x[1])
    bottom = lines[-1][1]
    margin = height - bottom
    top = lines[0][0]

    print(f"页数      {doc.page_count}")
    print(f"页高      {height:.1f} pt")
    print(f"正文起    {top:.1f} pt")
    print(f"末行底    {bottom:.1f} pt")
    print(f"余量      {margin:+.1f} pt", "← 溢出被裁！" if margin < 0 else "")
    print(f"末行内容  {lines[-1][2][:58]}")

    if doc.page_count > 1:
        print("\n⚠ 多于 1 页——初筛以单页为优，检查是不是内容真的放不下")
    if margin < 0:
        print(f"\n✗ 溢出 {abs(margin):.1f}pt（约 {abs(margin)/LINE_PT:.1f} 行）")
        return 1
    print(f"\n✓ 未溢出（余量 {margin:.1f}pt ≈ {margin/LINE_PT:.1f} 行）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", action="store_true", help="先从 HTML 重导 PDF 再量")
    args = ap.parse_args()
    if args.export:
        export()
    return measure()


if __name__ == "__main__":
    raise SystemExit(main())
