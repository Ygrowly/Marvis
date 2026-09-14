# 08｜Mock 容量、性能、成本与事实审计

## 1. 使用边界

本篇数字全部是：

> **Mock 压测口径 / 容量估算建议值，不是长期生产监控结论。**

用途：

- 建立内部一致的系统规模感；
- 回答面试官“并发、延迟、成本和容量”追问；
- 指导后续真实压测和告警配置；
- 避免随口给出互相矛盾的数字。

项目完成后，应以实际 Benchmark、Railway 运行和压测结果替换对应估算。

---

## 2. 建议部署基线

### Mock 配置

| 服务 | 建议起步配置 | 职责 |
| --- | --- | --- |
| Web/Control API | 1 vCPU / 1 GB，1 实例 | API、静态前端、SSE |
| Attack Worker | 1 vCPU / 1 GB，1 实例 | BFS、三策略、Replay、Minimize |
| Commerce Sandbox | 1 vCPU / 1 GB，1 实例 | 业务 HTTP API 和事务 |
| PostgreSQL | 小型托管实例 | control + sandbox 权威数据 |
| Redis | 256～512 MB | ARQ 队列、限流、短期进度 |

设计取向：个人在线 Demo，先保证闭环、恢复和成本上限，不追求大规模高可用。

### 公开 Demo 使用假设

建议记忆值：

```text
日访问：约 50 人
日 Live Run：约 10 次
Frozen Run 浏览：50～200 次/日
同时 Live Run：默认 2
公开排队上限：10
单 Run 硬超时：90 秒
```

合理范围：

- 日访问 20～200；
- Live Run 5～30/日；
- 并发 1～3。

这不是用户增长预测，只是部署和成本保护的保守口径。

---

## 3. 单次 Live Run 工作量估算

### 建议记忆值

```text
策略数：3
平均每策略模型调用：5 次
总模型调用：约 15 次
模拟动作：30～80 步
候选路径：1～3 条
真实 API Replay：8～20 个动作
Oracle 检查：每步轻量检查 + 最终完整检查
```

### Token

假设每次模型调用：

- 输入 1,000～2,000 tokens；
- 输出 150～300 tokens。

则单 Run：

```text
输入：15,000～30,000 tokens
输出：2,250～4,500 tokens
总量：约 20,000～35,000 tokens
建议记忆值：约 25,000 tokens/run
```

预算告警建议：

- soft limit：40,000 tokens/run；
- hard limit：50,000 tokens/run。

超过上限应停止并返回 `NO_VIOLATION_WITHIN_BUDGET` 或明确的预算结果，不自动扩容。

---

## 4. 延迟口径

### 组件级 Mock 目标

| 操作 | P50 | P95 | 说明 |
| --- | ---: | ---: | --- |
| Control 普通 GET | 80 ms | 300 ms | 不含模型 |
| 创建 Run | 100 ms | 400 ms | 写 DB + enqueue |
| Sandbox 单动作 | 60 ms | 200 ms | 本地/同区域私网 |
| Snapshot | 100 ms | 300 ms | 聚合规范化状态 |
| 8 步确定性 Replay | 0.8 s | 3 s | 不含模型 |
| BFS 开发 Case | 0.2 s | 2 s | 受状态空间影响 |
| 单次 Live Attack | 35～50 s | 80～90 s | 主要受 LLM 影响 |

Live Run 建议记忆值：

```text
P50 ≈ 45 秒
P95 ≈ 80 秒
硬超时 = 90 秒
```

内部推导：约 15 次模型调用，三个策略部分并行；单次模型调用 2～5 秒，加上调度、Simulator 和 Replay，得到 35～80 秒是合理范围。

---

## 5. 吞吐和容量

Worker 同时运行 2 个 Live Run，若平均 60 秒：

```text
理论上限 ≈ 2 run/min ≈ 120 run/hour
```

但考虑：

- 模型 Provider 限流；
- Token 成本；
- P95 延迟；
- Sandbox/DB；
- Minimize 和多次 Replay；
- 公共安全预算。

不应按理论值开放。建议安全运营容量：

```text
20～40 Live Run/hour
公开默认上限 10～30 Live Run/day
```

为什么日上限远小于技术吞吐：个人 Demo 的主要限制是模型成本与滥用风险，不是 CPU。

### 扩容条件

满足任一项再考虑加 Worker：

- queue wait P95 连续超过 3 分钟；
- queue depth >10 持续 5 分钟；
- LLM 429 <2%，DB/Sandbox 健康，确认瓶颈在 Worker；
- Live Run 有稳定真实需求且成本预算允许。

---

## 6. Benchmark 成本估算

> **2026-09-14 口径更新**：算式按当前 golden-v4 的实际运行形态重算（dev 跑四基线、hidden 只跑 Multi 且重复 3 次），不再按「全矩阵」估算——旧版按 24 Case 算出的 288 / 144 已作废。

实际运行矩阵：

