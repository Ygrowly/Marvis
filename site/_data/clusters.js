/* 能力簇与主线清单 —— 进度页数据源
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
  {
    id: 'llm', name: 'LLM 与上下文', zone: '一档',
    topics: [
      { id: '1', name: '模型为什么不可靠', href: 'modules/LLM与上下文-01-模型为什么不可靠.html', cards: ['C4', 'C5'], pages: ['topics/LLM与上下文-母题-C4-幻觉的成因与可控性.html', 'topics/LLM与上下文-母题-C5-模型选型与降级三角.html'] },
      { id: '2', name: '上下文怎么装配与维持', href: 'modules/LLM与上下文-02-上下文怎么装配与维持.html', cards: ['C1', 'C6'], pages: ['topics/LLM与上下文-母题-C1-上下文组装与窗口预算.html', 'topics/LLM与上下文-母题-C6-成本与长上下文截断.html'] },
      { id: '3', name: '输出怎么被约束与验收', href: 'modules/LLM与上下文-03-输出怎么被约束与验收.html', cards: ['C2', 'C3'], pages: ['topics/LLM与上下文-母题-C2-结构化输出与JSON可靠性.html', 'topics/LLM与上下文-母题-C3-Prompt版本管理与回归.html'] }
    ]
  },
  {
    id: 'mysql', name: 'MySQL', zone: '一档',
    topics: [
      { id: '1', name: '索引与表设计', href: 'modules/MySQL-01-索引与表设计.html', cards: ['M1', 'M2', 'M3', 'M4', 'M5'], pages: ['topics/MySQL-母题-M1-为什么用B+树.html', 'topics/MySQL-母题-M2-联合索引与最左前缀.html', 'topics/MySQL-母题-M3-聚簇索引与回表.html', 'topics/MySQL-母题-M4-索引代价与大表变更.html', 'topics/MySQL-母题-M5-引擎与表设计基本盘.html'] },
      { id: '2', name: 'SQL 执行与优化', href: 'modules/MySQL-02-SQL 执行与优化.html', cards: ['M6', 'M7'], pages: ['topics/MySQL-母题-M6-一条SQL的执行链路.html', 'topics/MySQL-母题-M7-慢查询与SQL优化手段.html'] },
      { id: '3', name: '事务与锁', href: 'modules/MySQL-03-事务与锁.html', cards: ['M8', 'M9', 'M10'], pages: ['topics/MySQL-母题-M8-隔离级别与ACID.html', 'topics/MySQL-母题-M9-MVCC.html', 'topics/MySQL-母题-M10-锁与死锁.html'] },
      { id: '4', name: '日志与持久化', href: 'modules/MySQL-04-日志与持久化.html', cards: ['M11', 'M12'], pages: ['topics/MySQL-母题-M11-三日志与两阶段提交.html', 'topics/MySQL-母题-M12-崩溃恢复.html'] },
      { id: '5', name: '长事务', href: 'modules/MySQL-05-长事务.html', cards: ['M13'], pages: ['topics/MySQL-母题-M13-长事务为什么危险.html'] },
      { id: '6', name: '数据增长与高可用', href: 'modules/MySQL-06-数据增长与高可用.html', cards: ['M14', 'M15'], pages: ['topics/MySQL-母题-M14-主从复制与延迟.html', 'topics/MySQL-母题-M15-数据增长治理.html'] },
      { id: '7', name: '业务并发场景', href: 'modules/MySQL-07-业务并发场景.html', cards: ['M16', 'M17'], pages: ['topics/MySQL-母题-M16-乐观锁与悲观锁.html', 'topics/MySQL-母题-M17-排行榜与防超卖.html'] }
    ]
  },
  {
    id: 'agent', name: 'Agent 运行时与工具', zone: '一档',
    topics: [
      { id: '1', name: '循环怎么转、什么时候停', href: 'modules/Agent运行时与工具-01-循环怎么转、什么时候停.html', cards: ['A1', 'A2'], pages: ['topics/Agent运行时与工具-母题-A1-计划执行循环与停止条件.html', 'topics/Agent运行时与工具-母题-A2-工具调用与MCP边界.html'] },
      { id: '2', name: '中断与失败之后怎么继续', href: 'modules/Agent运行时与工具-02-中断与失败之后怎么继续.html', cards: ['A3', 'A4', 'A5'], pages: ['topics/Agent运行时与工具-母题-A3-失败恢复与幂等.html', 'topics/Agent运行时与工具-母题-A4-长任务状态与Checkpoint.html', 'topics/Agent运行时与工具-母题-A5-上下文压缩与记忆.html'] },
      { id: '3', name: '风险与复杂度怎么管', href: 'modules/Agent运行时与工具-03-风险与复杂度怎么管.html', cards: ['A6', 'A7', 'A8'], pages: ['topics/Agent运行时与工具-母题-A6-沙箱权限与可信执行.html', 'topics/Agent运行时与工具-母题-A7-多Agent拆分与协作.html', 'topics/Agent运行时与工具-母题-A8-动态计划下的可靠执行.html'] }
    ]
  },
  {
    id: 'redis', name: 'Redis 与缓存', zone: '一档',
    topics: [
      { id: '1', name: '它为什么快、五种结构各解决什么问题', href: 'modules/Redis-01-它为什么快、五种结构各解决什么问题.html', cards: ['R1'], pages: ['topics/Redis-母题-R1-Redis数据结构与选型.html'] },
      { id: '2', name: '数据怎么不丢', href: 'modules/Redis-02-数据怎么不丢.html', cards: ['R2'], pages: ['topics/Redis-母题-R2-持久化与内存淘汰.html'] },
      { id: '3', name: '缓存怎么用不出事故', href: 'modules/Redis-03-缓存怎么用不出事故.html', cards: ['R3'], pages: ['topics/Redis-母题-R3-缓存一致性与三类事故.html'] },
      { id: '4', name: '生产里怎么不出大事', href: 'modules/Redis-04-生产里怎么不出大事.html', cards: ['R4', 'R5'], pages: ['topics/Redis-母题-R4-大key与热key.html', 'topics/Redis-母题-R5-缓存的边界.html'] }
    ]
  },
  {
    id: 'rag', name: 'RAG 与检索', zone: '一档',
    topics: [
      { id: '1', name: '知识怎么进来', href: 'modules/RAG与检索-01-知识怎么进来.html', cards: ['G1', 'G6'], pages: ['topics/RAG与检索-母题-G1-切分策略与索引粒度.html', 'topics/RAG与检索-母题-G6-知识更新与增量索引.html'] },
      { id: '2', name: '怎么把对的证据捞回来', href: 'modules/RAG与检索-02-怎么把对的证据捞回来.html', cards: ['G2', 'G3'], pages: ['topics/RAG与检索-母题-G2-向量与关键词的混合检索.html', 'topics/RAG与检索-母题-G3-重排与召回质量.html'] },
      { id: '3', name: '捞回来之后怎么用、怎么证明', href: 'modules/RAG与检索-03-捞回来之后怎么用、怎么证明.html', cards: ['G4', 'G5'], pages: ['topics/RAG与检索-母题-G4-引用绑定与证据可追溯.html', 'topics/RAG与检索-母题-G5-RAG评测与幻觉率.html'] }
    ]
  },
  {
    id: 'net', name: '网络基础', zone: '一档',
    topics: [
      { id: '1', name: '一次请求怎么走完', href: 'modules/网络基础-01-一次请求怎么走完.html', cards: ['N1'], pages: ['topics/网络-母题-N1-一次请求的完整路径.html'] },
      { id: '2', name: '数据怎么从服务端到客户端', href: 'modules/网络基础-02-数据怎么从服务端到客户端.html', cards: ['N2'], pages: ['topics/网络-母题-N2-SSE与推送模型.html'] },
      { id: '3', name: '怎么同时扛住很多连接', href: 'modules/网络基础-03-怎么同时扛住很多连接.html', cards: ['N3'], pages: ['topics/网络-母题-N3-进程线程与协程.html'] }
    ]
  },
  {
    id: 'eval', name: '评测观测与治理', zone: '一档',
    topics: [
      { id: '1', name: '怎么定义什么算好', href: 'modules/评测观测与治理-01-怎么定义什么算好.html', cards: ['E1'], pages: ['topics/评测观测与治理-母题-E1-评测集设计与pass^k.html'] },
      { id: '2', name: '怎么看见为什么', href: 'modules/评测观测与治理-02-怎么看见为什么.html', cards: ['E2', 'E3'], pages: ['topics/评测观测与治理-母题-E2-Trace与可观测性.html', 'topics/评测观测与治理-母题-E3-回归门禁与发布卡口.html'] },
      { id: '3', name: '怎么安全地变', href: 'modules/评测观测与治理-03-怎么安全地变.html', cards: ['E4', 'E5', 'E6', 'E7'], pages: ['topics/评测观测与治理-母题-E4-成本控制与限流.html', 'topics/评测观测与治理-母题-E5-越权与提示注入防护.html', 'topics/评测观测与治理-母题-E6-灰度发布与回滚.html', 'topics/评测观测与治理-母题-E7-AgentOps平台与自建Trace-Eval.html'] }
    ]
  },
  {
    id: 'mq', name: '消息队列', zone: '一档',
    topics: [
      { id: '1', name: '消息怎么才能不丢', href: 'modules/消息队列-01-消息怎么才能不丢.html', cards: ['Q1'], pages: ['topics/消息队列-母题-Q1-消息为什么会丢怎么才不丢.html'] },
      { id: '2', name: '消息为什么会重复、会乱序', href: 'modules/消息队列-02-消息为什么会重复、会乱序.html', cards: ['Q2'], pages: ['topics/消息队列-母题-Q2-重复与乱序.html'] },
      { id: '3', name: 'MQ 撑不住的时候怎么办', href: 'modules/消息队列-03-MQ 撑不住的时候怎么办.html', cards: ['Q3'], pages: ['topics/消息队列-母题-Q3-积压与高可用.html'] }
    ]
  },
  {
    id: 'lock', name: '并发与锁', zone: '一档',
    topics: [
      { id: '1', name: '要不要加锁', href: 'modules/并发与锁-01-要不要加锁.html', cards: ['L1'], pages: ['topics/并发与锁-母题-L1-乐观锁与悲观锁.html'] },
      { id: '2', name: '锁画多大', href: 'modules/并发与锁-02-锁画多大.html', cards: ['L2'], pages: ['topics/并发与锁-母题-L2-锁的粒度与临界区.html'] },
      { id: '3', name: '多台机器怎么抢同一份资源', href: 'modules/并发与锁-03-多台机器怎么抢同一份资源.html', cards: ['L3'], pages: ['topics/并发与锁-母题-L3-分布式锁与fencing-token.html'] }
    ]
  },
  {
    id: 'linux', name: 'Linux 与部署', zone: '一档',
    topics: [
      { id: '1', name: '盒子', href: 'modules/Linux与部署-01-盒子.html', cards: ['X1'], pages: ['topics/Linux与部署-母题-X1-容器是什么.html'] },
      { id: '2', name: '上线', href: 'modules/Linux与部署-02-上线.html', cards: ['X2'], pages: ['topics/Linux与部署-母题-X2-服务怎么上线.html'] },
      { id: '3', name: '排查', href: 'modules/Linux与部署-03-排查.html', cards: ['X3'], pages: ['topics/Linux与部署-母题-X3-线上排查的顺序.html'] }
    ]
  },
  {
    id: 'pg', name: 'PostgreSQL', zone: '二档',
    topics: [
      { id: '1', name: '索引与表设计', href: 'modules/PostgreSQL-01-索引与表设计.html', cards: ['P1', 'P2', 'P3', 'P4', 'P5'], pages: ['topics/PostgreSQL-母题-P1-索引类型选型.html', 'topics/PostgreSQL-母题-P2-堆表与回表.html', 'topics/PostgreSQL-母题-P3-部分索引与表达式索引.html', 'topics/PostgreSQL-母题-P4-索引代价与在线建索引.html', 'topics/PostgreSQL-母题-P5-表设计与数据类型.html'] },
      { id: '2', name: 'SQL 执行与优化', href: 'modules/PostgreSQL-02-SQL 执行与优化.html', cards: ['P6', 'P7'], pages: ['topics/PostgreSQL-母题-P6-执行计划怎么看.html', 'topics/PostgreSQL-母题-P7-统计信息与慢查询定位.html'] },
      { id: '3', name: '事务与锁', href: 'modules/PostgreSQL-03-事务与锁.html', cards: ['P8', 'P9', 'P10'], pages: ['topics/PostgreSQL-母题-P8-隔离级别与读一致性.html', 'topics/PostgreSQL-母题-P9-序列化失败与重试.html', 'topics/PostgreSQL-母题-P10-无间隙锁与锁变体.html'] },
      { id: '4', name: '日志与持久化', href: 'modules/PostgreSQL-04-日志与持久化.html', cards: ['P11', 'P12'], pages: ['topics/PostgreSQL-母题-P11-WAL与checkpoint.html', 'topics/PostgreSQL-母题-P12-流复制与逻辑复制.html'] },
      { id: '5', name: '长事务', href: 'modules/PostgreSQL-05-长事务.html', cards: ['P13', 'P14', 'P15'], pages: ['topics/PostgreSQL-母题-P13-MVCC与可见性.html', 'topics/PostgreSQL-母题-P14-长事务与表膨胀.html', 'topics/PostgreSQL-母题-P15-VACUUM与事务ID回卷.html'] },
      { id: '6', name: '数据增长与高可用', href: 'modules/PostgreSQL-06-数据增长与高可用.html', cards: ['P16', 'P17'], pages: ['topics/PostgreSQL-母题-P16-分区表.html', 'topics/PostgreSQL-母题-P17-连接模型与连接池.html'] },
      { id: '7', name: '业务并发场景', href: 'modules/PostgreSQL-07-业务并发场景.html', cards: ['P18', 'P19'], pages: ['topics/PostgreSQL-母题-P18-乐观并发控制.html', 'topics/PostgreSQL-母题-P19-唯一约束与UPSERT.html'] }
    ]
  },
  {
    id: 'os', name: '操作系统', zone: '二档',
    topics: [
      { id: '1', name: 'CPU 怎么决定先跑谁', href: 'modules/操作系统-01-CPU 怎么决定先跑谁.html', cards: ['O1'], pages: ['topics/操作系统-母题-O1-上下文切换与死锁.html'] },
      { id: '2', name: '内存为什么看起来够用', href: 'modules/操作系统-02-内存为什么看起来够用.html', cards: ['O2'], pages: ['topics/操作系统-母题-O2-虚拟内存与缺页.html'] },
      { id: '3', name: 'IO 为什么慢、内核能省掉什么', href: 'modules/操作系统-03-IO 为什么慢、内核能省掉什么.html', cards: ['O3'], pages: ['topics/操作系统-母题-O3-IO模型与零拷贝.html'] }
    ]
  },
  {
    id: 'store', name: '数据存储选型', zone: '二档',
    topics: [
      { id: '1', name: '分野', href: 'modules/数据存储选型-01-分野.html', cards: ['S1'], pages: ['topics/数据存储选型-母题-S1-OLTP与OLAP的分野与选型.html'] },
      { id: '2', name: '扩展', href: 'modules/数据存储选型-02-扩展.html', cards: ['S2'], pages: ['topics/数据存储选型-母题-S2-单机不够了怎么扩.html'] },
      { id: '3', name: '边界', href: 'modules/数据存储选型-03-边界.html', cards: ['S3'], pages: ['topics/数据存储选型-母题-S3-什么时候不该用关系数据库.html'] },
      { id: '4', name: '语义', href: 'modules/数据存储选型-04-语义.html', cards: ['S4'], pages: ['topics/数据存储选型-母题-S4-语义层与Ontology.html'] }
    ]
  },
  {
    /* 项目线：本簇不进 zone 轮转，由 progress.html 单开「项目线」板块，每天派 1 条。
       proj 字段用来按项目分组显示进度——三个项目各 2 条
       （90 秒骨架 → 决策链，后者要等前者到 L2 才解锁）。 */
    id: 'pitch', name: '项目口述', zone: '表达',
    topics: [
      { id: 'T1', name: 'EnergyOps 90 秒骨架', proj: 'EnergyOps', href: 'projects/energyops.html#skel', src: 'projects/EnergyOps/EnergyOps-快速学习掌握与面试实战.md' },
      { id: 'T2', name: 'EnergyOps 决策链', proj: 'EnergyOps', href: 'projects/energyops.html#chain', src: 'projects/EnergyOps/EnergyOps-快速学习掌握与面试实战.md' },
      { id: 'T3', name: '数驭穹图 90 秒骨架', proj: '数驭穹图', href: 'projects/shuyu.html#skel', src: 'projects/数驭穹图/16-项目表达与面试题库.md' },
      { id: 'T4', name: '数驭穹图 决策链', proj: '数驭穹图', href: 'projects/shuyu.html#chain', src: 'projects/数驭穹图/16-项目表达与面试题库.md' },
      { id: 'T5', name: 'RuleArena 90 秒骨架', proj: 'RuleArena', href: 'projects/rulearena.html#skel', src: 'projects/RuleArena/01-project-mainline.md' },
      { id: 'T6', name: 'RuleArena 决策链', proj: 'RuleArena', href: 'projects/rulearena.html#chain', src: 'projects/RuleArena/01-project-mainline.md' }
    ]
  }
];

