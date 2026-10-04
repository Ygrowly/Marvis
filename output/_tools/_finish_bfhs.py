# -*- coding: utf-8 -*-
"""把 并发与锁-一页通.html 脚手架补成定稿页（一次性工具，跑完即删）。"""
import io, re, os

OUT = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(OUT, '并发与锁-一页通.html')
s = io.open(P, encoding='utf-8').read()
assert 'ONEPAGER-SCAFFOLD' in s, '不是脚手架页'

B, O, P_, G = '#1664FF', '#F59E0B', '#8B5CF6', '#22C55E'
BD, OD, PD, GD = '#0E42B5', '#B45309', '#6D28D9', '#15803D'
BS, OS, PS, GS = '#E8F0FF', '#FEF3D6', '#F1ECFE', '#E8F8EE'
TX2, GREY, LINE = '#4E5969', '#86909C', '#E5E6EB'

# ---------------------------------------------------------------- 01 主干图
SVG01 = u"""<svg viewBox="0 0 1450 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="并发与锁 主干图">
    <defs>
      <marker id="mB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>
      <filter id="sh" x="-20%%" y="-20%%" width="140%%" height="150%%">
        <feDropShadow dx="0" dy="1.5" stdDeviation="2.4" flood-color="#0E42B5" flood-opacity="0.10"/>
      </filter>
    </defs>

    <rect x="180" y="24" width="1100" height="56" rx="10" fill="#fff" stroke="%s"/>
    <g font-size="11" fill="%s">
      <line x1="280" y1="52" x2="304" y2="52" stroke="%s" stroke-width="2.4" marker-end="url(#mB)"/>
      <text x="312" y="56">蓝 · 决策主线（要不要 → 画多大 → 跨机怎么办）</text>
      <line x1="720" y1="52" x2="744" y2="52" stroke="%s" stroke-width="2.2" marker-end="url(#mB)"/>
      <text x="752" y="56">橙 · 判据与算式</text>
      <line x1="890" y1="52" x2="914" y2="52" stroke="%s" stroke-width="2.2" marker-end="url(#mB)"/>
      <text x="922" y="56">紫 · 失效与边界</text>
      <line x1="1060" y1="52" x2="1084" y2="52" stroke="%s" stroke-width="2.2" marker-end="url(#mB)"/>
      <text x="1092" y="56">绿 · 项目落地与共享原则</text>
    </g>

    <g filter="url(#sh)">
      <rect x="90" y="100" width="1270" height="112" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>
      <text x="106" y="124" font-size="13" font-weight="800" fill="%s">① 要不要加锁（L1）—— 悲观 = 排队不白干；乐观 = 条件更新，可能白干重试</text>
      <text x="106" y="146" font-size="11.5" fill="%s">第一句话报冲突频率，第二句才谈机制——判据是 1/(1−p)：p 过半，白干的工作量就超过省下的排队</text>
      <text x="106" y="166" font-size="11.5" fill="%s">数据库乐观锁 = 条件更新（version / 状态进 WHERE）+ 失败重试，不是「不加锁」；影响 0 行是业务分支</text>
      <text x="106" y="186" font-size="11.5" fill="%s">重试必须显式定参：退避 + 抖动 + 上限——重试的请求又回到竞争池，无限重试 = 正反馈成重试风暴</text>
      <text x="1344" y="204" font-size="10.5" font-weight="700" fill="%s" text-anchor="end">RuleArena：version 条件更新 + UNIQUE 兜底 · EnergyOps：租约版本条件抢占（一条 UPDATE 完成锁+判断+推进）</text>
    </g>
    <line x1="725" y1="212" x2="725" y2="245" stroke="%s" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="252" width="1270" height="130" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>
      <text x="106" y="276" font-size="13" font-weight="800" fill="%s">② 锁画多大（L2）—— 锁有三笔账：获取、等待 + 记账、对吞吐的影响；前两笔随临界区反向变化</text>
      <text x="106" y="298" font-size="11.5" fill="%s">外部调用绝不进临界区：50ms 的 HTTP 把 0.5ms 的临界区放大 100 倍——先在锁外拿好数据，进锁只做计算与写回</text>
      <text x="106" y="318" font-size="11.5" fill="%s">分段锁的前提是访问能均匀分散：热键照样打爆一段——热点要换方案（本地聚合 / 队列串行 / 每节点累加器）</text>
      <text x="106" y="338" font-size="11.5" fill="%s">自旋还是睡眠看比值：两次切换 ≈2μs；「先自旋一会儿再睡」是临界区长度不可预知时的工程折中</text>
      <text x="106" y="358" font-size="11.5" fill="%s">读写锁只在「读多写少 + 长临界区」划算；CAS 无锁快但有三个边界：ABA（版本号 / stamp）、循环重试、单变量</text>
      <text x="1344" y="376" font-size="10.5" font-weight="700" fill="%s" text-anchor="end">数驭穹图：并发配额代替锁——「争资源」用限流排队，「争状态」才用锁或条件更新，两件事不能混</text>
    </g>
    <line x1="725" y1="382" x2="725" y2="415" stroke="%s" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="422" width="1270" height="130" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>
      <text x="106" y="446" font-size="13" font-weight="800" fill="%s">③ 跨机怎么办（L3）—— 三种实现：Redis SET NX PX + 唯一值 + Lua 原子释放 / ZK 临时顺序节点 / DB 唯一约束</text>
      <text x="106" y="468" font-size="11.5" fill="%s">失效根因只有一个：「锁是否被持有」由锁服务按时间判，「我还在跑」只有客户端知道——GC / 时钟 / 分区 → 两个持有者</text>
      <text x="106" y="488" font-size="11.5" fill="%s">TTL 是无解的两难：设短了 GC 期间过期（互斥破）、设长了挂了白等；看门狗续期能缓解，不解决根因</text>
      <text x="106" y="508" font-size="11.5" fill="%s">Redis 锁的天然弱点：主从复制异步——写入主还没同步到从时主挂，锁「没存在过」（Redlock 为此而生，也有争议）</text>
      <text x="106" y="528" font-size="11.5" font-weight="700" fill="%s">锁只给「大概互斥」：fencing token 让资源侧校验单调递增 token 才是保证——而能幂等就不用锁</text>
      <text x="1344" y="546" font-size="10.5" font-weight="700" fill="%s" text-anchor="end">RuleArena：稳定幂等键 + 唯一约束，「谁先写进唯一约束谁生效」· EnergyOps：租约挡不住已发出的外部调用</text>
    </g>
    <line x1="725" y1="552" x2="725" y2="585" stroke="%s" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="592" width="1270" height="72" rx="8" fill="%s" stroke="%s" stroke-width="1.6"/>
      <text x="725" y="622" font-size="14.5" font-weight="800" fill="%s" text-anchor="middle">共享原则：并发控制的目标不是「不出错」，而是「给出错定价」</text>
      <text x="725" y="646" font-size="11.5" fill="%s" text-anchor="middle">乐观锁接受「重试」 · CAS 接受「失败重来」 · 分布式锁接受「可能失效所以再校验一次」——每种方案都在给定错价，而不是消灭它</text>
    </g>
  </svg>""" % (B, LINE, TX2, B, O, P_, G,
               BS, B, BD, TX2, TX2, OD, GD,
               B,
               OS, O, OD, TX2, TX2, TX2, P_, GD,
               B,
               PS, P_, PD, TX2, TX2, TX2, OD, GD,
               B,
               GS, G, GD, TX2)