```text
development 21 Case × 4 Baseline × 1 次 =  84 个 baseline-case runs
hidden      17 Case × 1 Baseline × 3 次 =  51 个 baseline-case runs
                                      总计 135 个 baseline-case runs
```

其中 Random/BFS 不调用 LLM；Single/Multi 调用 LLM：

```text
development：21 × 2 × 1 =  42 个 LLM runs
hidden     ：17 × 1 × 3 =  51 个 LLM runs
                    总计 93 个 LLM runs
```

按平均 25,000 tokens/run：

```text
总 Token ≈ 2,325,000
合理范围：1.8M～3.5M tokens
```

时间估算：

- 单 Run 45～80 秒；
- 并发 3；
- 93 个 LLM runs 理论约 24～42 分钟；
- 加上队列、Replay、限流和失败重试，建议口径 30～60 分钟。

> **为什么 hidden 只跑 Multi**：hidden 的用途是**最终裁决**而不是横向对比，重复 3 次是为了把 `pass@k` 与 `pass^k` 分开（这一步正是本项目最有价值的实测发现）。**扩到四基线的代价 = hidden 17 × 4 × 3 = 204 个 baseline-case runs，其中 102 个是 LLM run**，按上面的口径约翻一倍——是否值得，取决于下一轮要回答的问题。

### 成本公式

不固定绑定某家模型价格：

```text
cost = input_tokens × input_price
     + output_tokens × output_price
     + optional tool/provider cost
```

为了容量估算，可假设综合每百万 Token 1～5 美元，则 2.3M tokens：

```text
约 2.3～11.5 美元/完整 golden-v4 口径 Benchmark
```

这只是示意区间。真实面试应说：具体成本由实际模型计价、输入/输出比例和缓存命中决定，项目会从原始 LLMCall 统计。

### 控制策略

- PR 只跑无真实 LLM 的确定性子集；
- 完整 Benchmark 按需或发布前运行；
- 失败 Case 定向复测；
- Prompt/模型没有变化时不重复花费；
- Frozen Demo 不产生模型成本。

---

## 7. 存储估算

单 Run 结构化数据：

```text
Run/Strategy/Step 元数据：20～50 KB
Action/Receipt/Event/Snapshot：50～150 KB
Trace 与指标：50～150 KB
总计：约 100～300 KB/run
建议记忆值：200 KB/run
```

则：

```text
1,000 runs ≈ 200 MB 原始数据
加索引、JSONB 膨胀和临时数据：约 400～600 MB
10,000 runs：约 4～6 GB
```

保留策略：

- Counterexample、Benchmark 和 P0 Trace 长期保留；
- 普通公开 Live Run 原始细粒度 Trace 保留 30 天；
- 聚合指标长期保留；
- LLM 原始回复默认只保存受控摘要/Hash；
- 定期清理无价值 Snapshot，不清理审计证据。

---

## 8. 质量指标建议

| 指标 | MVP 目标/估算 | 类型 |
| --- | ---: | --- |
| Golden Set | 21 + 17 双评测集 | TARGET（**已建成**，E1）；**发现率实测 8/14，未达 75% 门槛** |
| normal Confirmed 误报 | 0 | TARGET/GATE（**实测 dev 0/7、hidden 0/3**） |
| Confirmed Replay | 3/3 | TARGET/GATE（**实测稳定重放 42/42**） |
| hidden 漏洞发现率 | ≥75% | TARGET/GATE |
| 历史 P0 回归 | 100% | TARGET/GATE |
| Ground Truth 泄漏 | 0 | TARGET/GATE |
| RuleSpec Schema 通过率 | 90%～98% | ESTIMATE |
| Candidate 确认率 | 30%～60% | ESTIMATE |
| Simulator/Sandbox divergence | <10% 目标 | ESTIMATE |
| Run INFRA_FAILED | <5% | ESTIMATE/ALERT |
| Action UNKNOWN | 理想 0，出现即调查 | TARGET/ALERT |

Candidate 确认率不是越高越好到 100%。Agent 搜索未知路径允许一定探索噪声，但确认层必须高精度。

---

## 9. 告警阈值建议

| 告警 | 建议阈值 | 处理 |
| --- | --- | --- |
| queue depth | >10 持续 5 min | 限流/检查 Worker 和 Provider |
| queue wait P95 | >180 s | 暂停新 Live Run或扩 Worker |
| Run duration P95 | >90 s | 检查模型延迟/Prompt/预算 |
| LLM 429 | >5% / 15 min | 降并发、按 Retry-After 退避 |
| INFRA_FAILED | >5% / 15 min | 区分 Provider/DB/Sandbox |
| tokens/run | >40k soft；>50k hard | 压缩 Context/停止 |
| Sandbox action P95 | >500 ms | 检查 DB 锁、连接池和事务 |
| ACTION_UNKNOWN | 任意出现 | P1/P0 调查副作用 |
| normal Confirmed | 任意出现 | P0 阻断 Gate |
| Ground Truth canary | 任意出现 | P0 停止评测 |
| stale Run | >180 s 无更新 | 检查 Worker/Checkpoint |
| SSE active | >100/实例 | 限制连接和检查泄漏 |

