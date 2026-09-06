# 07｜线上故障发现、止血、定位、恢复与预防

## 1. 通用排障框架

任何故障都按六步回答：

```text
发现
→ 止血
→ 定位
→ 修复/恢复
→ 验证
→ 预防
```

再补两条边界：

- 真实发生过的才能说“线上事故”；
- 本手册中的案例默认是 `上线风险演练`，除非未来仓库和运行记录证明真实发生。

---

## 2. 故障一：退款超时后发生重复退款

### 现象

- 同一订单出现两条退款记录；
- `refunded_amount > paid_amount`；
- 两个 action_id 对应同一业务意图；
- Oracle 触发 INV-01/INV-05。

### 可能原因

- 超时后换新 idempotency_key 重试；
- ToolCallID 被当成业务幂等键；
- Receipt 与退款不在同一事务；
- 数据库没有唯一约束；
- 两个 Worker 同时执行同一 Step。

### 止血

- 暂停相关 Run/退款动作；
- 禁止自动重试；
- 保留订单、Refund、Receipt、Event 和 Trace；
- 公共 Demo 临时关闭 Live Run，Frozen 可继续。

### 定位

1. 按 order_id 和业务参数聚合 Refund；
2. 对比 idempotency_key 和 request_hash；
3. 检查两个事务时间线；
4. 检查 Worker 重投和 Checkpoint；
5. 检查唯一约束与受影响行数；
6. 找到第一次重复效果的入口。

### 修复

- 稳定业务幂等键；
- Receipt、业务写、账本和事件同事务；
- 数据库唯一约束；
- 结果未知时先查询；
- expected status/aggregate version 条件更新。

### 验证

- 相同请求并发/串行 10 次效果仍为 1；
- 提交前和提交后超时故障注入；
- Worker 重启；
- INV-01/05 回归。

### 预防

- duplicate effect、idempotency conflict、ACTION_UNKNOWN 告警；
- P0 Counterexample 加入 PR Gate。

---

## 3. 故障二：Worker 崩溃后 Run 永远卡在 SEARCHING

### 现象

- Run 长时间无进度；
- Worker heartbeat 消失；
- 队列任务已确认但状态未结束；
- SSE 仍保持旧状态。

### 可能原因

- Checkpoint 保存位置错误；
- 没有 lease/heartbeat 超时恢复；
- Run status 只存在内存或 Redis；
- Worker 崩溃在 ToolResult 与 Checkpoint 之间；
- 恢复任务无法重新认领。

### 止血

- 标记 stale worker；
- 停止继续向故障 Worker 分配；
- 不直接把 Run 改成 COMPLETED；
- 从 PostgreSQL 和 Receipt 判断最后进度。

### 定位

1. 查看 AttackRun/StrategyRun 状态和更新时间；
2. 找最后一个持久化 Step；
3. 查询最后写动作 Receipt；
4. 检查 Checkpoint version；
5. 对比 Worker 日志和 queue delivery；
6. 判断可恢复、unknown 或需失败结束。

### 恢复

- 新 Worker 使用 expected status/lease 认领；
- 读取权威 Run 和 Snapshot；
- 校准最后 Step；
- 从 Checkpoint 继续；
- 无法判断的副作用进入 ACTION_UNKNOWN。

### 验证

- 在每个关键中断点 kill Worker；
- 确保重复效果为 0；
- 完成、失败或 unknown 最终都能收敛；
- UI 刷新后显示正确状态。

### 预防

- Worker heartbeat、stale Run 数量、最长状态停留告警；
- chaos test 纳入发布前检查。

---

## 4. 故障三：SSE 断线后 UI 显示运行完成，但后端仍在重放

### 现象

- 页面与 GET `/runs/{id}` 不一致；
- 刷新后状态跳回；
- 进度条 100%，Outcome 为空；
- 某些事件重复或乱序。

### 根因

- 前端把 SSE 当权威状态；
- 丢失/乱序事件没有 event_id；
- 收到 Strategy 完成误判整个 Run 完成；
- 重连后没有重新获取快照。

### 止血

- UI 显示“状态同步中”；
- 禁止根据本地进度触发发布/回归按钮；
- 立即 GET Run API 校准。

### 定位

- 对比 SSE event_id、时间和 Run status version；
- 检查前端 reducer；
- 查看是否混淆 Strategy/AttackRun 事件；
- 检查代理超时和重连。

### 修复

- SSE 只做 notification；
- 首次加载、重连、页面恢复都 GET 权威状态；
- 事件带单调序号或版本；
- UI 对旧版本事件丢弃；
- Outcome 只来自 Run API。

### 验证

