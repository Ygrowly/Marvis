# 03｜核心难题一：可执行世界、Sandbox 与独立 Oracle

## 1. 这道难题在解决什么

Agent 很容易生成一份听起来合理的风险报告：

> “退款后可能存在积分残留，建议检查。”

但技术上仍然没有回答：

- 这条路径在真实系统里是否合法；
- 每一步 API 是否真的成功；
- 最终状态是否真的违规；
- 问题来自规则冲突还是实现错误；
- 同样路径能否稳定复现；
- 去掉无关步骤后是否仍成立。

RuleArena 最核心的工程难题就是：

> **如何把模型的风险猜测变成可执行、可复现、可裁决的业务证据。**

---

## 2. 决策链

### 业务问题

人工无法枚举所有规则组合；Agent 能探索，但会幻觉和误判。

### 约束与规模

- 动作空间有限，但组合随深度指数增长；
- 不能在生产环境自由试错；
- 全部路径都走 HTTP 太慢；
- 只用模拟器会形成“自己实现、自己证明”；
- 资金和权益结论必须稳定、可重复；
- 两周 MVP 不能建设完整电商平台。

### 系统必须保证

1. 搜索足够快；
2. 确认结论来自真实 API 执行；
3. 裁决逻辑与被测实现独立；
4. 同版本和 seed 可复现；
5. Candidate 与 Confirmed 严格区分；
6. 反例能用于修复和回归。

### 整体方案

```text
策略 Agent
→ Reference Simulator 快速搜索
→ Candidate
→ 干净 Commerce Sandbox HTTP Replay
→ Snapshot + Receipt + Event
→ Deterministic Oracle
→ Confirmed Counterexample
→ Delta Debugging
→ Fixed Regression
```

---

## 3. 什么是“可执行业务世界”

可执行业务世界不是一份 PRD，也不是模型想象的状态。它至少包含：

```text
State + Action + Preconditions + Transition + Event + Invariant
```

### State

- 用户余额、积分、新用户状态；
- 优惠券面值、门槛、状态、关联订单；
- 订单原价、优惠、实付、累计退款、积分、状态；
- 会员实付、状态；
- 权益发放、消费和撤销数量。

### Action

- 创建用户；
- 发券；
- 创建订单；
- 用券；
- 支付；
- 取消；
- 退款；
- 积分兑换；
- 开通/取消会员；
- 消费权益；
- 检查状态。

### Preconditions

例如：

- 只有 `PENDING_PAYMENT` 订单可以支付；
- 只有可用且达门槛的券可以使用；
- 累计退款不能超过订单剩余可退；
- 积分余额足够才能兑换；
- 已退款订单不能再次退款。

### Transition

```text
state_before + valid_action + RuleVersion
→ state_after + receipt + events
```

### Invariant

无论经历多少合法动作都不应被破坏的规则，例如退款守恒、积分账本一致和幂等效果唯一。

---

## 4. Reference Simulator

### 作用

Simulator 是纯 Python 的快速参考状态机，用于：

- 在内存中执行大量候选动作；
- 根据前置条件过滤非法动作；
- 计算规范化 state_hash；
- 去重和剪枝；
- 快速发现可能违反 invariant 的路径。

理想接口：

```text
next_state, simulation_events = transition(rule, state, action)
```

### 为什么要尽量纯函数

- 相同输入得到相同输出；
- 容易单元测试和属性测试；
- 不依赖数据库时间、主键和事务；
- 可以复制状态并并行探索；
- 更容易定位状态空间和哈希错误。

### state_hash

只包含影响未来行为的语义字段：

- 余额和积分；
- 券状态、使用次数和关联订单；
- 订单状态、实付、退款和已发积分；
- 会员和权益数量。

不包含：

- 数据库自增 ID；
- created_at；
- Trace ID；
- HTTP 请求 ID；
- 不影响未来转换的展示字段。

### Simulator 的局限

它不能证明真实实现有漏洞，因为：

- 转换逻辑可能写错；
- 没有数据库约束和事务；
- 不包含序列化、API Validator 和幂等实现；
- 可能与 Sandbox 版本漂移；
- 仍是项目作者定义的参考模型。

因此 Simulator 只能把路径升级为 `Candidate`。

---

## 5. Commerce Sandbox

### 定位

Sandbox 是独立可运行的测试业务服务，不是 Simulator 的 HTTP 包装。

它应具备：

- 独立 FastAPI 服务；
- PostgreSQL 事务；
- control/sandbox 数据库角色隔离；
- 每 Run 独立业务数据；
- 订单、券、退款、积分账本、会员和权益聚合；
- ActionReceipt；
- 只追加 BusinessEvent；
- Vulnerable/Fixed Profile；
- 内部令牌和私网访问。

### 为什么走真实 HTTP

它验证的不只是业务公式，还包括：

- 请求 Schema 和序列化；
- 路由和鉴权；
- 事务边界；
- 幂等键；
- 数据库约束；
- 错误映射；
- Receipt 和事件；
- 超时后的最终状态查询。

如果 Worker 直接 import Sandbox service 函数，很多真实边界被跳过，也会让 Replay 难以迁移到外部系统。