STORY = u"""<div class="story">
    <b>主干叙事（一段读完）</b>：这一模块的一条线是三步决策「<b>要不要加锁 → 锁画多大 → 跨机怎么办</b>」，共享同一个前提：<b>并发控制的目标不是不出错，而是给出错定价</b>。
    <b>要不要</b>：悲观 = 排队不白干、乐观 = 条件更新可能白干重试 —— 先报冲突频率再谈机制，判据是 <b>1/(1−p)</b>（p 过半就该换悲观）；重试必须显式定参（退避 / 抖动 / 上限），否则重试回竞争池、正反馈成风暴。
    <b>画多大</b>：锁有三笔账且随临界区反向变化 —— <b>外部调用绝不进临界区</b>（50ms HTTP 把 0.5ms 临界区放大 100 倍，单锁吞吐只剩 ≈20 QPS）；分段锁前提是访问能均匀分散；自旋还是睡眠看 2μs 的比值；CAS 无锁快但有 ABA，用版本号兜住。
    <b>跨机</b>：Redis / ZK / DB 三种实现各有一个软肋，失效根因只有一个 —— <b>「锁是否被持有」由锁服务按时间判，「我还在跑」只有客户端知道</b>；TTL 设多少都错（GC 3s vs P99 200ms），看门狗只缓解，<b>fencing token 让资源侧校验单调 token 才是保证</b>；而能幂等就不用锁 —— 幂等只依赖自己的数据库。
  </div>
  <div class="cap"><b>读法</b>：三个大框就是决策顺序，从上往下走；橙字是判据与算式（要能现场算），紫字是失效与边界（要能举反例），绿字是三个项目各自的落点。<b>底部一句是全模块的母题</b>：每种方案都在给定错定价。</div>"""

