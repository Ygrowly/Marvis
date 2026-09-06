# 09｜高频面试题、场景追问、项目表达与复习

## 1. 20 秒项目介绍

> 我做了一个电商规则对抗验证平台。它把退款、优惠和积分规则转成可确认的 RuleSpec，让 Agent 搜索异常操作组合，再通过真实 API 重放和确定性 Oracle 判断是否真的造成资金或权益异常，最后把问题沉淀成可回归的最小反例。

关键词：

```text
电商规则 / Agent 搜路径 / API 重放 / Oracle / 最小反例
```

---

## 2. 90 秒项目介绍

> 电商里很多问题不是单条规则错误，而是订单、优惠券、积分和退款按特殊顺序组合后出错。人工测试只能覆盖想到的路径，单纯让 LLM 审 PRD 又只能给风险提示，所以我设计了 RuleArena。系统先把自然语言规则编译成严格 RuleSpec，存在歧义必须人工确认；然后用 BFS 和三个隔离策略搜索动作序列，先在 Reference Simulator 中快速探索，再从干净环境调用独立 Commerce Sandbox 的真实 HTTP API 重放。模型只能提出动作，漏洞是否成立由 Oracle 根据退款、积分、优惠券、会员权益和幂等不变量判断。确认问题会被压缩为 1-minimal 反例，修复后继续回归。项目还设计了 24 个开发和隐藏 Case，对比 Random、BFS、Single Agent 和 Multi-strategy，避免把多 Agent 当成没有证据的卖点。最终在线 Demo 展示规则确认、攻击路径、状态 Diff、确定性证据和修复前后对比。

---

## 3. 5 分钟项目介绍

### 业务背景

> 电商中的优惠、积分、订单、退款和会员通常是不同模块。单条规则不难，风险来自合法动作的组合，例如订单支付发积分，全额退款恢复优惠券，但实现遗漏积分撤销，用户退款后还能用残留积分兑换新券。传统单元测试依赖人提前想到路径，LLM 阅读 PRD 又只能生成可能风险，无法证明系统真的可复现。

### 产品方案

> RuleArena 是规则上线前的对抗验证和发布门禁平台。用户从内置模板修改自然语言规则，Rule Compiler 生成严格 RuleSpec；Pydantic 和领域 Validator 校验字段、金额和引用，存在歧义时要求人工确认，最终冻结不可变 RuleVersion。

### Agent Runtime

> 主流程由显式 Workflow 控制，Agent 只负责未知路径搜索。系统先运行 Random 和 BFS，再启动 ValueFlow、Lifecycle、Boundary 三个隔离策略。Agent 只能看到当前状态、合法动作、有限历史和预算，只输出结构化 ActionProposal，不能访问数据库、代码或 Ground Truth。

### 真实验证

> 路径先在纯 Python Reference Simulator 中快速执行，用 state_hash 去重；可疑路径只是 Candidate。它必须从干净环境调用独立 Commerce Sandbox 的 HTTP API 重放，获取 Receipt、事件和规范化 Snapshot。确定性 Oracle 不复用 Sandbox 的状态转换，只按 RuleVersion 检查退款、积分、券、权益、幂等和账本不变量。连续重放 3/3 后才算 Confirmed，再通过删除式 Delta Debugging 得到 1-minimal Counterexample。

### 工程可靠性

> 写动作使用业务幂等键，Receipt、聚合、账本和事件同事务提交。超时后先用相同 key 查询权威状态，无法确认就记录 ACTION_UNKNOWN，而不是盲目重试。PostgreSQL 保存权威 Run 和 Sandbox 状态，Redis/ARQ 只做队列，SSE 只通知；Worker 崩溃后通过 Checkpoint、Receipt 和 Snapshot 恢复。

### 评测和价值

