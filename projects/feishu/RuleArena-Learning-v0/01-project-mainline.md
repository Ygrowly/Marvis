# 01｜项目全貌、业务主线与黄金案例

## 1. 本篇目标

学完后能够：

- 用一句话解释 RuleArena；
- 讲清目标用户和真实业务问题；
- 从输入一直讲到发布门禁；
- 用黄金案例解释项目价值；
- 区分项目设计、测试业务服务和真实企业生产。

---

## 2. 一句话定位

> **RuleArena 是面向电商促销、退款、积分和会员权益规则变更的 AI 对抗验证与发布门禁平台。它让 Agent 搜索异常操作组合，通过真实 API 重放和确定性 Oracle 裁决，并把确认问题沉淀为可长期回归的最小反例。**

关键词：

```text
电商规则变更 / 对抗搜索 / API 重放 / Oracle / 最小反例 / 发布门禁
```

---

## 3. 业务问题从哪里来

电商中存在多个相互影响的模块：

- 订单；
- 支付与退款；
- 优惠券；
- 积分；
- 会员与次数型权益。

单个模块的规则通常容易测试，问题经常出在跨模块组合：

```text
支付成功发积分
+ 退款恢复优惠券
+ 积分可以兑换新券
+ 退款没有撤销积分
= 用户退款后仍保留额外权益
```

其他典型问题：

- 重复退款或多次部分退款累计超过实付；
- 取消订单后优惠券重复恢复；
- 已消费会员权益后仍然全额退款；
- 请求超时重试造成重复积分或重复权益；
- 单步合法动作按照特殊顺序组合后到达非法状态。

### 传统方法为什么不够

| 方法 | 擅长 | 不足 |
| --- | --- | --- |
| 单元测试 | 已知函数和边界 | 依赖开发者提前想到路径 |
| 人工业务测试 | 主流程和经验 Case | 组合空间大、更新成本高 |
| 模糊测试 | 随机输入、协议异常 | 不理解业务状态和价值关系 |
| 模型审 PRD | 生成风险清单 | 无法证明真实系统能复现 |
| 纯 Agent 操作 | 探索未知路径 | 模型可能误判、成本不稳定 |

RuleArena 的补位不是替代全部测试，而是：

> **在单元测试和人工 Case 之外，主动搜索没有被想到的跨规则动作序列，并把发现变成确定性回归资产。**

---

## 4. 用户与核心任务

| 用户 | 使用 RuleArena 的时机 | 最终需要的结果 |
| --- | --- | --- |
| 产品经理 | 规则评审或变更 | 歧义、冲突和发布风险 |
| 测试工程师 | 设计回归集 | 可重放动作序列和 pytest |
| 后端开发 | 修复规则实现 | 请求、事件、状态 Diff 和 invariant |
| 风控 | 寻找套利路径 | 资金/权益异常的确定性证据 |
| 运营 | 上线促销/会员活动 | 修复前后对比和发布结论 |

核心 JTBD：

> 当一组电商规则准备上线或变更时，在不修改生产数据的前提下，搜索可能造成资金或权益异常的路径，确认其是否真实可复现，并把结果纳入修复回归和发布门禁。

---

## 5. 输入、输出与边界

### 输入

- 内置业务规则模板；
- 用户的自然语言规则修改；
- Scenario 初始状态；
- Sandbox Profile 和版本；
- 搜索深度、时间、Token、模型调用预算；
- Golden/Benchmark Case。

### 输出

- 经确认的 RuleVersion；
- Candidate Path；
- Sandbox Replay；
- Oracle Finding；
- 1-minimal Counterexample；
- 状态 Diff、Receipt、Event 和 Trace；
- Fixed Regression；
- Benchmark 和 Release Gate。

### 不负责

- 不直接连接真实支付生产环境；
- 不自动修复和发布业务代码；
- 不证明规则绝对安全；
- 不支持任意行业自由建模；
- 不审查任意产品方案、商业模式或 UX；
- 不替代单元测试、集成测试和人工验收。

---

## 6. 完整业务主线

### 第一步：规则输入

用户选择“优惠 + 退款积分”模板，用自然语言修改：

> 新用户获得 50 元券，订单实付满 100 元发放 100 积分；全额退款后恢复优惠券；100 积分可以兑换 20 元券。

### 第二步：规则编译和确认

LLM 只负责生成候选 RuleSpec。Pydantic 和领域 Validator 检查：

- 字段和枚举是否合法；
- 金额是否非负；
- 引用的优惠券、积分和 invariant 是否存在；
- “全额退款恢复券”是否还需要说明积分处理；
- 是否超出固定领域能力。

存在歧义时停在 `NEEDS_CONFIRMATION`。用户确认后冻结不可变 RuleVersion。

### 第三步：确定性基线

先运行规则检查、Random 和 BFS：

- 建立不用 LLM 的能力下限；
- 发现浅层和明显问题；
- 为 Multi-Agent 的价值提供比较基线。