### 为什么不需要完整商城

RuleArena 只需要承载不变量所依赖的最小业务状态，不需要：

- 商品搜索与详情；
- 库存履约；
- 物流；
- 商家结算；
- 用户增长系统；
- 完整后台和账户体系。

第一性原理是：

> **构建足以执行目标规则和暴露目标故障的最小真实系统。**

---

## 6. Oracle

### 定位

Oracle 是独立确定性裁决器，回答：

> 给定冻结规则、真实快照、Receipt 和事件，这条路径是否违反业务不变量？

### 输入

- RuleVersion；
- before/after Snapshot；
- ActionReceipt；
- BusinessEvent；
- OracleVersion。

### 输出

- invariant_id；
- passed/failed；
- expected value；
- actual value；
- evidence_refs；
- classification；
- oracle_version。

### 示例

```text
INV-02 Reward Conservation

订单实付：100
累计退款：100
净实付：0
规则允许积分：0
积分账本净额：100
结果：FAIL
证据：order-9 snapshot + ledger entries 31/45 + refund event 77
```

### 为什么不能用 LLM Judge

资金、积分、数量和状态转换有明确公式，LLM Judge 会带来：

- 同样输入结果不稳定；
- 数值计算错误；
- 受描述方式影响；
- 难以做精确回归；
- 无法成为发布阻断依据。

LLM Judge 适合后续评估：

- 风险说明是否清晰；
- 修复建议是否可读；
- 用户界面是否正确表达证据。

它不负责核心 invariant 裁决。

---

## 7. 如何避免“自己验证自己”

这是最容易被技术面试官击穿的点。

### 错误设计

```text
Sandbox 使用 calculate_refund()
Oracle 也调用 calculate_refund()
```

如果函数本身错误，两者会一致地给出错误结果。

### 正确隔离

| 层 | 实现方式 | 数据来源 |
| --- | --- | --- |
| Simulator | 纯参考状态转换 | RuleSpec + 内存 State |
| Sandbox | 独立业务服务和 ORM | HTTP 请求 + PostgreSQL |
| Oracle | 独立 invariant 公式 | 规范化 Snapshot + Ledger + Event |
| Evaluation | 私有 Ground Truth | Case metadata + Replay evidence |

允许共享：

- Action Schema；
- Decimal、Currency 等值对象；
- 枚举；
- Snapshot 公共结构。

禁止共享：

- 退款/积分状态转换实现；
- “是否有漏洞”函数；
- vulnerable profile；
- expected invariant/path。

### 独立性的验证

1. 对 Sandbox 注入一个积分撤销缺陷，Oracle 应失败；
2. 对 Simulator 注入同类错误，Sandbox Replay 仍应以真实状态重新裁决；
3. 修改 Oracle 阈值，版本必须变化且旧 Benchmark 失效；
4. Static import 检查阻止 Oracle import Sandbox private module；
5. Contract tests 确保共享的只是 Schema，不共享业务实现。

---

## 8. Candidate、Confirmed 与分类

### Candidate

Agent/Simulator 认为可疑，但还没有真实 API 证据。

### Confirmed Violation

必须同时满足：

1. 从干净 Sandbox Run 开始；
2. 所有动作通过真实 API；
3. Receipt 和事件完整；
4. Oracle 对真实快照检测到 invariant 失败；
5. 版本元组固定；
6. 同一路径连续 Replay 3/3。

### 分类

| 分类 | 判断 |
| --- | --- |
| POLICY_CONFLICT | 参考规则本身允许到达非法状态 |
| IMPLEMENTATION_DIVERGENCE | 参考模型安全，但 Sandbox 实现偏离 |
| UNCONFIRMED_CANDIDATE | 模拟可疑但真实 API 不能复现 |
| AMBIGUOUS_POLICY | 规则无法唯一解释 |
| UNSUPPORTED_RULE | 超出固定领域原语 |

分类意义：产品冲突交给产品经理，代码偏离交给开发，无法确认不应制造误报。

---

## 9. Replay 为什么必须从干净环境开始

如果复用 Agent 搜索过程中的环境，可能存在：

- 前一条路径残留的订单和优惠券；
- 重复积分；
- 未清理 Receipt；
- 不同策略互相污染；
- 数据库主键和顺序差异。

正确做法：

```text
创建新 Sandbox Run
→ 加载固定 ScenarioVersion
→ 按顺序执行 Candidate Actions
→ 每步记录 Receipt/Event/Snapshot
→ Oracle 检查
→ 保存 final_snapshot_hash
```

可复现版本元组：

```text
RuleVersion
+ ScenarioVersion
+ SandboxVersion/Profile
+ OracleVersion
+ runtime/prompt/model version
+ seed/budget
```

---

## 10. Counterexample 最小化

### 为什么需要

Agent 找到的路径可能有 10～12 步，其中只有 5～6 步真正必要。长路径：

- 开发难以理解；
- 修复定位困难；
- 回归耗时；
- 容易包含偶然状态。

### 删除式 Delta Debugging