SEC01 = u"""<!-- 01 主干图 -->
<section class="lv-quick">
  <h2><span class="num">01</span>主干：要不要加锁 → 锁画多大 → 跨机怎么办<span class="src">正本 wiki/topics/并发与锁/</span></h2>
  <div class="h2sub">三条主线就是<b>三步决策，顺序即依赖</b>：先判断要不要付这个代价，再决定怎么付得少，最后才考虑把范围扩到多台机器。</div>
  <div class="fig">
  %s
  </div>
  %s
</section>""" % (SVG01, STORY)

# ---------------------------------------------------------------- 02 检索表
ROWS = [
    (u'L1 要不要加锁', u'乐观 vs 悲观怎么选', u'先报冲突频率再谈机制：悲观 = 排队不白干，乐观 = 条件更新 + 可能白干重试；判据 1/(1−p)，p 过半换悲观；乐观锁不是「不加锁」——同样拿行锁，只是持锁从整个业务压到一条 UPDATE；重试显式定参防重试风暴', u'1–6', u'RuleArena：version 条件更新 + UNIQUE(run_id, action_type, idempotency_key) 兜底；EnergyOps：租约版本条件抢占——一个原子 UPDATE 完成加锁、判断、推进三件事'),
    (u'L2 锁画多大', u'粒度 / 临界区 / 自旋 / CAS', u'锁有三笔账且随临界区反向变化；外部调用不进临界区（50ms HTTP 放大 100 倍、单锁吞吐 ≈20 QPS）；分段锁前提 = 访问能均匀分散，热键照样打爆一段；自旋 vs 睡眠看 2μs 比值；读写锁只在读多写少 + 长临界区划算；CAS 有 ABA，用版本号 / stamp', u'7–12', u'数驭穹图：并发配额代替锁——多租户查询之间没有共享状态要保护，只是争资源：争资源限流，争状态才锁'),
    (u'L3 跨机互斥', u'分布式锁与它的边界', u'三实现（Redis SET NX PX + Lua 原子释放 / ZK 临时顺序节点 / DB 唯一约束）；失效根因 = 锁服务按时间判 vs 客户端只有自己知道（GC / 时钟 / 分区 → 两个持有者）；TTL 两难无解 → fencing token 资源侧校验才给保证；能幂等就不用锁', u'13–20', u'RuleArena：稳定幂等键 + 唯一约束，「谁先写进唯一约束谁生效」——比分布式锁简单且不依赖锁服务；EnergyOps：租约挡不住已发出的外部调用，那要靠幂等键 + 权威状态查询'),
]
tbody = u'\n'.join(
    u'      <tr><td class="k">%s</td><td>%s</td><td class="ans"><span class="a">%s</span></td><td>%s</td><td class="ans"><span class="a">%s</span></td></tr>'
    % r for r in ROWS)

