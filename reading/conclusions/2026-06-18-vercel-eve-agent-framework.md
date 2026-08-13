---
type: integrated_reading
source: raw/2026-06-18T150744+0800 - Vercel 放大招：前端 Agent 框架 Eve 来了！.md
date: 2026-06-18
discussion: reading/discussions/2026-06-18-vercel-eve-agent-framework-discussion.md
status: integrated
human_reviewed: true
---

# Vercel Eve：前端 Agent 约定式框架

## 一句话理解

Vercel 发布了开源 AI Agent 框架 Eve，用目录结构和文件约定把 Agent 开发从"拼 Demo"推进到"工程化框架"阶段。

## 核心观点

1. **Eve 是框架，不是 SDK** — 它定义目录结构、文件约定和执行流程，开发者按规则组织 Agent 代码，而不是调用 API
2. **约定大于配置** — 一个 Agent 就是一个目录，tools/skills/subagents/channels 都是文件，放进目录就自动生效
3. **Tools vs Skills** — Tools 是 Agent 能做什么（能力），Skills 是 Agent 知道什么（知识，如业务定义、规则）
4. **生产级能力是核心卖点** — 持久化执行（durable workflow）、沙箱执行（sandbox）、人工审批（needsApproval），解决的是"能不能管"而非"能不能跑"
5. **Channel 系统** — Agent 通过 Channel adapter 同时跑在 Slack、GitHub、Linear、Teams 等多个入口
6. **行业信号** — Agent 开发进入框架化阶段，以前拼模型和 Prompt，接下来拼工程化能力

## 我的最终理解

Vercel 发布的 Eve 是一个开源 AI Agent 框架，核心思路是用前端开发者熟悉的"约定式框架"模式来组织 Agent 开发。一个 Agent 就是一个目录，包含 agent.ts（模型配置）、instructions.md（系统提示词）、tools/（能力）、skills/（知识）、subagents/（子 Agent）、channels/（渠道入口）、schedules/（定时任务）。

Eve 区别于其他 Agent SDK 的关键在于工程化能力：持久化执行让任务可以暂停恢复，沙箱执行隔离危险操作，人工审批让关键步骤需要人类确认。加上评测（eve eval）和一键部署（vercel deploy），形成完整的生产闭环。

Vercel 内部已有 100+ 个 Agent 在生产运行，Agent 触发的部署从 3% 增长到 29%。这说明 Agent 开发正在从实验阶段进入工程化阶段。

## 这篇内容真正有价值的地方

- 不是 Eve 的 API 细节（那些会变），而是**"Agent 开发框架化"这个趋势判断**
- **Tools vs Skills 的区分**值得借鉴：能力 ≠ 知识，分开管理更清晰
- **生产级三件套**（持久化、沙箱、审批）是做任何 Agent 产品都要面对的问题

## 我之前的理解偏差

- 把框架说成 SDK — 框架是约束你怎么做，SDK 是你调用它
- 漏了 Skills — 业务知识文件化是 Eve 的重要设计
- 漏了生产级能力 — 持久化/沙箱/审批才是核心卖点

## 可以迁移到哪里

### 项目

- MetricOps Agent：可以借鉴 Skills 的设计，把业务指标定义文件化
- 任何 Agent 项目：持久化执行和人工审批是通用需求

### 面试

- 面试中讲 Agent 开发时，可以提"框架化 vs 拼 Demo"这个趋势
- 问到 Agent 生产化时，可以讲持久化/沙箱/审批三个核心问题

### 职业判断

- Agent 开发正在从"会调 API"变成"会做工程"，工程化能力越来越重要

### 行动规则

- 关注 Agent 框架的演进，但不要追新，重点理解其设计思路
