# -*- coding: utf-8 -*-
"""把 MySQL-一页通.html 脚手架补成定稿页（一次性工具，跑完即删）。

替换：页头一条线 / 01 主干图 SVG + 主干叙事 / 02 检索表 17 行 / 04 两笔账 / 05 数字板 / 06 误判 / JS 判据。
"""
import io, re, sys, os

OUT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(OUT, 'MySQL-一页通.html')
s = io.open(P, encoding='utf-8').read()
assert 'ONEPAGER-SCAFFOLD' in s, '不是脚手架页'

B, O, P_, G = '#1664FF', '#F59E0B', '#8B5CF6', '#22C55E'
BD, OD, PD, GD = '#0E42B5', '#B45309', '#6D28D9', '#15803D'
BS, OS, PS, GS = '#E8F0FF', '#FEF3D6', '#F1ECFE', '#E8F8EE'
TX2, GREY, LINE = '#4E5969', '#86909C', '#E5E6EB'


def box(x, y, w, h, fill, stroke, title, tcol, lines, accent):
    """lines: list[str]; accent 最后一行橙色加粗"""
    ys = [24, 46, 66] if h >= 100 else [22, 42, 60]
    out = [u'<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>'
           % (x, y, w, h, fill, stroke)]
    out.append(u'<text x="%d" y="%d" font-size="13" font-weight="800" fill="%s">%s</text>'
               % (x + 16, y + ys[0], tcol, title))
    yy = ys[1]
    for ln in lines:
        out.append(u'<text x="%d" y="%d" font-size="11.5" fill="%s">%s</text>' % (x + 16, y + yy, TX2, ln))
        yy += 19 if h >= 100 else 18
    out.append(u'<text x="%d" y="%d" font-size="10.5" font-weight="700" fill="%s">%s</text>'
               % (x + 16, y + (86 if h >= 100 else 78), OD, accent))
    return u'\n    '.join(out)


