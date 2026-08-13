---
type: discussion
source: raw/2026-06-18T150744+0800 - Vercel 放大招：前端 Agent 框架 Eve 来了！.md
date: 2026-06-18
reader_note: reading/notes/2026-06-18-vercel-eve-agent-framework.md
status: reading
---

# 讨论记录：Vercel Eve Agent 框架

## 用户原始理解

> Vercel 发了一个 AI Agent SDK，很像前端开发的约定式框架，把 Agent 工具、上下文、权限、subAgent、评测及部署等能力文件化，有固定的模板。核心就是可以把 Agent 应用开发模板化，一些固定能力可以沉淀、封装起来。

## AI 校验结论

### 理解正确的地方

- 约定式框架的核心类比 — 准确
- 能力文件化 — 准确
- 对自己开发应用有帮助 — 方向对

### 可能偏差

1. **SDK vs 框架** — 文章明确说"不是 SDK"，Eve 是框架，约束开发者怎么组织代码
2. **"上下文"应为 Skills** — 文章区分 Tools（能力）和 Skills（知识），不是"上下文"
3. **"权限"表述不够精确** — 文章讲的是三个独立的生产级能力：持久化执行、沙箱执行、人工审批

### 被遗漏的关键点

1. **Skills 概念** — 业务知识文件化，和 Tools 分开管理
2. **生产级三件套** — 持久化执行、沙箱执行、人工审批是核心卖点
3. **Channel 系统** — 多渠道 adapter 设计
4. **行业趋势判断** — Agent 开发进入框架化阶段，从拼模型到拼工程化

## 用户二次复述

> Vercel 发了一个 AI Agent 的约定式框架。它定义了目录结构、文件约定和执行流程，来表示 Agent 的能力。核心能力包括 Tools、Sub-agents、Channels；工程化能力包括持久化执行、沙箱执行、人工审批。通过 Channel 把不同 App 入口做成 Adapter，让一个 Agent 可以同时跑在多个渠道。

## AI 最终校正

- "Verso" → "Vercel"（拼写）
- "Kernel" → "Channel"（术语）
- 仍漏 Skills（业务知识文件化）
- 整体结构清晰，核心理解到位，可以进入 reviewed 状态
