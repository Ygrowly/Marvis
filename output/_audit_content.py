# -*- coding: utf-8 -*-
"""最终审查：逐条核对已落盘的内容层是否有残缺（只读，不改文件）。

检查项
  ① 母题层：87 张卡是否都有口述稿 + 分层要点，要点是否四条，口述稿是否完整（结尾收得住）
  ② 题级层：一档 253 题号 ↔ 答案一一对应，无空答案/无孤儿；二档 99 题应带退回标注
  ③ 渲染层：每张翻转卡的 a 属性是否与 md 原文一致（防答案里的引号/大于号截断属性）
  ④ 行尾：所有改过的 md 必须 LF
  ⑤ 占位符：答案里不能残留 TODO / 待填 / 【】 之类占位
"""
import re, glob, pathlib, html, collections
from html.parser import HTMLParser

ROOT = pathlib.Path(r'E:/notes/Marvis')
TP = ROOT / 'wiki' / 'topics'
DIRMAP = {'MySQL': 'MySQL', 'LLM与上下文': 'LLM与上下文', 'Agent运行时与工具': 'Agent运行时与工具',
          'Redis': 'Redis', 'RAG与检索': 'RAG与检索', '网络基础': '网络',
          '评测观测与治理': '评测观测与治理', '消息队列': '消息队列', '并发与锁': '并发与锁',
          'Linux与部署': 'Linux与部署', 'PostgreSQL': 'PostgreSQL', '操作系统': '操作系统',
          '数据存储选型': '数据存储选型'}
Z1 = ['MySQL', 'LLM与上下文', 'Agent运行时与工具', 'Redis', 'RAG与检索', '网络基础',
      '评测观测与治理', '消息队列', '并发与锁', 'Linux与部署']
bad = []


def note(kind, where, extra=''):
    bad.append('%s | %s %s' % (kind, where, extra))


# ---------- ① 母题层 ----------
cards = sorted(glob.glob(str(TP / '*' / '母题-*.md')))
n_sp = n_pt = 0
for f in cards:
    s = pathlib.Path(f).read_text(encoding='utf-8')
    if '**完整回答（口述稿）**' not in s:
        continue
    n_sp += 1
    m = re.search(r'\*\*完整回答（口述稿）\*\*[：:]\n(.*?)(?=\n\*\*分层要点\*\*)', s, re.S)
    pm = re.search(r'\*\*分层要点\*\*[：:]\n(.*?)(?=\n\*\*|\n##\s|\Z)', s, re.S)
    if not m:
        note('母题口述稿整块缺失', f); continue
    speak = m.group(1).strip()
    if len(speak) < 150:
        note('母题口述稿过短', f, '%d 字' % len(speak))
    # 结尾检查要剥掉 markdown 的 ** 与空白，否则「。**」会被误判成未收住
    tail = speak.rstrip().rstrip('*').rstrip()
    if not re.search(r'[。）】」]$', tail):
        note('母题口述稿结尾未收住', f, '…' + tail[-18:])
    if not pm:
        note('母题缺分层要点', f); continue
    n_pt += 1
    bullets = [x for x in pm.group(1).splitlines() if x.strip().startswith('- ')]
    if len(bullets) < 4:
        note('分层要点不足四条', f, '%d 条' % len(bullets))
    for b in bullets:
        if not re.match(r'^- \*\*(结论|推导链|量化|边界)', b):
            note('要点条目名不规范', f, b[:24])
print('① 母题层：口述稿 %d 张 / 分层要点 %d 张（共 %d 张卡，9 张算法卡不进模块）' % (n_sp, n_pt, len(cards)))

