# 02｜RuleSpec、Workflow 与 Agent Harness

## 1. 本篇目标

学完后能够回答：

- 为什么自然语言必须先变成 RuleSpec；
- RuleSpec、RuleVersion、ScenarioVersion 分别解决什么；
- Workflow、Agent 和 Tool 的边界如何划分；
- Agent Context 中应该放什么，不应该放什么；
- 为什么项目不是一段 Prompt、Skill 或 LangGraph Demo。

---

## 2. 从自然语言到可执行规则

### 业务问题

自然语言经常省略：

- 退款时积分是否撤销；
- 部分退款如何按比例处理；
- 优惠券恢复是否受使用次数限制；
- 已消费会员权益是否允许全额退款；
- 重复请求以哪个业务键判重。

如果模型直接按自然语言执行，不同轮次可能给出不同理解，系统无法复现也无法回归。

### 系统必须保证

- 相同 RuleVersion 语义不变；
- 未确认歧义不能运行；
- 规则只能使用系统支持的领域原语；
- 规则不能携带任意可执行代码；
- 历史 Run 永远绑定当时版本。

### 方案

```text
模板 + 用户修改
→ LLM 候选 RuleSpec
→ Pydantic Schema
→ Deterministic Validator
→ Ambiguity List
→ Human Confirmation
→ Immutable RuleVersion
```

### RuleSpec 包含

- promotion_rules；
- refund_rules；
- points_rules；
- membership_rules；
- invariant_refs；
- parameters。

### RuleSpec 不包含

- Python 或 JavaScript；
- SQL；
- 任意表达式解释器；
- 动态 import；
- Shell、URL 和外部工具权限；
- 模型生成的“是否有漏洞”答案。

---

## 3. 为什么需要人工确认

LLM 结构化输出只保证“像一个合法 JSON”，不能保证规则是业务真实意图。

例如：

> 全额退款恢复优惠券。

仍然可能有多个合法解释：

1. 无条件恢复；
2. 只恢复未过期券；
3. 只恢复一次；
4. 恢复券但撤销积分；
5. 已使用积分兑换权益时禁止全额退款。

系统应给有限选项，而不是让用户重新写一大段话。确认后的答案进入 RuleVersion，模型不能在运行中改变。

### Human-in-the-loop 的位置

只在高价值不确定点介入：

- 规则存在多个合法解释；
- 新 RuleVersion 准备冻结；
- 候选修复准备应用；
- Release Gate 有 P1 风险需要接受。

不需要人工逐步批准 Sandbox 中的测试动作，因为环境隔离且无生产副作用。

---

## 4. Workflow 与 Agent 怎样分工

### 判断原则

> **可以画成有限状态机、失败语义明确的部分用 Workflow；目标开放、路径未知但动作受限的部分用 Agent。**

### Workflow 控制

- RuleVersion 是否已确认；
- Run 状态转换；
- 预算和超时；
- 可用动作集合；
- 三策略的创建和隔离；
- Candidate Replay；
- Oracle 裁决；
- 反例最小化；
- 取消、Checkpoint 和恢复；
- Outcome 和发布门禁。

### Agent 负责

- 根据当前状态选择有风险价值的下一动作；
- 判断应继续探索价值流、生命周期还是边界条件；
- 在受限动作空间中组合此前未覆盖的路径；
- 给出结构化 ActionProposal 和简短原因。

### Agent 不负责

- 直接执行 SQL/Shell；
- 修改 Sandbox 数据；
- 决定动作是否真正成功；
- 判断漏洞是否 Confirmed；
- 读取 Ground Truth；
- 自行增加预算；
- 生成并执行修复代码。

---

## 5. Runtime 状态机

```text
DRAFT
→ NEEDS_CONFIRMATION
→ READY
→ SEARCHING
→ REPLAYING
→ COMPLETED
```

生命周期表示“任务走到哪里”，Outcome 表示“业务结果是什么”。

可能的 Outcome：

- `CONFIRMED_VIOLATION`；
- `UNCONFIRMED_CANDIDATE`；
- `NO_VIOLATION_WITHIN_BUDGET`；
- `AMBIGUOUS_POLICY`；
- `UNSUPPORTED_RULE`；
- `INFRA_FAILED`；
- `CANCELLED`。

重要区别：

```text
status = COMPLETED
不等于
outcome = 成功或安全
```

状态更新应使用条件更新：