> 项目用 16 个 development 和 8 个 hidden Case 比较 Random、BFS、Single 和 Multi-strategy，报告发现率、normal Confirmed 误报、Candidate 确认率、重放稳定性、Token、延迟和 pass@k/pass^k。所有指标从原始 Run 重算并绑定完整版本元组。如果多策略在公平预算下没有优势，我会降低 Multi-Agent 宣传。最终交付不是一份模型报告，而是一条可重放、可裁决、可回归的业务反例。

---

## 4. 最高频面试题与答案

### 1. RuleArena 解决什么问题？

解决电商退款、优惠、积分和会员规则在特殊动作顺序、重复请求和状态恢复中的组合漏洞。它主动搜索未知路径，并把风险转换成真实 API 可复现、Oracle 可裁决的反例。

### 2. 为什么不是一段 Prompt？

Prompt 只能生成风险猜测。RuleArena 还有不可变 RuleVersion、可执行 Sandbox、副作用幂等、独立 Oracle、Replay、最小化、回归和 Benchmark，这些都是确定性工程系统能力。

### 3. 为什么选择电商领域？

它有清晰业务价值、有限动作和状态、可计算的不变量、直观损失故事，并与交易后端、售后 Agent 和 Agent Commerce 可迁移。

### 4. 没有真实电商项目，业务世界从哪里来？

通过独立 FastAPI + PostgreSQL Commerce Sandbox 实现最小可执行交易和售后服务，使用真实 HTTP、事务、账本、事件和幂等。它不是企业生产，但保留真实业务机制并提供可控 Ground Truth。

### 5. RuleSpec 的作用是什么？

把自然语言的不确定性压缩到编译阶段，形成可校验、可版本化、可复现的业务契约。未确认歧义不能运行，执行阶段不允许模型重新解释规则。

### 6. 为什么需要人工确认？

合法 JSON 不代表符合业务意图。退款时积分、优惠券和权益处理可能有多个合法解释，必须由业务人确认后冻结。

### 7. Workflow 和 Agent 怎么分工？

状态、权限、预算、执行、裁决、重试和恢复由 Workflow 控制；路径未知的动作选择由 Agent 负责。能画成有限状态机的部分不用 Agent 自由决定。

### 8. 为什么不用 LangGraph？

MVP 状态机有限，显式实现能更清楚控制条件更新、Outcome、Checkpoint 和失败语义，也避免框架隐藏面试核心。分支和团队复用显著增加时再评估。

### 9. 为什么需要 Simulator 和 Sandbox 两套？

Simulator 用于快速复制状态和搜索，Sandbox 用于真实 HTTP、事务和实现验证。前者降低成本，后者提供可信证据；只用一个无法兼顾吞吐和真实性。

### 10. 如何避免 Simulator 和 Oracle 自己验证自己？

Simulator、Sandbox 和 Oracle 独立实现，只共享动作/快照 Schema 和值对象，不共享状态转换和漏洞判断。Oracle 只读取真实快照、账本、Receipt 和事件，并通过变异测试验证独立性。

### 11. 什么情况下才算 Confirmed Violation？

Candidate 从干净 Sandbox API 重放成功、Oracle 对真实状态检测到 invariant 失败、版本固定且连续 Replay 3/3。Agent confidence 不参与裁决。

### 12. 反例为什么要最小化？

减少无关步骤，让开发更容易定位和修复，也降低回归成本。每次删除后必须从干净环境重放，最终只声称 1-minimal，不声称全局最短。

### 13. 幂等键怎么设计？

根据 run、动作类型、目标、规范化参数、RuleVersion 和逻辑 Step 构造稳定业务键。不能使用随机请求 ID 或 ToolCallID。

### 14. 写动作超时后怎么办？

用相同 idempotency_key 查询 Receipt。成功则读取 Snapshot 后继续，明确失败按错误类型处理，不存在且确认未接收可相同 key 重试，仍无法确认则 ACTION_UNKNOWN 并停止分支。

### 15. Checkpoint 和幂等有什么区别？

Checkpoint 保存 Agent 进度，幂等保证业务效果一次，Receipt/权威查询判断动作状态。Checkpoint 可能落后于业务提交，不能防重复副作用。