### 第四步：策略搜索

三个策略独立探索：

- ValueFlow 看钱和权益是否守恒；
- Lifecycle 看状态转换是否合法；
- Boundary 看重复、部分退款和异常顺序。

Agent 只能输出 ActionProposal，不能直接写数据库或决定结果。

### 第五步：模拟探索

Reference Simulator 在内存状态中快速执行动作：

- 计算下一状态；
- 跳过非法动作；
- 使用 state_hash 去重；
- 达到深度/成本边界时停止；
- 将可疑路径标记为 Candidate。

### 第六步：真实 API 重放

每个 Candidate 从干净 Sandbox Run 开始：

- 调用独立 HTTP API；
- 每个写动作携带 idempotency_key；
- 保存 ActionReceipt；
- 查询状态快照和业务事件；
- 不直接访问 Sandbox 数据库实现细节。

### 第七步：确定性裁决

Oracle 检查：

- 累计退款是否超过实付；
- 有效积分是否超过净实付应得；
- 优惠券是否重复产生价值；
- 会员退款和权益回收是否一致；
- 相同幂等键是否只产生一次效果；
- 状态转换、账本和非负资产是否一致。

### 第八步：最小反例

只有 Replay 成功且 Oracle 失败的路径才是 Confirmed。系统逐段删除动作，每次从干净环境重放；删除后仍违反同一 invariant 才接受。

结果称为当前删除空间中的 `1-minimal`，不宣称全局最短。

### 第九步：修复回归

切换 Fixed Profile 或新 RuleVersion：

- 旧 Counterexample 不再触发；
- 正常支付、退款和优惠券流程仍通过；
- 历史 P0 反例加入长期回归集。

### 第十步：发布门禁

Gate 检查当前完整版本元组对应的实际 Benchmark：

- normal confirmed 误报；
- 反例 3/3；
- hidden 发现率；
- 历史 P0；
- Ground Truth 泄漏；
- 模型成本和稳定性。

---

## 7. 黄金案例逐步推演

### 初始规则和状态

```text
用户：新用户，余额 200 元，积分 0
优惠券：无
订单：无
```

### 动作 1：发放优惠券

```text
issue_coupon(value=50, threshold=100)
```

状态：用户拥有一张可用 50 元券。

### 动作 2：创建订单

```text
create_order(amount=150)
```

状态：订单进入 `PENDING_PAYMENT`。

### 动作 3：使用优惠券

```text
apply_coupon(order, coupon)
```

状态：原价 150，优惠 50，应付 100；券 `RESERVED/USED`。

### 动作 4：支付

```text
pay_order(order)
```

状态：

- 余额减少 100；
- 订单 `PAID`；
- 产生 `PAYMENT_CAPTURED`；
- 发放 100 积分和 `POINTS_GRANTED`。

### 动作 5：全额退款

```text
refund_order(order, 100)
```

Vulnerable v1：

- 余额退回 100；
- 订单 `REFUNDED`；
- 优惠券恢复；
- 没有生成 `POINTS_REVOKED`；
- 用户仍有 100 积分。

### 动作 6：兑换积分

```text
redeem_points(100)
```

状态：用户用退款后残留积分兑换 20 元券。

### Oracle 判断

订单净实付为 0：

```text
net_paid = paid_amount - refunded_amount = 100 - 100 = 0
allowed_points = points_function(0) = 0
actual_valid_points_value > 0
```

违反 Reward Conservation。模型的解释只是辅助，成立依据是账本、快照、事件和规则函数。

### Fixed v2

退款事务同时：

- 记录退款；
- 撤销订单积分；
- 按明确规则恢复优惠券；
- 写入 Receipt 和事件。

旧路径不再产生额外权益；正常退款仍能完成。

---

## 8. 核心业务对象

| 对象 | 关键状态/字段 | 为什么重要 |
| --- | --- | --- |
| RuleVersion | 规则、歧义、prompt_version | 保证运行绑定固定语义 |
| ScenarioVersion | 初始状态、Profile、visibility | 保证重放起点一致 |
| Order | 原价、优惠、实付、退款、积分、状态 | 连接价值和生命周期 |
| Coupon | 面值、门槛、状态、关联订单 | 防重复价值和错误恢复 |
| Refund | 金额、状态、idempotency_key | 资金守恒和重复执行 |
| PointsLedger | GRANT/REVOKE/REDEEM | 积分投影可由账本重建 |
| Membership | 实付和状态 | 会员退款生命周期 |
| Entitlement | 发放/消费/撤销数量 | 权益与退款一致性 |
| BusinessEvent | 只追加事件 | 审计和后置验证 |
| Counterexample | 原始/最小动作、invariant | 回归和修复证据 |

---

## 9. 八条业务不变量

### INV-01 Refund Conservation

```text
累计退款 <= 订单实付
```

### INV-02 Reward Conservation

```text
有效订单积分 <= 净实付应得积分
```

### INV-03 Coupon Single Value