/* 独立日课：不进主进度盘（手撕是肌肉记忆，与建理解是两件事），单独计连续天数
   2026-09-25 扩池：原 9 题 → 37 题。D1–D9 沿用已有母题卡页面；D10–D37 指向
   《算法手撕-32题闭卷清单》的作战卡（output/算法手撕-32题每日作战卡.html）对应行锚点。
   派单规则不变：没练过的优先，练过的排队尾，队首 = 最久没练。 */
window.MARVIS_DRILL = {
  id: 'drill', name: '手撕算法', goal: 37, zone: '日课',
  topics: [
    { id: 'D1', name: '两数之和', href: 'topics/算法-母题-01-两数之和.html' },
    { id: 'D2', name: '字母异位词分组', href: 'topics/算法-母题-02-字母异位词分组.html' },
    { id: 'D3', name: '最长连续序列', href: 'topics/算法-母题-03-最长连续序列.html' },
    { id: 'D4', name: '移动零', href: 'topics/算法-母题-04-移动零.html' },
    { id: 'D5', name: '盛最多水的容器', href: 'topics/算法-母题-05-盛最多水的容器.html' },
    { id: 'D6', name: '三数之和', href: 'topics/算法-母题-06-三数之和.html' },
    { id: 'D7', name: '合并 K 个有序链表', href: 'topics/算法-母题-33-合并K个有序链表.html' },
    { id: 'D8', name: 'LRU 缓存', href: 'topics/算法-母题-34-LRU缓存.html' },
    { id: 'D9', name: '二叉树中序遍历', href: 'topics/算法-母题-35-二叉树中序遍历.html' },
    /* --- S 层：面试手撕必杀（目标闭卷 3 分钟） --- */
    { id: 'D10', name: '无重复字符的最长子串', href: '../output/算法手撕-32题每日作战卡.html#S2' },
    { id: 'D11', name: '反转链表', href: '../output/算法手撕-32题每日作战卡.html#S3' },
    { id: 'D12', name: '合并两个有序链表', href: '../output/算法手撕-32题每日作战卡.html#S4' },
    { id: 'D13', name: '环形链表 II', href: '../output/算法手撕-32题每日作战卡.html#S5' },
    { id: 'D14', name: '二叉树层序遍历', href: '../output/算法手撕-32题每日作战卡.html#S6' },
    { id: 'D15', name: '二叉树最大深度与直径', href: '../output/算法手撕-32题每日作战卡.html#S7' },
    { id: 'D16', name: '最近公共祖先', href: '../output/算法手撕-32题每日作战卡.html#S8' },
    { id: 'D17', name: '有效的括号', href: '../output/算法手撕-32题每日作战卡.html#S9' },
    { id: 'D18', name: '第 K 大与 TopK', href: '../output/算法手撕-32题每日作战卡.html#S11' },
    { id: 'D19', name: '搜索旋转排序数组', href: '../output/算法手撕-32题每日作战卡.html#S12' },
    { id: 'D20', name: '岛屿数量', href: '../output/算法手撕-32题每日作战卡.html#S13' },
    { id: 'D21', name: '合并区间', href: '../output/算法手撕-32题每日作战卡.html#S14' },
    /* --- A 层：高频变体 --- */
    { id: 'D22', name: '最小覆盖子串', href: '../output/算法手撕-32题每日作战卡.html#A1' },
    { id: 'D23', name: '最大子数组和', href: '../output/算法手撕-32题每日作战卡.html#A2' },
    { id: 'D24', name: '和为 K 的子数组', href: '../output/算法手撕-32题每日作战卡.html#A3' },
    { id: 'D25', name: 'K 个一组翻转链表', href: '../output/算法手撕-32题每日作战卡.html#A4' },
    { id: 'D26', name: '验证二叉搜索树', href: '../output/算法手撕-32题每日作战卡.html#A5' },
    { id: 'D27', name: '前序与中序构造二叉树', href: '../output/算法手撕-32题每日作战卡.html#A6' },
    { id: 'D28', name: '全排列', href: '../output/算法手撕-32题每日作战卡.html#A7' },
    { id: 'D29', name: '每日温度', href: '../output/算法手撕-32题每日作战卡.html#A8' },
    { id: 'D30', name: '跳跃游戏', href: '../output/算法手撕-32题每日作战卡.html#A9' },
    { id: 'D31', name: '打家劫舍', href: '../output/算法手撕-32题每日作战卡.html#A10' },
    /* --- B 层：笔试难题（识别模型 + 拿部分分） --- */
    { id: 'D32', name: '零钱兑换', href: '../output/算法手撕-32题每日作战卡.html#B1' },
    { id: 'D33', name: '最长公共子序列', href: '../output/算法手撕-32题每日作战卡.html#B2' },
    { id: 'D34', name: '课程表（拓扑判环）', href: '../output/算法手撕-32题每日作战卡.html#B3' },
    { id: 'D35', name: '腐烂橘子（多源 BFS）', href: '../output/算法手撕-32题每日作战卡.html#B4' },
    { id: 'D36', name: '单词搜索', href: '../output/算法手撕-32题每日作战卡.html#B5' },
    { id: 'D37', name: '柱状图最大矩形', href: '../output/算法手撕-32题每日作战卡.html#B6' }
  ]
};