# ---------------------------------------------------------------- 01 主干图
L1 = [
    box(90, 100, 230, 100, BS, B, u'表设计基本盘（M5）', BD,
        [u'引擎 InnoDB：并发写+不丢', u'主键自增；UUID 扇出→390'],
        u'页数翻倍 → 缓存减半'),
    box(350, 100, 230, 100, BS, B, u'B+ 树（M1）', BD,
        [u'16KB 页 → 扇出 ≈1170', u'3 层装 2000 万行 = 3 次 IO'],
        u'哈希无范围；红黑树 IO 多'),
    box(610, 100, 230, 100, BS, B, u'联合索引（M2）', BD,
        [u'字典序连续区间 → 最左前缀', u'顺序不同，扫描量差 30 倍'],
        u'ICP 省回表，不省扫描'),
    box(870, 100, 230, 100, BS, B, u'聚簇 / 回表（M3）', BD,
        [u'二级叶子 = 主键 → 必回表', u'回表随命中行数线性涨'],
        u'覆盖索引：Using index'),
    box(1130, 100, 230, 100, BS, B, u'索引代价 / DDL（M4）', BD,
        [u'读的快照、写的负债', u'每次写要维护 N 棵 B+ 树'],
        u'DDL 危险 = 不可控等待；影子表'),
]
L2 = [
    box(90, 260, 620, 100, OS, O, u'SQL 执行五层（M6）', u'#1D2129',
        [u'连接器 → 分析器 → 优化器 → 执行器 → 引擎层；五层里只有优化器在做决定',
         u'SQL 慢的第一嫌疑人 = 优化器估算错（一次可放大 50 倍）——先查统计信息再动手'],
        u'查询缓存死于「以表为粒度失效」——写多的表上任何整体失效缓存都不成立'),
    box(740, 260, 620, 100, OS, O, u'慢查询优化（M7）', u'#1D2129',
        [u'少扫（最左前缀 / 避开大偏移）· 少回（覆盖 / ICP）· 少排（索引序匹配 ORDER BY）',
         u'深分页代价 = 偏移量线性涨：第 100 万页是第 1 页的 10 万倍'],
        u'有时全表扫是优化器的正确决定——先分清「写法问题」还是「成本判断」'),
]
L3 = [
    box(90, 420, 400, 100, PS, P_, u'隔离级别与 ACID（M8）', PD,
        [u'谱系单调：RU → RC → RR → 串行化', u'A=undo · D=redo · I=锁+MVCC · C 是结果'],
        u'MVCC 把读摘出冲突：冲突面 ≈1%；串行化还回 19%'),
    box(515, 420, 400, 100, PS, P_, u'MVCC（M9）', PD,
        [u'undo 版本链 + ReadView 判可见性', u'RC / RR 只差生成时机（每语句 / 首次）'],
        u'回收看最老 ReadView → 长事务让全库回收停摆'),
    box(940, 420, 400, 100, PS, P_, u'锁与死锁（M10）', PD,
        [u'锁的可寻址对象只有索引项——无索引 = 锁全表', u'Record → Gap → Next-Key（防插入+护已有）'],
        u'死锁 = 顺序不一致成环；InnoDB 回滚代价小者，报错 ≠ 挂库'),
]
L4 = [
    box(90, 580, 400, 100, '#fff', P_, u'三日志与 2PC（M11）', PD,
        [u'WAL：随机页写 → 顺序日志写（差 2–3 个数量级）', u'redo 环形 + checkpoint；binlog 管复制/回档（Row）'],
        u'redo+binlog 分属两组件 → 2PC 捆成原子，否则崩溃窗口造主从不一致'),
    box(515, 580, 400, 100, '#fff', P_, u'崩溃恢复（M12）', PD,
        [u'崩溃瞬间三态，日志痕迹决定动作', u'先 redo 重放（幂等）再 undo 回滚——反了丢已提交'],
        u'prepare 态由 2PC 裁决：恢复与主从一致在同一处收口'),
    box(940, 580, 400, 100, '#fff', P_, u'长事务（M13）', PD,
        [u'按住两样：全库 undo 回收边界（只读也按）+ 锁', u'72 ms：只读事务让别人读一行慢 72ms'],
        u'分批同时治锁 / undo / 主从延迟 / 数据增长'),
]
L5 = [
    box(250, 740, 550, 100, GS, G, u'主从复制（M14）', GD,
        [u'复制的是 binlog 变更流，不是数据页', u'主写 &gt; 从放 → 延迟结构性累积（并行按库 → WRITESET）'],
        u'半同步治「丢不丢」（RPO），不治「读到旧」'),
    box(850, 740, 550, 100, GS, G, u'数据增长（M15）', GD,
        [u'「8000 万行」先定位症状再动手', u'索引 → 冷热分离 → 归档 → 读写分离 → 分表（贵且难回头放最后）'],
        u'分片键 = 查询形状的属性——整套设计里最难改的决定'),
]
L6 = [
    box(250, 900, 550, 90, OS, O, u'乐观 vs 悲观锁（M16）', u'#1D2129',
        [u'第一句报冲突频率，第二句才谈机制', u'高冲突：乐观 N² vs 悲观 N——差 N 倍'],
        u'影响行数 0 = 业务分支：读权威快照再判定，不无脑重试'),
    box(850, 900, 550, 90, OS, O, u'排行榜 / 防超卖（M17）', u'#1D2129',
        [u'ZSet 把排名内建进结构：O(logN) vs MySQL O(N)', u'防超卖 = 判断下推进原子操作（条件更新）'],
        u'强一致（钱）走 DB 原子更新；高并发 Redis 前置 + DB 兜底'),
]