同一优惠券不能对两个最终有效订单同时产生优惠价值；恢复必须由规则允许。

### INV-04 Entitlement Refund Consistency

会员全额退款后，未消费权益必须撤销；已消费权益必须扣减退款或拒绝全退。

### INV-05 Idempotent Effect

相同业务幂等键只产生一次效果和一份成功 Receipt。

### INV-06 Legal Transition

取消订单不能支付，已全额退款订单不能再次退款。

### INV-07 Ledger Consistency

```text
points_balance == signed_sum(points_ledger)
```

### INV-08 Non-negative Assets

余额、积分、剩余权益和未退款金额不能为负。

记忆方式：

```text
钱、积分、券、权益、幂等、状态、账本、非负
```

---

## 10. 为什么这是真实业务项目

“真实”分五层：

| 层次 | 项目中的真实性 |
| --- | --- |
| 问题 | 退款、优惠、积分和权益组合是实际电商问题 |
| 服务 | 独立 FastAPI + PostgreSQL，通过 HTTP 执行动作 |
| 缺陷 | Vulnerable Profile 是可解释的真实类型实现错误 |
| 裁决 | 读取权威状态、账本、事件和 Receipt |
| 工程 | 队列、幂等、恢复、Trace、评测和部署真实运行 |

但必须明确：

> MVP 使用的是可执行测试业务服务，不是企业真实生产流量，也没有真实用户损失数据。

这种设计的价值是能够低成本、可控地得到 Ground Truth，同时保留生产系统中最关键的状态、一致性和验证问题。

---

## 11. 与已有项目的能力互补

| 项目 | 主要能力 | RuleArena 新增信号 |
| --- | --- | --- |
| EnergyOps | 数据质量、调度、告警、账单 | 对抗搜索、状态空间和发布门禁 |
| 数驭穹图 | RAG/NL2SQL、权限、可信结果 | 可执行世界、Oracle、Agent Eval |
| Ovanta | 交易、会员、审核、业务后端 | 独立个人产品、验证平台和在线 Demo |
| RuleArena | 规则、Agent、回放、裁决、回归 | AI 应用完整设计和工程闭环 |

RuleArena 不需要再塞入 RAG、NL2SQL 或完整商城；它的价值正是补充独立 Agent Runtime、验证和评测能力。

---

## 12. 高频问题与标答

### Q1：为什么不让 LLM 直接审查规则？

因为 LLM 能提出风险，但不能证明系统能执行该路径，也无法稳定判断资金和状态是否违规。RuleArena 让模型负责搜索，让真实 API 和确定性 Oracle 提供证明。

### Q2：它和自动生成测试用例有什么区别？

普通生成器输出测试文本或代码，RuleArena 维护可执行状态、动作空间、真实 API Replay、Oracle 和修复回归。重点不是生成多少用例，而是找到并确认一个此前未知的反例。

### Q3：为什么不用生产系统？

生产环境有真实副作用、隐私和风控风险，无法自由探索。MVP 使用独立 Sandbox 获得可控 Ground Truth；后续通过 TargetAdapter 接入开源系统或企业 Staging，而不是直接写生产。

### Q4：为什么选择电商规则？

它有具体业务价值、有限动作和状态、可计算的不变量、直观的损失故事，也与退款 Agent、交易后端和 Agent Commerce 具有迁移关系。

### Q5：系统能证明规则安全吗？

不能。只能声明在固定版本、Scenario、seed 和预算内发现或未发现违规。搜索空间有边界，Agent 和测试集也有覆盖限制。

### Q6：最有价值的输出是什么？

经过干净 API 重放、Oracle 确认、连续复现并最小化的 Counterexample，以及修复后的回归结果。

---

## 13. 90 秒回答骨架

关键词：

```text
跨规则组合风险
→ 单元测试已知 / LLM 只猜测
→ RuleSpec + 人审
→ BFS + 三策略
→ Simulator 搜索
→ Sandbox API Replay
→ Oracle
→ 1-minimal
→ Fixed 回归 + 24 Case 消融
```

标答：

> 电商里很多问题不是单条规则错误，而是订单、优惠券、积分和退款按特殊顺序组合后出错。人工测试只能覆盖想到的路径，单纯让 LLM 审 PRD 又只能给风险提示，所以我设计了 RuleArena。系统先把自然语言规则编译成严格 RuleSpec，存在歧义必须人工确认；然后用 BFS 和三个隔离策略搜索动作序列，先在参考模拟器中快速探索，再从干净环境调用独立 Commerce Sandbox 的 HTTP API 重放。模型只能提出动作，漏洞是否成立由 Oracle 根据退款、积分、优惠券、权益和幂等不变量判断。确认问题会被压缩为 1-minimal 反例，修复后继续回归。项目还设计了 24 个开发和隐藏 Case，对比 Random、BFS、Single Agent 和 Multi-strategy，避免把多 Agent 当成没有证据的卖点。

半开卷复述时只看上面的关键词，不逐字背诵。