- 中断网络、丢事件、乱序、重复、刷新；
- 最终 UI 与 PostgreSQL 一致。

### 预防

- frontend/backend state mismatch 指标；
- E2E 包含断线与刷新。

---

## 5. 故障四：Redis 不可用导致任务丢失或重复

### 现象

- 新 Run 长时间 READY；
- queue depth 异常；
- 同一 Run 被多个 Worker 执行；
- Redis 恢复后任务集中重投。

### 止血

- 暂停接受 Live Run 或限制创建；
- Frozen Demo 继续；
- 不手工把 Run 标记完成；
- 检查 PostgreSQL 中 READY/SEARCHING 与 Worker lease。

### 定位

- Redis 连接和内存/eviction；
- enqueue 返回与 Run 创建事务关系；
- 重试和重复投递记录；
- Worker expected status 是否生效；
- 是否把 Redis 进度当权威。

### 恢复

- Redis 恢复后扫描 PostgreSQL 中可调度 Run；
- 幂等重新 enqueue；
- Worker 条件认领；
- 已有 Checkpoint 继续。

### 设计优化

MVP 可用“数据库 Run 记录 + 可重建队列”。如果创建 Run 与 enqueue 之间经常出现空窗，可引入 transactional outbox/dispatcher，但不必一开始上复杂 MQ。

### 告警

- queue wait P95；
- READY 超时数量；
- enqueue failure；
- duplicate lease conflict。

---

## 6. 故障五：Simulator 与 Sandbox 发生语义漂移

### 现象

- Candidate 确认率突然下降；
- 大量路径在某一步 Replay 失败；
- 相同动作前后状态字段不同；
- 某新 Sandbox 版本后出现。

### 止血

- 不把 Candidate 升级为 Confirmed；
- 暂停使用受影响 Simulator 结果做发布结论；
- 保留 divergence Trace。

### 定位

1. 按版本比较 Candidate 确认率；
2. 找每条路径第一个不同 Step；
3. 对比 Action Contract；
4. 检查 RuleVersion 解析；
5. 检查 Decimal、券恢复、积分比例和状态枚举；
6. 判断参考模型错还是实现偏离。

### 修复

- 只修错误一侧；
- 增加共享契约但不共享转换逻辑；
- 为 divergence 建回归；
- 更新 Simulator/SandboxVersion；
- 旧 Benchmark 失效。

### 预防

- 每个动作的 contract test；
- 正常路径状态 Diff；
- Candidate confirmation rate 和 divergence step 分布监控。

---

## 7. 故障六：Oracle 新版本导致正常 Case 大量误报

### 现象

- normal confirmed 误报从 0 升高；
- 同一 Sandbox Run 在新旧 Oracle 结论不同；
- Release Gate 阻断。

### 止血

- 保持 Gate 阻断；
- 不回退/删除原始 Run；
- 暂停公开“Confirmed”新结论；
- 双跑新旧 Oracle。

### 定位

- 对比 OracleVersion diff；
- 检查单位、符号和 Decimal；
- 是否把合法优惠恢复当重复价值；
- 是否使用最终状态而忽略 RuleVersion；
- Snapshot Schema 是否变化；
- normal Case Ground Truth 是否错误。

### 修复

- 修正 invariant 或 Snapshot 映射；
- 新增正常边界 Case；
- 保留旧 Oracle 结果历史；
- 新版本重新跑全部 Benchmark。

### 预防

- Oracle 变异测试；
- 新旧版本差异报告；
- 核心 invariant 变更人工 Review。

---

## 8. 故障七：Ground Truth 泄漏导致 hidden 发现率异常高

### 现象

- hidden 从普通水平突然接近 100%；
- Agent reason 出现 expected invariant/path 词语；
- Prompt/Trace 含 profile 或 ground_truth_ref；
- Multi-strategy 提升异常且成本未变。

### 严重性

P0。所有受影响 Benchmark 和宣传指标失效。

### 止血

- 立即停用 Release Gate；
- 下线受影响公开指标；
- 冻结相关版本和日志；
- 不先清理证据。

### 定位数据流

```text
Case storage
→ Loader
→ Evaluation Runner
→ Runtime input
→ Prompt
→ Tool Result
→ Trace/Error
→ API/SSE/UI
```

逐层搜索 expected path、invariant、profile 和 canary marker。

### 修复

- 分离数据模型和权限；
- Runtime 使用不含 ground truth 的 Case view；
- hidden 只在最终裁决加载；
- Trace/API 字段白名单；
- 加入 canary 泄漏测试；
- 重新版本化 Case 并全量重跑。

### 预防