SVG01 = u"""<svg viewBox="0 0 1450 1010" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="MySQL 主干图">
    <defs>
      <marker id="mB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>
      <marker id="mG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>
      <filter id="sh" x="-20%%" y="-20%%" width="140%%" height="150%%">
        <feDropShadow dx="0" dy="1.5" stdDeviation="2.4" flood-color="#0E42B5" flood-opacity="0.10"/>
      </filter>
    </defs>

    <rect x="180" y="24" width="1100" height="56" rx="10" fill="#fff" stroke="%s"/>
    <g font-size="11" fill="%s">
      <line x1="230" y1="52" x2="254" y2="52" stroke="%s" stroke-width="2.4" marker-end="url(#mB)"/>
      <text x="262" y="56">蓝 · 主线（存 → 读 → 写得稳与恢复 → 落地）</text>
      <line x1="590" y1="52" x2="614" y2="52" stroke="%s" stroke-width="2.2" marker-end="url(#mB)"/>
      <text x="622" y="56">橙 · 关键手段与数字账</text>
      <line x1="820" y1="52" x2="844" y2="52" stroke="%s" stroke-width="2.2" marker-end="url(#mB)"/>
      <text x="852" y="56">紫 · 并发与恢复</text>
      <line x1="990" y1="52" x2="1014" y2="52" stroke="%s" stroke-width="2.4" marker-end="url(#mG)"/>
      <text x="1022" y="56">绿 · 治理回灌（删索引 / 冷热分离 / 分批）</text>
    </g>

    <g filter="url(#sh)">
    %s
    </g>

    <g stroke="%s" stroke-width="2">
      <line x1="205" y1="200" x2="205" y2="223"/><line x1="465" y1="200" x2="465" y2="223"/><line x1="725" y1="200" x2="725" y2="223"/><line x1="985" y1="200" x2="985" y2="223"/><line x1="1245" y1="200" x2="1245" y2="223"/>
      <line x1="205" y1="230" x2="1245" y2="230"/>
    </g>
    <g stroke="%s" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="400" y1="230" x2="400" y2="253"/><line x1="1050" y1="230" x2="1050" y2="253"/>
    </g>

    <g filter="url(#sh)">
    %s
    </g>

    <g stroke="%s" stroke-width="2">
      <line x1="400" y1="360" x2="400" y2="383"/><line x1="1050" y1="360" x2="1050" y2="383"/>
      <line x1="290" y1="390" x2="1140" y2="390"/>
    </g>
    <g stroke="%s" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="290" y1="390" x2="290" y2="413"/><line x1="715" y1="390" x2="715" y2="413"/><line x1="1140" y1="390" x2="1140" y2="413"/>
    </g>

    <g filter="url(#sh)">
    %s
    </g>

    <g stroke="%s" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="290" y1="520" x2="290" y2="573"/><line x1="715" y1="520" x2="715" y2="573"/><line x1="1140" y1="520" x2="1140" y2="573"/>
    </g>

    <g filter="url(#sh)">
    %s
    </g>

    <g stroke="%s" stroke-width="2">
      <line x1="290" y1="680" x2="290" y2="703"/><line x1="715" y1="680" x2="715" y2="703"/><line x1="1140" y1="680" x2="1140" y2="703"/>
      <line x1="290" y1="710" x2="1140" y2="710"/>
    </g>
    <g stroke="%s" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="525" y1="710" x2="525" y2="733"/><line x1="1125" y1="710" x2="1125" y2="733"/>
    </g>

    <g filter="url(#sh)">
    %s
    </g>

    <g stroke="%s" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="525" y1="840" x2="525" y2="893"/><line x1="1125" y1="840" x2="1125" y2="893"/>
    </g>

    <g filter="url(#sh)">
    %s
    </g>

    <path d="M 250 790 L 48 790 L 48 150 L 83 150" fill="none" stroke="%s" stroke-width="2.4" marker-end="url(#mG)"/>
    <text x="38" y="470" font-size="11" font-weight="800" fill="%s" text-anchor="middle" transform="rotate(-90 38 470)">治理回灌 · 删无用索引 / 冷热分离 / 分批</text>
  </svg>""" % (B, G, LINE, TX2, B, O, P_, G,
              '\n    '.join(L1), B, B, '\n    '.join(L2), O, O, '\n    '.join(L3),
              P_, '\n    '.join(L4), O, O, '\n    '.join(L5),
              O, '\n    '.join(L6), G, GD)

STORY = u"""<div class="story">
    <b>主干叙事（一段读完）</b>：这一模块的一条线是「<b>怎么存 → 怎么读得快 → 怎么写得稳与恢复 → 业务怎么落地</b>」。
    <b>存</b>：引擎与主键是被「并发写 + 不能丢」逼出来的 —— InnoDB、自增主键（UUID 让扇出 1170→390，总页数约翻倍、缓存减半）；但<b>树矮只保证定位便宜，真实成本 = 扫描行数 + 回表次数</b>，索引设计全部围绕少扫 / 少回 / 少排。
    <b>读</b>：一条 SQL 走五层，五层里<b>只有优化器在做决定</b> —— 慢的第一嫌疑人是它估算错了（一次可放大 50 倍），先查统计信息再动手；有时全表扫是优化器的正确决定。
    <b>写得稳</b>：A 靠 undo、D 靠 redo、I 靠锁 + MVCC，C 是结果不是机制；RR 的快照读靠 ReadView、当前读靠 next-key lock；崩溃恢复<b>先 redo 再 undo（顺序不能反）</b>，redo 与 binlog 分属两个组件，靠 2PC 捆成原子。
    拖垮系统的是<b>长事务</b>：它按住全库的 undo 回收边界（只读也按）和锁 —— <b>分批</b>同时治锁、undo、主从延迟、数据增长四个问题。
    <b>落地</b>：先报冲突频率再选乐观 / 悲观锁（高冲突乐观 N² vs N）；排行榜把计算内建进 ZSet（O(logN)），防超卖把判断下推进原子操作 —— <b>同一条原理的两个应用</b>。
  </div>
  <div class="cap"><b>读法</b>：蓝线是主线；橙框是执行与优化（数字账最密的一层）；紫框是并发与恢复（面试最容易被追问的一层）；绿框是治理；绿线是治理回灌。<b>读慢先问优化器、写挂先问锁与日志、拖垮全库先问长事务</b>——三段失败分开归因。</div>"""

