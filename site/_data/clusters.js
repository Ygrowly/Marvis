/* 能力簇与母题清单 —— 进度页数据源
   约定：
   1. href = 站内 html 页面（site/ 下相对路径），src = 库内 md（渲染成 obsidian 链接）。
   2. 两者都为空的母题 = 尚未建卡，只显示为「未接触」，不进派单池（没材料不能派活）。
   3. M3 阶段由 build.py 自动生成，当前手工维护。
   ⚠️ 本表的**母题范围必须以模块卡正本为准**（`wiki/topics/{模块}/{模块}模块卡.md` 的「母题清单」节）。
      2026-09-12 清理：删掉 14 行旧规划残留（M18–M21 / R4–R8 / N4–N8），它们的计划内容已被现有卡合并
      （例：R5「过期与内存淘汰」并进了 R2）。**要扩母题先改模块卡，再回来加行**，否则进度页会挂出假欠账。
   PostgreSQL 19 张卡已完成但**暂不进本表**（2026-09-12 决定）：模块页从训练台「模块学习」栏可达，不进派单。
*/
window.MARVIS_CLUSTERS = [
  {
    id: 'sql', name: 'SQL 与索引', zone: '后端底盘',
    topics: [
      { id: 'M1', name: '为什么用 B+ 树', href: 'topics/MySQL-母题-M1-为什么用B+树.html' },
      { id: 'M2', name: '联合索引与最左前缀', href: 'topics/MySQL-母题-M2-联合索引与最左前缀.html' },
      { id: 'M3', name: '聚簇索引与回表', href: 'topics/MySQL-母题-M3-聚簇索引与回表.html' },
      { id: 'M4', name: '索引代价与大表变更', href: 'topics/MySQL-母题-M4-索引代价与大表变更.html' },
      { id: 'M5', name: '引擎与表设计基本盘', href: 'topics/MySQL-母题-M5-引擎与表设计基本盘.html' },
      { id: 'M6', name: '一条 SQL 的执行链路', href: 'topics/MySQL-母题-M6-一条SQL的执行链路.html' },
      { id: 'M7', name: '慢查询与 SQL 优化手段', href: 'topics/MySQL-母题-M7-慢查询与SQL优化手段.html' }
    ]
  },
  {
    id: 'tx', name: '事务与并发', zone: '后端底盘',
    topics: [
      { id: 'M8', name: '隔离级别与 ACID', href: 'topics/MySQL-母题-M8-隔离级别与ACID.html' },
      { id: 'M9', name: 'MVCC', href: 'topics/MySQL-母题-M9-MVCC.html' },
      { id: 'M10', name: '锁与死锁', href: 'topics/MySQL-母题-M10-锁与死锁.html' },
      { id: 'M13', name: '长事务为什么危险', href: 'topics/MySQL-母题-M13-长事务为什么危险.html' },
      { id: 'M16', name: '乐观锁与悲观锁', href: 'topics/MySQL-母题-M16-乐观锁与悲观锁.html' },
      { id: 'M17', name: '排行榜与防超卖', href: 'topics/MySQL-母题-M17-排行榜与防超卖.html' }
    ]
  },
  {
    id: 'ha', name: '日志与高可用', zone: '后端底盘',
    topics: [
      { id: 'M11', name: '三日志与两阶段提交', href: 'topics/MySQL-母题-M11-三日志与两阶段提交.html' },
      { id: 'M12', name: '崩溃恢复', href: 'topics/MySQL-母题-M12-崩溃恢复.html' },
      { id: 'M14', name: '主从复制与延迟', href: 'topics/MySQL-母题-M14-主从复制与延迟.html' },
      { id: 'M15', name: '数据增长治理', href: 'topics/MySQL-母题-M15-数据增长治理.html' }
    ]
  },
  {
    id: 'redis', name: 'Redis 与缓存', zone: '后端底盘',
    topics: [
      { id: 'R1', name: 'Redis 数据结构与选型', href: 'topics/Redis-母题-R1-Redis数据结构与选型.html' },
      { id: 'R2', name: '持久化与内存淘汰', href: 'topics/Redis-母题-R2-持久化与内存淘汰.html' },
      { id: 'R3', name: '缓存一致性与三类事故', href: 'topics/Redis-母题-R3-缓存一致性与三类事故.html' }
    ]
  },
  {
    id: 'net', name: '网络与 IO', zone: '后端底盘',
    topics: [
      { id: 'N1', name: '一次请求的完整路径', href: 'topics/网络-母题-N1-一次请求的完整路径.html' },
      { id: 'N2', name: 'SSE 与推送模型', href: 'topics/网络-母题-N2-SSE与推送模型.html' },
      { id: 'N3', name: '进程线程与协程', href: 'topics/网络-母题-N3-进程线程与协程.html' }
    ]
  },
  {
    id: 'llm', name: 'LLM 与上下文工程', zone: 'AI 主战场',
    /* 2026-09-12：C1–C6 已教材化，href 指到母题页；课程底库降为资料索引（study/02·01·10） */
    topics: [
      { id: 'C1', name: '上下文组装与窗口预算', href: 'topics/LLM与上下文-母题-C1-上下文组装与窗口预算.html', src: 'study/02-LLM与Context-Engineering.md' },
      { id: 'C2', name: '结构化输出与 JSON 可靠性', href: 'topics/LLM与上下文-母题-C2-结构化输出与JSON可靠性.html', src: 'study/02-LLM与Context-Engineering.md' },
      { id: 'C3', name: 'Prompt 版本管理与回归', href: 'topics/LLM与上下文-母题-C3-Prompt版本管理与回归.html', src: 'study/02-LLM与Context-Engineering.md' },
      { id: 'C4', name: '幻觉的成因与可控性', href: 'topics/LLM与上下文-母题-C4-幻觉的成因与可控性.html', src: 'study/02-LLM与Context-Engineering.md' },
      { id: 'C5', name: '模型选型与降级三角', href: 'topics/LLM与上下文-母题-C5-模型选型与降级三角.html', src: 'study/01-第一性原理与业务AI化.md' },
      { id: 'C6', name: '成本与长上下文截断', href: 'topics/LLM与上下文-母题-C6-成本与长上下文截断.html', src: 'study/10-生产治理安全性能与成本.md' }
    ]
  },
  {
    id: 'rag', name: 'RAG 与检索', zone: 'AI 主战场',
    /* 2026-09-12：G1–G6 全部教材化，本簇完成 */
    topics: [
      { id: 'G1', name: '切分策略与索引粒度', href: 'topics/RAG与检索-母题-G1-切分策略与索引粒度.html', src: 'study/03-RAG与企业知识系统.md' },
      { id: 'G2', name: '向量与关键词的混合检索', href: 'topics/RAG与检索-母题-G2-向量与关键词的混合检索.html', src: 'study/03-RAG与企业知识系统.md' },
      { id: 'G3', name: '重排与召回质量', href: 'topics/RAG与检索-母题-G3-重排与召回质量.html', src: 'study/03-RAG与企业知识系统.md' },
      { id: 'G4', name: '引用绑定与证据可追溯', href: 'topics/RAG与检索-母题-G4-引用绑定与证据可追溯.html', src: 'study/03-RAG与企业知识系统.md' },
      { id: 'G5', name: 'RAG 评测与幻觉率', href: 'topics/RAG与检索-母题-G5-RAG评测与幻觉率.html', src: 'study/07-Eval-Trace与Observability.md' },
      { id: 'G6', name: '知识更新与增量索引', href: 'topics/RAG与检索-母题-G6-知识更新与增量索引.html', src: 'study/03-RAG与企业知识系统.md' }
    ]
  },
  {
    id: 'agent', name: 'Agent 运行时与工具', zone: 'AI 主战场',
    /* 2026-09-12：A1–A3 已教材化；A4–A8 建完一张换一张 */
    topics: [
      { id: 'A1', name: '计划执行循环与停止条件', href: 'topics/Agent运行时与工具-母题-A1-计划执行循环与停止条件.html', src: 'study/04-Agent-Runtime与Harness.md' },
      { id: 'A2', name: '工具调用与 MCP 边界', href: 'topics/Agent运行时与工具-母题-A2-工具调用与MCP边界.html', src: 'study/05-Tool-MCP-Skill与可信执行.md' },
      { id: 'A3', name: '失败恢复与幂等', href: 'topics/Agent运行时与工具-母题-A3-失败恢复与幂等.html', src: 'study/04-Agent-Runtime与Harness.md' },
      { id: 'A4', name: '长任务状态与 checkpoint', src: 'study/06-Workflow-多Agent与长任务.md' },
      { id: 'A5', name: '上下文压缩与记忆', src: 'study/04-Agent-Runtime与Harness.md' },
      { id: 'A6', name: '沙箱权限与可信执行', src: 'study/05-Tool-MCP-Skill与可信执行.md' },
      { id: 'A7', name: '多 Agent 拆分与协作', src: 'study/06-Workflow-多Agent与长任务.md' },
      { id: 'A8', name: '动态计划下的可靠执行', src: 'projects/RuleArena/RuleArena-项目说明.md' }
    ]
  },
  {
    id: 'eval', name: '评测观测与治理', zone: 'AI 主战场',
    topics: [
      { id: 'E1', name: '评测集设计与 pass^k', src: 'study/07-Eval-Trace与Observability.md' },
      { id: 'E2', name: 'Trace 与可观测性', src: 'study/07-Eval-Trace与Observability.md' },
      { id: 'E3', name: '回归门禁与发布卡口', src: 'projects/RuleArena/RuleArena-项目说明.md' },
      { id: 'E4', name: '成本控制与限流', src: 'study/10-生产治理安全性能与成本.md' },
      { id: 'E5', name: '越权与提示注入防护', src: 'study/10-生产治理安全性能与成本.md' },
      { id: 'E6', name: '灰度发布与回滚', src: 'study/10-生产治理安全性能与成本.md' }
    ]
  },
  {
    id: 'pitch', name: '项目口述', zone: '表达',
    topics: [
      { id: 'P1', name: 'EnergyOps 90 秒骨架', src: 'wiki/interview/个人项目含金量表达铁律.md' },
      { id: 'P2', name: 'EnergyOps 决策链', src: 'projects/EnergyOps/EnergyOps-项目说明.md' },
      { id: 'P3', name: '数驭穹图 90 秒骨架', src: 'wiki/interview/个人项目含金量表达铁律.md' },
      { id: 'P4', name: '数驭穹图决策链', src: 'projects/数驭穹图/数驭穹图项目说明.md' },
      { id: 'P5', name: 'RuleArena 90 秒骨架', src: 'wiki/interview/个人项目含金量表达铁律.md' },
      { id: 'P6', name: 'RuleArena 决策链', src: 'projects/RuleArena/RuleArena-项目说明.md' }
    ]
  }
];

