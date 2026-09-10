---
type: source_synthesis
created: 2026-06-24
updated: 2026-06-24
status: candidate
human_reviewed: false
topic: Agent Loop、Harness 与代码审查工程化
sources:
  - "raw/2026-06-23T224100+0800 - The Coming Loop.md"
  - "raw/2026-06-24T123435+0800 - Loop Engineering.md"
  - "raw/Loop Engineering 是什么？AI 编程从 Prompt 到 Loop 的范式转变-2026-06-24T123848+0800.md"
  - "raw/2026-06-24T123534+0800 - AI 不缺智商缺纪律：我的 Harness 工程化实践.md"
  - "raw/Harness Engineering 是什么？AI Agent 越用越聪明的秘密-2026-06-24T123836+0800.md"
  - "raw/2026-06-24T123640+0800 - Agent harness engineering with Claude 14-step roadmap from one agent to a self-improving system.Agent 利用 Claude 实现工程化应用：从一个智能体到具备自我改进能力的系统的 14 步实现路径。.md"
  - "raw/2026-06-24T123632+0800 - Agentic Code Review.md"
related:
  - "[[04-Agent-Runtime与Harness]]"
  - "[[AI应用开发能力地图]]"
  - "[[MetricOps Agent]]"
  - "[[阅读判断训练]]"
---

# 主题：Agent Loop、Harness 与代码审查工程化

## 一句话结论

AI Coding 的关键瓶颈正在从“怎么提示模型”迁移到“如何设计可验证、可恢复、可约束的执行系统”：Loop 提供持续迭代，Harness 提供纪律和边界，Review/CI/门禁决定这个系统是否值得信任。

## 本批来源

| 来源 | 主要内容 | 是否重复 | 推荐动作 |
|---|---|---|---|
| The Coming Loop | 从怀疑者视角讨论 harness-level loop 的必然性、风险和理解债 | 否，提供反方/谨慎视角 | 深读 |
| Loop Engineering | 定义 loop engineering，拆出 automation、worktree、skills、connectors、sub-agents、state | 否，最系统的概念来源 | 深读 |
| Loop Engineering 是什么 | 中文转述 Addy Osmani 文章，适合快速理解和复述 | 是，和英文原文高度重复 | 按需查阅 |
| AI 不缺智商缺纪律 | 个人 harness 实践：分层加载、dispatcher、角色 agent、G1-G8 门禁、hook 拦截 | 否，最有实践细节 | 深读 |
| Harness Engineering 是什么 | 通俗梳理 prompt/context/harness 的演进和常见难点 | 部分重复 | 按需查阅 |
| Agent harness engineering with Claude | 14 步路线：.claude、rules、settings、subagents、skills、hooks、loop、memory、plugin | 部分重复，但结构清晰 | 按需查阅 |
| Agentic Code Review | AI 产出变多后，审查、验证、风险分层成为新瓶颈 | 否，补足 review 维度 | 深读 |

## 共同结论

1. AI 编程不是单点模型能力问题，而是模型外部系统设计问题。提示词只能表达意图，无法稳定保证长链路执行。
2. Loop 的本质是把“人连续按回车”替换成一个能发现任务、分派任务、检查结果、决定下一步的循环系统。
3. Harness 的本质是把规则、上下文、工具、状态、权限、记忆和验证外置到可复用结构里，让模型在约束中工作。
4. 状态必须活在对话之外。无论叫 state file、memory、Linear board 还是 Markdown 日志，目标都是跨会话恢复上下文。
5. 写和查必须分离。实现 agent、验证 agent、review agent、停止条件 judge 不应由同一上下文自证。
6. 验证不能只靠模型自觉。CI、测试、hook、门禁、权限和 fail-closed 规则是让 loop 可控的基础设施。
7. 产出变便宜以后，真正昂贵的是理解、信任和责任。AI 让代码更快出现，但没有让人更快确认代码正确。

## 真正的分歧