SEC01 = u"""<!-- 01 主干图 -->
<section class="lv-quick">
  <h2><span class="num">01</span>主干：怎么存 → 怎么读得快 → 怎么写得稳 → 业务怎么落地<span class="src">正本 wiki/topics/MySQL/</span></h2>
  <div class="h2sub">七条主线压成四段：<b>存（M1–M5）→ 读（M6–M7）→ 写得稳（M8–M13）→ 治理与落地（M14–M17）</b>。三段失败必须能分开归因。</div>
  <div class="fig">
  %s
  </div>
  %s
</section>""" % (SVG01, STORY)

# ---------------------------------------------------------------- 02 检索表
ROWS = [
    (u'M1 B+ 树', u'为什么不用别的树', u'唯一指标是「定位一行几次 IO」：16KB 页 → 扇出 ≈1170 → 2000 万行 3 层 3 次 IO；哈希不支持范围、红黑树扇出小 IO 多；「矮」只省定位，回表才是大头', u'1', u'未使用 —— 原理题不挂项目，别编'),
    (u'M2 最左前缀', u'联合索引怎么设计', u'索引按字典序连续存放，缺最左列 = 满足条件的行散落在每段里、无连续区间可扫；顺序不同扫描量差 30 倍；范围列后的列失「缩小扫描」不失「过滤」（ICP 省回表不省扫描）', u'11、13', u'EnergyOps：索引按「等值在前、时间范围在后」设计（device_id, energy_type, stat_date）'),
    (u'M3 回表 / 覆盖', u'为什么覆盖索引快', u'二级索引叶子 = 索引列 + 主键 → 命中后回聚簇树取整行，回表次数随命中行数线性涨；覆盖索引 = 索引自己答完（Using index）；真实成本 = 扫描行数 + 回表次数', u'10、12', u'EnergyOps：先修范围与 JOIN 再建联合索引——判断一条 SQL 看回表，不只看 EXPLAIN 的 rows'),
    (u'M4 索引代价 / DDL', u'加索引为什么能搞挂库', u'索引是读的快照、写的负债：每次写维护 N 棵 B+ 树；大表 DDL 的危险是「不可控的等待」（MDL 排队被并发放大）；影子表（pt-osc / gh-ost）= 新建 + 双写 + 验证 + 切换', u'14、15', u'未使用 —— 判据记牢：没有查询在用的索引是纯负债，只在写入时收费'),
    (u'M5 引擎 / 主键 / 类型', u'表怎么建才不埋雷', u'「并发写 + 不丢数据」逼出 InnoDB（MyISAM 叶子存地址、无事务）；主键 UUID(36B) → 扇出 1170→390、总页数约翻倍、缓存减半；char 只用于长度真固定的字段', u'2–9', u'未使用 —— 代价讲不出 = 没选过：引擎 / 主键 / 类型都在回答「写入顺不顺、以后改不改得动」'),
    (u'M6 SQL 执行五层', u'一条 SQL 怎么走、慢在哪', u'连接器 → 分析器 → 优化器 → 执行器 → 引擎层，五层里只有优化器在做决定 → SQL 慢第一嫌疑人是估算错（一次可放大 50 倍）；查询缓存死于「以表为粒度失效」', u'16、17', u'EnergyOps：慢的根因不是单条 SQL，是先展开归属与事实再过滤园区——先修范围与 JOIN，不是先换库'),
    (u'M7 慢查询优化', u'优化手段怎么归类', u'一切手段归三类：少扫（最左前缀 / 避开大偏移）· 少回（覆盖 / ICP）· 少排（索引序匹配 ORDER BY）；先分清「写法问题」还是「成本判断」——有时全表扫是优化器的正确决定', u'18–23', u'EnergyOps：修范围与 JOIN → 联合索引 → 消 N+1 → 最后才缓存（P95 20.4s→2.8s，待验证口径，先说口径）'),
    (u'M8 隔离级别 / ACID', u'并发为什么不会乱', u'并发只有两种冲突关系；隔离谱系单调 RU→RC→RR→串行化；ACID 有分工：A 靠 undo、D 靠 redo、I 靠锁+MVCC，C 是结果不是机制；MVCC 把读摘出冲突（1%）', u'24、25', u'RuleArena：权威状态在同一个事务内提交——事务边界即业务边界（A 的范围）'),
    (u'M9 MVCC', u'读为什么不用加锁', u'读看旧版本：undo 版本链 + ReadView 判可见性；RC/RR 只差生成时机（每语句 / 首次快照）；旧版本回收由最老 ReadView 决定——一个长事务就能让全库回收停摆', u'26、27', u'未使用 —— 机制题；但「回收边界」这条直接连到 M13 长事务与 PG 的 idle in transaction'),
    (u'M10 锁与死锁', u'锁什么时候会变大', u'锁的可寻址对象只有索引项——条件无索引可用时锁全表（1 条 → 100 万条，差 6 个数量级）；RR 默认 Next-Key = 间隙 + 记录（防插入 + 护已有）；死锁 = 顺序不一致成环', u'28–30', u'RuleArena：条件更新替代 SELECT … FOR UPDATE，避开 RR 下 next-key lock 的范围放大'),
    (u'M11 三日志 / 2PC', u'断电为什么不丢', u'WAL：随机页写 → 顺序日志写（机械盘差 2–3 个数量级）；redo 环形 + checkpoint 推进；binlog 管复制与回档（Row 主流）；redo+binlog 分属两组件 → 2PC 捆成原子', u'31–35', u'数驭穹图：接入 MySQL 源优先用 Binlog（CDC 的前提）；「双一」才是断电不丢的配置'),
    (u'M12 崩溃恢复', u'重启后数据怎么回来', u'崩溃瞬间事务三态、各有日志痕迹：先 redo 重放（幂等：做前判是否做过）再 undo 回滚——顺序反了会丢已提交；prepare 态由 2PC 裁决', u'36、37', u'未使用 —— 恢复时长能算：≈ checkpoint 落后的 redo 量 ÷ 重放速度'),
    (u'M13 长事务', u'它凭什么拖垮全库', u'按住两样东西：全库 undo 回收边界（由最老 ReadView 决定，只读也按）+ 锁——两条独立链；外部系统的响应时间绑进事务 = 事故；分批同时治四个问题', u'38', u'RuleArena：事务只包数据库操作、Checkpoint 不当业务事实——动作与 Checkpoint 间永远有崩溃窗口'),
    (u'M14 主从复制', u'延迟为什么是结构性的', u'复制的是 binlog 变更流不是数据页 → 主写 &gt; 从放则延迟累积（结构如此，不是故障）；并行度按库 → WRITESET；无主键表 Row 回放拖慢从库；半同步治丢不治旧', u'39、40', u'数驭穹图：SNAPSHOT / LIVE_READ 按新鲜度选访问模式——「哪些读可以旧」是业务决策'),
    (u'M15 数据增长', u'数据大了先做什么', u'「8000 万行」先定位症状（慢 / 大 / 贵）再动手；五步按复杂度递增：索引 → 冷热分离（量降 1/10、树高 4→3）→ 归档 → 读写分离 → 分库分表（最难回头）', u'41–43', u'EnergyOps：Raw → 可信聚合 → hourly → daily 分层，热查询不打冷数据；数驭穹图：快照 + 位点 + 校验换生产隔离'),
    (u'M16 乐观 vs 悲观', u'冲突频率决定选型', u'先报冲突频率再谈机制：乐观 = 期望值进 WHERE（CAS），高冲突时总工作量 N² vs 悲观 N（p→1 发散）；影响行数 0 是业务分支：读权威快照 → 判定，不无脑重试', u'44', u'RuleArena：version 条件更新 + UNIQUE(run_id, action_type, idempotency_key) 兜底——理由是权威性，不是「低频写」'),
    (u'M17 排行榜 / 防超卖', u'场景题怎么拿分', u'第一动作是澄清（榜单范围 / 更新频率 / 历史榜 / 防作弊——9.9 没问的四个）；MySQL O(N) vs ZSet O(logN) 随榜单长度拉开；防超卖 = 判断下推进原子操作', u'45、46', u'RuleArena：资金正确性靠数据库唯一约束兜底，不靠内存锁或 Redis 锁；「榜单挂了不能影响主链路」是底线'),
]
tbody = u'\n'.join(
    u'      <tr><td class="k">%s</td><td>%s</td><td class="ans"><span class="a">%s</span></td><td>%s</td><td class="ans"><span class="a">%s</span></td></tr>'
    % r for r in ROWS)