/* 独立日课：不进主进度盘（手撕是肌肉记忆，与建理解是两件事），单独计连续天数 */
window.MARVIS_DRILL = {
  id: 'drill', name: '手撕算法', goal: 30, zone: '日课',
  topics: [
    { id: 'D1', name: '两数之和', href: 'topics/算法-母题-01-两数之和.html' },
    { id: 'D2', name: '字母异位词分组', href: 'topics/算法-母题-02-字母异位词分组.html' },
    { id: 'D3', name: '最长连续序列', href: 'topics/算法-母题-03-最长连续序列.html' },
    { id: 'D4', name: '移动零', href: 'topics/算法-母题-04-移动零.html' },
    { id: 'D5', name: '盛最多水的容器', href: 'topics/算法-母题-05-盛最多水的容器.html' },
    { id: 'D6', name: '三数之和', href: 'topics/算法-母题-06-三数之和.html' },
    { id: 'D7', name: '合并 K 个有序链表', href: 'topics/算法-母题-33-合并K个有序链表.html' },
    { id: 'D8', name: 'LRU 缓存', href: 'topics/算法-母题-34-LRU缓存.html' },
    { id: 'D9', name: '二叉树中序遍历', href: 'topics/算法-母题-35-二叉树中序遍历.html' }
  ]
};