### 16. 为什么 PostgreSQL 是权威状态，Redis 不是？

PostgreSQL 提供事务、约束、版本和持久审计；Redis/ARQ 负责可重建队列和短期进度。即使 Redis 丢失或重投，业务仍能从数据库恢复。

### 17. SSE 断线会不会丢状态？

可能丢通知，但不丢权威状态。SSE 只推送，页面加载、重连和刷新都通过 Run API 重新读取 PostgreSQL 状态。

### 18. 为什么多 Agent 不互相聊天？

三个策略是独立搜索视角，不需要协商共同产物。隔离能减少重复、冲突和上下文污染，并让每种策略的贡献可评估。

### 19. 怎样证明 Multi-Agent 有价值？

在相同 Case、模型和总预算下与 BFS/Single 比较 hidden 发现率、误报、确认率、延迟和单位缺陷成本；还要报告并行时间口径。没有优势就降低宣传。

### 20. 为什么要 hidden Case？

development 容易过拟合。hidden 用来评估未针对调试的泛化，并通过 loader、权限和数据流隔离防止 Runtime 自动泄题。

### 21. pass@k 和 pass^k 区别？

pass@k 是 k 次中至少一次成功，衡量能力上限；pass^k 是 k 次全部成功，衡量稳定性。生产 Agent 不能只展示前者。

### 22. 为什么 normal Confirmed 误报目标是 0？

Confirmed 会阻断发布，误报成本高。Candidate 可以有探索噪声，但经过真实 Replay 和确定性 Oracle 后仍误报属于 P0。

### 23. Trace 保存什么？

保存 Run/Strategy/Step、版本、动作摘要、before/after hash、模型调用、Token、延迟、重试、Receipt、Event、Snapshot 和 Oracle Evidence；不保存密钥、hidden 预期和 Chain-of-Thought。

### 24. 项目如何防 Prompt Injection？

用户规则始终作为数据，LLM 输出只能进入严格 Schema；Agent 工具白名单且无 Shell/SQL/文件，Ground Truth 和内部 Profile 无访问路径，所有动作还要经过 Runtime 和状态校验。

### 25. 如果 LLM 服务挂了怎么办？

Live Agent Run 明确失败或暂停；已冻结规则的 BFS、历史反例回归和 Frozen Demo 继续。不能伪造结果或用旧结果冒充当前 Run。

### 26. 为什么不做 RAG/长期记忆？

当前规则由内置模板和单次 RuleVersion 完整提供，不存在大规模知识检索问题。加入 RAG 会增加泄漏、版本和评测复杂度，却不提升核心闭环。

### 27. 怎么扩展到其他行业？

新领域必须有有限动作、明确状态、可执行环境和确定性不变量。可以复用 Orchestrator、Replay、Trace 和 Eval，但必须重建领域 RuleSpec、Action Contract、Snapshot 和 Oracle。

### 28. 项目最大的局限是什么？

MVP 状态空间和规则类型有限，不覆盖真实分布式并发、完整电商链路和形式化安全证明；24 Case 规模也只适合作为 MVP 回归基线。

### 29. 如何证明没有过度设计？

每个组件都对应不可合并的正确性边界：规则冻结、快速搜索、真实执行、独立裁决、异步恢复和评测。主动没有引入 K8s、MQ、RAG、通用 DAG、插件和完整商城。

### 30. 你个人最有价值的工作是什么？

安全口径：这个个人项目的价值不只是完成代码，而是从业务问题反推可执行领域模型，明确 Agent 与确定性系统的边界，并设计 Sandbox/Oracle 隔离、副作用恢复和无泄漏评测闭环。具体“已实现”内容按仓库事实回答。

---

## 5. 高频场景题回答骨架

### 场景一：发现重复退款

