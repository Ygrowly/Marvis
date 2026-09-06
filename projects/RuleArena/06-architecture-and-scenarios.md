# 06｜架构选型卡与系统设计场景题

## 1. 使用方式

每张卡按同一条决策链记忆：

```text
业务问题
→ 约束与规模
→ 必须保证
→ 当前选择
→ 为什么
→ 替代方案与代价
→ 故障风险
→ 验证方式
→ 升级条件
```

面试不要只回答“我用了什么”，而要回答：

> **在当时规模和约束下，什么是最小充分方案；如果条件变化，什么时候升级。**

---

## 2. 选型卡一：RuleSpec vs 直接 Prompt

### 业务问题

自然语言规则省略多、语义可能冲突，同一 Prompt 运行结果也不稳定。

### 必须保证

- 规则含义可确认；
- 历史运行可复现；
- 不支持内容显式拒绝；
- 金额、引用和状态由代码校验。

### 选择

LLM 生成候选 RuleSpec，Pydantic + 领域 Validator 校验，人工确认歧义，冻结 RuleVersion。

### 为什么

把语言理解的不确定性限制在编译阶段，执行阶段只处理类型化业务契约。

### 替代方案

- 直接 Prompt：快，但语义漂移、难回归；
- 自定义 DSL 文本编辑器：更严谨，但用户门槛高；
- 动态规则引擎：扩展强，但两周 MVP 过度设计且安全面大。

### 风险与验证

- 风险：合法 JSON 但语义错误；
- 验证：歧义 Case、未知字段、非法引用、版本不可变、prompt injection。

### 升级条件

规则模板稳定且外部团队需要批量配置时，再设计可视化规则编辑器或受限 DSL。

一句话：

> Prompt 负责理解，RuleSpec 才是可执行和可版本化的业务契约。

---

## 3. 选型卡二：显式 Workflow/FSM vs LangGraph

### 业务问题

Run 有固定生命周期、明确失败语义和发布门禁。

### 约束

- 两周 MVP；
- 需要掌握状态、条件更新和恢复细节；
- 只有少数固定分支；
- 不需要动态拖拽编排。

### 选择

显式状态机 + Python Orchestrator + PostgreSQL 条件更新。

### 为什么

- 核心状态清晰；
- 失败和 Outcome 不被框架隐藏；
- 容易做幂等和恢复；
- 面试能解释底层机制；
- 减少第三方抽象和依赖。

### 替代方案

- LangGraph：有持久状态、图编排生态，但会增加适配和隐藏机制；
- Celery Canvas/DAG：适合任务依赖，不解决 Agent 语义和业务状态；
- 完全 Agent Loop：路径灵活但权限、成本、停止不稳。

### 风险与验证

- 风险：手写状态机遗漏非法转换；
- 验证：状态迁移表、条件更新、重复 Worker、取消和恢复测试。

### 升级条件

分支/人工节点大量增加、多个团队复用流程、可视化与长期持久图成为明确需求时评估框架。

一句话：

> 有限业务流程先用显式 Workflow，Agent 只处理路径未知的局部搜索。

---

## 4. 选型卡三：Simulator + Sandbox vs 单一执行世界

### 业务问题

搜索需要快，确认需要真实。

### 约束

- 组合空间大；
- HTTP/数据库重放昂贵；
- 纯模拟又不能证明实现有问题。

### 选择

Simulator 快速搜索 Candidate，Sandbox 真实 HTTP Replay Confirmed。

### 为什么

分离吞吐和可信度：大部分路径在内存剪枝，只有可疑路径承担真实执行成本。

### 替代方案

- 只用 Simulator：快但自证；
- 全走 Sandbox：真实但慢、状态分支复制困难；
- 直接生产：副作用和合规不可接受。

### 风险与验证

- 风险：Simulator/Sandbox 语义漂移；
- 验证：contract test、每步状态 Diff、divergence 指标、版本绑定。

### 升级条件

外部系统 API 性能允许且场景创建便宜时，可以增加 Sandbox-first 模式；不能取消独立确认层。

一句话：

> Simulator 优化搜索成本，Sandbox 提供真实执行证据，两者职责不能混为一体。

---

## 5. 选型卡四：确定性 Oracle vs LLM Judge

### 业务问题

