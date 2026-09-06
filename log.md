# Log

## 2026-09-06

- 决策：主循环改为问题驱动，`questions.md` 成为系统骨架（问题台账）
- 原因：两套系统（markdown 工作流 + feishu-knowledge-growth）均未持续使用；漏斗断在深读/沉淀（raw 77 篇、summaries 52 篇，reading 仅 1 篇），加工是欠债驱动而非需求驱动
- 新增：`questions.md`，从 2026-08-13 备战综述的阅读问题播种 6 个活跃问题（项目表达、简历三层深挖、RAG 全流程、记忆系统、前缀缓存、生产四问）
- 调整：`CLAUDE.md`、`workflow.md` —— 定向加工取代全库批扫，`summaries/` 默认停更，唯一指标改为每周闭环 ≥ 1 个问题
- 封存：`feishu-knowledge-growth/` 六表设计暂缓启用（见其 `STATUS.md`），重启条件与迁移路径已记录；终局仍是一个系统一个事实源
- 后续：核心闭环跑通后，优先在飞书侧落地手机捕获口（机器人/收集箱 → raw/）

## 2026-08-13

- 整理：仓库目录结构全面整理
- 重构：`resume/` 更名为 `summaries/`，定位为 AI 逐篇摘要区，与 `wiki/sources/` 主题综述互补
- 摊平：`raw/new/`、`raw/案例/`、`raw/知识库/`、`raw/研发范式/`、`raw/评测/` 全部并入 `raw/`，恢复「raw 不分类」原则
- 去重：删除 10 个重复 raw 文件（字节级重复和同文章多次抓取，各保留最完整版本）
- 分流：根目录简历母稿×6 → `output/resume/`；面试训练方案 → `wiki/interview/`；个人思考笔记 → `wiki/thinking/`；外部文章 → `raw/`
- 删除：根目录与 `raw/` 重复的牛客网文章 2 篇；`summaries/` 内部重复 1 篇
- 清理：删除空目录 `tmp/`、`output/summaries/`
- 更新：`CLAUDE.md`、`index.md`、`workflow.md` 同步新结构
- 粗加工：对 raw/ 59 篇 + summaries/ 29 篇做批量主题聚类、去重与价值判断
- 新增：5 篇主题综述（candidate）——Agent 运行时工程、得物生产级实践、Agent 评测与可观测、数据智能 Agent、2027 秋招面试备战
- 判断：GEO、AI 可见性与求职目标弱相关，按需查阅不建页；小浣熊/OpenClaw/Eve 已入旧综述不重复处理
- 调整：`summaries/` 中一篇全文转载（Tw93 Claude Code 六层）移回 `raw/`，保持 summaries 只存加工品

## 2026-06-24

- 执行：对 `raw/` 当前文章做第一步批量粗加工
- 聚类：合并为两个候选主题
  - `wiki/sources/2026-06-24-agent-loop-harness-review.md`
  - `wiki/sources/2026-06-24-agent-product-adoption.md`
- 去重：Vercel Eve 已有独立集成页，本次只作为背景来源，不重复生成摘要
- 判断：Loop/Harness/Agentic Review 主题与 [[MetricOps Agent]]、AI 应用开发和面试表达直接相关，推荐优先深读
- 判断：OpenClaw/小浣熊主题更偏 Agent 产品形态与用户采用路径，推荐按需深读
- 保持：`raw/` 原文不移动、不改写，继续作为 captured 来源

## 2026-06-23

- 确定：`raw/` 为唯一外部素材入口
- 重构：工作流改为“按文章捕获，按主题加工，按问题深读，按知识沉淀”
- 统一：状态改为 `captured → candidate → reading → integrated`
- 删除：`ai_draft`、`discussed`、`reviewed`、`mastered` 等旧流程状态
- 新增：批量主题聚类、去重、主题综述和代表来源选择规则
- 新增：raw 捕获、主题综述、阅读笔记、讨论和阅读结论模板
- 调整：`reading/reviewed/` 改为 `reading/conclusions/`
- 修复：Vercel Eve 样例缺失的 reader note 和错误 discussion 引用
- 原因：降低高信息量场景下的逐篇处理成本，让系统以知识积累而不是摘要积累为目标
- 影响页面：`CLAUDE.md`、`workflow.md`、`index.md`、`issue.md`、模板、状态字段和 Eve 样例

## 2026-06-18

- 创建：SecondBrain 知识库骨架搭建
- 原因：初始化知识库结构，建立 Human-first Reading Workflow
- 影响页面：全部目录和骨架文件
- 后续待办：
  - 迁移现有 `E:\notes\` 下的资料到 `raw/`
  - 填充初始 wiki 页面内容
  - 测试阅读工作流

## 2026-06-18（续）

- 创建：`workflow.md`（日常使用流程）
- 修改：`CLAUDE.md`（加入双通道工作流、Mode A/B/C、掌握状态系统）
- 修改：所有 wiki 页面 frontmatter 加入 `status: ai_draft` + `human_reviewed: false`
- 修改：模板文件加入 status 字段
- 原因：避免系统沦为 AI 自动总结库，保护用户阅读判断训练能力
- 影响页面：CLAUDE.md, workflow.md, 15个 wiki 页面, 4个模板
- 后续待办：
  - 在 Obsidian 中测试 Dataview 按 status 筛选页面

## 2026-06-18（Mode C 试跑）

- 创建：reading/discussions/2026-06-18-vercel-eve-agent-framework-discussion.md
- 创建：reading/reviewed/2026-06-18-vercel-eve-agent-framework.md
- 创建：wiki/sources/2026-06-18-vercel-eve-agent-framework.md
- 更新：wiki/topics/Agent-RAG-MCP.md（加入框架化趋势、Tools vs Skills）
- 更新：index.md（加入已完成阅读）
- 原因：首次 Mode C 完整流程试跑
- 影响页面：5 个文件
- 后续待办：
  - 选择更多素材试跑 Mode B（AI Draft）对比效率
  - 填充其他 ai_draft wiki 页面内容