# ---------------------------------------------------------------- 04 两笔账
SVG04 = u"""<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="MySQL 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="%s"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="%s">主键的扇出账（BIGINT vs UUID）</text>
      <text x="80" y="78" font-size="11.5" fill="%s">非叶节点每条 = 键长 + 6B 页号；页 16KB：BIGINT 8+6=14B → 扇出 ≈1170；UUID 36+6=42B → ≈390</text>
      <rect x="80" y="92" width="420" height="24" rx="4" fill="%s" opacity="0.85"/>
      <text x="88" y="108" font-size="12" font-weight="800" fill="#fff">　扇出 ≈1170（BIGINT 自增）</text>
      <rect x="80" y="124" width="140" height="24" rx="4" fill="%s" opacity="0.9"/>
      <text x="230" y="140" font-size="12" font-weight="800" fill="%s">≈390（UUID）</text>
      <text x="80" y="180" font-size="12" font-weight="800" fill="#1D2129">二级索引叶子 = 索引列 + 主键 → 每个二级索引一起变胖</text>
      <text x="80" y="204" font-size="11.5" fill="%s">5000 万行 × 5 个二级索引：每条索引项 8B→36B，总页数约翻倍</text>
      <text x="80" y="228" font-size="11.5" fill="%s">buffer pool 装的页减半 → 读也变慢；扇出 390 下 2000 万行要 4 层（多一次 IO）</text>
      <text x="80" y="262" font-size="11.5" fill="%s">树高别背「都是 3 层」：小表根页即叶（高 1），2000 万行才到 3 层</text>
      <text x="80" y="292" font-size="10.5" fill="%s">雪花 ID 是权衡不是破例：趋势递增保住「大致有序」，代价是跨节点时钟回拨可能插到中间</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="%s"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="%s">乐观锁的成本发散（9.9 一面原题）</text>
      <text x="760" y="78" font-size="11.5" fill="%s">期望尝试次数 E = 1/(1−p)：p=0.05→1.05 · 0.3→1.4 · 0.7→3.3 · 0.9→10（p→1 发散）</text>
      <g font-size="11.5" fill="%s">
        <text x="760" y="106">10 并发 — 乐观≈50 · 悲观≈10 · 差 5 倍</text>
        <rect x="760" y="112" width="100" height="12" rx="3" fill="%s"/>
        <text x="760" y="140">50 并发 — 乐观≈1250 · 悲观≈50 · 差 25 倍</text>
        <rect x="760" y="146" width="260" height="12" rx="3" fill="%s"/>
        <text x="760" y="174">100 并发 — 乐观≈5000 · 悲观≈100 · 差 50 倍</text>
        <rect x="760" y="180" width="420" height="12" rx="3" fill="%s"/>
      </g>
      <text x="760" y="204" font-size="12" font-weight="800" fill="#1D2129">所以第一句话报冲突频率，第二句才谈机制——没有 p 就没有选型</text>
      <text x="760" y="228" font-size="11.5" fill="%s">「影响行数 0」是业务分支：读权威快照 → 判定 → 决定，不写 while(true) 重试（要退避、抖动、上限）</text>
      <text x="760" y="252" font-size="11.5" fill="%s">RuleArena：version 条件更新 + UNIQUE(run_id, action_type, idempotency_key) 兜底资金正确性</text>
      <text x="760" y="286" font-size="10.5" fill="%s">别说满「不用锁」：项目文档原话是「在事务中锁定订单行，或使用乐观版本条件更新」——锁留到真实高竞争再评估</text>
    </g>
  </svg>""" % (LINE, BD, TX2, B, O, OD, TX2, OD, TX2, GREY,
               LINE, OD, TX2, TX2, O, O, O, TX2, OD, GREY)

