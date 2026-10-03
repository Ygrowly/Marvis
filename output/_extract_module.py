# -*- coding: utf-8 -*-
# 可复用：把某个模块的模块卡 + 所有母题卡，抽成「够写一页复习舱」的紧凑素材
# 用法：python _extract_module.py <topics下的模块目录名> [教材每节字符上限]
import os, re, sys, io

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wiki', 'topics')

def read(p):
    return io.open(p, encoding='utf-8').read()

def module_card(d):
    # 模块卡文件名不统一（xx模块卡.md / xx模块深挖卡.md），优先取含「模块」且非母题卡的 md
    cands = [f for f in os.listdir(os.path.join(BASE, d))
            if f.endswith('.md') and not f.startswith('母题-') and '模块' in f]
    if not cands:
        cands = [f for f in os.listdir(os.path.join(BASE, d))
                if f.endswith('.md') and not f.startswith('母题-')]
    if not cands:
        return '（该模块目录下没有模块卡 md）'
    s = read(os.path.join(BASE, d, sorted(cands)[0]))
    out = []
    # 只要 0 边界 / 2 主线 / 3 母题 / 4 题单 / 5 项目映射 / 6 验收门 / 8 题级答案
    for marker in ['## 0.', '## 2.', '## 3.', '## 4.', '## 5.', '## 6.', '## 8.']:
        i = s.find(marker)
        if i < 0: continue
        j = s.find('\n## ', i + 5)
        out.append(s[i:j if j > 0 else len(s)].strip())
    return '\n\n'.join(out)

def tagged(sec, cap):
    """抽取带标签的关键句：每个标签取后面的一句话（到句号/换行为止）"""
    lines = []
    for m in re.finditer(r'【(事实|推导|推论|结论|取舍|推断|补充)】([\s\S]{0,%d}?)(?=【|$)' % cap, sec):
        t = ' '.join(m.group(2).split())
        t = re.sub(r'\[\[|\]\]', '', t)
        t = re.sub(r'\*\*', '', t)
        if len(t) > 12:
            # 截到第一个句号后 1 句，避免过长
            cut = re.match(r'(.{10,220}?[。！？])', t)
            lines.append((m.group(1), cut.group(1) if cut else t[:220]))
    return lines

def card(path, cap):
    s = read(path)
    t = re.search(r'## 一、教材(.*?)\n## 二、自测', s, re.S)
    body = t.group(1) if t else ''
    out = ['\n### 卡: ' + os.path.basename(path)]
    for sec in re.split(r'\n### ', body)[1:]:
        title = sec.split('\n')[0].strip()
        out.append('  · ' + title)
        for tag, sent in tagged(sec, 260)[:3]:
            out.append('      [%s] %s' % (tag, sent))
    # 自测：题头 + 问句 + 纠错原话
    st = re.search(r'## 二、自测(.*?)\n## 三、', s, re.S)
    if st:
        out.append('  · 自测题')
        for q in re.finditer(r'\*\*Q(\d)（([^）]+)）\*\*(.{0,500}?)\*\*A\1\*\*', st.group(1), re.S):
            seg = q.group(3)
            head = re.search(r'\*\*：(.{0,160}?)(?:\n|问)', seg, re.S)
            w = re.search(r'问：(.{0,160}?)(?:\n|\*\*)', seg, re.S)
            quote = re.findall(r'^> (.+)$', seg, re.M)
            txt = (head.group(1).strip() if head else '') or (w.group(1).strip() if w else '')
            if txt: out.append('      Q%s(%s): %s' % (q.group(1), q.group(2), ' '.join(txt.split())[:150]))
            for x in quote[:1]:
                out.append('      原话: ' + ' '.join(x.split())[:150])
    m = re.search(r'\*\*通过证据\*\*：(.*?)\n', s, re.S)
    out.append('  · 判据: ' + (' '.join(m.group(1).split()) if m else 'NONE'))
    return '\n'.join(out)

if __name__ == '__main__':
    d = sys.argv[1]
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 260
    print('#' * 30 + ' 模块卡 ')
    print(module_card(d))
    files = sorted(f for f in os.listdir(os.path.join(BASE, d)) if f.startswith('母题-'))
    for f in files:
        print('\n' + '#' * 30)
        print(card(os.path.join(BASE, d, f), cap))
