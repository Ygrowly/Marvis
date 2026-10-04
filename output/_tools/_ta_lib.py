# -*- coding: utf-8 -*-
"""母题级「完整回答（口述稿）+ 分层要点」通用写入工具（2026-09-28）。

用法：
    from _ta_lib import write_topic
    write_topic('LLM与上下文', {
        'C1': ('口述稿…', '- **结论**：…\n- **推导链**：…\n- **量化**：…\n- **边界与常见误解**：…'),
        …
    })

落盘：wiki/topics/<模块>/母题-<id>-*.md 的「三、面试输出」里，
插在 `**完整回答骨架**` 之后；幂等（已有则整块替换）。
md 一律 LF。字段与 MySQL 那批完全一致（**完整回答（口述稿）** / **分层要点**）。
"""
import re, pathlib

ROOT = pathlib.Path(r'E:/notes/Marvis')


def write_topic(module, A):
    d = ROOT / 'wiki' / 'topics' / module
    for tid in sorted(A):
        fs = sorted(d.glob('母题-%s-*.md' % tid))
        assert len(fs) == 1, (module, tid, fs)
        p = fs[0]
        s = p.read_text(encoding='utf-8')
        assert '\r\n' not in s, 'md 必须 LF：%s' % p
        speak, points = A[tid]
        sp = '**完整回答（口述稿）**：\n' + speak
        pt = '**分层要点**：\n' + points
        if '**完整回答（口述稿）**' in s:
            s2, n1 = re.subn(r'\*\*完整回答（口述稿）\*\*[：:]\n.*?(?=\n\*\*分层要点\*\*)', sp, s, flags=re.S)
            assert n1 == 1, '口述稿替换失败：%s' % p
            s2, n2 = re.subn(r'\*\*分层要点\*\*[：:]\n.*?(?=\n\*\*|\n##\s|\Z)', pt, s2, flags=re.S)
            assert n2 == 1, '要点替换失败：%s' % p
        else:
            m = re.search(r'^\*\*完整回答骨架\*\*[：:].*$', s, re.M)
            assert m, '没找到骨架行：%s' % p
            s2 = s[:m.end()] + '\n\n' + sp + '\n\n' + pt + s[m.end():]
        p.write_text(s2, encoding='utf-8', newline='')
    n = len(A)
    tot = sum(len(re.sub(r'\s', '', a[0])) for a in A.values())
    print('  %s：%d 张母题（口述稿合计实测 %d 字）' % (module, n, tot))
    return n
