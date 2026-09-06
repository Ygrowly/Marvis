# 04｜核心难题二：副作用、幂等、结果未知与恢复

## 1. 为什么这是生产级 Agent 的核心

读取失败通常可以重试，退款、发券、扣积分等写动作不能简单重试。

典型场景：

```text
Worker 调用 refund_order
→ Sandbox 已提交退款事务
→ HTTP 响应在网络中丢失
→ Worker 超时
```

此时 Worker 不知道：

- 请求没到；
- 请求到了但失败；
- 事务已成功但响应丢失；
- 事务仍在处理中。

如果直接重试，可能重复退款；如果直接放弃，运行状态又不完整。

核心问题：

> **请求结果未知时，怎样避免重复副作用，并让任务恢复到可判断状态。**

---

## 2. 三个概念必须分开

### 幂等键

定义同一个业务意图，多次请求只产生一次业务效果。

推荐组成：

```text
run_id + action_type + target_id + normalized_arguments + rule_version + logical_step
```

### ActionReceipt

记录某个幂等键的处理事实：是否接受、完成、拒绝或未知，并提供后置查询信息。

### Checkpoint

保存 Agent/Workflow 执行到哪里、frontier 和预算，用于进程恢复。它不证明业务动作是否成功。

一句话：

> **幂等键防重复效果，Receipt 判断一次动作，Checkpoint 恢复任务进度，权威状态查询确认业务现实。**

---

## 3. ToolCallID 为什么不能当幂等键

ToolCallID 由模型或 Agent Runtime 为一次调用生成，只用于关联 ToolCall 和 ToolResult。

同一个业务意图在以下情况下可能产生不同 ToolCallID：

- 模型重新规划；
- Worker 重启；
- 会话恢复；
- HTTP 超时后重新发起；
- 两个策略恰好提出相同动作。

业务幂等键必须基于业务身份稳定构造，而不是依赖某次技术调用 ID。

---

## 4. ActionReceipt 设计

建议字段：

```text
receipt_id
run_id
action_type
idempotency_key
request_hash
aggregate_type / aggregate_id
processing_status
business_status
result_json
error_type
aggregate_version
created_at / completed_at
```

处理状态：

- `ACCEPTED`：已接收，尚未确认完成；
- `COMPLETED`：事务已成功；
- `REJECTED`：确定性拒绝，没有副作用；
- `UNKNOWN`：当前无法确认，需要人工/后续恢复。

同一个 idempotency_key 如果 request_hash 不同，必须返回冲突，不能静默复用旧结果。

---

## 5. 单个写动作的事务边界

以退款为例，一个数据库事务中完成：

1. 查询/锁定订单；
2. 查询已有 Receipt；
3. 验证订单状态和剩余可退；
4. 创建 Refund；
5. 更新订单累计退款与状态；
6. 撤销积分或权益；
7. 写入不可变账本；
8. 追加 BusinessEvent；
9. 写入成功 Receipt；
10. 提交事务。

必须有数据库唯一约束，例如：

```text
UNIQUE(run_id, action_type, idempotency_key)
```

为什么业务校验和数据库约束都要有：

- 业务校验给出清晰错误；
- 唯一约束防止并发竞态穿透；
- 事务保证业务效果、事件和 Receipt 一致提交。

---

## 6. 超时后的恢复决策

```text
写动作超时
→ 使用相同 idempotency_key 查询 Receipt
    ├── COMPLETED：读取权威 Snapshot，继续
    ├── REJECTED：记录失败，根据错误决定是否换业务动作
    ├── ACCEPTED：短暂等待/轮询，受预算限制
    ├── 不存在：在确认请求未被接受后，可使用相同 key 重试
    └── 无法查询：ACTION_UNKNOWN，停止当前分支
```

关键点：

- 重试仍使用同一个业务幂等键；
- 不能因为没收到响应就假设失败；
- 不能换新 key 规避重复检查；
- Receipt 成功后仍读取 Snapshot/Event 做后置验证；
- 无法判断时宁可停止分支，不制造第二次副作用。

---

## 7. 三种超时情况

### 请求到达前超时

Sandbox 没有 Receipt。相同 key 重试可安全执行。

### 事务提交前失败

事务回滚，Receipt 和业务效果都不存在或明确 REJECTED。相同 key 可按错误类型重试。

### 事务提交后响应丢失

Receipt 为 COMPLETED。Worker 查询后复用原结果，不能再次退款。

系统无法仅根据客户端异常区分三者，因此必须依赖服务端幂等和权威查询。

---

## 8. 重试分类

### 可以有界重试

