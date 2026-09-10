# -*- coding: utf-8 -*-
"""Marvis 卡片构建器

扫描 md 里的 ::card 块，生成 site/_data/deck.json 与 deck.js。
单向流：md 正本 -> deck.json/js -> html 页面。html 永不回写 md。

用法：
    python site/build.py

卡片写法（可写在任何被扫描的 md 里）：
    ::card id=lru-01 tag=算法
    Q: 问题
    A: 答案，可以
       换多行
    ::end
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
OUT_DIR = SITE / "_data"

# 扫描范围：卡片可以内联在笔记里，不必集中放
SCAN_DIRS = [
    "site/cards",
    "wiki/topics/算法",
    "study",
    "wiki/interview",
    "wiki/topics",
    "wiki/thinking",
    "projects",
]

CARD_RE = re.compile(r"^::card\s+id=(?P<id>\S+)(?:\s+tag=(?P<tag>\S+))?\s*$")


def parse_file(path: Path):
    cards, cur, field = [], None, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        m = CARD_RE.match(line)
        if m:
            if cur:
                cards.append(cur)
            cur = {
                "id": m.group("id"),
                "tag": m.group("tag") or "未分类",
                "q": "",
                "a": "",
                "src": path.relative_to(ROOT).as_posix(),
            }
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
            field = "q"
            cur["q"] += line[2:].lstrip()
        elif line.startswith("A:"):
            field = "a"
            cur["a"] += line[2:].lstrip()
        elif field:
            cur[field] += "\n" + line.strip()
    if cur:
        cards.append(cur)
    return cards


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cards, seen = [], set()

    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            if OUT_DIR in p.parents:
                continue
            for c in parse_file(p):
                if not c["q"] or not c["a"]:
                    print("[skip] %s 缺 Q 或 A (%s)" % (c["id"], c["src"]))
                    continue
                if c["id"] in seen:
                    print("[dup ] %s 重复，已跳过 (%s)" % (c["id"], c["src"]))
                    continue
                seen.add(c["id"])
                cards.append(c)

    (OUT_DIR / "deck.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # deck.js 供 file:// 直接打开（fetch 本地 json 会被 CORS 拦）
    (OUT_DIR / "deck.js").write_text(
        "window.MARVIS_DECK = " + json.dumps(cards, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    print("卡片 %d 张 -> %s" % (len(cards), (OUT_DIR / "deck.json").as_posix()))
    by_tag = {}
    for c in cards:
        by_tag.setdefault(c["tag"], []).append(c["id"])
    for tag in sorted(by_tag):
        print("  [%s] %s" % (tag, " ".join(by_tag[tag])))


if __name__ == "__main__":
    main()
