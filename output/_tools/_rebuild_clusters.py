# -*- coding: utf-8 -*-
"""把 clusters.js 的簇从「档位分组」改成「模块 = 簇」：
   每个模块一条链，链内按主线序号 01→02→03 顺序推进（scanOne 本来就有
   「前一条到 L1 才解锁下一条」的门控，所以顺序由簇内数组序保证）。
   模块之间的先后 = 前面定好的优先级：一档十模块 → 二档三模块。"""
import re, io

SRC = r'E:/notes/Marvis/site/_data/clusters.js'
src = open(SRC, encoding='utf-8').read()

# 解析现有主线行
TOPIC_RE = re.compile(
    r"\{ id: '([^']+)', name: '([^']+)', href: '([^']*)',"
    r" cards: \[([^\]]*)\], pages: \[([^\]]*)\] \}")
topics = {}
for m in TOPIC_RE.finditer(src):
    tid, name, href, cards, pages = m.groups()
    topics[tid] = dict(id=tid, name=name, href=href, cards=cards, pages=pages)
print('解析到主线', len(topics), '条')

# 抓 pitch 簇（原样保留）
pitch = re.search(r"id: 'pitch'.*?topics: \[(.*?)\n    \]\n", src, re.S).group(0)
pitch_topics = re.search(r"id: 'pitch'.*?topics: \[(.*?)\n    \]", src, re.S).group(1)

MODULES = [
    ('llm',   'LLM 与上下文',     '一档'),
    ('mysql', 'MySQL',            '一档'),
    ('agent', 'Agent 运行时与工具', '一档'),
    ('redis', 'Redis 与缓存',      '一档'),
    ('rag',   'RAG 与检索',        '一档'),
    ('net',   '网络基础',          '一档'),
    ('eval',  '评测观测与治理',     '一档'),
    ('mq',    '消息队列',          '一档'),
    ('lock',  '并发与锁',          '一档'),
    ('linux', 'Linux 与部署',      '一档'),
    ('pg',    'PostgreSQL',       '二档'),
    ('os',    '操作系统',          '二档'),
    ('store', '数据存储选型',       '二档'),
]

def line_of(tid):
    return int(tid.split('-')[1])

out = []
total = 0
for pre, mname, zone in MODULES:
    mine = sorted([t for t in topics.values() if t['id'].split('-')[0] == pre],
                  key=lambda t: line_of(t['id']))
    assert mine, '模块 %s 没有主线' % pre
    rows = []
    for t in mine:
        n = line_of(t['id'])
        rows.append(
            "      { id: '%d', name: '%s', href: '%s', cards: [%s], pages: [%s] }"
            % (n, t['name'], t['href'], t['cards'], t['pages']))
    total += len(mine)
    out.append(
        "  {\n    id: '%s', name: '%s', zone: '%s',\n    topics: [\n%s\n    ]\n  }"
        % (pre, mname, zone, ',\n'.join(rows)))
print('模块主线合计', total)

HEADER = """/* 能力簇与主线清单 —— 进度页数据源
   约定：
   1. href = 站内 html 页面（site/ 下相对路径）。主线条目的 href 指向**主线页**
      （`modules/{模块}-NN-{主线}.html`）——那页第一节就是「本主线骨架」，是复述用的纸。
   2. cards = 这条主线下所有母题的 id；pages = 这些母题的单卡页（用来聚合断点）。
      两者为空的主线 = 还没建卡，不进派单池。
   3. 本表由脚本从 13 张模块卡抽取（output/_rebuild_clusters.py 重排过一次），
      改内容请改模块卡再重跑，别手写。

   ── 2026-09-25 改制：推进单位 = 一条主线 ─────────────────────
   真实学习流程：一次看完一条主线下**所有母题** → 大致背下 → 按完整回答骨架复述 →
   之后在不同时间节点回顾骨架再讲一遍。母题卡退成「教材 + 骨架」。

   ── 2026-09-25 晚再改：**簇 = 模块**，模块内严格按序号推进 ──────
   主人要求：派单按模块优先级走，但**每个模块都从它的第 01 条主线开始，按顺序**——
   后面的主线会用到前面的知识，跳着派等于派了个答不出来的题。
   所以一个模块 = 一个簇，簇内 topics 数组序就是序号序（01 → 02 → 03 …），
   progress.html 的 scanOne 有「前一条到「会了」(L1) 才解锁下一条」的门控，顺序由它保证。
   模块之间的先后 = 档位：一档十个模块（两周内必须能讲）走完，才派二档三个模块。
   档位内按完成率升序轮转（哪簇落得多先补哪簇），每天最多派 quota 条（1–4，看昨天表现）。

   ── 改这条表的规矩 ──────────────────────────────────────────
   **要扩母题先改模块卡，再回来加 pages；要加主线先改模块卡第 2 节。**
   母题范围以模块卡正本为准（`wiki/topics/{模块}/{模块}模块卡.md` 的「母题清单」节），
   否则进度页会挂出假欠账。改完必须跑 `node site/_tests/*.js` 三个回归测试。

   ── 项目线 ─────────────────────────────────────────────────
   `zone: '表达'` 的 pitch 簇不参与档位轮转，由 progress.html 单开板块每天派 1 条。
*/
window.MARVIS_CLUSTERS = [
%s
  {
    /* 项目线：本簇不进 zone 轮转，由 progress.html 单开「项目线」板块，每天派 1 条。
       proj 字段用来按项目分组显示进度——三个项目各 2 条
       （90 秒骨架 → 决策链，后者要等前者到 L2 才解锁）。 */
    id: 'pitch', name: '项目口述', zone: '表达',
    topics: [%s
    ]
  }
];
""" % (',\n'.join(out), pitch_topics)

# 原文件的日课段原样接在后面
drill = src[src.index('/* 独立日课'):]
open(SRC, 'w', encoding='utf-8', newline='\n').write(HEADER + '\n' + drill)
print('written', SRC)
