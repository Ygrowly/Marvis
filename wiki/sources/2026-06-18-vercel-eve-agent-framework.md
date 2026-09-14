---
type: source
source: raw/2026-06-18T150744+0800 - Vercel 放大招：前端 Agent 框架 Eve 来了！.md
date: 2026-06-18
reading_note: reading/notes/2026-06-18-vercel-eve-agent-framework.md
discussion: reading/discussions/2026-06-18-vercel-eve-agent-framework-discussion.md
conclusion: reading/conclusions/2026-06-18-vercel-eve-agent-framework.md
status: integrated
human_reviewed: true
tags: [agent, framework, vercel, eve]
---

# Vercel 发布 AI Agent 框架 Eve

## 一句话摘要

Vercel 发布开源 AI Agent 框架 Eve，用目录结构和文件约定把 Agent 开发推进到工程化阶段。

## 核心内容

- Eve 是框架不是 SDK，用约定式目录结构组织 Agent 代码
- 一个 Agent = 一个目录：agent.ts + instructions.md + tools/ + skills/ + subagents/ + channels/ + schedules/
- Tools（能力）和 Skills（知识）分离管理
- 生产级能力：持久化执行、沙箱执行、人工审批
- Channel 系统：Slack、GitHub、Linear、Teams 等多渠道 adapter
- 评测：eve eval 回归测试
- 部署：vercel deploy，和 Vercel 平台深度集成

## 关键概念

- [[04-Agent-Runtime与Harness]] — Agent 框架化趋势
- 约定式框架 — 文件约定 > 代码配置
- 持久化执行 — 任务可暂停恢复
- 沙箱执行 — 隔离危险操作
- 人工审批 — 关键步骤需人类确认

## 与项目的连接

- MetricOps Agent：可借鉴 Skills 设计，把业务指标定义文件化
- 任何 Agent 项目：持久化/沙箱/审批是通用需求

## 面试可用点

- 讲 Agent 开发趋势时，可提"框架化 vs 拼 Demo"
- 讲 Agent 生产化时，提持久化/沙箱/审批三个核心问题

## 关联页面

- [[04-Agent-Runtime与Harness]]
- [[AI应用开发能力地图]]
- [[EnergyOps-项目说明]]