必须判断退款、积分、优惠和权益是否违规。

### 约束

- 金额和状态有明确公式；
- 发布门禁要求稳定；
- 需要 0 normal Confirmed 误报目标。

### 选择

核心 invariant 使用确定性代码；LLM Judge 只评估报告表达等软质量。

### 为什么

可重复、可单测、可审计、可版本化，适合作为 P0 发布依据。

### 替代方案

- LLM Judge：灵活但不稳定；
- 人工审核：权威但慢，适合歧义和争议；
- 形式化验证：更强，但规则建模成本高。

### 风险与验证

- 风险：Oracle 自身错误和与 Sandbox 共用逻辑；
- 验证：独立实现、正反 Case、变异测试、normal 零误报、OracleVersion。

### 升级条件

开放文本规则无法确定性判断时，可引入“规则评分 + LLM Judge + 人工复核”分层，但不能让软判断自动触发资金类 P0。

一句话：

> 能用代码计算的业务正确性，不交给概率模型裁决。

---

## 6. 选型卡五：BFS + Agent vs 纯 Agent

### 业务问题

需要寻找未知组合，同时证明 Agent 相对传统搜索的价值。

### 约束

- 浅层问题 BFS 擅长；
- 深层组合状态爆炸；
- Agent 成本和随机性高；
- 必须有无模型基线。

### 选择

Random/BFS 作为确定性基线，Agent 在风险启发下搜索高价值分支。

### 为什么

- 简单问题不浪费模型；
- 有可比较基线；
- Agent 的边际贡献可量化；
- BFS 结果可用于调试 Action/Hash。

### 替代方案

- 纯 BFS：覆盖稳定但状态爆炸；
- 纯 Agent：Demo 炫但无法证明必要性；
- 强化学习：需要大量环境交互和训练数据，MVP 不合适。

### 风险与验证

- 风险：Agent 只是使用更多预算；
- 验证：等总预算消融、单位缺陷成本、hidden 发现率。

### 升级条件

积累大量轨迹后，可训练启发式评分或使用学习型搜索，但必须保留确定性 Baseline。

一句话：

> BFS 提供能力下限，Agent 把有限预算集中到更可能出问题的路径。

---

## 7. 选型卡六：隔离策略 vs 自由 Agent Team

### 业务问题

价值流、生命周期和边界条件需要不同搜索偏好。

### 约束

- 三个任务可并行；
- 不需要共同编辑同一产物；
- 需要评估各策略贡献；
- Token 预算有限。

### 选择

Orchestrator-Worker；三个策略 Context/frontier/budget/Trace 隔离，不互相聊天。

### 为什么

- 无冲突仲裁需求；
- 减少重复和上下文污染；
- 贡献可归因；
- 并行执行简单；
- 更符合任务结构。

### 替代方案

- Peer Team：适合需要协商共同产物，但协调复杂；
- 单 Agent 角色切换：成本低但策略容易趋同；
- 顺序 Reviewer：可能改善候选质量，但增加延迟。

### 风险与验证

- 风险：三策略输出高度重复；
- 验证：Candidate overlap、unique confirmed、策略消融和 Token/缺陷。

### 升级条件

只有出现真正共享任务、认领、冲突和仲裁需求时才引入 Agent Team 控制面。

一句话：

> 多 Agent 不是让角色开会，而是用可隔离、可评测的不同搜索偏好扩大覆盖。

---

## 8. 选型卡七：PostgreSQL + Redis/ARQ

### 业务问题

Run 时间较长，需要异步执行、持久状态、队列和恢复。

### 约束

- 公开 Demo 并发不高；
- 需要事务和审计；
- 任务可能重复投递；
- 不需要大规模消息平台。

### 选择

PostgreSQL 保存权威状态；Redis + ARQ 负责队列、限流和短期进度。

### 为什么

- PostgreSQL 已承担领域数据和事务；
- Redis 简单满足 MVP 异步任务；
- 状态与队列职责清晰；
- 部署成本低。

### 替代方案

- Celery/RabbitMQ：生态强，但部署和语义更复杂；
- 只用 FastAPI BackgroundTask：进程重启丢失，缺少队列控制；
- Redis 同时做权威状态：持久和事务不足。

### 风险与验证

