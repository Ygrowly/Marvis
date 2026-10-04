# -*- coding: utf-8 -*-
"""PostgreSQL 一页通定稿（一次性工具）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _onepage_lib import (B, O, P_, G, BD, OD, PD, GD, BS, OS, PS, GS, TX, TX2, TX3, GREY, LINE,
                          SVG_DEFS, box, legend, finish)

def j(parts):
    return '\n    '.join(parts)

# ---------------------------------------------------------------- 01 主干图
L1 = [
    box(90, 100, 230, 100, BS, B, '索引选型（P1）', BD,
        ['B-tree 默认：覆盖最广', 'GIN 倒排：答「包含」'],
        'GiST 范围/几何 · BRIN 时序'),
    box(350, 100, 230, 100, BS, B, '堆表回表（P2）', BD,
        ['索引只是路标 → 必回表', 'Index Only 看可见性'],
        '前提：VACUUM 一直正常跑'),
    box(610, 100, 230, 100, BS, B, '部分索引（P3）', BD,
        ['只索引活跃行：1/100', '表达式索引：函数可走'],
        '最大风险：静默失效'),
    box(870, 100, 230, 100, BS, B, '在线建索引（P4）', BD,
        ['每个索引 = 写放大 + VACUUM', 'CONCURRENTLY 两阶段'],
        '失败留 INVALID：删掉重建'),
    box(1130, 100, 230, 100, BS, B, '类型（P5）', BD,
        ['text = varchar（无性能差）', 'jsonb 可建 GIN 索引'],
        'timestamptz 是默认答案'),
]
L2 = [
    box(90, 260, 620, 100, OS, O, '执行计划（P6）', TX,
        ['EXPLAIN ANALYZE 才是真相；cost 只能比较同一条 SQL 的两个计划',
         'loops 是乘数：total = actual × loops——从最贵的叶子往上看，不是从根往下'],
        'BUFFERS 必加：分不清「算法差」还是「缓存冷」就白看'),
    box(740, 260, 620, 100, OS, O, '统计信息（P7）', TX,
        ['估行数 = 独立假设相乘；JOIN 后行数膨胀 → 优化器选错方案',
         '默认 100 桶 + MCV 只兜最热 100 值；大表导入后手动 ANALYZE 是刚需'],
        'pg_stat_statements 按总耗时排，不按单次——「贵」是系统视角'),
]
L3 = [
    box(90, 420, 400, 100, PS, P_, '默认 RC（P8）', PD,
        ['默认 READ COMMITTED（不是 RR）',
         'RR：快照取自第一条语句，写冲突直接报错'],
        '级别调高更「安全」→ 死元组更多、膨胀更快', accent_col=PD),
    box(515, 420, 400, 100, PS, P_, 'SSI（P9）', PD,
        ['Serializable = SSI：不阻塞，事后中止',
         '40001 必须重试——COMMIT 也会失败'],
        '写偏斜 RR 挡不住；SSI 防的是「组合不可串行」', accent_col=PD),
    box(940, 420, 400, 100, PS, P_, '无间隙锁（P10）', PD,
        ['没有间隙锁：先查再插天然有竞态',
         '跨行不变量靠显式约束 + 条件更新'],
        'FOR UPDATE 四变体；锁默认无限等（死锁超时 1s）', accent_col=PD),
]
L4 = [
    box(90, 580, 620, 100, '#fff', P_, 'WAL（P11）', PD,
        ['只有一套日志：WAL（没有 undo）——旧版本只能靠 VACUUM 回收',
         '恢复时长 = checkpoint 落后的 WAL 量 ÷ 重放速度（max_wal_size 是上界）'],
        'full_page_writes：checkpoint 越勤，WAL 越大（整页镜像）'),
    box(740, 580, 620, 100, '#fff', P_, '复制（P12）', PD,
        ['流复制 = 整实例字节级；逻辑复制 = 按表、可跨版本、可筛选',
         'synchronous_commit 五档 = RPO 与延迟的官方矩阵（local/on/remote_apply…）'],
        '复制槽默认无限保留 WAL：一个消费者掉线，一天内主库不可写'),
]
L5 = [
    box(90, 740, 400, 100, GS, G, 'MVCC（P13）', GD,
        ['xmin / xmax：更新即新版本',
         '读 = 拿快照比事务 ID，读永不阻塞写'],
        '代价：死元组留在堆里，索引也指向它'),
    box(515, 740, 400, 100, GS, G, '长事务（P14）', GD,
        ['回收边界 = 最老快照（xmin）',
         '2h × 1000 行/s = 720 万死元组'],
        'idle in transaction 也要防（有专门超时参数）'),
    box(940, 740, 400, 100, GS, G, 'VACUUM（P15）', GD,
        ['常规 VACUUM 只标可复用，不缩文件',
         'autovacuum 阈值 = 50 + 0.2 × 行数'],
        '事务 ID 32 位：靠冻结重置防回卷'),
]
L6 = [
    box(250, 900, 550, 100, GS, G, '分区（P16）', GD,
        ['裁剪：查询只扫命中的分区',
         'DROP PARTITION = 元数据操作；DELETE = 大清理'],
        '唯一约束必须带分区键——「分区」结构的数学后果'),
    box(850, 900, 550, 100, GS, G, '连接池（P17）', GD,
        ['进程模型：连接贵，连接池是刚需',
         '事务池化省最多，但破坏预处理语句'],
        'work_mem 是每操作的：连接数 × 节点数 × work_mem'),
]
L7 = [
    box(250, 1060, 550, 100, OS, O, '乐观并发（P18）', TX,
        ['条件更新：期望值（version）进 WHERE',
         'FOR UPDATE 吞吐 = 1÷持锁时长——排队是硬天花板'],
        '影响 0 行 = 业务分支：读权威快照再判定'),
    box(850, 1060, 550, 100, OS, O, '唯一约束（P19）', TX,
        ['幂等的最终防线：失败是确定的（23505）',
         'UPSERT：excluded 可能已被触发器改过'],
        '幂等键按业务身份构造；复合唯一别漏 NOT NULL'),
]

SVG01 = f'''<svg viewBox="0 0 1450 1290" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PostgreSQL 主干图">
    {SVG_DEFS}
    {legend([(B, 'mB', '蓝 · 主线（存 → 读 → 并发 → 持久 → 回收 → 增长 → 落地）'),
             (O, 'mO', '橙 · 手段与落地'),
             (P_, 'mP', '紫 · 并发与失效'),
             (G, 'mG', '绿 · 回收与增长（PG 的主戏）')])}

    <g filter="url(#sh)">
    {j(L1)}
    </g>

    <g stroke="{B}" stroke-width="2">
      <line x1="205" y1="200" x2="205" y2="223"/><line x1="465" y1="200" x2="465" y2="223"/><line x1="725" y1="200" x2="725" y2="223"/><line x1="985" y1="200" x2="985" y2="223"/><line x1="1245" y1="200" x2="1245" y2="223"/>
      <line x1="205" y1="230" x2="1245" y2="230"/>
    </g>
    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="400" y1="230" x2="400" y2="253"/><line x1="1050" y1="230" x2="1050" y2="253"/>
    </g>

    <g filter="url(#sh)">
    {j(L2)}
    </g>

    <g stroke="{B}" stroke-width="2">
      <line x1="400" y1="360" x2="400" y2="383"/><line x1="1050" y1="360" x2="1050" y2="383"/>
      <line x1="290" y1="390" x2="1140" y2="390"/>
    </g>
    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="290" y1="390" x2="290" y2="413"/><line x1="715" y1="390" x2="715" y2="413"/><line x1="1140" y1="390" x2="1140" y2="413"/>
    </g>

    <g filter="url(#sh)">
    {j(L3)}
    </g>

    <g stroke="{B}" stroke-width="2">
      <line x1="290" y1="520" x2="290" y2="543"/><line x1="715" y1="520" x2="715" y2="543"/><line x1="1140" y1="520" x2="1140" y2="543"/>
      <line x1="290" y1="550" x2="1140" y2="550"/>
    </g>
    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="400" y1="550" x2="400" y2="573"/><line x1="1050" y1="550" x2="1050" y2="573"/>
    </g>

    <g filter="url(#sh)">
    {j(L4)}
    </g>

    <g stroke="{B}" stroke-width="2">
      <line x1="400" y1="680" x2="400" y2="703"/><line x1="1050" y1="680" x2="1050" y2="703"/>
      <line x1="290" y1="710" x2="1140" y2="710"/>
    </g>
    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="290" y1="710" x2="290" y2="733"/><line x1="715" y1="710" x2="715" y2="733"/><line x1="1140" y1="710" x2="1140" y2="733"/>
    </g>

    <g filter="url(#sh)">
    {j(L5)}
    </g>

    <g stroke="{B}" stroke-width="2">
      <line x1="290" y1="840" x2="290" y2="863"/><line x1="715" y1="840" x2="715" y2="863"/><line x1="1140" y1="840" x2="1140" y2="863"/>
      <line x1="290" y1="870" x2="1140" y2="870"/>
    </g>
    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="525" y1="870" x2="525" y2="893"/><line x1="1125" y1="870" x2="1125" y2="893"/>
    </g>

    <g filter="url(#sh)">
    {j(L6)}
    </g>

    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="525" y1="1000" x2="525" y2="1053"/><line x1="1125" y1="1000" x2="1125" y2="1053"/>
    </g>

    <g filter="url(#sh)">
    {j(L7)}
    </g>

    <g stroke="{B}" stroke-width="2.4" marker-end="url(#mB)">
      <line x1="525" y1="1160" x2="525" y2="1183"/><line x1="1125" y1="1160" x2="1125" y2="1183"/>
    </g>

    <g filter="url(#sh)">
      <rect x="90" y="1190" width="1270" height="76" rx="8" fill="{BS}" stroke="{B}" stroke-width="1.6"/>
      <text x="725" y="1220" font-size="14" font-weight="800" fill="{BD}" text-anchor="middle">七处 MySQL / PG 差异（面试安全底线，说反等于自曝）</text>
      <text x="725" y="1246" font-size="11.5" fill="{TX2}" text-anchor="middle">默认 RC（非 RR）· 版本留堆（非 undo 链）· VACUUM 回收（非自动 purge）· 无间隙锁靠 SSI · 堆表必回表 · 单一日志 WAL · 进程模型连接贵</text>
    </g>
  </svg>'''

STORY = u'''<b>主干叙事（一段读完）</b>：PG 的一切差异都从两个结构性事实推出来 —— <b>堆表</b>（索引只是「指向数据的路标」，所有索引都要回表）和<b>版本留在堆里</b>（更新即新版本，旧版本靠 VACUUM 回收，<b>回收不自动</b>）。
    <b>存与索引</b>：B-tree 是默认（覆盖面最广），GIN 的倒排天然匹配「包含」；部分索引把调度器索引做到 1/100 但会静默失效；CONCURRENTLY 失败留下 invalid 索引——它仍被优化器计算，纯负债，删掉重建。
    <b>执行</b>：EXPLAIN ANALYZE 看 actual rows 与 loops（total = actual × loops，从最贵叶子往上看）；估行数失真先查统计信息（默认 100 桶，大表导入后手动 ANALYZE）。
    <b>事务与锁</b>：默认 <b>READ COMMITTED</b>；Serializable 是 SSI——<b>代价是失败（40001）不是等待</b>，应用必须能重试；<b>没有间隙锁</b>，跨行不变量靠显式约束 + 条件更新，不靠「先查一遍」。
    <b>持久化</b>：只有一套 WAL（没有 undo）——这正是旧版本必须靠 VACUUM 回收的原因；恢复时长 = checkpoint 落后的 WAL 量 ÷ 重放速度。
    <b>回收是主戏</b>：长事务按住回收边界（idle in transaction 也要防），2 小时 × 1000 行/s = 720 万死元组；autovacuum 默认要堆 20% 死元组才动手；事务 ID 32 位靠冻结重置。
    <b>增长与落地</b>：分区的价值是「丢弃即归档」；进程模型连接贵，连接池是刚需（事务池化破坏预处理语句）；业务侧用条件更新（FOR UPDATE 吞吐 = 1÷持锁时长）+ 唯一约束兜底幂等。'''

CAP = u'''<b>读法</b>：蓝线主线；紫框是并发与失效（PG 与 MySQL 差异最大的一段）；绿框是回收与增长（PG 独有的运维主戏）；底部横幅是七处 MySQL/PG 差异——<b>每一条都能从「堆表 + 版本留堆」两个根推出</b>。'''

ROWS = [
    (u'P1 索引选型', u'五种索引各答什么', u'索引能回答哪类查询由组织方式决定：B-tree 默认（等值/范围/排序覆盖面最广）；GIN 倒排天然匹配「包含」（JSONB/数组）；GiST 范围几何、BRIN 时序大表；GIN 写入贵——先问操作符，再看组织方式，最后看写路径', u'1、2', u'未使用 —— 判据：「先建哪个」考的是知不知道 GIN 更贵'),
    (u'P2 堆表回表', u'为什么都要回表', u'PG 是堆表：索引只存「值 → 位置」，回表随命中行数线性涨（InnoDB 至少主键不回）；Index Only Scan 的判据是「页全可见」不是「列齐」——前提是 visibility map 正常，即 VACUUM 一直在跑', u'3、5', u'EnergyOps：事实表按（等值在前、范围在后）建索引；优化重心是减少扫描与回表，不凑覆盖索引'),
    (u'P3 部分索引', u'什么场景省一大截', u'部分索引只覆盖「WHERE 里那部分行」（调度器只查活跃态 → 体积 1/100、写入与 VACUUM 同步减负）；表达式索引把 lower(email) 的结果当索引键；部分唯一索引 = 软删除经典解；最大风险：需求变了它静默失效', u'4', u'未使用 —— 部分索引必须写清「它服务谁」，这是它和普通索引最大的不同'),
    (u'P4 索引代价', u'在线建索引的坑', u'三项代价：写放大（每个索引多一份维护）、空间、VACUUM 压力；HOT 更新（不改索引列 + 页内有空间）免索引维护；CONCURRENTLY 两阶段不阻塞写入但慢——失败留下 INVALID 索引：仍被计算、拖慢规划，删掉重建', u'6、7、34', u'未使用 —— PG 方言：CONCURRENTLY 失败留 invalid（MySQL 影子表方案对应物不同）'),
    (u'P5 类型选型', u'text / jsonb / 主键 / 时间', u'text 与 varchar 无性能差（存法一样）、char(n) 真实有代价；jsonb 可建 GIN（选了它才有索引可言）但丢重复键改键序——签名校验会悄悄坏；identity 替代 serial（SQL 标准）；timestamptz 默认答案，timestamp 只留给「墙上时间」', u'8–12', u'EnergyOps：能耗事实表用 timestamptz + 数值类型按口径选'),
    (u'P6 执行计划', u'看计划看什么', u'EXPLAIN ANALYZE 才是真相（cost 是估算、只能比同一条 SQL 的两个计划）；loops 是乘数（total = actual × loops），从最贵叶子往上看；BUFFERS 必加——分不清算法差还是缓存冷；Bitmap Heap Scan = 两步走（索引定位 + 堆顺序取）', u'13、15', u'EnergyOps：EXPLAIN ANALYZE 是索引设计唯一依据；坑：把「看到 Index Scan」当成功，接口还是慢'),
    (u'P7 统计信息', u'估行为什么不准', u'估行数 = 各条件独立假设相乘，JOIN 后膨胀；默认 100 桶 + MCV 兜最热 100 值，长尾列失真；大表 auto-analyze 阈值是行数比例——批量导入后必须手动 ANALYZE；generic plan 在参数分布倾斜时翻车（EXPLAIN 快、线上慢的标准答案）', u'14、16', u'EnergyOps：JOIN 后行数膨胀导致优化器选错——先修统计信息与写法，不是先换索引'),
    (u'P8 隔离级别', u'默认 RC 与读一致性', u'默认 READ COMMITTED（每条语句取新快照）；PG 的 RR 比 SQL 标准强（快照取自事务第一条语句）但写冲突直接报错；「调高级别更安全」的反向代价：快照更旧更久 → 死元组更多 → 膨胀更快；序列不是事务性的（自增必有洞）', u'17、18', u'数驭穹图：LIVE_READ 强制只读事务 + 超时 + 取消能力——事务边界是生产纪律'),
    (u'P9 SSI 失败重试', u'Serializable 为什么失败', u'SSI 不额外阻塞、检测到「组合不可串行」就中止（40001）；谓词锁会升级（读 264KB 就把整表标读过）→ 冲突面放大；错误用错误码判（40001 是契约），重试框架必须覆盖 COMMIT 失败；对确定性错误无脑重试 = 制造重复副作用', u'19', u'未使用 —— 判据：能重试就用 SSI/乐观；冲突率高到重试成本超过加锁才用悲观'),
    (u'P10 无间隙锁', u'幻读与不变量靠什么', u'PG 无间隙锁：「先查一遍再插入」天然竞态，必须唯一约束兜底；幻读防护靠 SSI（可选），业务不变量靠显式约束 + 条件更新；FOR UPDATE 四变体按冲突矩阵选（外键用最弱的 FOR KEY SHARE）；advisory lock 会话级回滚不释放；锁默认无限等', u'20–22', u'RuleArena：PG 无间隙锁 → 跨行不变量（refunded+amount≤paid）不能靠「我先查」，只能条件更新 + 约束'),
    (u'P11 WAL', u'提交过为什么不丢', u'WAL 单一日志（无 undo）：synchronous_commit 是唯一承诺的落盘点（无备库时 remote_apply 与 on 无区别）；checkpoint 把脏页落盘、允许重用 WAL；恢复时长 = checkpoint 落后量 ÷ 重放速度；full_page_writes 让 checkpoint 越勤 WAL 越大（整页镜像）', u'23、24', u'数驭穹图：PG 源的增量同步路径建立在 WAL / 逻辑复制上'),
    (u'P12 复制', u'流复制 vs 逻辑复制', u'流复制复制存储变化（整实例、字节级、备只读）；逻辑复制复制数据变化（按表、可跨版本、可筛选）；synchronous_commit 五档 = RPO 与延迟的正交矩阵；复制槽默认无限保留 WAL——一个消费者掉线，不到一天主库不可写', u'25、26', u'数驭穹图：只要「授权的分析数据集」→ 走逻辑路径；第一版快照 + 轮询，不上完整 CDC'),
    (u'P13 MVCC', u'xmin/xmax 与死元组', u'版本留在堆里：UPDATE = 插新版本 + 旧版本标 xmax；可见性 = 拿快照比 xmin/xmax，读不加锁；代价：一张更新频繁的表占用可达有效数据数倍；索引也指向死元组 → 索引多则 VACUUM 更累；HOT 更新免索引维护（可量化：n_tup_hot_upd 占比）', u'27、28', u'RuleArena：条件更新读权威 Snapshot 判定——多版本让「读权威」随时可行'),
    (u'P14 长事务', u'表膨胀的机制', u'回收边界由最老快照决定：2 小时长事务 + 每秒 1000 次更新 = 720 万死元组（且复制到每个索引）；只读长事务同样按边界（idle in transaction 有专门超时参数）；膨胀正反馈：扫描更多页 → 缓存有效行变少 → 更慢 → 事务更长', u'29', u'数驭穹图：长事务阻塞 VACUUM、拉长快照持有——发布前校验新鲜度与位点'),
    (u'P15 VACUUM', u'回收与事务 ID 回卷', u'VACUUM 三件事：清死元组（空间标可复用不缩文件）、更新可见性映射、冻结旧元组；autovacuum 阈值 = 50 + 0.2×行数（大表最经不起堆积却最晚动手，max_workers 默认 3）；事务 ID 32 位 ≈ 43 亿：靠冻结重置，回卷红线前 PG 宁肯拒服；膨胀已发生：先切源头再 pg_repack', u'30–32', u'未使用 —— 判据：「跑完 VACUUM 表还是 10GB」是设计不是故障'),
    (u'P16 分区', u'什么时候才值得分', u'三种分区（范围/列表/哈希）；收益一：分区裁剪（扫描量降到命中分区）；收益二（更值钱）：DROP PARTITION = 元数据操作，DELETE = 大清理；代价：唯一约束必须含分区键（分区结构的数学后果）、分区上在线建索引是一套流程；EnergyOps 当前规模未分区', u'33', u'EnergyOps：分区列为「暂缓」——等容量与 SLO 证明不足才升级，不预先优化'),
    (u'P17 连接池', u'连接为什么贵', u'进程模型：每连接一个进程（内存 + fork 成本），连接很贵 → 池是刚需；work_mem 是「每个操作」的上限：实际内存 = 连接数 × 节点数 × work_mem（100×4MB=400MB 是错的）；三种池化：会话安全省最少、事务省最多但破坏预处理语句（pgbouncer 经典坑）', u'35', u'未使用 —— 判据：池化解决「连接多」，超时解决「事务长」——正交问题都要做'),
    (u'P18 乐观并发', u'项目里怎么选', u'条件更新 = 期望值进 WHERE（version 防状态回流；状态会 READY→SEARCHING→READY 时只有版本号能区分两轮）；影响 0 行是业务分支；FOR UPDATE 吞吐 = 1÷持锁时长（与并发无关）vs 条件更新成本 = 1/(1−p)——冲突率定选型；「用不用乐观」最终是幂等设计问题', u'36、39', u'EnergyOps + RuleArena：条件更新 + version；理由是「权威性」不是「低频写」，别说满「不用锁」'),
    (u'P19 唯一约束', u'幂等的最终防线', u'应用层幂等不够：唯一约束的失败是确定的（23505 = 「做过」，可查 Receipt 返回原结果）；幂等键按业务身份构造（ToolCallID 每次都变是反例）；复合唯一别漏 NOT NULL（NULL 不参与唯一判重）；UPSERT 四坑：excluded 可能被触发器改过、序列必有洞、DO UPDATE 需要 NOT DEFERRABLE 排除约束、死元组加速消耗', u'37、38', u'RuleArena：UNIQUE(run_id, action_type, idempotency_key) 兜底资金正确性；副作用与 Receipt 同一事务提交'),
]

SVG04 = f'''<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="PostgreSQL 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="{GD}">长事务的膨胀账（PG 比 MySQL 更狠的一段）</text>
      <text x="80" y="78" font-size="11.5" fill="{TX2}">一个 2 小时长事务按住回收边界；期间每秒 1000 次更新 → 720 万死元组，且复制到每个索引</text>
      <rect x="80" y="92" width="420" height="22" rx="4" fill="{O}" opacity="0.9"/>
      <text x="88" y="108" font-size="12" font-weight="800" fill="#fff">　死元组 7,200,000（堆 + 每个索引各一份）</text>
      <text x="80" y="150" font-size="12" font-weight="800" fill="{TX}">autovacuum 默认阈值 = 50 + 0.2 × 行数：1000 万行的表要堆 200 万死元组才动手</text>
      <text x="80" y="176" font-size="11.5" fill="{TX2}">大表最经不起堆积、却最晚触发——max_workers 默认 3，表多还要排队</text>
      <text x="80" y="202" font-size="11.5" fill="{TX2}">只读长事务同样按边界（idle in transaction）：它「什么都没干」，但 xmin 挡住全库回收</text>
      <text x="80" y="228" font-size="11.5" fill="{TX2}">膨胀正反馈：扫描更多页 → 缓存有效行变少 → 查询更慢 → 事务拖更长</text>
      <text x="80" y="260" font-size="11.5" font-weight="700" fill="{GD}">三道防线：idle_in_transaction_session_timeout / 事务不包外部调用 / 先切源头再 pg_repack</text>
      <text x="80" y="292" font-size="10.5" fill="{GREY}">事务 ID 32 位 ≈ 43 亿：500 TPS 约 100 天走完一圈——靠冻结重置，回卷红线前 PG 宁肯拒服</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="{OD}">FOR UPDATE 的天花板 vs 条件更新</text>
      <text x="760" y="78" font-size="11.5" fill="{TX2}">FOR UPDATE 的吞吐 = 1 ÷ 持锁时长，与并发数无关——排队是硬天花板（持锁 5ms → 200 TPS）</text>
      <g font-size="11.5" fill="{TX2}">
        <text x="760" y="104">并发 10 —— 吞吐 200 TPS</text>
        <rect x="960" y="94" width="200" height="12" rx="3" fill="{O}"/>
        <text x="760" y="126">并发 50 —— 吞吐 200 TPS（不变）</text>
        <rect x="960" y="116" width="200" height="12" rx="3" fill="{O}"/>
        <text x="760" y="148">并发 100 —— 吞吐 200 TPS（仍不变）</text>
        <rect x="960" y="138" width="200" height="12" rx="3" fill="{O}"/>
      </g>
      <text x="760" y="184" font-size="11.5" fill="{TX2}">条件更新成本 = 期望尝试次数 1/(1−p)：p=0.3 → 1.4 次、p=0.6 → 2.5 次——冲突率决定选型</text>
      <text x="760" y="210" font-size="11.5" fill="{TX2}">影响行数 0 = 业务分支：读权威 Snapshot → 判定 → 决定，不写 while(true) 重试</text>
      <text x="760" y="236" font-size="11.5" fill="{TX2}">RC 下「先查再写」必然有竞态；第二个更新者会等第一个提交后基于新值再判——不是报错</text>
      <text x="760" y="266" font-size="11.5" font-weight="700" fill="{OD}">RuleArena 的理由是「权威性」不是「低频写」：资金正确性靠 UNIQUE(run_id, action_type, idempotency_key) 兜底</text>
      <text x="760" y="292" font-size="10.5" fill="{GREY}">能幂等就不用锁——幂等键按业务身份构造（ToolCallID 每次都变，是标准反例）</text>
    </g>
  </svg>'''

NUMS = [
    ('b', u'两小时长事务', u'720 万死元组', u'1000 行/s × 7200s，且复制到每个索引——长事务拖全库的不是 CPU，是回收停摆。'),
    ('o', u'autovacuum 阈值', u'50 + 0.2 × 行数', u'1000 万行的表要堆 200 万死元组才触发——大表最经不起堆积、却最晚动手。'),
    ('b', u'SSI 谓词锁升级', u'264 KB = 整表', u'读 264KB 就把整张表标「我读过」（16GB 表的 1/60000）——40001 的冲突面被放大到表级。'),
    ('b', u'FOR UPDATE 天花板', u'200 TPS', u'吞吐 = 1 ÷ 持锁时长（5ms），加并发无效；条件更新的成本是期望尝试次数，与冲突率相关。'),
    ('o', u'条件更新', u'p=0.6 → 2.5 次', u'E = 1/(1−p)：冲突率 60% 时期望 2.5 次尝试——与「悲观排队」的成本曲线交点就是选型。'),
    ('b', u'事务 ID 回卷', u'43 亿 ≈ 100 天', u'32 位事务 ID，500 TPS 约 100 天走完一圈——靠冻结重置；回卷红线前 PG 宁肯拒绝服务。'),
    ('o', u'work_mem 乘法', u'100×3×4MB', u'work_mem 是「每个操作」的上限：实际内存 = 连接数 × 排序/哈希节点数 × work_mem ≈ 1.2GB，不是 400MB。'),
    ('b', u'统计桶', u'默认 100 个', u'MCV 只兜最热 100 值、直方图 100 桶——长尾列估算失真；大表导入后手动 ANALYZE 是刚需。'),
    ('o', u'部分索引', u'体积 1/100', u'调度器只查活跃态：只索引活跃行，写入与 VACUUM 同步减负——代价是会静默失效。'),
]

MIS = [
    (u'✗「PG 默认 RR，跟 MySQL 一样」', u'✓ 默认 READ COMMITTED；PG 的 RR 也比 SQL 标准强（快照取自第一条语句），且写冲突直接报错。'),
    (u'✗「PG 的 MVCC 靠 undo log」', u'✓ 版本留在堆里（xmin/xmax），旧版本靠 VACUUM 回收——「回收不自动」是 PG 一切运维课题的来源。'),
    (u'✗「看到 Index Scan 就是优化成功」', u'✓ 真正看 actual rows / loops / 过滤行数 + 分段计时——EnergyOps 的坑：接口还是慢。'),
    (u'✗「Index Only Scan 就是索引列齐了」', u'✓ 判据是可见性：页全可见才免回表——前提是 VACUUM 一直正常跑。'),
    (u'✗「PG 没间隙锁，幻读没防护」', u'✓ 防护靠 SSI（可串行化，可选）；业务不变量靠显式约束 + 条件更新，不是默认级别。'),
    (u'✗「VACUUM 完表应该变小」', u'✓ 常规 VACUUM 只把空间标为可复用，表文件不变小是设计；要缩表用 pg_repack / VACUUM FULL（排他锁）。'),
    (u'✗「更新列不在索引里就没代价」', u'✓ 只有 HOT 路径成立（不动索引列 + 页内有空间）；否则每个索引多一个死元组等 VACUUM。'),
    (u'✗「连接池配好就万事大吉」', u'✓ 池化解决「连接多」，超时解决「事务长」——正交问题；事务池化还会破坏预处理语句。'),
]

CRITS = [
    u'能用「操作符 → 组织方式 → 写路径」三步做索引选型；能说清 GIN 为什么天然答「包含」；能判断「先建哪个」考的是 GIN 更贵。',
    u'能从「堆表 vs 索引组织表」推出回表必然后；能说清 Index Only Scan 的判据是可见性不是列齐；能给出 INCLUDE 的用法。',
    u'能算部分索引的体积收益（1/100）并说出静默失效风险；能用部分唯一索引解软删除；能解释 now() 为什么不能建表达式索引。',
    u'能算写放大的元组数并说清 HOT 的两个条件；能解释 CONCURRENTLY 失败为什么留 INVALID 索引、为什么它是纯负债。',
    u'能算 varchar(255) 与 text 同数据的存储并说「无性能差」；能给出 jsonb 的两个真实代价；能分清 timestamptz 与 timestamp 的语义。',
    u'能背五步看计划顺序；能用 loops 算总耗时；能解释 cost 为什么不能跨 SQL 比；能说出 BUFFERS 区分算法差与缓存冷。',
    u'能算 auto-analyze 的触发阈值；能用独立假设解释 JOIN 膨胀；能说出 generic plan 翻车的参数分布与「EXPLAIN 快线上慢」的答案。',
    u'能答对默认 RC 并说清 RC 下两次查询结果不同；能解释 PG 的 RR 为什么更强还报错；能说出「调高级别 → 膨胀更快」的反向代价。',
    u'能说清 SSI 的代价是失败不是等待；能用 264KB 的谓词锁升级解释冲突面放大；能设计覆盖 COMMIT 失败的重试框架。',
    u'能解释无间隙锁下「先查再插」的竞态；能按冲突矩阵选 FOR UPDATE 变体；能说出会话级 advisory lock 回滚不释放的坑。',
    u'能说出 synchronous_commit 是唯一落盘承诺并解释 remote_apply 无备库时无效；能算恢复时长 = checkpoint 落后量 ÷ 重放速度。',
    u'能用「复制存储变化 vs 数据变化」推出两种复制的全部差异；能背 synchronous_commit 五档矩阵；能算复制槽掉线多久主库不可写。',
    u'能画 xmin/xmax 的可见性判定；能算一次 UPDATE 的元组代价；能解释「索引多 → VACUUM 更累」的机制链。',
    u'能算 2 小时长事务的死元组数；能解释只读长事务为什么同样有害；能画出膨胀的正反馈环。',
    u'能说清 VACUUM 的三件事与「不缩文件」的设计；能算 autovacuum 触发阈值；能拆冻结三级阶梯并解释回卷保护。',
    u'能给出三种分区与两条收益（裁剪 + 丢弃即归档）；能解释唯一约束为什么必须带分区键；能反向说出「不该分区」的判据。',
    u'能从进程模型推出连接贵；能算 work_mem 的三因子乘法；能说出事务池化破坏预处理语句的现场表现。',
    u'能写出条件更新的完整形态（含 version 防回流）；能算 FOR UPDATE 的吞吐天花板；能把项目选型讲成「权威性」理由。',
    u'能解释唯一约束为什么是最终防线（失败是确定的）；能构造业务幂等键并给出 ToolCallID 反例；能说出 UPSERT 的四个坑。',
]

finish('PostgreSQL',
       headline=u'19 张母题 · 39 道题 · 3 个项目 —— 一条线：两个根（堆表 + 版本留堆）推出全部差异 → 七条主线 → 七处 MySQL/PG 差异',
       sec01_title=u'主干：两个根 → 七条主线（读快 → 写稳 → 持久 → 回收 → 增长 → 落地）',
       sec01_sub=u'<b>一切差异的根只有两个</b>：堆表（索引只是路标）与版本留在堆里（回收不自动）。七条主线从这两个根推出；底部横幅是七处 MySQL/PG 差异的安全底线。',
       svg01=SVG01, story=STORY, cap=CAP, rows=ROWS,
       sec04_title=u'两笔账：长事务的膨胀账，FOR UPDATE 的天花板',
       sec04_sub=u'左边是 PG 独有的回收危机（回收不自动的代价），右边是并发控制的选型账——都是数量级问题。',
       sec04_src=u'正本 母题-P14/P15 · 母题-P18',
       svg04=SVG04, nums=NUMS, mis=MIS, crits=CRITS)