/* 独立准则段（2026-09-28 建）—— 行事准则派单池
   ─────────────────────────────────────────────────────────────
   **目前未激活**：本对象单独挂着，没有 push 进 MARVIS_CLUSTERS，
   所以现有档位轮转与派单完全不受影响。这样做是为了让「接入」这件事
   变成一次可回滚的小改动（明天改 progress.html 时再 push）。
   题面（场景 + 标准动作）在 site/_data/rules.js，用同一个 id 对齐；
   本段只挂 href 供派单跳转，不复制题面。
   正本：wiki/thinking/行动规则.md / 0713再就业男团-逆境准则.md / 性命双修执行案.md

   为什么写在文件末尾：_rebuild_clusters.py 只重写
   HEADER + 13 个模块簇 + pitch，然后原样接上 index('/* 独立日课') 之后的内容——
   所以本段和 drill 段一样，重跑脚本不会被冲掉。

   接入清单（明天做，四处）：
     ① progress.html 顶部加 var RULE_CID = 'rule';
     ② clusterOrder() 与 scanClusters() 的 zone 收集都要排除 RULE_CID（照 PROJECT_CID 的写法）
     ③ 加 ruleNext()（照 projectNext()），buildDay 里补一条：每天派 1 条准则
     ④ TYPE_TAG/TYPE_CLS/TYPE_ORD 三张表同加 rule（漏一张标签静默消失）
     ⑤ runRule 的日序：一天派 1 条，答对进 1-3-7-14，答错明天重派
     接入后跑：node output/_verify_progress.js && node site/_tests/*.js（三个必须全绿） */
