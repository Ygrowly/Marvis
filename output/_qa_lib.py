# -*- coding: utf-8 -*-
"""题级答案写入工具（2026-09-26）。

用法：在数据脚本里 `from _qa_lib import write_module`，然后
    write_module('LLM与上下文', {1: ('必背', '答案…'), …})

落盘位置：wiki/topics/<模块>/<模块>模块卡.md（或 模块深挖卡.md）的**第 8 节「题级答案」**：
    ## 8. 题级答案（「本主线的题」翻转卡背面 · 先说后翻）
    ### <题号> （必背|理解|了解）
    <答案>
幂等：整节替换。md 一律 LF。
"""
import re, pathlib

ROOT = pathlib.Path(r'E:/notes/Marvis')

TITLE = """## 8. 题级答案（「本主线的题」翻转卡背面 · 先说后翻）

> 题号与第 4 节题单一一对应。**必背**题写成能直接说出口的一段话；**理解 / 了解**题写 1–3 句。
> 翻转卡背面先给这道题的答案，再挂上「所属母题的完整回答（口述稿）」与单卡入口——两段合起来才是深挖。
"""


def _card_file(module):
    d = ROOT / 'wiki' / 'topics' / module
    for name in ('%s模块深挖卡.md' % module, '%s模块卡.md' % module):
        p = d / name
        if p.exists():
            return p
    # 兜底：目录下第一个 *模块*卡.md
    for p in sorted(d.glob('*模块*卡.md')):
        return p
    raise FileNotFoundError('找不到模块卡：%s' % module)


def write_module(module, A, dry=False):
    p = _card_file(module)
    s = p.read_text(encoding='utf-8')
    assert '\r\n' not in s, '模块卡 md 必须是 LF：%s' % p
    body = TITLE
    for no in sorted(A):
        pri, ans = A[no]
        body += "\n### %d （%s）\n%s\n" % (no, pri, ans)
    if '## 8. 题级答案' in s:
        s2 = re.sub(r'## 8\. 题级答案[\s\S]*?(?=^## 关联|^---\s*$|\Z)', body + '\n', s, flags=re.M)
    else:
        m = re.search(r'^## 关联', s, re.M)
        s2 = (s[:m.start()] + body + '\n' + s[m.start():]) if m else (s.rstrip() + '\n\n' + body)
    if not dry:
        p.write_text(s2, encoding='utf-8', newline='')
    n = len(A)
    tot = sum(len(re.sub(r'\s', '', a)) for _, a in A.values())
    must = sum(1 for pri, _ in A.values() if pri == '必背')
    print('  %s：写入 %d 题（必背 %d），实测 %d 字 → %s' % (module, n, must, tot, p.name))
    return n