SEC04 = u"""<!-- 04 两笔账 -->
<section class="lv-deep">
  <h2><span class="num">04</span>两笔账：主键怎么改写 B+ 树，乐观锁怎么在高冲突下发散<span class="src">正本 母题-M1/M5 · 母题-M16</span></h2>
  <div class="h2sub">左边是空间与缓存的账，右边是冲突与重试的账——都是数量级问题，不是优化问题。</div>
  <div class="fig">
  %s
  </div>
</section>""" % SVG04

# ---------------------------------------------------------------- 05 数字板
NUMS = [
    ('b', u'一张 B+ 树多高', u'2000 万 = 3 次 IO', u'16KB 页，非叶 14B/条 → 扇出 1170；1170² × 16 ≈ 2000 万行，定位一行 3 次 IO；小表根页即叶（高 1）。'),
    ('o', u'UUID 主键的账', u'扇出 1170 → 390', u'36B+6B=42B/条；二级索引每条也带主键 → 总页数约翻倍，buffer pool 能装的页减半——读跟着变慢。'),
    ('b', u'索引顺序的账', u'30 倍', u'同样的字段、同样的条件，只是列顺序不同，扫描量差约 30 倍——字段顺序不是风格问题，是成本问题。'),
    ('o', u'深分页的账', u'10 万倍', u'LIMIT 1000000,20 的扫描与回表量 = 偏移量，线性涨：第 100 万页是第 1 页的 10 万倍；解法方向是把「翻页」变成「按上次位置继续」。'),
    ('b', u'串行化的代价', u'1% → 19%', u'MVCC 把读摘出冲突（冲突面 ≈1%）；串行化把读也拉回排队（≈19%）——把 MVCC 挣来的并发又还回去。'),
    ('o', u'锁的膨胀', u'1 条 → 100 万条', u'同样是「更新 pending 任务」：走唯一索引锁 1 条；条件无索引可用时锁全表 100 万条——差 6 个数量级。'),
    ('o', u'长事务的账', u'72 ms', u'一个「什么都没干」的只读事务按住回收边界，别人读那一行要沿 undo 链回溯、慢 72ms——链是别人造成的。'),
    ('o', u'乐观锁发散', u'p=0.9 → 10 次', u'期望尝试次数 E=1/(1−p)：0.05→1.05、0.9→10；N 个并发写同一行总工作量 N² vs N——高冲突差 N 倍。'),
    ('b', u'榜单内存', u'1/100', u'2000 万 DAU 全量 vs 每关只存 Top 1000（1000 关）→ 内存差 100 倍；头部精确 O(logN)、长尾近似 O(1)。'),
]
nums_html = u'\n'.join(
    u'    <div class="ncard %s"><div class="t">%s</div><div class="big">%s</div>\n      <div class="d">%s</div></div>'
    % (c, t, b_, d) for c, t, b_, d in NUMS)
