# -*- coding: utf-8 -*-
"""消息队列 一页通定稿（一次性工具）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _onepage_lib import (B, O, P_, G, BD, OD, PD, GD, BS, OS, PS, GS, TX, TX2, TX3, GREY, LINE,
                          SVG_DEFS, legend, finish)

SVG01 = f'''<svg viewBox="0 0 1450 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="消息队列 主干图">
    {SVG_DEFS}
    {legend([(B, 'mB', '蓝 · 排查顺序（别丢 → 别重复 → 扛不住）'),
             (O, 'mO', '橙 · 判据与算式'),
             (P_, 'mP', '紫 · 失效与毒教材点'),
             (G, 'mG', '绿 · 项目落点与共享前提')])}

    <g filter="url(#sh)">
      <rect x="90" y="100" width="1270" height="112" rx="8" fill="{BS}" stroke="{B}" stroke-width="1.6"/>
      <text x="106" y="124" font-size="13" font-weight="800" fill="{BD}">① 别丢（Q1）—— 消息的一生是三段接力：发送（acks）→ 存储（持久化 + 多副本）→ 消费（先处理后 ack）；会丢只有这三个位置</text>
      <text x="106" y="146" font-size="11.5" fill="{OD}">acks = all 的真义：「所有在 ISR 里的副本」而不是「所有副本」——ISR 剩 1 个照样成功，必须配 min.insync.replicas</text>
      <text x="106" y="166" font-size="11.5" fill="{TX2}">Kafka 3.0 起 acks 默认已是 all（幂等生产者要求）——「默认 1 要改 all」是过期答案；消费端「收到就 ack」= 处理崩了消息丢</text>
      <text x="106" y="186" font-size="11.5" fill="{PD}">本地事务和发消息不可能原子 → 事务消息 / 本地消息表 / Outbox；MQ 写入报错是「在保护数据」，不是「MQ 坏了」</text>
      <text x="1344" y="204" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">EnergyOps：Alarm / Notification Outbox 同一本地事务落库；超时标 result_unknown 不直接重试——先查外部权威状态</text>
    </g>
    <line x1="725" y1="212" x2="725" y2="245" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="252" width="1270" height="130" rx="8" fill="{OS}" stroke="{O}" stroke-width="1.6"/>
      <text x="106" y="276" font-size="13" font-weight="800" fill="{TX}">② 别重复、别乱序（Q2）—— 重复 / 乱序 / 丢失是同一个根源：「确认」本身可能丢 → 框架只保证至少一次，宁重勿丢</text>
      <text x="106" y="298" font-size="11.5" fill="{TX2}">幂等 = 执行多次效果一样：五种方案只是「查重方式」不同；生产组合 = Redis 查重（快）+ 数据库唯一约束兜底（硬）</text>
      <text x="106" y="318" font-size="11.5" fill="{PD}">幂等键必须是稳定业务键（业务 + 动作 + 目标 + 参数 + 版本）——消息 ID / ToolCallID 重投时会变，查重永不命中</text>
      <text x="106" y="338" font-size="11.5" fill="{OD}">顺序 = 局部串行：同一订单 / 同一 Key 一个分区；保序的粒度就是并行的粒度——100 分区拿 100 倍吞吐，单订单上限仍是单分区 200 TPS</text>
      <text x="106" y="358" font-size="11.5" fill="{TX2}">生产者重试会把顺序打乱（max.in.flight &gt; 1 且非幂等）；消费端多线程处理同一队列同样破坏顺序——串到多细要想清</text>
      <text x="1344" y="376" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">RuleArena：稳定幂等键 + UNIQUE(run_id, action_type, idempotency_key)——超时先查 Receipt，不是换 key 重试</text>
    </g>
    <line x1="725" y1="382" x2="725" y2="415" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="422" width="1270" height="130" rx="8" fill="{PS}" stroke="{P_}" stroke-width="1.6"/>
      <text x="106" y="446" font-size="13" font-weight="800" fill="{PD}">③ 扛不住怎么办（Q3）—— 积压先查根因再扩容（顺序反了会放大故障：加消费者只是让更多线程去撞慢查询）</text>
      <text x="106" y="468" font-size="11.5" fill="{OD}">消净速度 = 生产 λ − 消费 μ；消费硬天花板 = 分区数——消费者多于分区白加；加分区要迁移、可能改 Key 哈希影响顺序</text>
      <text x="106" y="488" font-size="11.5" fill="{TX2}">海量积压的应急：临时 Topic 嫁接——搬运程序只转发不处理业务，否则搬运速度=消费速度，等于没搬</text>
      <text x="106" y="508" font-size="11.5" fill="{TX2}">高可用三层递进：多副本 → 自动选主 → 路由感知（少一层等于没有）；ISR 缩水后选主 = 可用性 vs 一致性的正面对决</text>
      <text x="106" y="528" font-size="11.5" fill="{TX2}">Kafka 快的四件套：顺序写 + 批量 + 压缩 + 零拷贝；Pull 让消费端自控速率（Push 会压垮慢消费者）</text>
      <text x="1344" y="546" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">RuleArena：Redis / ARQ 队列——MVP 要「能异步、能查状态」不是高吞吐 · EnergyOps：604 台设备不上 MQ，算过账</text>
    </g>
    <line x1="725" y1="552" x2="725" y2="585" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="592" width="1270" height="72" rx="8" fill="{GS}" stroke="{G}" stroke-width="1.6"/>
      <text x="725" y="622" font-size="14.5" font-weight="800" fill="{GD}" text-anchor="middle">共享前提：跨进程通信没有「恰好一次」——MQ 的全部设计都是「至少一次 + 幂等」去逼近它</text>
      <text x="725" y="646" font-size="11.5" fill="{TX2}" text-anchor="middle">引入前先付三笔代价：可用性下降 · 复杂度上升 · 一致性——EnergyOps 算过账：604 台设备用任务表就够，升级条件写明才引入</text>
    </g>
  </svg>'''

STORY = u'''<b>主干叙事（一段读完）</b>：消息队列的一条线就是排查顺序：「<b>别丢 → 别重复别乱序 → 扛不住怎么办</b>」，共享前提是<b>跨进程通信没有恰好一次</b> —— MQ 的全部设计都是「至少一次 + 幂等」去逼近它。
    <b>别丢</b>：消息的一生是三段接力（发送 acks → 存储持久化多副本 → 消费先处理后 ack），<b>acks = all 是「所有 ISR 内副本」不是全部副本</b>，必须配 min.insync.replicas；MQ 写入报错是在保护数据，不是坏了；本地事务和发消息不可能原子，用 Outbox 兜。
    <b>别重复别乱序</b>：重复 / 乱序 / 丢失同一根源（确认本身可能丢），框架只保证至少一次、宁重勿丢 —— <b>去重是业务层的事</b>：稳定业务幂等键 + Redis 查重 + 唯一约束兜底；顺序 = 局部串行，<b>保序的粒度就是并行的粒度</b>（100 分区拿 100 倍吞吐，单订单上限仍是单分区）。
    <b>扛不住</b>：积压先查根因再扩容；<b>消费者天花板 = 分区数</b>（多开白加），加分区要迁移且可能改 Key 哈希；高可用三层递进（多副本 → 自动选主 → 路由感知），ISR 缩水后选主是可用性 vs 一致性的正面对决。
    EnergyOps 反着讲一遍：604 台设备<b>不上 MQ</b> —— 三笔代价（可用性 / 复杂度 / 一致性）立刻要付，收益门槛还远，升级条件写明。'''

CAP = u'''<b>读法</b>：三个大框就是排查顺序；橙字是判据与算式（要能现场算），紫字是毒教材高发区（acks=ISR / 重复无法框架层杜绝 / 消费者超分区白加）；绿字是三个项目的落点。<b>底部一行是全模块的前提</b>。'''

ROWS = [
    (u'Q1 消息怎么不丢', u'三段接力各要做对什么', u'会丢只有三段：发送（acks 语义）→ 存储（持久化 + 多副本 + min.insync.replicas）→ 消费（先处理后 ack，重试到尽头进死信）；Kafka 3.0 起 acks 默认 all；acks = all 是「所有 ISR 内副本」≠ 全部副本；本地事务 + 发消息不可能原子 → Outbox / 本地消息表；MQ 写入报错 = 在保护数据', u'1–9', u'EnergyOps：Alarm / Notification Outbox 同事务落库，超时标 result_unknown 先查权威状态（短信发出去没法回滚）；RuleArena：超时不换 key 重试，先查 Receipt'),
    (u'Q2 重复与乱序', u'至少一次 → 只生效一次', u'重复 / 乱序 / 丢失同根源：确认本身可能丢 → 框架只保证至少一次（宁重勿丢）；幂等 = 执行多次效果一样，五种方案只是查重方式不同；组合 = Redis 查重 + DB 唯一约束兜底；幂等键必须稳定业务键（消息 ID / ToolCallID 必错）；顺序 = 局部串行：保序粒度 = 并行粒度，全局串行 = 吞吐归零', u'10–16', u'RuleArena：稳定幂等键 + UNIQUE(run_id, action_type, idempotency_key)；数驭穹图：无依赖子查询并发、写回顺序确定——「局部串行」的非 MQ 形态'),
    (u'Q3 积压与高可用', u'撑不住的时候怎么办', u'积压先查根因再扩容（顺序反了放大故障）；消净速度 = λ − μ；消费硬天花板 = 分区数（消费者多于分区白加）；加分区要迁移且可能改 Key 哈希影响顺序；海量积压用临时 Topic 嫁接（搬运程序不做业务）；高可用三层递进：多副本 → 自动选主 → 路由感知；Kafka 快：顺序写 + 批量 + 压缩 + 零拷贝', u'17–26', u'RuleArena：Redis / ARQ 队列——MVP 要「能异步、能查状态」不是高吞吐（选型判据）；EnergyOps：604 台设备不上 MQ，三笔代价立刻要付、升级条件写明'),
]

SVG04 = f'''<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="消息队列 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="{BD}">确认加严的账（replication=3、min.insync.replicas=2、acks=all）</text>
      <text x="80" y="78" font-size="11.5" fill="{TX2}">正常 / 坏 1 台：ISR ≥ 2，照常写入；坏 2 台：ISR = 1 &lt; min.insync.replicas → 生产者被拒绝写入</text>
      <rect x="80" y="92" width="240" height="22" rx="4" fill="{G}" opacity="0.85"/>
      <text x="88" y="108" font-size="12" font-weight="800" fill="#fff">　ISR 3 / 2 → 正常写（延迟=最慢 ISR 副本）</text>
      <rect x="80" y="124" width="440" height="22" rx="4" fill="{O}" opacity="0.9"/>
      <text x="88" y="140" font-size="12" font-weight="800" fill="#fff">　ISR 1 → 写入报错：在保护数据，不是 MQ 坏了</text>
      <text x="80" y="180" font-size="11.5" fill="{PD}">若 unclean.leader.election = true：ISR=1 时选落后副本当 leader → 已确认消息消失——「可用性 vs 一致性」的开关</text>
      <text x="80" y="208" font-size="12" font-weight="800" fill="{TX}">消费端的重复窗口：enable.auto.commit = 5s，100 条 × 50ms = 5s</text>
      <text x="80" y="232" font-size="11.5" fill="{TX2}">处理完 100 条恰好在提交前崩溃 → 这 100 条重新投递：最多重复 = 提交间隔内的量（不是丢，是至少一次）</text>
      <text x="80" y="260" font-size="11.5" font-weight="700" fill="{OD}">「不丢」的定义：收到成功 ack 的消息永不消失——宁可重复，不可丢失；重复交给幂等</text>
      <text x="80" y="292" font-size="10.5" fill="{GREY}">EnergyOps 的 Outbox 是同一件事在没有 MQ 时的形态：通知与业务同事务落库，Worker 拿幂等键调外部平台</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="{OD}">积压的账（能算出来的问题）</text>
      <text x="760" y="78" font-size="11.5" fill="{TX2}">积压 1000 万条、生产 2000 条/s、单消费者 500 条/s：20 个消费者但只有 10 个分区</text>
      <g font-size="11.5" fill="{TX2}">
        <text x="760" y="106">20 个消费者（10 个闲置）→ 实际 = 10 × 500 = 5000 条/s</text>
        <rect x="1155" y="96" width="205" height="12" rx="3" fill="{O}"/>
        <text x="760" y="132">净消速度 = 5000 − 2000 = 3000 条/s → 1000 万 ≈ 56 分钟</text>
        <rect x="1155" y="122" width="123" height="12" rx="3" fill="{G}"/>
      </g>
      <text x="760" y="166" font-size="11.5" fill="{PD}">先查根因：如果消费慢是因为代码里多了一次慢查询，加消费者 = 让更多线程撞它、把下游打得更死</text>
      <text x="760" y="192" font-size="11.5" fill="{TX2}">越过天花板的唯一办法是加分区——代价：数据迁移 + Key 哈希分布变化 + 顺序语义受影响（设计期就该估好）</text>
      <text x="760" y="218" font-size="11.5" fill="{TX2}">应急：临时 Topic 嫁接——搬运程序只转发不处理业务，配几十倍队列数的消费者清积压</text>
      <text x="760" y="244" font-size="11.5" fill="{TX2}">保序场景再算一笔：单分区 200 TPS 是「单订单」的上限——加 100 分区拿 100 倍总吞吐，单订单还是 200</text>
      <text x="760" y="270" font-size="11.5" font-weight="700" fill="{OD}">顺序：处理顺序必须是「根因 → 容量」；跳过 / 重置 offset = 丢数据，不是消积压</text>
      <text x="760" y="292" font-size="10.5" fill="{GREY}">数驭穹图同构：队列只做「限流排队」一个职责——不为削峰，只为保护源库</text>
    </g>
  </svg>'''

NUMS = [
    ('b', u'acks=all 的真义', u'ISR ≠ 全部副本', u'ISR 剩 1 个照样 ack 成功——必须配 min.insync.replicas 才有「已确认不丢」的保证。'),
    ('o', u'min ISR 拒写', u'2 台坏 → 报错', u'ISR=1 < min.insync.replicas=2 → 生产者被拒绝：在保护数据，不是 MQ 坏了。'),
    ('b', u'重复窗口', u'5s ≈ 100 条', u'auto.commit 间隔 5s × 100 条 × 50ms：提交前崩溃 = 这 100 条重新投递（至少一次）。'),
    ('o', u'幂等键必错式', u'消息 ID', u'重投时 ID 变了、查重永不命中——稳定业务键 = 业务 + 动作 + 目标 + 参数 + 版本。'),
    ('b', u'保序天花板', u'200 TPS / 单订单', u'100 分区拿 100 倍总吞吐，单个订单仍是单分区 200 TPS——保序粒度 = 并行粒度。'),
    ('b', u'积压消净', u'≈ 56 分钟', u'10 分区 × 500 − 2000 = 净 3000 条/s；1000 万条 ÷ 3000 ≈ 56 分钟——积压是能算出来的问题。'),
    ('o', u'消费者白加', u'20 消费者 / 10 分区', u'多出的 10 个全闲置：同一分区同一时刻只被一个消费者消费——天花板是分区数。'),
    ('b', u'三笔代价', u'可用性·复杂度·一致性', u'604 台设备不上 MQ（EnergyOps）：收益门槛还远、代价立刻要付——升级条件写明。'),
    ('o', u'Kafka 快四件套', u'顺序写·批量·压缩·零拷贝', u'每件都在省「磁盘随机写」与「用户态搬运」——与操作系统模块的零拷贝同一笔账。'),
]

MIS = [
    (u'✗「acks=all 是所有副本确认」', u'✓ 是所有在 ISR 里的副本；ISR 剩 1 个照样成功——必须配 min.insync.replicas。'),
    (u'✗「Kafka 默认 acks=1，要手动改成 all」', u'✓ 3.0 起默认已是 all（幂等生产者默认开启）——过期答案，很多资料还在讲。'),
    (u'✗「配了 min.insync.replicas 就安全了」', u'✓ 它只在 acks=all 时生效；配 acks=1 的话它一点作用都没有。'),
    (u'✗「消息重复消费是 bug，换个 MQ 就好」', u'✓ 框架只保证至少一次：「处理」与「记录进度」无法原子化——去重必须落在业务键上。'),
    (u'✗「用消息 ID 做幂等键」', u'✓ 重投时 ID 变了、查重永不命中；要稳定业务键（业务 + 动作 + 目标 + 参数 + 版本）。'),
    (u'✗「消费者多开几个就能更快消费」', u'✓ 同一分区同一时刻只被一个消费者消费——天花板 = 分区数；顺序是先查根因、再加分区、再加消费者。'),
    (u'✗「加分区没代价」', u'✓ 要数据迁移，且可能改变 Key 哈希分布、影响顺序语义——分区数应在设计期估算。'),
    (u'✗「MQ 挂了业务就得停服」', u'✓ 写路径先问「为什么强依赖 MQ」：本地消息表 / Outbox 让业务先落库、投递后补——队列可以丢或重投。'),
]

CRITS = [
    u'能画出三段接力并指出每段会丢的位置；能说对 acks = all 的真义（ISR）与 min.insync.replicas 的配合；能算 auto.commit 窗口内崩溃的重复量；能解释「MQ 写入报错是在保护数据」。',
    u'能把重复 / 乱序归到同一根源（确认可能丢）；能比较幂等方案并给出「Redis 查重 + 唯一约束」组合的理由；能构造稳定幂等键并指出消息 ID 反例；能用算式说明「保序粒度 = 并行粒度」。',
    u'能按「根因 → 容量」处理积压并算出消净时间；能解释消费者天花板 = 分区数与加分区的代价；能按三层讲 MQ 高可用与 ISR 选主取舍；能用 EnergyOps 反着讲「不上 MQ」的账。',
]

finish('消息队列',
       headline=u'3 张母题 · 26 道题 · 3 个项目 —— 一条线：别丢 → 别重复别乱序 → 扛不住怎么办（前提：跨进程没有恰好一次）',
       sec01_title=u'主干：别丢 → 别重复别乱序 → 扛不住怎么办',
       sec01_sub=u'三个大框就是<b>排查顺序</b>——线上出问题先问丢了没、再问重复没、最后问扛不住了吗；底部横幅是全模块的前提与「什么时候不该上 MQ」。',
       svg01=SVG01, story=STORY, cap=CAP, rows=ROWS,
       sec04_title=u'两笔账：确认加严的账，积压的账',
       sec04_sub=u'左边是「ISR 缩水时谁在保护数据」与重复窗口，右边是「积压是能算出来的问题」——都要能现场算。',
       sec04_src=u'正本 母题-Q1 · 母题-Q3',
       svg04=SVG04, nums=NUMS, mis=MIS, crits=CRITS)