# ---------------------------------------------------------------- 04 两笔账
SVG04 = u"""<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="并发与锁 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="%s"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="%s">临界区的放大账（外部调用进了锁里）</text>
      <text x="80" y="78" font-size="11.5" fill="%s">临界区本该 0.5 ms（计算 + 写库），里面塞了一次 50 ms 的外部 HTTP → 锁持有 50.5 ms</text>
      <rect x="80" y="92" width="6" height="24" rx="2" fill="%s"/>
      <text x="94" y="108" font-size="12" font-weight="800" fill="%s">0.5 ms（纯计算 + 写库）</text>
      <rect x="80" y="124" width="560" height="24" rx="4" fill="%s" opacity="0.9"/>
      <text x="88" y="140" font-size="12" font-weight="800" fill="#fff">　50.5 ms（含外部调用）—— 放大 100 倍</text>
      <text x="80" y="180" font-size="12" font-weight="800" fill="#1D2129">单把锁的吞吐 = 1s ÷ 50.5ms ≈ 20 QPS——应用层并发再高也没用</text>
      <text x="80" y="206" font-size="11.5" fill="%s">自旋还是睡眠：一次往返切换 ≈2μs，临界区 500μs ≫ 2μs → 直接睡；「先自旋再睡」留给长度不可预知的锁</text>
      <text x="80" y="232" font-size="11.5" fill="%s">读写锁反例：读占 99%%、读写临界区各 1ms——额外记账可能比省下的等待还贵，还有写者饥饿</text>
      <text x="80" y="264" font-size="11.5" font-weight="700" fill="%s">外部调用 / IO / 远程调用一律放锁外：先在锁外把数据拿好，进锁只做计算与写回</text>
      <text x="80" y="292" font-size="10.5" fill="%s">数驭穹图同构：多租户查询没有共享状态、只是争资源 → 用并发配额，不用锁</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="%s"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="%s">TTL 的两难（P99 200ms vs GC 3s）</text>
      <text x="760" y="78" font-size="11.5" fill="%s">业务 P99 = 200 ms；同进程（大堆 JVM）实测最长 GC 停顿 3 s——TTL 设多少都错：</text>
      <g font-size="11.5" fill="%s">
        <text x="760" y="106">TTL = 300ms（&gt; P99）→ GC 3s 期间锁过期 → 第二个客户端进入 → 两个持有者，互斥已破</text>
        <rect x="760" y="114" width="60" height="12" rx="3" fill="%s"/>
        <text x="760" y="146">TTL = 5s（&gt; GC）→ 持有者真挂了 → 其他客户端白等 5s，可用性买单</text>
        <rect x="760" y="152" width="600" height="12" rx="3" fill="%s"/>
      </g>
      <text x="760" y="196" font-size="12" font-weight="800" fill="#1D2129">根因：锁是否被持有 = 锁服务按时间判；我还在跑 = 只有客户端自己知道——必然脱节</text>
      <text x="760" y="222" font-size="11.5" fill="%s">看门狗续期缓解不解决根因（客户端整体挂掉时，续期线程跟着没了的是「锁还在」的假象）</text>
      <text x="760" y="246" font-size="11.5" font-weight="700" fill="%s">fencing token：资源侧校验单调递增 token，旧的写入直接拒绝——这才是互斥的保证</text>
      <text x="760" y="270" font-size="11.5" fill="%s">RuleArena 的答案更进一步：能幂等就不用锁——幂等键只依赖自己的数据库，不新增可用性依赖</text>
      <text x="760" y="292" font-size="10.5" fill="%s">EnergyOps 的对应坑：租约挡住了本地旧写，撤不回旧 Worker 已发出的外部调用——副作用要靠幂等键兜</text>
    </g>
  </svg>""" % (LINE, BD, TX2, G, GD, O, TX2, TX2, OD, GREY,
               LINE, OD, TX2, TX2, O, O, TX2, OD, TX2, GREY)