- 连接暂时失败；
- 429/503；
- 数据库短暂连接错误；
- 明确未提交的临时失败；
- Receipt 查询暂时不可用。

要求：

- 相同幂等键；
- 指数退避 + jitter；
- 最大次数/时间；
- 完整 Trace。

### 不应重试

- 参数非法；
- 权限拒绝；
- 订单状态不允许；
- 退款超过剩余可退；
- RuleVersion 不一致；
- request_hash 与旧 Receipt 冲突。

### 结果未知

不能归入成功或失败。保存 `ACTION_UNKNOWN`，停止当前路径，运行 Outcome 可为 `INFRA_FAILED` 或部分失败语义。

---

## 9. Worker、队列与至少一次投递

Redis/ARQ 任务通常应按“可能重复投递”设计，而不是假设 exactly-once。

流程：

1. Worker 领取 AttackRun；
2. 使用 expected status 条件更新认领；
3. 从 PostgreSQL 读取版本和 Checkpoint；
4. 执行一个有界步骤；
5. 持久化 Step/Receipt/Trace；
6. 更新 Checkpoint；
7. 继续或结束。

重复 Worker：

- 条件更新只有一个能获得合法状态；
- 同一动作的幂等键唯一；
- 已完成 Step 可以从权威状态跳过；
- 不依赖内存锁保证正确性。

---

## 10. Checkpoint 应该保存什么

- StrategyRun status；
- frontier；
- visited_state_hashes；
- 已用步骤、时间、Token、模型调用次数；
- Candidate 引用；
- Rule/Scenario/Sandbox/Oracle 版本；
- prompt/model config hash；
- checkpoint_version。

不应该保存并当作权威事实：

- “退款已经成功”但没有 Receipt；
- 仅存在于模型文本中的状态；
- 旧 Snapshot 冒充恢复后的当前状态。

恢复流程：

```text
加载 AttackRun 权威状态
→ 验证版本元组
→ 加载最新 Checkpoint
→ 对最后一个可能有副作用的 Step 查询 Receipt
→ 重新读取 Sandbox Snapshot
→ 校准 frontier 和预算
→ 继续
```

---

## 11. Worker 崩溃位置矩阵

| 崩溃位置 | 可能状态 | 恢复方法 |
| --- | --- | --- |
| 调用前 | 无业务效果 | 从 Checkpoint 继续 |
| 请求已发、未提交 | 可能无 Receipt | 相同 key 查询/重试 |
| 事务已提交、未返回 | 有 COMPLETED Receipt | 复用 Receipt，不重做 |
| ToolResult 已保存、Checkpoint 未保存 | 业务成功，进度旧 | 查询 Step/Receipt 后推进 |
| Checkpoint 已保存、SSE 未发 | 权威状态正确，UI 旧 | Run API 恢复 |
| Oracle 后、Counterexample 前 | Replay 有证据，产物缺失 | 幂等创建 Counterexample |

系统设计目标不是永不崩溃，而是：

> **任意中断点都能根据权威事实判断该继续、跳过、重试还是停止。**

---

## 12. 并发退款怎样防止超额

场景：两个请求同时读取剩余可退 100，都准备退款 80。

只在应用层先查再写会产生 160 元退款。

保守方案：

- 在事务中锁定订单行，或使用乐观版本条件更新；
- 数据库约束/条件保证 `refunded_amount + amount <= paid_amount`；
- Refund 幂等键唯一；
- 更新订单和退款记录在同一事务；
- Oracle 再检查最终账本。

乐观更新示例：

```sql
UPDATE orders
SET refunded_amount = refunded_amount + :amount,
    version = version + 1
WHERE id = :id
  AND version = :expected_version
  AND refunded_amount + :amount <= paid_amount;
```

受影响行数为 0 时重新读取并返回冲突，不盲目重试业务动作。

MVP 当前主要覆盖重复和顺序动作；真正并发需要后续加入 barrier 和并发测试，不能把设计说明成已完整实现。

---

## 13. Event 与 Outbox

MVP 中 BusinessEvent 与聚合、账本、Receipt 存在同一 PostgreSQL，可在同一事务写入。

如果未来需要把事件发布到 Kafka、通知或外部系统，不能在事务提交后直接“尽力发送”，应引入 Outbox：

```text
业务事务：聚合 + 账本 + Receipt + OutboxEvent
→ 提交
→ 异步 Publisher 读取 Outbox
→ 至少一次发布
→ 消费端幂等
```

当前不提前引入 Kafka/Outbox Worker，升级条件是出现真实跨服务事件投递需求。

---

## 14. 故障处理决策链