- 风险：Redis 丢任务、重复投递；
- 验证：PostgreSQL expected status、任务重投、Worker 重启、队列恢复。

### 升级条件

需要复杂路由、优先级、跨区域或高吞吐任务时评估 RabbitMQ/Kafka/Celery；仍不改变 PostgreSQL 权威状态。

一句话：

> 队列可以丢或重投，业务正确性必须落在可恢复的权威数据库里。

---

## 9. 选型卡八：SSE vs WebSocket

### 业务问题

浏览器需要看到 Run 进度，断线后恢复。

### 约束

- 主要是服务端向客户端单向推送；
- 用户操作通过普通 HTTP；
- 公共 Demo 规模小；
- 权威状态已经在 Run API。

### 选择

SSE 推送进度 + GET Run API 恢复；写操作使用 HTTP。

### 为什么

- 实现简单；
- 浏览器原生重连；
- 适合单向事件；
- 易于代理和调试；
- 不需要维护双向连接状态机。

### 替代方案

- WebSocket：适合高频双向控制，但生命周期复杂；
- 轮询：可靠简单，但实时性和请求成本较差；
- 只用 SSE 状态：错误，因为丢事件后无法恢复权威状态。

### 风险与验证

- 风险：断线丢事件、乱序、连接泄漏；
- 验证：event_id、Last-Event-ID/重连、页面刷新、GET Run 对账。

### 升级条件

真正需要实时双向协作、在线打字或高频控制时再引入 WebSocket。

一句话：

> SSE 负责通知，Run API 负责事实；当前单向进度不需要 WebSocket。

---

## 10. 系统设计场景一：接入一个真实售后退款 Agent

### 需求

Refund Agent 读取用户诉求并调用退款工具，RuleArena 验证它不会重复退款或违反规则。

### 设计

```text
User Request
→ Refund Agent
→ Tool Adapter
→ Commerce Sandbox
→ RuleArena Trace + Oracle
```

新增：

- 用户诉求到 ActionProposal 的评测；
- Agent 是否选择正确退款类型/金额；
- 高风险或歧义是否转人工；
- Tool ACK 后是否检查最终状态；
- Prompt/模型版本回归。

保持：

- Sandbox 和 Oracle 不变；
- Agent 不能访问 Ground Truth；
- 资金 invariant 仍由确定性程序裁决。

不做：直接接真实用户和支付。

---

## 11. 系统设计场景二：接入开源电商系统

### 需求

把内置 Sandbox 换成外部开源系统进行更真实的黑盒验证。

### 方案

定义 TargetAdapter：

```text
create_scenario
execute_action
get_receipt
get_snapshot
get_events
reset/cleanup
capabilities
```

关键问题：

- Action Contract 到目标 API 的映射；
- 目标系统不支持某动作时显式 UNSUPPORTED；
- 测试租户和数据清理；
- 目标版本和配置 Hash；
- 快照规范化；
- 外部 API 最终一致性和限流；
- Oracle 仍保持独立。

升级门槛：内置闭环和评测稳定后再做，不让适配器拖垮 MVP。

---

## 12. 系统设计场景三：支持真正并发攻击

### 需求

探索两个退款、退款和积分兑换同时发生的竞态。

### 新能力

- 并发 ActionGroup；
- barrier 控制多个请求同时到达关键点；
- logical clock 和操作时间线；
- 数据库隔离级别与锁等待 Trace；
- 可重复调度 seed；
- 并发 invariant 和最终状态检查。

### 难点

并发执行非确定性，Replay 3/3 可能不稳定。需要控制调度，而不是简单并发发送 HTTP。

### 边界

MVP 只覆盖重复和顺序动作；没有调度控制时不能声称完整支持分布式竞态。

---

## 13. 系统设计场景四：公开 Demo 突然有 100 个并发 Live Run

### 当前瓶颈

- LLM 限流和成本；
- Worker 并发；
- Sandbox 数据库连接；
- SSE 连接；
- Trace 写放大。

### 先止血

- 限制 Live Run 并发；
- 排队并展示预计等待；
- 默认 Frozen Run；
- 按 IP/Session 配额；
- 达到预算后拒绝新 Run。

### 扩容顺序

