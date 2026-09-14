# Log

## 2026-09-14（AI Coding 驱动工作流落盘）

- **新增正本**：`wiki/thinking/AI-Coding驱动工作流.md`（`candidate` / `human_reviewed: false`）。内容＝对本人原有 AI Coding 三步法的诊断 + 三个结构性缺口 + 三个转变 + 面试五维 + 行动规则 + 母题式验收。
- **为什么不并入现有正本**：MAP 里 CORE-28（JD 横向总览）、F10（能力地图）、`study/00` 的节点映射三处都只是**台账行 / 映射行**，承载不了方法论正文；方法论按目录职责归 `wiki/thinking/`。已按闸门第 2 条登记。
- **来源落 `raw/`**：5 篇官方一手资料（Claude Code 官方最佳实践、Finding your unknowns、Steering Claude Code、Claude 5 代上下文工程新规则、2026 三家 Agent 面试指南），违反唯一入口原则的临时抓取已归位。
- **同步更新**：`wiki/topics/AI应用开发能力地图.md` F10 行加双链并刷 `updated:`；`MAP.md` 学习区加登记行。
- **待办（本人）**：① 该文档的验收未过，需闭卷复述 + 两层追问 + 在 RuleArena/EnergyOps 真跑一次完整流程；② 是否把结论拆成 `questions.md` 的一条活跃问题（当前无对应问题，本次是显式要求下的例外加工）。

## 2026-09-14（RuleArena 转向 + 派单简化 + 冻结前全库审查）

- **RuleArena 定位转向**：从「电商规则对抗验证」转为「**业务 Agent 上线前的执行门禁**」（被测对象＝调工具的 Agent，裁决从离线搜索推进到运行时拦截）。正本 `projects/RuleArena/RuleArena-项目说明.md` 重写为 v0.3；未实现部分落成可执行规格 `E:\code\my\RuleArena\docs\agent-gateway-spec.md`（D1–D5 + 四条不变量）。
- **口径统一到 golden-v4**：全库旧口径（0–20% / 未超过 BFS / 24 Case / golden-v2 / deepseek-v3.2）清零，覆盖简历四份、账本、口述脚本、九本编号手册、7 份 wiki 材料。**顺手修掉一条超口径主张**：简历原写「反例一键导出 pytest 回归」，该功能只在 `docs/product-requirements.md` 待办里、无实现。
- **外部校验**：搜到两篇 2026 年 arXiv 论文（非原子工具调用 / agentic clearing），证实设计成立但**不能声称首创**；落综述 `wiki/sources/2026-09-14-agent-非原子工具调用与验证.md`。
- **归档**：`projects/PayTrace/`、`projects/Ovanta/` → `archive/`（25 条 rename，零删除）；新建 `archive/README.md`；账本、手册、两份 map 文件同步路径。
- **派单引擎简化**（`site/progress.html`）：① 等级 5 档 → 3 档（未接触/会了/常练）；② 复训间隔 1-3-7-14-30 → **1/3/7/14**，学完即进复训；③ 门控阈值降到 L1，抽检池单列 `EXAM_MIN=2`；④ 五板块各加「继续派发」按钮，当天封顶 8 条；⑤ 新增「强行解锁」（用户确认，系统只说明代价）；⑥ **修掉真 bug**：`clusters.js` 给全部母题补 `href` 后「有卡=读过」导致 `ready` 池恒空、主线新学一条也派不出。
- **修引用**：`study/NN` 旧编号 47 处（含复合写法 `study/08/09/11`）→ 迁移后的 wiki 路径；悬空双链 50 处（`wiki/sources` 历史链 + 母题卡短名互引）→ 改指现正本或拆为纯文本；`wiki/interview/2027届秋招总面试准备手册.md` 第 35 行旧路径失配。
- **清理**：删 `archive/PayTrace/*.bak`、`.workbuddy/tmp_*`；三个站点测试全绿；`site/build.py` 通过。
- **待办（冻结前唯一未决）**：派单迁移对 localStorage 存量数据的影响需本人确认——新规则把「无到期日且无自评日期」的 L1 一律回「未接触」，可能让页面上已读进度显示归零（教学上正确，是否接受由本人定）。
- **影响页面**：约 40 个 md + 站点视图全量重建

## 2026-09-10（全库治理第二轮：正本制 + 母题卡化）

