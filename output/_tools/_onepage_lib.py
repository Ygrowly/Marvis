# -*- coding: utf-8 -*-
"""一页通定稿公共库：被 _finish_*.py 引用，统一「脚手架 → 定稿」的补丁逻辑。

内容一律用 f-string / 拼接构造 SVG，避免 %-format 的占位符踩坑。
"""
import io, os

OUT = os.path.dirname(os.path.abspath(__file__))

B, O, P_, G = '#1664FF', '#F59E0B', '#8B5CF6', '#22C55E'
BD, OD, PD, GD = '#0E42B5', '#B45309', '#6D28D9', '#15803D'
BS, OS, PS, GS = '#E8F0FF', '#FEF3D6', '#F1ECFE', '#E8F8EE'
RD = '#B42318'
TX, TX2, TX3, GREY, LINE = '#1D2129', '#4E5969', '#86909C', '#86909C', '#E5E6EB'

SVG_DEFS = f'''<defs>
      <marker id="mB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{B}"/></marker>
      <marker id="mO" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{O}"/></marker>
      <marker id="mP" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{P_}"/></marker>
      <marker id="mG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{G}"/></marker>
      <filter id="sh" x="-20%" y="-20%" width="140%" height="150%">
        <feDropShadow dx="0" dy="1.5" stdDeviation="2.4" flood-color="#0E42B5" flood-opacity="0.10"/>
      </filter>
    </defs>'''


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def box(x, y, w, h, fill, stroke, title, tcol, lines, accent, accent_col=OD):
    """内容框：title + 若干正文行 + 底部橙色强调行。lines 每行 ~w/11.5 个全角字符内。"""
    ys = [24, 46, 66] if h >= 100 else [22, 42, 60]
    step = 19 if h >= 100 else 18
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>']
    out.append(f'<text x="{x + 16}" y="{y + ys[0]}" font-size="13" font-weight="800" fill="{tcol}">{title}</text>')
    yy = ys[1]
    for ln in lines:
        out.append(f'<text x="{x + 16}" y="{y + yy}" font-size="11.5" fill="{TX2}">{ln}</text>')
        yy += step
    out.append(f'<text x="{x + 16}" y="{y + (86 if h >= 100 else 78)}" font-size="10.5" font-weight="700" fill="{accent_col}">{accent}</text>')
    return '\n    '.join(out)


def legend(items, y=24, w=1100, x=180):
    """图例条。items: [(color, marker_id, text), ...] 均匀分布。"""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="56" rx="10" fill="#fff" stroke="{LINE}"/>']
    n = len(items)
    slot = w // n
    for i, (col, mk, txt) in enumerate(items):
        lx = x + slot * i + 44
        ly = y + 28
        out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 24}" y2="{ly}" stroke="{col}" stroke-width="2.4" marker-end="url(#{mk})"/>')
        out.append(f'<text x="{lx + 34}" y="{ly + 4}" font-size="11" fill="{TX2}">{txt}</text>')
    return '\n    '.join(out)


def finish(mod, headline, sec01_title, sec01_sub, svg01, story, cap, rows,
           sec04_title, sec04_sub, sec04_src, svg04, nums, mis, crits,
           mis_title='八句最容易说错的话', done_note='01/04/05 手写，02/06 机制与判据人工校订'):
    """把脚手架补成定稿页。rows: (k, what, mechanism, qnums, evidence)；nums: (color,t,big,d)；mis: (x, v)。"""
    p = os.path.join(OUT, mod + '-一页通.html')
    s = io.open(p, encoding='utf-8').read()
    assert 'ONEPAGER-SCAFFOLD' in s, mod + ' 不是脚手架页（或已定稿）'

    def cut(s_, a, b_):
        i = s_.find(a)
        j = s_.find(b_)
        assert 0 <= i < j, (mod, a)
        return i, j

    # 页头一条线
    i = s.find('<small>')
    j = s.find('</small>') + len('</small>')
    s = s[:i] + f'<small>{headline}</small>' + s[j:]

    # 01 节
    i, j = cut(s, '<!-- 01 主干图 -->', '<!-- 02 检索表 -->')
    sec01 = (f'<!-- 01 主干图 -->\n<section class="lv-quick">\n'
             f'  <h2><span class="num">01</span>{sec01_title}<span class="src">正本 wiki/topics/{mod}/</span></h2>\n'
             f'  <div class="h2sub">{sec01_sub}</div>\n  <div class="fig">\n  {svg01}\n  </div>\n'
             f'  <div class="story">\n{story}\n  </div>\n  <div class="cap">{cap}</div>\n</section>')
    s = s[:i] + sec01 + '\n' + s[j:]

    # 02 tbody
    i = s.find('<tbody>')
    j = s.find('</tbody>') + len('</tbody>')
    body = '\n'.join(
        f'      <tr><td class="k">{k}</td><td>{what}</td><td class="ans"><span class="a">{mech}</span></td>'
        f'<td>{qn}</td><td class="ans"><span class="a">{ev}</span></td></tr>'
        for k, what, mech, qn, ev in rows)
    s = s[:i] + '<tbody>\n' + body + '\n    </tbody>' + s[j:]

    # 04 节
    i, j = cut(s, '<!-- 04 第二张图 -->', '<!-- 05 数字板 -->')
    sec04 = (f'<!-- 04 两笔账 -->\n<section class="lv-deep">\n'
             f'  <h2><span class="num">04</span>{sec04_title}<span class="src">{sec04_src}</span></h2>\n'
             f'  <div class="h2sub">{sec04_sub}</div>\n  <div class="fig">\n  {svg04}\n  </div>\n</section>')
    s = s[:i] + sec04 + '\n' + s[j:]

    # 05 数字板
    nums_html = '\n'.join(
        f'    <div class="ncard {c}"><div class="t">{t}</div><div class="big">{big}</div>\n      <div class="d">{d}</div></div>'
        for c, t, big, d in nums)
    i = s.find('<div class="nums">')
    j = s.find('</section>', i)
    s = s[:i] + f'<div class="nums">\n{nums_html}\n  </div>\n' + s[j:]

    # 06 误判
    mis_html = '\n'.join(
        f'    <div class="mrow"><span class="x">{x}</span><span class="v">{v}</span></div>' for x, v in mis)
    i = s.find('<div class="mis">')
    j = s.find('</section>', i)
    block = s[i:j]
    end = block.rfind('</div>')
    s = s[:i] + f'<div class="mis">\n{mis_html}\n  </div>\n' + s[i + end:]
    old_t = '<span class="num">06</span>最容易说错的话'
    assert s.count(old_t) == 1
    s = s.replace(old_t, f'<span class="num">06</span>{mis_title}')

    # 判据（按 ORDER 顺序替换待补）
    need = '（待补：母题卡缺「通过判据」）'
    assert s.count(need) == len(crits), f'{mod}: crit 待补 {s.count(need)} != {len(crits)}'
    for c in crits:
        s = s.replace('"' + need + '"', '"' + c + '"', 1)

    # 标记
    i = s.find('<!-- ONEPAGER-SCAFFOLD')
    j = s.find('-->', i) + 3
    s = s[:i] + f'<!-- 定稿 2026-10-03 · 脚手架补全：{done_note} -->' + s[j:]

    io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
    print('finished', mod, len(s), 'chars')