这些阈值应在真实压测后调整，不能作为长期 SLA 承诺。

---

## 10. 系统容量上限怎样表达

建议口径：

> 当前是个人公开 Demo，按单 Worker 同时 2 个 Live Run、单 Run P95 80～90 秒设计。CPU 理论吞吐高于实际开放量，真正瓶颈是模型并发和成本，所以默认只开放 10～30 次 Live Run/日，其他用户查看 Frozen Run。若 queue wait P95 超过 3 分钟，而模型限流和数据库仍健康，再水平扩 Worker。这个口径是容量估算，后续会通过 k6/Locust、模型调用 Trace 和 Railway 指标正式校准。

---

## 11. 压测方案

### 控制 API

- 场景：GET Run、创建 Run、查询 Counterexample；
- 负载：1→10→50 并发；
- 观察：P50/P95、错误率、DB pool、CPU/内存；
- 写请求使用唯一 Idempotency-Key，避免污染数据。

### Sandbox

- 场景：8 步黄金 Replay；
- 负载：1、5、10 并发独立 run_id；
- 观察：事务延迟、锁等待、连接池和数据隔离；
- 增加相同 key 重复测试，不做大流量资金类破坏。

### Worker

- 使用 Stub LLM 分离本地 Runtime 性能；
- 再用真实模型小规模测 Provider 延迟；
- 观察 queue wait、tokens/run、Checkpoint 和恢复。

### SSE

- 建立 10、50、100 长连接；
- 模拟断线重连和慢客户端；
- 检查内存、连接释放和事件恢复。

压测报告必须注明环境、数据、版本和是否使用真实模型。

---

## 12. 事实审计表

| 对外 Claim | 需要的最低证据 |
| --- | --- |
| “实现三策略 Agent” | 代码、隔离测试和实际 Trace |
| “真实 API 重放” | Sandbox HTTP 日志/Receipt/E2E |
| “重放 3/3” | 同版本 ReplayRun IDs（golden-v4 实测 42/42） |
| “hidden ≥75%” | 当前完整 BenchmarkRun 和 Case 分母（**实测 8/14 = 57%，未达标**） |
| “0 正常误报” | normal Case 原始 Run 与重算 |
| “Token 降低 X%” | 同 Case/模型/预算前后实际数据 |
| “在线部署” | URL、版本和 smoke test |
| “真实用户使用” | 用户、访问和使用记录；Demo 浏览不能自动算 |
| “生产事故” | 真实事故记录；风险演练不能冒充 |
| “支持高并发” | 明确配置和压测结果，不用理论推导替代 |

---

## 13. 安全面试表达

### 容量

> 项目当时没有接入完整的长期生产 APM，这组数字不是生产 SLA，而是根据单 Run 的模型调用数、并发配置和小规模回放形成的容量估算。当前建议口径是 P50 约 45 秒、P95 约 80 秒、单 Worker 同时 2 个 Live Run；如果继续上线运行，我会通过 API 压测、模型 Trace、队列等待和数据库指标正式校准。

### Benchmark

> **2026-09-14 更新**：BenchmarkRun **已跑完**（golden-v4 / deepseek-v4.1-flash）。结果已按实测写进 README、简历与账本：dev 集 Multi 5/14 高于 BFS 2/14，hidden 重复三次 `pass@3 = 8/14` 而 `pass^3 = 1/14`；机制层误报 0 / 泄漏 0 / 稳定重放 42/42；门禁如实拒绝放行。**hidden 发现率 ≥75% 仍是 TARGET**（实测 57% 未达标）。

### 成本

> 单 Run 估算约 2～3.5 万 Token，完整三次重复的模型评测约 250 万到 500 万 Token。具体费用取决于模型输入输出价格，系统会记录每个 LLMCall 的 Token 和 cost，不用一个固定价格冒充长期事实。

### 真实业务

> 被验证的是实际电商规则和完整工程机制，但目标系统是独立测试业务服务，不是企业生产流量。这个边界让我能得到可控 Ground Truth，同时安全演练幂等、恢复和发布门禁。

---

## 14. 一分钟数字口径

```text
公开 Demo：约 50 访问/日，10 Live Run/日，2 并发
单 Run：15 次模型调用，20k～35k tokens
延迟：P50 45s，P95 80s，hard timeout 90s
真实 Replay：8～20 API actions，P95 3s 内
存储：约 200KB/run，1000 runs 含索引约 0.5GB
完整评测：dev 21 × 4 baselines × 1 + hidden 17 × 1 × 3
LLM runs 93，约 1.8M～3.5M tokens，30～60min
全部是 Mock 容量估算，最终以实际 Run 替换
```