window.MARVIS_RULE_CLUSTER = {
  id: 'rule', name: '行事准则', zone: '准则',
  topics: [
    { id: 'R1',  name: '机会成本门',        href: 'rules.html#r-R1',  src: 'wiki/thinking/行动规则.md' },
    { id: 'R2',  name: '有限计划会',        href: 'rules.html#r-R2',  src: 'wiki/thinking/行动规则.md' },
    { id: 'R3',  name: '决策门：单向还是双向', href: 'rules.html#r-R3', src: 'wiki/thinking/行动规则.md' },
    { id: 'R4',  name: '信息价值截止线',     href: 'rules.html#r-R4',  src: 'wiki/thinking/行动规则.md' },
    { id: 'R5',  name: '丑版本配额',        href: 'rules.html#r-R5',  src: 'wiki/thinking/行动规则.md' },
    { id: 'R6',  name: '我不负责清单',      href: 'rules.html#r-R6',  src: 'wiki/thinking/行动规则.md' },
    { id: 'R7',  name: '逆境：算自己的账',   href: 'rules.html#r-R7',  src: 'wiki/thinking/0713再就业男团-逆境准则.md' },
    { id: 'R8',  name: '逆境：情绪 0 分也照做', href: 'rules.html#r-R8', src: 'wiki/thinking/0713再就业男团-逆境准则.md' },
    { id: 'R9',  name: '命功是电池',        href: 'rules.html#r-R9',  src: 'wiki/thinking/性命双修执行案.md' },
    { id: 'R10', name: 'never miss twice', href: 'rules.html#r-R10', src: 'wiki/thinking/行动规则.md' }
  ]
};