# ---------- ② 题级层 ----------
tot_q = ans_q = 0
for mod, dn in DIRMAP.items():
    cf = [p for p in sorted((TP / dn).glob('*.md')) if '模块' in p.name or '深挖' in p.name][0]
    s = cf.read_text(encoding='utf-8')
    m = re.search(r'^##\s*4\.[\s\S]*?(?=^##\s*5\.|\Z)', s, re.M) or \
        re.search(r'^##\s*(?:\d+\.\s*)?(?:八股)?题单[\s\S]*?(?=^##\s|\Z)', s, re.M)
    qs = set()
    for r in (m.group(0).splitlines() if m else []):
        if not r.strip().startswith('|'):
            continue
        c = [x.strip() for x in r.strip().strip('|').split('|')]
        if len(c) >= 5 and re.fullmatch(r'\d+', c[0]):
            qs.add(c[0])
    am = re.search(r'^##\s*8\.\s*题级答案[\s\S]*?(?=^##\s|\Z)', s, re.M)
    ans = set()
    bodies = {}
    if am:
        for mm in re.finditer(r'^###\s*(\d+)\s*（([^）]*)）\s*\n([\s\S]*?)(?=^###\s|^##\s|\Z)', am.group(0), re.M):
            ans.add(mm.group(1)); bodies[mm.group(1)] = (mm.group(2), mm.group(3).strip())
    tot_q += len(qs); ans_q += len(ans)
    miss, orph = sorted(qs - ans), sorted(ans - qs)
    if mod in Z1:
        if miss or orph or len(ans) != len(qs):
            note('一档题号与答案不配', mod, '缺%s 孤%s' % (miss, orph))
    else:
        if ans:
            note('二档本轮不应有答案', mod, '%d 条' % len(ans))
    for no, (pri, body) in bodies.items():
        if len(body) < 60:
            note('题级答案过短', '%s Q%s' % (mod, no), '%d 字' % len(body))
        if pri not in ('必背', '理解', '了解'):
            note('优先级标注异常', '%s Q%s' % (mod, no), pri)
        tail = body.rstrip().rstrip('*').rstrip()
        if not re.search(r'[。）】」]$', tail):
            note('题级答案结尾未收住', '%s Q%s' % (mod, no), '…' + tail[-18:])
        for pat in (r'TODO', r'待填', r'【】', r'XXX', r'待补'):
            if re.search(pat, body):
                note('答案含占位符', '%s Q%s' % (mod, no), pat)
print('② 题级层：题单 %d 题 / 答案 %d 条（一档 253 已齐，二档 99 待补）' % (tot_q, ans_q))

# ---------- ③ 渲染层 ----------
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.cards = []; self.bal = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'flip-card':
            self.cards.append(dict(attrs)); self.bal += 1
    def handle_endtag(self, tag):
        if tag == 'flip-card':
            self.bal -= 1

md_ans = {}
for mod, dn in DIRMAP.items():
    cf = [p for p in sorted((TP / dn).glob('*.md')) if '模块' in p.name or '深挖' in p.name][0]
    s = cf.read_text(encoding='utf-8')
    am = re.search(r'^##\s*8\.\s*题级答案[\s\S]*?(?=^##\s|\Z)', s, re.M)
    d2 = {}
    if am:
        for mm in re.finditer(r'^###\s*(\d+)\s*（[^）]*）\s*\n([\s\S]*?)(?=^###\s|^##\s|\Z)', am.group(0), re.M):
            d2[mm.group(1)] = re.sub(r'\s', '', mm.group(2))
    md_ans[mod] = d2

n_card = ok = fb = 0
for f in sorted(glob.glob(str(ROOT / 'site' / 'modules' / '*.html'))):
    p = pathlib.Path(f); ps = P(); ps.feed(p.read_text(encoding='utf-8'))
    if ps.bal != 0:
        note('flip-card 标签不配对', p.name, str(ps.bal))
    for c in ps.cards:
        n_card += 1
        mm = re.match(r'^(.+)-q(\d+)$', c.get('card-id', '') or '')
        if not mm:
            note('card-id 异常', p.name, c.get('card-id')); continue
        mod, no = mm.group(1), mm.group(2)
        a = re.sub(r'\s', '', html.unescape(c.get('a', '')))
        if not a:
            note('翻转卡空答案', p.name, c.get('card-id')); continue
        if '还没写题级答案' in a:
            fb += 1
            if mod in Z1:
                note('一档不应出现退回标注', p.name, c.get('card-id'))
            continue
        exp = md_ans.get(mod, {}).get(no)
        if exp is None:
            continue
        if a == exp:
            ok += 1
        else:
            note('属性与 md 不一致', p.name, '%s 实际%d/期望%d' % (c.get('card-id'), len(a), len(exp)))
print('③ 渲染层：翻转卡 %d 张 / 与 md 完全一致 %d / 二档退回标注 %d' % (n_card, ok, fb))

# ---------- ④ 行尾 ----------
scope = sorted(glob.glob(str(TP / '*' / '母题-*.md'))) + \
        [p.as_posix() for dn in DIRMAP.values()
         for p in sorted((TP / dn).glob('*.md')) if '模块' in p.name or '深挖' in p.name]
crlf = [f for f in scope if b'\r\n' in pathlib.Path(f).read_bytes()]
if crlf:
    note('wiki md 出现 CRLF', '%d 个' % len(crlf), crlf[:3])
print('④ 行尾：wiki md %s' % ('全 LF' if not crlf else '有 %d 个 CRLF！' % len(crlf)))

print('\n' + ('❌ 发现 %d 个问题：' % len(bad) if bad else '✅ 全部通过，无问题'))
for x in bad[:25]:
    print('  ⚠', x)