> 先暂停相关写动作并保留证据；从订单、Refund、Receipt、Event 和 Trace 对比两个请求的幂等键和事务时间线，判断是换 key 重试、唯一约束缺失还是重复 Worker。修复采用稳定业务键、同事务 Receipt 和数据库约束，再做提交前/后超时、并发和 Worker 重启测试，并将反例加入 P0 回归。

### 场景二：hidden 发现率突然到 100%

> 先按 P0 泄漏处理，而不是立即宣传提升。停用 Gate，扫描 Case loader 到 Prompt、Tool、Trace、API、SSE 的完整路径，检查近重复和 Case 修改历史，加入 canary 后重跑。受影响结果全部失效。

### 场景三：Multi-Agent 成本三倍、发现率只高 5%

> 做等总预算和单位确认漏洞成本比较。如果边际收益不足，就使用 BFS + Single 为默认，将 Multi 作为高价值深度模式，而不是为了名词保留默认三策略。

### 场景四：要支持 100 并发

> 先判断瓶颈是模型、Worker、DB、Sandbox 还是 SSE。当前个人 Demo 先限流和排队；确认 Worker 饱和且 Provider/DB 健康后水平扩 Worker，继续依靠 expected status 和幂等。没有证据前不上 Kubernetes。

### 场景五：接入企业 Staging

> 用 TargetAdapter 映射动作、场景初始化、Receipt、Snapshot 和 Event；使用测试租户、最小权限和清理机制；Oracle 保持独立；先影子验证和只读/低风险动作，不直接进入生产。

### 场景六：Oracle 与业务方意见冲突

> 先判断是规则歧义还是 Oracle 实现错误。若存在多个合法口径，返回 AMBIGUOUS_POLICY 并由业务确认生成新 RuleVersion；如果 Oracle 错，发布新 OracleVersion，历史结果不覆盖，完整 Benchmark 重跑。

---

## 6. 简历项目描述模板

以下是设计模板，最终量化数字必须替换为实际证据。

> **RuleArena｜AI 驱动的电商规则对抗验证与发布门禁平台**

- 面向退款、优惠、积分与会员权益等跨流程规则变更，将自然语言规则编译为经人工确认的类型化 RuleSpec，以显式 Workflow 约束 Agent 动作、预算、状态和失败恢复。
- 设计 Reference Simulator + Commerce Sandbox + Deterministic Oracle 分层验证链路，由多策略搜索候选路径，经真实 HTTP API 重放、业务不变量裁决和 Delta Debugging 生成 1-minimal Counterexample。
- 建立 Random/BFS/Single/Multi 消融、development/hidden Golden Set、全链路 Trace 和版本化 Release Gate，评估发现率、误报、重放稳定性、Token、延迟与单位缺陷成本。

如果实际门禁达成，再补：

```text
在 [N] 个版本化 Case 上，normal Confirmed 误报 [X]，
Confirmed 反例重放 [X/X]，hidden 发现率 [X%]，
数据来自 BenchmarkRun [id/version]。
```

---

## 7. 事实安全卡

### 可以直接说

- “项目设计为……”；
- “核心闭环是……”；
- “MVP 的目标门禁是……”；
- “容量估算口径是……”；
- “如果上线，我会……”；
- “这是独立测试业务服务，不是生产系统。”

### 需要证据后再说

- “已实现 24 Case”；
- “hidden 发现率 75%”；
- “误报为 0”；
- “P95 80 秒”；
- “已在 Railway 部署”；
- “有真实用户持续使用”；
- “Multi-Agent 提升 X%”。

### 不能说

- “证明规则绝对安全”；
- “处理真实生产退款”——如果没有；
- “扛过真实高并发”——如果只是估算/压测；
- “线上事故”——如果只是风险演练；
- “企业采用”——如果只有开源 Demo。

---

## 8. 第一次 90 秒检查

闭卷回答：

1. 用户是谁？
2. 真实问题是什么？
3. 为什么传统测试和 Prompt 都不够？
4. RuleSpec、Simulator、Sandbox、Oracle 怎样串联？
5. 最终产物是什么？

只记录三个断点：