- 代码静态扫描 + 运行时 canary；
- hidden loader 独立角色；
- Case 修改审计；
- 评测异常提升先做泄漏排查。

---

## 9. 故障八：Release Gate 错误复用旧 Benchmark

### 现象

- Prompt/Sandbox/Oracle 已变更，Gate 仍显示通过；
- README 指标来自旧日期；
- 当前版本没有完整原始 Run。

### 根因

- Gate 只按“latest”取结果；
- 版本元组不完整；
- model_config_hash 或 budget 未绑定；
- 前端缓存旧汇总。

### 止血

- 阻断发布；
- 所有指标标记 STALE/NOT VERIFIED；
- 不用旧最好结果临时顶替。

### 定位

- 对比当前完整版本元组；
- 查询 BenchmarkRun 的每个字段；
- 检查 Gate SQL/逻辑；
- 检查前端 cache 和 API。

### 修复

- 完整 tuple 精确匹配；
- 任一字段变化生成新 BenchmarkRun；
- Gate 只接受 complete + verified；
- UI 展示版本和时间；
- 修改字段的负向测试。

### 预防

- build/deploy 中强制 Gate；
- Claim → BenchmarkRun 映射；
- stale benchmark 告警。

---

## 10. 故障九：LLM 429/延迟导致 Run 大量超时

### 现象

- model_call latency P95 上升；
- 429 增加；
- queue wait 增加；
- Run 接近 90 秒预算；
- INFRA_FAILED 上升。

### 止血

- 限制 Live Run；
- 降低 Worker 模型并发；
- Frozen Demo 兜底；
- 429 使用 Retry-After 和有界退避；
- 不把基础设施失败计为未发现。

### 定位

- 模型 Provider、区域和配额；
- token/run 是否异常；
- Prompt 膨胀或重复 Context；
- 三策略是否同时峰值；
- 重试风暴。

### 修复

- Context 压缩和字段白名单；
- 全局并发/速率限制；
- 分策略错峰；
- 可配置模型路由；
- 超预算及时停止。

### 预防

- model 429、P95、token/run、retry storm 告警；
- 成本熔断。

---

## 11. 故障十：公开 Demo 被恶意消耗成本

### 攻击

- 大量创建 Live Run；
- 超长规则输入；
- 保持大量 SSE；
- 重复 replay/minimize；
- 尝试访问内部 Sandbox。

### 防线

- IP + Session 限流；
- 请求大小和 RuleSpec 字段上限；
- 每日/每会话配额；
- 并发队列上限；
- Token/步骤/时间硬预算；
- 冻结案例优先；
- Sandbox 私网和内部令牌；
- 管理/评测 API 不公开。

### 处置

- 自动拒绝而不是排队无限增长；
- 关闭 Live Run 不影响 Frozen Demo；
- 轮换可能泄漏的内部令牌；
- 保留安全日志但脱敏。

---

## 12. 排障时的数据优先级

```text
PostgreSQL 权威状态/账本
→ ActionReceipt
→ BusinessEvent
→ Replay Snapshot
→ Structured Trace
→ Service Log
→ Agent 文本
→ 前端显示
```

越靠前越接近事实。Agent 文本和前端展示只能提供线索，不能反向覆盖权威状态。

---

## 13. 线上告警建议

以下是建议监控项，不代表已有生产数据：

- Run success/infra_failed/cancelled/outcome 分布；
- queue wait P50/P95；
- Run duration P50/P95；
- LLM 429、timeout、tokens/run、cost/run；
- Sandbox action error/unknown；
- duplicate/idempotency conflict；
- Simulator/Sandbox divergence；
- normal Confirmed false positive；
- Replay stability；
- stale Run/Worker heartbeat；
- SSE active connections/reconnect；
- Ground Truth canary leak；
- Gate stale/mismatch。

告警要指向 Run ID、版本元组和下一步 Runbook，不能只有“系统异常”。

---

## 14. 面试回答模板

> 如果线上出现【现象】，我不会先猜是模型问题。我会先根据影响止血，例如暂停 Live Run 或阻断 Release Gate，同时保留原始 Run。然后从 PostgreSQL 权威状态、Receipt、Event、Replay 和 Trace 找到第一个不一致点，区分业务错误、Runtime 恢复、模型基础设施还是评测口径。修复后不仅验证当前 Case，还会把最小复现加入回归，并补对应监控和版本门禁。对于本项目没有真实发生过的事故，我会明确说这是上线风险演练和预案。

半开卷关键词：

```text
发现 / 止血 / 保证证据
权威状态优先
first divergence
修复正确层
最小回归
监控与门禁
演练不冒充事故
```