以“退款调用超时”为例：

### 发现

- HTTP timeout；
- Trace 有 request_start 无 response；
- StrategyStep 停在 EXECUTING。

### 止血

- 不使用新 key 重试；
- 暂停该分支；
- 保留 Run、Step 和请求 Hash。

### 定位

1. 查询 Receipt；
2. 查询订单 Snapshot；
3. 查询 Refund、Ledger 和 Event；
4. 检查事务/服务日志；
5. 判断请求未到、回滚、已提交或未知。

### 修复

- 完善服务端幂等；
- 将 Receipt 与业务效果纳入同一事务；
- 增加后置查询；
- 调整错误分类和重试策略。

### 验证

- 提交前/后故障注入；
- 相同 key 重试 N 次效果仍为 1；
- Worker 重启后状态一致；
- Oracle 和账本一致。

### 预防

- unknown rate 告警；
- 幂等冲突指标；
- 事务和 Receipt contract test；
- 关键副作用历史回归。

---

## 15. 替代方案与代价

### 全局分布式锁

实现直观，但吞吐和可用性受锁服务影响，仍不能替代服务端幂等和事务。MVP 优先业务唯一键 + 条件更新。

### Exactly-once 消息

端到端 exactly-once 很难保证。更现实的设计是至少一次投递 + 幂等消费者 + 权威查询。

### 所有失败自动重试三次

简单但危险。必须按临时性、确定性和结果未知分类；副作用操作只能在幂等和可查询条件下重试。

### Checkpoint 之后才执行动作

无法消除动作与 Checkpoint 之间的崩溃窗口。正确方案仍是业务幂等和权威 Receipt，而不是寻找完美保存顺序。

---

## 16. 高频问题与标答

### Q1：幂等是“请求多次结果一样”吗？

更准确是同一个业务意图重复请求，只产生一次业务效果，并能返回与第一次一致的处理结果。不能只看 HTTP 返回文本相同。

### Q2：有幂等键为什么还要查询权威状态？

幂等键防重复，但不说明当前动作是成功、失败还是处理中。Receipt 和 Snapshot 用于判断真实业务状态。

### Q3：Checkpoint 能防重复退款吗？

不能。Checkpoint 是任务恢复层，可能落后于业务提交。重复副作用要靠服务端幂等、事务和权威查询。

### Q4：结果未知为什么不多重试几次？

因为请求可能已经成功，换 key 或无条件重试可能产生第二次副作用。先用相同 key 查询；无法确认时停止并暴露 unknown。

### Q5：消息队列能保证 exactly-once 吗？

通常不能端到端保证。系统按至少一次投递设计，依靠条件更新、业务幂等键和幂等消费者实现效果一次。

### Q6：Receipt 应该何时写？

成功 Receipt 应与业务效果、账本和事件在同一事务提交，否则会出现业务成功但无 Receipt，或 Receipt 成功但业务回滚。

### Q7：为什么不用 Redis 锁？

锁可以降低竞争，但不能成为资金正确性的唯一保证。数据库事务、条件更新和唯一约束更接近权威状态；只有真实高竞争时再评估锁。

### Q8：什么是 `ACTION_UNKNOWN`？

系统无法确认一个有副作用动作最终是否生效。它不是普通失败，不能自动重试或继续依赖该状态，应停止分支并保留调查证据。

---

## 17. 3 分钟标答

> Agent 系统里最危险的是有副作用动作超时，因为客户端不知道请求没到、事务失败，还是已经成功但响应丢失。RuleArena 不把 ToolCallID 当业务幂等键，而是根据 run、动作、目标、参数、规则版本和逻辑步骤构造稳定幂等键。Sandbox 在同一数据库事务中完成聚合更新、账本、BusinessEvent 和 ActionReceipt，并用唯一约束保证同一动作效果一次。Worker 超时后不会换 key 直接重试，而是先查询 Receipt：已完成就读取权威 Snapshot 后继续，明确失败再按错误类型决定是否重试，仍无法确认就记录 ACTION_UNKNOWN 并停止该分支。Checkpoint 只保存 Agent 的 frontier 和预算，用于恢复进度，不能替代业务事实。Worker 重启时先读取 AttackRun 和最后一个 Receipt，再校准 Checkpoint。这样系统接受队列至少一次投递和进程随时崩溃，但可以保证业务副作用不会因为恢复流程重复发生。

关键词：

```text
ToolCallID ≠ idempotency key
same transaction
Receipt + Snapshot
same key retry
ACTION_UNKNOWN
Checkpoint ≠ business truth
at-least-once + idempotent effect
```