```sql
UPDATE attack_run
SET status = :next
WHERE id = :run_id AND status = :expected;
```

这样重复 Worker 或乱序任务不能覆盖权威状态。

---

## 6. Agent = Model + Harness

概念公式：

```text
Agent = Model + Harness
Harness = Context + Tools + Constraints + Verification + Recovery
Agent System = Agent + State + Authority + Observability
```

### Context

每个策略只看到：

- 冻结 RuleVersion 的必要摘要；
- 当前规范化状态；
- 合法 Action Schema；
- 该策略的有限历史；
- 当前 budget；
- 已确认反例 ID 用于去重。

不看到：

- hidden expected path；
- Sandbox vulnerable/fixed 实现开关；
- Oracle 预期答案；
- 其他策略完整聊天；
- 无关历史 Run；
- 数据库、代码和文件系统。

### Tools

Agent 看到的是业务动作，而不是数据库能力：

```text
create_order
apply_coupon
pay_order
refund_order
redeem_points
activate_membership
consume_entitlement
inspect_state
```

每个工具定义：

- 输入和输出 Schema；
- 前置条件；
- 副作用；
- 权限；
- 幂等范围；
- 是否可安全重试；
- 后置验证；
- 错误类型。

### Constraints

- Pydantic 严格校验；
- 动作白名单；
- 当前状态前置条件；
- 最大深度；
- 每策略 Token/时间/调用预算；
- state_hash 去重；
- 不允许任意代码和外部访问；
- 高风险错误 fail closed。

### Verification

- Simulator 只做候选检查；
- Sandbox 真实执行；
- Receipt 确认动作处理；
- Snapshot/Event 确认业务状态；
- Oracle 判不变量；
- 独立重放 3/3（golden-v4 实测 42/42）；
- Fixed 回归。

### Recovery

- Strategy Checkpoint；
- 业务幂等键；
- Receipt 查询；
- `ACTION_UNKNOWN`；
- 取消状态；
- Worker 重启后从 PostgreSQL 恢复。

### State

- PostgreSQL：权威版本、运行、Counterexample、Benchmark 和 Sandbox 状态；
- Redis：队列、限流、短期进度；
- SSE：事件通知；
- Trace：执行证据，不替代业务状态。

### Authority

Agent 的最大权限是提出一个合法动作。执行、裁决、预算和发布由确定性系统掌握。

### Observability

每次 Run 可以追到策略、模型调用、ActionProposal、Simulator、Sandbox Replay、Receipt、Snapshot 和 Oracle Finding。

---

## 7. Tool Contract 示例

错误设计：

```json
{"success": true}
```

问题：不知道请求是否提交、是否完成、是否可以重试、最终状态是什么。

推荐结构：

```json
{
  "action_id": "act-123",
  "idempotency_key": "run-1:refund:order-9:v1",
  "aggregate_type": "order",
  "aggregate_id": "order-9",
  "processing_status": "COMPLETED",
  "business_status": "REFUNDED",
  "receipt_version": 1,
  "verification": {
    "type": "query_snapshot_and_events",
    "expected_event": "REFUND_ISSUED"
  }
}
```

它把工具从“模型函数”提升为具有前置条件、副作用和后置验证的业务能力。

---

## 8. 三策略为什么隔离

### ValueFlow

关注：

- 净实付；
- 累计退款；
- 优惠价值；
- 积分发放/撤销/兑换；
- 权益价值守恒。

### Lifecycle

关注：

- 订单状态；
- 优惠券 RESERVED/USED/RESTORED；
- 会员 ACTIVE/REFUNDED；
- 权益 GRANTED/CONSUMED/REVOKED；
- 非法动作顺序。

### Boundary

关注：

- 重复请求；
- 0、临界值和最大值；
- 部分退款组合；
- 取消后重试；
- 结果未知后的再次调用。

隔离的原因：

- 保持策略差异可归因；
- 避免一个 Agent 的错误污染全部；
- 减少重复对话和上下文腐烂；
- 独立预算和停止；
- 便于消融哪种策略真正贡献新缺陷。

共享内容只包括 RuleVersion、Action Contract 和已确认反例 ID。Agent 不需要互相聊天。

---

## 9. 搜索空间如何控制

如果平均每个状态有 8 个动作、深度 12，朴素组合约为：

```text
8^12 ≈ 687 亿
```

必须控制：