```text
原路径 actions
→ 删除一段/一个动作
→ 新建干净 Sandbox Run
→ 重放剩余动作
→ 是否仍违反同一 invariant？
    是：接受删除
    否：恢复动作
→ 直到任意单步再删除都会失效
```

### 为什么叫 1-minimal

它只保证当前序列中任何一个动作都不能单独删除，不保证在全部可能路径中全局最短。

安全表述：

> 系统通过删除式重放得到当前路径删除空间中的 1-minimal 反例，没有做形式化全局最短证明。

---

## 11. 故障场景、排查与恢复

### Candidate 在 Simulator 违规，但 Sandbox 不违规

可能原因：

- Simulator 语义错误；
- RuleVersion 映射不一致；
- Sandbox 已修复；
- API 动作被拒绝；
- 状态哈希误合并；
- Candidate 依赖隐含初始状态。

排查：

1. 对比完整版本元组；
2. 对比每步模拟状态和 Sandbox Snapshot；
3. 找到第一个 divergence step；
4. 检查 Action Contract 和前置条件；
5. 修复 Simulator 或标记 Unconfirmed；
6. 增加 contract/regression test。

### Oracle 突然大量误报

止血：暂停 Release Gate 和自动 Confirmed，不删除原始 Run。

排查：

- OracleVersion 是否变化；
- Decimal/单位/符号是否错误；
- Snapshot 字段是否变更；
- normal Case 是否覆盖；
- 账本投影和账本净额是否混用。

验证：对正常和已知漏洞 Case 双向回归，确认误报为 0 后再恢复。

### Replay 偶发 2/3

可能是：

- 非确定性时间；
- 未清理数据；
- 幂等键冲突；
- Worker 并发污染；
- 数据库读取时机；
- 随机 seed 或排序不稳定。

不能把 2/3 包装成 Confirmed。应保留失败 Trace，定位非确定性来源。

---

## 12. 替代方案与代价

### 只用 Simulator

优点：快、简单。  
代价：不能验证 API、事务和实现偏离，可信度不足。

### 所有搜索都直接走 Sandbox API

优点：更接近真实实现。  
代价：状态创建和 HTTP 成本高，搜索吞吐低，难以复制分支状态。

### 使用生产/Staging

生产不可接受；Staging 后续可用 TargetAdapter 接入。代价是数据准备、清理、权限、隐私和外部系统非确定性增加。

### 使用形式化模型检查

适合固定小状态机，能够提供更强覆盖；但需要精确形式化规则，接入真实 API 和复杂业务成本高。后续可以把 RuleSpec 导出到模型检查器，MVP 不需要。

### 用 LLM Judge 裁决

实现快，但资金状态不稳定、难回归，不适合作为核心 Gate。

---

## 13. 验证方法

- Simulator transition 单元和属性测试；
- state_hash 等价/非等价测试；
- Sandbox API + PostgreSQL 集成测试；
- Vulnerable Profile 定向注入；
- Oracle 每条 invariant 正反例；
- Static import/模块边界测试；
- Candidate → Replay divergence 测试；
- Replay 3/3；
- Delta Debugging 删除关键/非关键动作测试；
- Fixed 版本旧反例消失、正常 Case 仍通过。

---

## 14. 升级条件

### 接入外部开源电商

当内置 Sandbox 闭环稳定后，通过 TargetAdapter 映射统一 Action Contract。Oracle 仍读取规范化快照，不能依赖目标系统私有“正确答案”。

### 支持真实并发

当现有顺序与重复请求 Case 稳定后，再增加并发调度器、barrier、操作时间线和数据库隔离级别测试。MVP 不假装覆盖全部分布式竞争。

### 引入形式化验证

当 RuleSpec 已稳定、状态数量可控、业务需要更强安全保证时，可对核心状态机做模型检查；Agent 继续负责寻找复杂语义路径。

---

## 15. 3～5 分钟核心难题标答

> RuleArena 最难的问题不是让 Agent 生成测试，而是怎样证明它找到的问题真的成立。我的设计把搜索、执行和裁决拆成三层。第一层是 Reference Simulator，它是纯 Python 状态机，适合快速复制状态、计算 state_hash 和搜索大量路径，但它只能产生 Candidate，因为模拟逻辑本身也可能错误。第二层是独立 Commerce Sandbox，它通过真实 HTTP API、PostgreSQL 事务、幂等 Receipt 和业务事件执行路径，每个 Candidate 都从干净 Scenario 开始重放。第三层是确定性 Oracle，它不复用 Sandbox 的状态转换代码，只根据冻结 RuleVersion、规范化快照、账本、Receipt 和事件检查退款、积分、优惠券、权益和幂等不变量。只有 API Replay 成功、Oracle 失败并连续复现 3/3，才会生成 Confirmed Counterexample。之后再通过删除式 Delta Debugging，从干净环境反复重放，得到当前路径的 1-minimal 反例。这样既利用 Agent 探索未知组合，又把最终正确性放在确定性、可审计的系统里。

追问关键词：

```text
Simulator 只能 Candidate
Sandbox 真实 HTTP/事务
Oracle 独立公式
共享 Schema 不共享业务实现
clean replay
3/3
1-minimal
```

