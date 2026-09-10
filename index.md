# Marvis

> 我的知识库、职业资产和阅读训练系统。

## 三条入口

| 想去哪 | 去哪 |
|---|---|
| 规则是什么 | [[CLAUDE]] —— 全库唯一权威 |
| 某个主题的正本在哪 | [[MAP]] —— 主题正本登记表 |
| 现在该做什么 | [[questions]] —— 问题台账，加工的唯一驱动 |

## 核心流程

```text
raw/ 唯一入口
  ↓ AI 按活跃问题聚类、去重、粗加工
wiki/sources/ 候选主题综述
  ↓ 选择代表来源深读、讨论、复述
reading/ 深读与验证
  ↓ 沉淀为可复用资产
wiki/ 知识资产（母题卡为主）+ output/ 对外成品
```

加工由 [[questions|问题台账]] 的活跃问题拉动，唯一指标是每周闭环 ≥ 1 个问题。
细则见 [[CLAUDE]] 与 [[workflow]]，变更史见 [[log]]。

## 当前主线

- [[2027届秋招总面试准备手册]]（总纲）
- [[秋招冲刺路线]]
- [[四项目面试掌握与模拟训练方案]]
- [[简历逐句作战地图]]

## 核心项目

- [[EnergyOps-项目说明]]
- [[数驭穹图项目说明]]
- [[RuleArena-项目说明]]

## 学习与训练

- [[母题驱动证据闭环学习法]]（2026-09-08 起的学习执行内核，锁定 8 周）
- [[学习方法]]
- [[行动规则]]
- [[性命双修执行案]]
- [[00-算法母题索引|算法母题索引]]

## 技术能力

- [[AI应用开发能力地图]]（岗位基线 + 掌握度台账）
- [[00-学习总导航与知识生长协议|能力课程索引]]（`study/` 01–10）

## 阅读训练

- [[阅读判断训练]]
- [[2026-06-18-vercel-eve-agent-framework|Vercel Eve Agent 框架]]
- [[2026-06-24-agent-loop-harness-review|Agent Loop、Harness 与代码审查工程化]]
- [[2026-06-24-agent-product-adoption|Agent 产品形态与用户采用路径]]
- [[2026-08-13-agent-runtime-engineering|Agent 运行时工程：治理、记忆、自主迭代]]
- [[2026-08-13-dewu-agent-production-practice|生产级 Agent 工程实践（得物 12 篇）]]
- [[2026-08-13-agent-evaluation-observability|Agent 评测与可观测体系]]
- [[2026-08-13-data-intelligence-nl2sql|数据智能 Agent：NL2SQL、NL2BI 与意图识别]]
- [[2026-08-13-interview-prep-2027|2027 秋招 Agent 后端面试备战素材]]

## 目录职责速查

| 区域 | 用途 |
|---|---|
| `MAP.md` | 主题正本登记表（落盘前先查这里） |
| `questions.md` | 问题台账，加工的唯一驱动 |
| `raw/` | 唯一外部素材入口，允许积压 |
| `study/` | 跨项目能力课程（01–10），只放课程 |
| `wiki/topics/` | 技术知识母题卡，按模块分子目录 |
| `wiki/interview/` | 面试表达与题库 |
| `wiki/thinking/` | 学习方法、精力与行动规则 |
| `wiki/sources/` | AI 生成的主题综述候选 |
| `reading/` | 深读、讨论、结论 |
| `projects/` | 按项目一目录：项目说明 + 编号手册 |
| `jd/` | JD 融合核对表与参考简历 |
| `output/` | 对外成品（简历只放 `output/resume/`） |
| `site/` | 知识系统形式：md 正本 → html 练习界面 |
| `templates/` | 母题卡、模块深挖卡、一页纸、每日复盘模板 |