- 状态前置条件过滤非法动作；
- 规范化 state_hash 合并语义相同状态；
- BFS 提供浅层基线；
- Agent 优先高风险分支；
- Beam/frontier 限制；
- 无状态变化路径 Early Exit；
- 同 invariant Candidate 去重；
- 深度、时间、Token 和调用数硬预算。

状态哈希包含影响未来行为的字段：余额、积分、券状态、订单实付/退款/状态、会员与权益数量。

不包含：数据库 ID、创建时间、Trace ID 等不影响后续行为的字段。

---

## 10. 为什么不是 Prompt、Skill 或通用框架

### Prompt/Skill 缺少什么

- 不可变 RuleVersion；
- 真实可执行环境；
- 副作用幂等和恢复；
- 独立 Oracle；
- Replay 和最小化；
- Counterexample 回归；
- Benchmark 和发布门禁。

### 为什么不以 LangGraph 为核心

项目状态机有限、需要显式展示条件更新、Checkpoint、Outcome 和错误语义。自己实现 Runtime 能真正掌握这些机制，也避免框架抽象隐藏关键面试点。

不是说 LangGraph 不好。升级条件是：

- 工作流分支快速增加；
- 多个业务团队需要可视化编排；
- 状态持久化、重放和人工节点已经成为重复基础设施；
- 采用框架仍能保留核心不变量和可观测性。

### 为什么不做通用 Agent 平台

RuleArena 的价值来自电商领域模型和确定性验证。通用平台会把两周 MVP 变成工具注册、插件、记忆、权限、沙箱和多入口工程，反而削弱业务闭环。

---

## 11. 典型故障

### LLM 输出非法动作

处理：Schema 拒绝，记录 validation failure；在预算内允许重新规划，不执行 fallback 动作。

### Agent 重复探索同一状态

处理：规范化 state_hash 去重；若 hash 设计错误，需要修正字段并使旧 Benchmark 失效。

### Worker 重复消费任务

处理：AttackRun expected status 条件更新；StrategyRun 和写动作具备幂等键。

### Context 中混入 Ground Truth

处理：立即 P0，阻断 Benchmark 和发布；追踪 loader → prompt → trace → API 数据流并重跑全部评测。

---

## 12. 高频问题与标答

### Q1：RuleSpec 和 Prompt 有什么区别？

Prompt 是对模型行为的语言约束，RuleSpec 是系统可以校验、版本化和执行的业务契约。关键金额、状态和引用必须在 RuleSpec 中，由代码强制，而不是依赖模型记住。

### Q2：为什么 RuleSpec 还要 LLM？

LLM 降低自然语言到结构化字段的输入成本，但不拥有最终解释权。Schema、领域 Validator 和人工确认负责可靠性。

### Q3：Workflow 和 Agent 的边界是什么？

生命周期、权限、预算、执行、裁决和恢复由 Workflow 控制；路径未知的动作选择由 Agent 处理。判断标准是该部分能否稳定画成有限状态机。

### Q4：为什么 Agent 不能直接调用 Sandbox？

Agent 输出不可信。Runtime 需要先校验动作、参数、预算、状态和重复，再通过受控 Client 调用，并保存统一 Trace。

### Q5：为什么三个 Agent 不沟通？

任务本质是三个独立搜索视角，不需要协商共同答案。自由对话会增加重复、Token 和上下文污染，也破坏策略贡献的可归因性。

### Q6：为什么 `COMPLETED` 不表示成功？

任务可能正常结束但没有在预算内发现问题，也可能规则不支持或候选无法重放。生命周期状态和业务 Outcome 必须分离。

### Q7：Context 越多不是越好吗？

不是。过多历史会加入过时、重复和 Ground Truth 风险。Agent 只需要冻结规则、当前状态、合法动作、有限历史和预算；权威事实每步重新读取。

### Q8：ToolCallID 能不能作为幂等键？

不能。ToolCallID 只关联一次模型工具调用，不表达业务动作的唯一性。业务幂等键应由 run、动作类型、目标、参数和业务版本稳定构造。

---

## 13. 半开卷复述关键词

```text
自然语言有歧义
→ RuleSpec + Schema + Validator + 人审
→ immutable RuleVersion

Workflow：状态/预算/执行/裁决/恢复
Agent：未知路径动作选择

Harness：Context/Tools/Constraints/Verification/Recovery
+ State/Authority/Observability

三策略隔离
state_hash + budget
模型只提议，代码掌权
```