- 业务太抽象；
- Agent/确定性分工混乱；
- 没有讲出 Replay/Oracle/回归。

---

## 9. 核心难题检查

用 3～5 分钟讲：

> 如何证明 Agent 找到的风险是真的？

只追问：

1. Simulator 为什么不能直接作为 Ground Truth？
2. Oracle 如何避免自己验证自己？
3. 写动作超时后怎样保证重放不会重复副作用？

合格标准：

- 能讲清三层分离；
- 能讲清 Candidate/Confirmed；
- 能讲清 clean replay、Receipt、3/3 和 1-minimal；
- 不把模型 confidence 当证据。

---

## 10. 完整模拟面试顺序

### 第一段：项目理解

1. 90 秒介绍；
2. 用户和价值；
3. 黄金案例；
4. 系统边界。

### 第二段：技术深挖

5. RuleSpec 与歧义；
6. Workflow/Agent；
7. Simulator/Sandbox/Oracle；
8. state_hash；
9. Replay/minimize；
10. 幂等/unknown/recovery。

### 第三段：评测

11. 24 Case；
12. hidden 隔离；
13. Baseline 公平；
14. pass@k/pass^k；
15. Release Gate。

### 第四段：工程和场景

16. Worker 崩溃；
17. SSE 断线；
18. Redis 故障；
19. 100 并发；
20. 接入 Staging。

### 第五段：真实性

21. 哪些已实现；
22. 哪些是目标；
23. 指标证据；
24. 最大局限；
25. 如果再做一版改什么。

每轮只修三个最严重断点，不试图一次修完全部表达细节。

---

## 11. 第 1、3、7 天具体复习题

### 第 1 天

- 讲 90 秒；
- 回答题 1、2、5、7、9、11、14、19、21、28；
- 讲一次黄金 Case；
- 复述八条 invariant；
- 记录三个断点。

### 第 3 天

- 随机抽四张选型卡；
- 回答重复退款、Worker 崩溃、Ground Truth 泄漏；
- 手算 p=0.8 的 pass@3/pass^3；
- 讲三分钟核心难题；
- 更新三个断点。

### 第 7 天

- 20 秒、90 秒、5 分钟各讲一次；
- 完成上面的 25 题模拟；
- 核对简历 Claim 和实际仓库；
- 只修复最严重三个问题；
- 把真实面试新问题加入 Bad Case 队列。

---

## 12. 当前最可能的三个能力断点

在尚未正式模拟前，预判而非事实：

### 断点一：容易把 Simulator、Sandbox 和 Oracle 讲成重复组件

修复关键词：

```text
快搜 / 真执行 / 独立裁决
Candidate / Confirmed
共享 Schema，不共享逻辑
```

### 断点二：知道幂等术语，但容易混淆 Checkpoint、Receipt 和权威状态

修复关键词：

```text
幂等键防重复
Receipt 判动作
Checkpoint 恢复进度
Snapshot 是业务现实
```

### 断点三：会背指标，但不易解释分母、公平预算和真实性

修复关键词：

```text
raw Run recompute
INFRA_FAILED separate
equal budget
pass@k vs pass^k
TARGET ≠ MEASURED
```

正式模拟后，以真实暴露的三个断点替换本节。

---

## 13. 最终关键词总卡

```text
业务：跨规则组合漏洞
输入：模板 + 自然语言
契约：RuleSpec + 人审 + RuleVersion
控制：显式 Workflow
探索：BFS + ValueFlow/Lifecycle/Boundary
快速世界：Reference Simulator
真实世界：Commerce Sandbox HTTP + PostgreSQL
裁决：Deterministic Oracle
证据：Receipt/Event/Snapshot/Trace
产物：3/3 + 1-minimal Counterexample
恢复：idempotency + Receipt + Checkpoint + ACTION_UNKNOWN
评测：16 dev + 8 hidden + 4 baselines
门禁：0 normal FP / hidden target / P0 regression / leakage 0
边界：预算内未发现 ≠ 绝对安全
```