SEC04 = u"""<!-- 04 两笔账 -->
<section class="lv-deep">
  <h2><span class="num">04</span>两笔账：临界区被外部调用放大 100 倍，TTL 设多少都错<span class="src">正本 母题-L2 · 母题-L3</span></h2>
  <div class="h2sub">左边是「锁里面塞了什么」的账，右边是「锁服务凭什么判断」的账——都是数量级问题，不是调参问题。</div>
  <div class="fig">
  %s
  </div>
</section>""" % SVG04

# ---------------------------------------------------------------- 05 数字板
NUMS = [
    ('o', u'冲突 60% 的账', u'2.5 次 ≈ 12.5ms', u'单次尝试 5ms、冲突率 60% → 期望尝试 E=1/(1−p)=2.5 次、期望耗时 12.5ms——p 过半，悲观锁开始占优。'),
    ('o', u'高冲突发散', u'N² vs N', u'乐观锁 N 个并发写同一行总工作量 ≈N²/2，悲观锁 ≈N：10 并发差 10 倍、100 并发差 100 倍——p→1 时发散。'),
    ('b', u'临界区放大', u'100 倍', u'0.5ms 的临界区塞进一次 50ms 外部 HTTP → 持锁 50.5ms：外部调用 / IO 一律放锁外。'),
    ('b', u'单锁吞吐', u'≈ 20 QPS', u'1s ÷ 50.5ms ≈ 19.8——锁住的资源每秒只能过 20 个请求，应用层并发再高也白搭。'),
    ('b', u'自旋判据', u'2 μs', u'抢不到锁睡下去再唤醒 ≈ 两次上下文切换 ≈2μs；临界区远大于 2μs 就直接睡——先自旋再睡是折中。'),
    ('b', u'TTL 两难', u'15 倍', u'GC 最长 3s ÷ 业务 P99 200ms ≈ 15：TTL 盖住 P99 会被 GC 打穿（两个持有者），盖住 GC 就得接受挂了白等。'),
    ('o', u'看门狗的边界', u'缓解 ≠ 解决', u'续期把 TTL 顶回去能缓解「活着的持有者」，但客户端整体挂掉 / 长暂停时根因仍在——所以还需要 fencing token。'),
    ('o', u'Redis 的定位', u'256–512MB', u'RuleArena 给 Redis 只配 256~512MB：队列与限流走 Redis，权威状态在 PostgreSQL——不把正确性押在锁服务上。'),
    ('b', u'幂等的收益', u'少一个依赖', u'锁要引入锁服务的可用性依赖；幂等只依赖自己的数据库——「能幂等就不用锁」是 L3 最后一条追问的答案。'),
]
nums_html = u'\n'.join(
    u'    <div class="ncard %s"><div class="t">%s</div><div class="big">%s</div>\n      <div class="d">%s</div></div>'
    % (c, t, b_, d) for c, t, b_, d in NUMS)
SEC05_NUMS = u'<div class="nums">\n%s\n  </div>' % nums_html