SEC05_NUMS = u'<div class="nums">\n%s\n  </div>' % nums_html

# ---------------------------------------------------------------- 06 误判
MIS = [
    (u'✗「B+ 树因为矮所以快」', u'✓ 矮只保证「定位到索引项」便宜；要取整行还得回表（二级索引场景），那才是大头。'),
    (u'✗「树高 3 层，所以这条查询一定快」', u'✓ 树高对任何查询都一样，解释不了差异；差异在扫了多少行、回了多少次表。'),
    (u'✗「RR 已经完全解决了幻读」', u'✓ 快照读靠 MVCC、当前读靠间隙锁，各不幻读；混用时仍会「看起来像幻读」。'),
    (u'✗「RR 下普通 SELECT 也会加锁」', u'✓ 普通 SELECT 是快照读，不加锁；只有当前读（FOR UPDATE / 写条件）才加锁。'),
    (u'✗「有 redo 就不需要 binlog 了」', u'✓ 职责不同：redo 只服务崩溃恢复、用完即弃；binlog 服务复制与时间点恢复，必须长期保留。'),
    (u'✗「重放和回滚谁先谁后无所谓」', u'✓ 必须先 redo 重放再 undo 回滚；反过来会在「已提交但页未落盘」时丢掉已提交数据。'),
    (u'✗「长事务危险就是持锁久」', u'✓ 它还按住全库的 undo 回收边界——只读长事务照样拖慢别人（72ms 那条链）。'),
    (u'✗「乐观锁比悲观锁先进，尽量用乐观」', u'✓ 没有冲突频率就没有选型：高冲突时乐观 N²、悲观 N——差 N 倍；影响行数 0 是业务分支。'),
]
mis_html = u'\n'.join(
    u'    <div class="mrow"><span class="x">%s</span><span class="v">%s</span></div>' % m for m in MIS)