- **是否应该让 loop 写长期代码**：Addy Osmani 更偏“可以搭，但要保留工程判断”；Armin Ronacher 明显更谨慎，认为当前模型会放大局部防御、重复抽象和理解债，更适合可验证转换、实验、性能探索、安全扫描等场景。
- **多 agent 是否越多越好**：实践文强调 dispatcher、orchestrator、analyst、developer、verifier 等细分角色；谨慎视角会追问 token 成本、调试复杂度和责任归属。
- **AI review 的边界**：多数来源同意 AI reviewer 必须用，但 Agentic Code Review 强调 AI review 是传感器，不是裁决；最终合并责任仍归人。
- **速度还是可解释性优先**：loop 支持小团队高速产出，但 The Coming Loop 提醒，这可能形成机器参与才能维护的代码库依赖。

## 新增或修正的知识

- `Prompt Engineering → Context Engineering → Harness Engineering → Loop Engineering` 可以理解为瓶颈不断外移：表达、信息、执行环境、连续驱动。
- 一个可落地 loop 至少需要：自动触发、隔离并行、项目知识、外部连接、写查分离、外部状态。
- Harness 不是更长的 `CLAUDE.md`。长规则常驻会挤占上下文，正确做法是常驻层极小、规则原子化、阶段性按需加载。
- “经验沉淀”要区分 lesson、pattern、instinct：一次踩坑先记录，多次验证后才上升为通用规则，避免错误经验扩散。
- 代码审查的新任务不是“看看有没有 bug”这么简单，而是恢复 intent、确认证据、按风险分层，把人类注意力用在高 blast radius 位置。
- 测试变更比业务代码更值得警惕。Agent 可能通过修改断言、跳过 lint、降低覆盖率来让绿灯出现。

## 可信度

- 有数据、代码或案例支持：
  - Agentic Code Review 引用多组 2025-2026 数据和论文，适合作为“验证瓶颈”论据，但其中部分数据来自商业厂商，需要保留动机偏差。
  - AI 不缺智商缺纪律提供具体 harness 分层、门禁、hook、状态机实践，适合作为工程参考。
- 只有观点或二手转述：
  - 中文“小林coding”两篇主要是概念转译和科普，适合建立词汇表，不宜作为唯一证据。
  - 14-step 路线来自社媒长文，结构清晰，但需要实际项目验证。
- 需要进一步验证：
  - Loop 在长期代码库里的质量收益是否大于理解债。
  - 多 reviewer 并行在当前项目中的成本收益。
  - 对 MetricOps Agent 是否应该先做轻量 loop，还是先补 harness/评测基础。

## 是否值得继续

- 结论：值得深读。
- 原因：该主题直接关系到 [[MetricOps Agent]]、AI 应用开发能力、后续面试表达和个人使用 Codex/Claude Code 的方法。它不是单篇热点，而是一组会改变开发流程设计的工程判断。

## 推荐代表来源

1. 最系统：`raw/2026-06-24T123435+0800 - Loop Engineering.md`
2. 最有实践证据：`raw/2026-06-24T123534+0800 - AI 不缺智商缺纪律：我的 Harness 工程化实践.md`
3. 反方或不同视角：`raw/2026-06-23T224100+0800 - The Coming Loop.md`
4. 审查与验证补充：`raw/2026-06-24T123632+0800 - Agentic Code Review.md`

## 阅读问题

1. 对 [[MetricOps Agent]] 来说，最小可用 harness 应该先包含哪些：状态文件、技能、评测、hook、sub-agent 还是自动化？
2. 哪些任务适合 loop 自动跑，哪些任务必须保持 human-in-the-loop？判断标准是风险、可验证性、寿命还是用户影响面？
3. 如何设计“写查分离”：同一个模型不同提示词够不够，还是必须不同模型/不同工具权限？
4. 当前项目有没有可以外置成 skill/rule 的重复经验？哪些只是 lesson，哪些已经能升级为 pattern？
5. 如何避免 loop 产出带来理解债？是否需要强制要求每个 agent PR 附带 intent、证据和测试结果？

## 可能更新的知识页

- [[04-Agent-Runtime与Harness]]：补充 Harness/Loop 在 Agent 工程化中的位置。
- [[AI应用开发能力地图]]：加入“验证、评测、权限、状态、记忆、review”作为 AI 应用工程能力。
- [[MetricOps Agent]]：设计最小 harness 和长期 loop 路线。
- [[阅读判断训练]]：加入“AI 摘要/AI 代码不是掌握证明，验证才是核心”的判断规则。