# ---------------------------------------------------------------- 06 误判
MIS = [
    (u'✗「乐观锁就是不加锁」', u'✓ 数据库里同样拿行锁，只是持锁时间从「整个业务」压缩到「一条 UPDATE」；代价变成「可能白干」。'),
    (u'✗「乐观锁一定比悲观锁快」', u'✓ 看冲突率：p 过半时白干的工作量超过省下的排队（期望尝试 2 次以上）；判据是 1/(1−p)，不是感觉。'),
    (u'✗「悲观锁慢，高并发要避免」', u'✓ 悲观是把不确定性换成排队；临界区短、冲突高时反而更稳——慢是因为临界区长，不是锁本身。'),
    (u'✗「库存扣减先查再改就行」', u'✓ 查和改之间有窗口：判断必须下推进原子操作（条件更新 / 原子扣减），否则高并发下超卖。'),
    (u'✗「分段锁能解决热点问题」', u'✓ 分段按 key 分派，热键始终在同一段；热点要换方案：本地聚合、队列串行、每节点累加器。'),
    (u'✗「读多写少就上读写锁」', u'✓ 临界区极短时记账比省下的等待还贵，还有写者饥饿；长临界区的读多写少才明显划算。'),
    (u'✗「分布式锁保证了互斥」', u'✓ 它给的是「大概互斥」：GC / 时钟 / 分区能造出两个持有者；资源侧校验 fencing token 才是保证。'),
    (u'✗「用 Redis 锁就够了」', u'✓ 主从异步切换时锁会丢（还没同步主就挂）；且引入新的可用性依赖——Redis 挂了业务卡住。'),
]
mis_html = u'\n'.join(
    u'    <div class="mrow"><span class="x">%s</span><span class="v">%s</span></div>' % m for m in MIS)

# ---------------------------------------------------------------- 判据
CRITS = [
    u'能先报冲突频率再谈机制；能算 1/(1−p) 并给出 p=50% 分界（60% → 2.5 次）；能把「影响 0 行」讲成业务分支而不是异常；能给出重试三参数并解释重试风暴的正反馈。',
    u'能算临界区被外部调用放大的倍数与吞吐损失（100 倍 / ≈20 QPS）；能给出自旋 / 睡眠的比值判据（2μs）；能说清分段锁的前提与热点的正确解法；能讲 CAS 三边界与 ABA 解法（版本号 / stamp）。',
    u'能背三种实现与各自失效场景（Redis 主从异步丢锁 / ZK 重 / DB 慢）；能解释 TTL 两难为何无解（3s vs 200ms）；能说清 fencing token 为什么是必要补充；能论证「能幂等就不用锁」。',
]

# ---------------------------------------------------------------- 应用补丁
def replace_once(s, old, new, tag):
    assert s.count(old) == 1, 'patch %s: count=%d' % (tag, s.count(old))
    return s.replace(old, new)

i = s.find('<small>')
j = s.find('</small>') + len('</small>')
s = s[:i] + u'<small>3 张母题 · 20 道题 · 3 个项目 —— 一条线：要不要加锁 → 锁画多大 → 跨机怎么办（顺序即决策顺序）</small>' + s[j:]

i = s.find('<!-- 01 主干图 -->')
j = s.find('<!-- 02 检索表 -->')
assert 0 < i < j
s = s[:i] + SEC01 + u'\n' + s[j:]

i = s.find('<tbody>')
j = s.find('</tbody>') + len('</tbody>')
s = s[:i] + u'<tbody>\n' + tbody + u'\n    </tbody>' + s[j:]

i = s.find('<!-- 04 第二张图 -->')
j = s.find('<!-- 05 数字板 -->')
assert 0 < i < j
s = s[:i] + SEC04 + u'\n' + s[j:]

i = s.find('<div class="nums">')
j = s.find('</section>', i)
s = s[:i] + SEC05_NUMS + u'\n' + s[j:]

i = s.find('<div class="mis">')
j = s.find('</section>', i)
block = s[i:j]
end = block.rfind('</div>')
s = s[:i] + u'<div class="mis">\n%s\n  </div>\n' % mis_html + s[i + end:]

s = replace_once(s, u'<span class="num">06</span>最容易说错的话', u'<span class="num">06</span>八句最容易说错的话', 'mis-title')

need = u'（待补：母题卡缺「通过判据」）'
assert s.count(need) == len(CRITS), 'crit count=%d' % s.count(need)
for c in CRITS:
    s = s.replace('"' + need + '"', '"' + c + '"', 1)

i = s.find('<!-- ONEPAGER-SCAFFOLD')
j = s.find('-->', i) + 3
s = s[:i] + u'<!-- 定稿 2026-10-03 · 脚手架补全：01/04/05/06 手写，02 机制与判据人工校订 -->' + s[j:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('finished 并发与锁 page:', len(s), 'chars')
