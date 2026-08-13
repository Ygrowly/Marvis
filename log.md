# Log

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
