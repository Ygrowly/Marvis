# -*- coding: utf-8 -*-
"""13 页一页通完整性审查（临时工具）。"""
import io, re, json, glob, os

OUT = os.path.dirname(os.path.abspath(__file__))

def extract_json(s, marker):
    i = s.find(marker)
    i = s.find('{', i)
    depth, j, instr, esc = 0, i, False, False
    while True:
        c = s[j]
        if instr:
            if esc:
                esc = False
            elif c == chr(92):
                esc = True
            elif c == '"':
                instr = False
        else:
            if c == '"':
                instr = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return s[i:j + 1]
        j += 1

ok = True
keys = {}
for p in sorted(glob.glob(os.path.join(OUT, '*-一页通.html'))):
    s = io.open(p, encoding='utf-8').read()
    name = os.path.basename(p)[:-len('-一页通.html')]
    raw = extract_json(s, 'var CARDS = ')
    # 手写页是 JS 字面量（键不带引号），先归一成严格 JSON
    raw = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*):', r'\1"\2":', raw)
    cards = json.loads(raw)
    order = json.loads(re.search(r'var ORDER = (\[[^\]]*\]);', s).group(1))
    key = re.search(r'var KEY = "([^"]+)"', s).group(1)
    issues = []
    if len(cards) != len(order):
        issues.append('CARDS %d != ORDER %d' % (len(cards), len(order)))
    if list(cards.keys()) != order:
        issues.append('键序 != ORDER')
    for k, c in cards.items():
        if not c.get('q') or not c.get('pts'):
            issues.append('%s 缺 q/pts' % k)
        if '待补' in c.get('crit', ''):
            issues.append('%s crit 待补' % k)
    if 'ONEPAGER-SCAFFOLD' in s:
        issues.append('仍带脚手架标记')
    todo = s.count('TODO：')
    t = re.search(r'<title>([^<]+)</title>', s).group(1)
    stat = 'OK' if not issues else '!! ' + '; '.join(issues)
    if issues:
        ok = False
    if key in keys:
        issues.append('KEY 重复: ' + keys[key])
        ok = False
    keys[key] = name
    print('%-9s key=%-26s cards=%2d todo=%-2d %s' % (name, key, len(order), todo, stat))
print('ALL OK' if ok else 'HAS ISSUES')