# ---------------------------------------------------------------- 判据（按 M1..M17 顺序）
CRITS = [
    u'能算出扇出 1170→390 与 3 层 2000 万 = 3 次 IO；能逐个淘汰哈希 / 红黑树 / 跳表并说清适用边界（内存里跳表合理）；能反驳「矮 = 快」（回表才是大头）。',
    u'能用「字典序连续区间」推出最左前缀；能算同条件换顺序的扫描量差（30 倍）；能说清 ICP 省回表不省扫描、范围列后的列失缩小不失过滤。',
    u'能说清二级叶子 = 主键所以必须回表；能算回表次数随命中行数线性涨；能区分 Using index（覆盖）与 key 有值（走了索引）两件事。',
    u'能算一次写维护几棵 B+ 树；能说清 DDL 危险在「不可控的等待」并给出影子表三步；能判断哪些索引是纯负债。',
    u'能算 UUID 的页数与缓存损失；能说清 InnoDB 是被哪两条需求逼出来的；能给 char/varchar 与 DATETIME/TIMESTAMP 的判断句（长度定不定 / 2038）。',
    u'能背五层并指出只有优化器在做决定；能用 rows 估算 vs 实际定位「是不是优化器问题」；能解释查询缓存被移除的量化理由。',
    u'能把任一手段归进少扫 / 少回 / 少排；能算深分页的线性代价；能说清「优化器主动弃索引」与「写法失效」的排查顺序不能反。',
    u'能给四级谱系与各自解决的读现象；能背 ACID 分工并指出 C 是结果；能算 MVCC 摘走的冲突面（1% vs 19%）。',
    u'能画版本链 + ReadView 判定；能说清 RC/RR 只差生成时机；能推出「回收看最老 ReadView」并连到长事务危害。',
    u'能说清锁对象 = 索引项、无索引锁全表（1 条 → 100 万条）；能背 Record/Gap/Next-Key 的叠加逻辑；能从死锁日志回溯加锁顺序。',
    u'能算随机写与顺序写的数量级差；能说清 redo 环形与 checkpoint 推进；能推出不做 2PC 的崩溃窗口后果（主从不一致）。',
    u'能给三态 - 动作表；能论证先 redo 后 undo 的顺序不能反；能估恢复时长（checkpoint 落后的 redo 量 ÷ 重放速度）。',
    u'能拆出两条独立危害链（回收边界 + 锁）；能解释只读长事务为何拖人（72ms）；能把「分批」连到锁 / undo / 主从 / 增长四张卡。',
    u'能背三步复制流程并指出复制的是变更流；能比较按库与 WRITESET 并行；能分开「半同步治丢」与「读到旧」两件事。',
    u'能把「8000 万行」拆成三种问题；能背五步顺序并解释为什么（复杂度递增、后步改变前步对象）；能说清分片键 = 查询形状的属性。',
    u'能先报冲突频率再谈机制；能算 1/(1−p) 与 N² vs N；能把 RuleArena 的条件更新讲成「权威性理由」，并说出「不用锁」哪里说满了。',
    u'能背 9.9 澄清清单（范围 / 频率 / 历史榜 / 防作弊）；能算 ZSet O(logN) 与全量内存 1/100；能给出防超卖三条路与「不拖主链路」底线。',
]

# ---------------------------------------------------------------- 应用补丁
def replace_once(s, old, new, tag):
    assert s.count(old) == 1, 'patch %s: count=%d' % (tag, s.count(old))
    return s.replace(old, new)

# 页头一条线
i = s.find('<small>')
j = s.find('</small>') + len('</small>')
s = s[:i] + u'<small>17 张母题 · 46 道题 · 3 个项目 —— 一条线：怎么存 → 怎么读得快 → 怎么写得稳与恢复 → 业务怎么落地</small>' + s[j:]

# 01 节整体替换
i = s.find('<!-- 01 主干图 -->')
j = s.find('<!-- 02 检索表 -->')
assert 0 < i < j
s = s[:i] + SEC01 + u'\n' + s[j:]

# 02 tbody
i = s.find('<tbody>')
j = s.find('</tbody>') + len('</tbody>')
s = s[:i] + u'<tbody>\n' + tbody + u'\n    </tbody>' + s[j:]

# 04 节整体替换
i = s.find('<!-- 04 第二张图 -->')
j = s.find('<!-- 05 数字板 -->')
assert 0 < i < j
s = s[:i] + SEC04 + u'\n' + s[j:]

# 05 数字板
i = s.find('<div class="nums">')
j = s.find('</section>', i)
s = s[:i] + SEC05_NUMS + u'\n' + s[j:]

# 06 误判
i = s.find('<div class="mis">')
j = s.find('</div>', s.find('</div>', i) + 1) + len('</div>')  # mis 内部还有嵌套? 没有：mrow 内是 span
# 简化：找到 mis 后第一个 '</div>\n</section>'
j = s.find('</section>', i)
block = s[i:j]
end = block.rfind('</div>')
s = s[:i] + u'<div class="mis">\n%s\n  </div>\n' % mis_html + s[i + end:]

# 06 标题改八句
s = replace_once(s, u'<span class="num">06</span>最容易说错的话', u'<span class="num">06</span>八句最容易说错的话', 'mis-title')

# 判据：按顺序替换 17 个待补
need = u'（待补：母题卡缺「通过判据」）'
assert s.count(need) == len(CRITS), 'crit count=%d' % s.count(need)
for c in CRITS:
    s = s.replace('"' + need + '"', '"' + c + '"', 1)

# 去脚手架标记
i = s.find('<!-- ONEPAGER-SCAFFOLD')
j = s.find('-->', i) + 3
s = s[:i] + u'<!-- 定稿 2026-10-03 · 脚手架补全：01/04/05 手写，02/06 机制与判据人工校订 -->' + s[j:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('finished MySQL page:', len(s), 'chars')