- **背景**：09-06 那次治理只治了目录、没治产出行为。之后 4 天新增约 30 份文件，无一份是更新已有正本 —— 全库再次分散。
- **诊断**：乐元素 9 份（1 正本 + 5 快照切片 + 1 互补 + 2 单日快照）；算法 `output/算法` 9 张单卡是 `study/17+18` 的打印切片；`wiki/topics` 四个 06-18 空骨架；元文档 CLAUDE / workflow / index 正文重复。
- **关键发现**：① 母题法 §四 早已写死落点规则（母题卡放 `wiki/interview/` 或 `wiki/topics/`）但从未被执行；② 现存 9 张算法卡缺全部训练字段（母题/恢复关键词/追问/断点/证据/复训），是讲解稿而非母题卡。
- **删除**：`wiki/topics` 四个空骨架（FDE能力地图 / Python后端工程 / SQL与业务指标 / Agent-RAG-MCP）、`output/晨报/` 2 份、`jd/all.md` 与 `jd/快手-JD.md`、`templates/interview-answer-template.md`、`wiki/thinking/` 三份早期随笔与「职业判断」空壳。
- **迁移**：`study/` 的 11、12、13、15、16、17、18、20、21 共 9 份 → `wiki/interview/` 与 `wiki/topics/{算法,MySQL}/`；`study/` 只留 00 + 01–10 + 14 + 19，回归纯能力课程。
- **算法母题卡化**：9 张卡迁入 `wiki/topics/算法/` 并按 `母题-NN-名称.md` 重命名（去掉全角冒号），逐张补齐母题 / 为什么重要 / 一句话结论 / 恢复关键词 / 两层追问 / 可迁移场景 / 本次断点 / 通过证据 / 复训日期；`study/17`、`18` 降级为「母题池」底库（只查不练）；新建 `00-算法母题索引.md` 作模块主线地图。
- **乐元素收敛 9 → 2**：6 份材料合并为《乐元素-游戏服务端一二面冲刺手册》正本（章节级保留全部内容，标题降级），《乐元素-服务端一二面复盘报告》去日期保留；其余 5 份原件与算法 P0 包解散 —— P0 包转正为 `wiki/topics/算法/母题组-乐元素面试与笔试P0.md`（它是合格的题型组卡，有独立算法价值）。
- **立骨架**：新建 `MAP.md`（主题正本登记表 + 落盘闸门三条）；新建 `templates/母题卡模板.md`（主线 / 扩展 / 拼接 三段式）；`CLAUDE.md` 新增〈落盘闸门（正本制）〉节与母题卡命名规范；`workflow.md` 压缩为速查卡（删除与 CLAUDE 重复的正文）；`index.md` 重做为「三条入口 + 目录速查」。
- **修引用**：全库修复 30+ 处失效引用（旧文件名、已删骨架、旧路径），断链清零。
- **根因**：分散的制度性原因是缺「一个主题一个正本」的落盘闸门。本轮把闸门写进 `CLAUDE.md`，正本登记从 `MAP.md` 可查。
- **遗留**：`projects/Ovanta`、`projects/PayTrace` 与部分 `wiki/sources/` 综述仍引用 09-06 前删除的历史页面（如 `[[AI BI Text-to-SQL]]`），非本轮引入，按需清理。

## 2026-09-06（仓库治理）

- 分支：`repo-governance`
- 归拢：`projects/` 三棵平行树（根级说明 / study 手册 / feishu 导出）→ 每项目一目录（`{项目}-项目说明.md` + 编号手册），git mv 保留历史
- 删除：`projects/study/EnergyOps` 与飞书「完整学习资料包」9 文件字节级重复（保留 study 侧）、RuleArena 旧版说明 v0.1（9/1，被 9/4 版取代）、55 行能力地图旧骨架（被 607 行掌握度台账取代并继承页面名与关联链接）、`issue.md`（决策已吸收进 CLAUDE.md/workflow.md/log）、空目录（`.agents/`、`projects/my/`）、`summaries/附件/` 重复图 3 张、`.firecrawl/` 搜索 json 草稿、`output/` 根目录旧版 BOSS 简历（9/5 早于 resume/ 内 9/6 版）与旧版 2027届 PDF（8/10）
- 迁移：`.firecrawl/` 5 篇内容抓取 → `raw/`（恢复唯一入口原则）；飞书能力掌握度台账 → `wiki/topics/AI应用开发能力地图.md`；`jd/resume/`（他人简历）→ `jd/参考简历/`；飞书 `JD.md`（快手全文，与 all.md 不重叠）→ `jd/快手-JD.md`；output 根目录简历导出 PDF/HTML → `output/resume/`
- 修复：口述脚本、秋招总面试准备手册、快速上手指南、简历写作方法论共 9 处旧路径引用
- 卫生：`.workbuddy/`（工具本地记忆）加入 `.gitignore` 并移出跟踪，本地文件保留
- 元文档：CLAUDE.md 目录职责新增 study/projects/jd/output 四节；index.md 快速导航同步
- 原因：热区三棵树并存、新旧版本跨目录混放、抓取产物违反唯一入口、协议文档多头

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