1. 观察 queue wait、LLM 429、DB pool；
2. Worker 水平扩容，仍用条件更新和幂等；
3. Sandbox 按 run 分区/池化；
4. SSE 连接与静态资源分离；
5. Trace 异步批量写；
6. 模型路由和缓存只用于安全可复用部分。

不先上 Kubernetes；先确认真实瓶颈和成本模型。

---

## 14. 系统设计场景五：Multi-Agent 比 BFS 更差

### 不能做

- 删掉 BFS 能找到、Agent 找不到的 Case；
- 给 Multi 更多预算却不披露；
- 只展示一次最好结果；
- 用角色对话增加“高级感”。

### 应做

1. 比较 Case 深度和动作类型；
2. 看策略是否趋同；
3. 看 Candidate 重复率；
4. 看 Token 花在解释还是探索；
5. 调整 Context 和动作反馈；
6. 继续保留 BFS 作为主能力；
7. 在简历中写“混合搜索”，不强行强调 Multi-Agent。

这反而体现成熟工程判断。

---

## 15. 系统设计场景六：迁移到游戏权益

### 适用条件

- 有有限动作：购买、消耗、赠送、退款、回滚；
- 有明确状态：货币、道具、活动奖励；
- 有可执行测试服；
- 有不变量：付费资产守恒、奖励不可重复、回滚一致。

### 需要新建

- Game RuleSpec；
- Game Action Contract；
- Scenario 和 Snapshot；
- Game Oracle；
- 对应 Golden Set。

### 可以复用

- Orchestrator；
- Strategy 接口；
- Replay/Minimizer；
- Trace/Evaluation/Gate；
- UI 证据结构。

不能通过把电商字段改名就声称通用，领域状态和不变量必须重建。

---

## 16. 系统设计场景七：Oracle 规则也会变化怎么办

### 方案

- OracleVersion 不可变；
- Finding 绑定 OracleVersion；
- 新版本对历史 Snapshot 进行双跑；
- 比较新增、消失和分类变化；
- 旧 Benchmark 不能用于新 Gate；
- 高风险 invariant 变更需要人工 Review。

如果 Oracle 修复了误报，保留旧 Run 和旧结论历史，不能覆盖审计记录。

---

## 17. 系统设计场景八：LLM 服务不可用

### 降级

- Rule Compiler 可使用已冻结模板；
- Random/BFS 和历史 Counterexample 回归继续运行；
- Live Agent Run 返回明确 `INFRA_FAILED` 或暂不可用；
- Frozen Demo 可浏览；
- 不用伪造 Agent 结果或静默回退到旧回答。

这体现：Agent 能力不可用不应破坏确定性质量底座。

---

## 18. 系统设计场景九：业务方要求自动修复规则

### 风险

- 模型可能修掉一个漏洞但改变业务意图；
- 自动修改 Sandbox 实现会扩大权限；
- 修复和 Oracle 可能互相迎合；
- 发布副作用高。

### 保守方案

- Agent 生成候选 RuleSpec Diff；
- 展示受影响 invariant 和回归 Case；
- 人工确认生成新 RuleVersion；
- 全量 Golden + Counterexample Regression；
- 不自动写业务代码和上线。

只有企业 CI、代码 Review、灰度和回滚成熟后，才考虑自动生成 PR，不自动 merge。

---

## 19. 系统设计场景十：如何证明没有过度设计

回答结构：

1. 业务必须有：类型化规则、可执行环境、裁决和回归；
2. 因长任务和重试需要：PostgreSQL + Redis Worker；
3. 因搜索/确认成本不同需要：Simulator + Sandbox；
4. 因模型不可靠需要：Oracle 和 Eval；
5. 主动删除：K8s、RabbitMQ、RAG、Memory、通用 DAG、动态插件、真实支付；
6. 每个未引入组件都有明确升级条件。

一句话：

> 架构看起来有多个组件，但每个组件都对应一个不可合并的正确性边界；与正确性无关的通用平台能力都被删除了。

---

## 20. 选型卡半开卷关键词

```text
RuleSpec > Prompt：语义冻结
FSM > LangGraph：有限流程显式控制
Simulator + Sandbox：快搜 + 真验
Oracle > LLM Judge：确定性发布依据
BFS + Agent：基线 + 启发
isolated strategies > team chat：可归因低协调
Postgres truth + Redis queue
SSE notify + Run API truth
```

