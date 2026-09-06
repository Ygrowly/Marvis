# 05｜核心难题三：Agent 评测、Trace 与 Ground Truth

## 1. 为什么“跑通 Demo”不够

一个 Agent 在黄金案例上找到漏洞，只能证明：

- 在这个 Case；
- 用这个模型和 Prompt；
- 在这次随机运行中；
- 在这个预算下；
- 它恰好成功了一次。

不能证明：

- 对正常规则不会误报；
- 对隐藏漏洞也有效；
- Multi-Agent 比 BFS 或单 Agent 更好；
- 换 Prompt/模型后没有回退；
- 结果不是因为泄题；
- 单次成功能稳定复现；
- 成本值得。

核心问题：

> **怎样用可重复、无泄漏、预算公平的评测证明 Agent Runtime 的真实边际价值。**

---

## 2. 决策链

### 业务问题

规则、模型、Prompt、搜索策略会持续变化，不能依赖人工观看几个 Demo 决定发布。

### 约束

- LLM 有随机性；
- 测试集规模有限；
- hidden 在开源仓库中难以绝对保密；
- 多策略可能只是使用更多 Token；
- 基础设施失败不能算模型未发现；
- 指标可能被版本漂移和挑样本污染。

### 必须保证

1. Ground Truth 可重放；
2. 开发集和隐藏集隔离；
3. 四种 Baseline 公平可比；
4. 指标从原始 Run 重算；
5. 模型/规则/环境版本完整绑定；
6. 正常误报和成本同样进入门禁；
7. 任何结论能追到 Trace 和证据。

---

## 3. Golden Set 设计

MVP 固定 24 个 Case：

- development 16；
- hidden 8。

必须覆盖：

- 优惠券；
- 退款与积分；
- 会员权益；
- vulnerable 与 fixed/normal；
- 动作顺序；
- 重复/幂等；
- 部分退款；
- 生命周期；
- 价值守恒；
- 无漏洞正常场景。

每个 Case 固定：

```text
case_id
RuleVersion
ScenarioVersion
SandboxVersion/Profile
OracleVersion
budget
visibility
expected_outcome
expected_invariant_ids
ground_truth_ref
构造理由与首次重放证据
```

---

## 4. Ground Truth 怎样建立

不能让 LLM 自己生成答案，再用答案评估自己。

Ground Truth 来源：

1. 明确业务不变量推导；
2. 可解释的 Vulnerable/Fixed 实现差异；
3. 从干净 Sandbox 手工/确定性执行路径；
4. Oracle 产生明确证据；
5. 同版本连续 Replay 3/3；
6. 记录构造理由和版本。

正常 Case 也需要证明：

- 设计的关键合法路径通过；
- 不触发 Confirmed invariant；
- 不是因为动作全部被拒绝或测试没有覆盖到规则。

### Case 进入集合的门槛

- 规则含义明确；
- Sandbox 可执行；
- Oracle 能确定裁决；
- vulnerable/fixed 差异可解释；
- 不是看完模型表现后临时改答案；
- 版本历史可追踪。

---

## 5. Development 与 Hidden 隔离

### Development

- 开发期间可见；
- 用于调试、回归和错误分类；
- Agent Runtime 仍不应读取 expected path，只能正常执行 Case。

### Hidden

- Runtime 无加载路径；
- 只由 Evaluation Runner 在最终裁决时读取；
- expected invariant/path 不进入 Prompt、工具、SSE、Trace、错误栈和公开 API；
- 部署时作为私有配置或数据库权限隔离。

### 开源项目的诚实威胁模型

公共仓库无法保证作者本人不知道 hidden 内容。能保证的是：

- Runtime 代码没有读取接口；
- Prompt 和 Agent 工具无访问能力；
- 执行 Trace 不含预期答案；
- 评测资产与运行权限隔离；
- Case 版本和修改历史公开；
- 不根据模型结果删题或改答案。

这不是竞赛级保密，但足以验证系统数据流没有自动泄题。

---

## 6. 四种 Baseline

### Random

从合法动作中随机选择。作用：证明领域约束和随机探索的最低能力。

### BFS

按深度遍历状态，使用 state_hash 去重。作用：确定性浅层搜索基线。

### Single Agent

一个通用策略，在相同总预算下选择动作。作用：判断角色拆分是否必要。

### Multi-strategy

ValueFlow + Lifecycle + Boundary。作用：判断策略差异是否提升隐藏缺陷发现率或单位成本。

---

## 7. 公平预算

如果 Multi-strategy 拥有三倍 Token 和时间，它发现更多漏洞不一定来自架构优势。

公平比较至少报告两种口径：

### 等总预算

Single Agent 和 Multi-strategy 总共拥有相同：

- Token；
- 模型调用次数；
- 搜索步骤；
- Wall-clock 或计算预算。

用于回答“同样成本谁更好”。

### 等并行时间

允许三个策略并行，报告总 Token 和 wall-clock。

用于回答“如果愿意多花成本，能否更快得到高价值结果”。

必须同时展示：

- 发现率；
- normal 误报；
- Candidate 确认率；
- 时间；
- steps；
- tokens/cost；
- 重复 Candidate 比例。

---

## 8. 核心指标

### RuleSpec Schema 通过率

```text
合法 RuleSpec 数 / 编译尝试数
```

只说明结构和 Validator 接受，不说明业务语义正确。

### 漏洞发现率

```text
至少找到一个正确 Confirmed invariant 的 vulnerable Case 数
/ vulnerable Case 数
```

### 正常确认误报率

```text
产生 Confirmed Violation 的 normal Case 数
/ normal Case 数
```

MVP 目标为 0。普通 Candidate 不算 Confirmed 误报，但应单独统计用户干扰成本。

### Candidate 确认率

```text
confirmed candidates / replayed candidates
```

低说明 Agent 提议很多无法在真实系统复现的噪声。

### 重放稳定率

```text
违反同一 invariant 的成功重放次数 / 重放次数
```

Confirmed 发布要求 3/3。

### 单位确认漏洞成本

```text
总 tokens/cost/时间 / confirmed unique violations
```

如果 confirmed 为 0，返回 N/A，不能除零或填 0。

### 延迟和成本

报告 mean、median、P95，不能只选最好值。

---

## 9. pass@k 与 pass^k

### pass@k

k 次独立运行中至少一次成功的概率。

若单次成功率为 p，独立近似：

```text
pass@k = 1 - (1 - p)^k
```

它衡量能力上限：多试几次能不能找到。

### pass^k

k 次运行全部成功：

```text
pass^k = p^k
```

它衡量稳定性：每次都能不能做到。

### 例子

单次成功率 0.8，k=3：

```text
pass@3 = 1 - 0.2^3 = 0.992
pass^3 = 0.8^3 = 0.512
```

只展示 pass@3 会让系统看起来接近 99.2%，但连续三次都成功只有 51.2%。生产 Agent 需要同时看能力和稳定性。

实际有限样本中优先直接按 Case/Run 的全称和存在聚合计算，不盲目依赖独立分布公式。

---

## 10. 失败状态怎样进入指标

### INFRA_FAILED

模型、数据库、Worker 或 Sandbox 失败。不能算“没有发现漏洞”，应单独统计并阻止不公平比较。

### CANCELLED

用户取消。通常不进入能力分母，但必须披露取消数量和原因。

### NO_VIOLATION_WITHIN_BUDGET

任务正常完成但预算内未发现。对 vulnerable Case 算漏检；对 normal Case 不自动等于正确，需要确认测试确实覆盖了目标路径。

### N/A

分母为 0 或条件不成立。不能用 0% 或 100% 替代。

指标定义必须在代码和文档中固定，不能看完结果后更改分母。

---

## 11. Trace 设计

```text
AttackRun
├── StrategyRun
│   ├── LLMCall
│   ├── ActionProposal
│   └── SimulationStep
├── SandboxReplay
│   ├── HTTPAction
│   ├── Receipt
│   ├── Event
│   └── Snapshot
└── OracleCheck
```

每层至少保存：

- run/strategy/step ID；
- 完整版本元组；
- 模型和 prompt_version；
- 动作和参数摘要；
- before/after state hash；
- latency；
- input/output tokens 和 cost；
- retry_count；
- status/error_type；
- EvidenceRef。

### Trace 不保存

- API 密钥；
- hidden expected path；
- vulnerable profile 提示；
- 完整敏感规则原文；
- 不受控 Chain-of-Thought。

保存结构化 reason 摘要和工具事实即可。

---

## 12. Trace、Log、Metric 和 Audit 的区别

| 类型 | 回答的问题 |
| --- | --- |
| Log | 某个时间发生了什么事件 |
| Metric | 系统整体是否异常、趋势怎样 |
| Trace | 一次 Run 跨组件经历了什么 |
| Audit | 谁在什么版本下做了什么高风险操作 |
| Business Event | 业务状态为什么发生变化 |

RuleArena 的 Finding 应从 UI 一路追到 Replay、Receipt、Event 和 Oracle，而不是只展示模型文字。

---

## 13. 版本绑定与 Release Gate

一个 BenchmarkRun 至少绑定：

```text
benchmark_version
runtime_version
RuleVersion
ScenarioVersion
SandboxVersion
OracleVersion
model_config_hash
prompt_version
baseline
seed
budget
```

Gate 只能使用完全匹配当前版本元组的最新完整 Benchmark。修改任意字段后，旧结果失效。

为什么：

- Oracle 改了，误报口径可能变；
- Sandbox 修了，旧漏洞可能消失；
- Prompt 改了，Agent 稳定性可能变化；
- 预算改了，发现率不可比较；
- RuleVersion 改了，业务含义已经不同。

---

## 14. 发布门禁

目标口径：

- 24 Case；
- normal Confirmed 误报 0；
- Confirmed 反例 Replay 3/3；
- hidden 漏洞发现率 ≥75%；
- 历史 P0 回归 100%；
- Ground Truth 泄漏 0；
- 当前版本完整 Benchmark。

Multi-strategy 未优于 Single/BFS 时：

- 不删除实现；
- 如实报告；
- 降低“多 Agent”宣传；
- 分析是任务不适合、策略不独立、预算浪费还是 Case 太浅；
- 下一版本再验证，不修改答案迎合结果。

---

## 15. Bad Case 回流

Bad Case 不是简单把失败对话加到 Prompt。

流程：

```text
失败 Run
→ 按阶段归因
→ 形成最小复现
→ 决定修复层
→ 加入 development regression
→ 新版本全量回归
```

归因类型：

- Rule Compiler 误解；
- Validator 漏检；
- 动作 Schema 不完整；
- Strategy 搜索失败；
- state_hash 错误；
- Simulator/Sandbox 漂移；
- Oracle 误报/漏报；
- Replay/幂等故障；
- Trace/指标错误；
- 基础设施失败。

修复应落在错误发生的层，不要所有问题都通过扩大 Prompt 解决。

---

## 16. 典型评测事故

### Multi-strategy 发现率更高，但 Token 是三倍

不能直接得出架构更好。补等总预算对照，并报告单位确认漏洞成本和 wall-clock。

### hidden 突然接近 100%

先怀疑泄漏、近重复和 Case 修改，再考虑能力提升。扫描 Prompt、Trace、公开 API、错误栈和 loader 权限。

### normal 误报 1 个

P0 发布阻断。定位 Oracle、规则歧义、Case 标注或 Sandbox 污染，不能从分母删除。

### 新 Prompt 只在最好 seed 提升

报告多 seed、mean/P95、pass@k/pass^k；单次最好结果不能替代稳定性。

### Benchmark 指标无法复算

说明系统只保存汇总，没有原始事实。暂停公开指标，补齐原始 Run 和可重算查询。

---

## 17. 替代方案与代价

### 只做人工评审

可判断报告质量，但慢、主观且难以频繁回归。核心业务正确性应使用确定性 Oracle，人工负责争议和产品表达。

### 只看最终答案

可能答案碰巧正确但路径错误、使用了泄漏信息或不完整数据。Agent 评测必须覆盖轨迹和工具事实。

### 只用 development 集

容易 Prompt/策略对已知 Case 过拟合，无法证明泛化。需要 hidden 和版本历史。

### 使用线上用户反馈

未来有价值，但真实漏洞反馈稀疏、延迟且高风险。MVP 先建立可控 Ground Truth，线上只补充新的 Bad Case 来源。

---

## 18. 验证方法

- 24 Case 数量和分布检查；
- 每个 Ground Truth 3/3；
- hidden loader 权限测试；
- 人为注入 Ground Truth 标记，泄漏测试必须失败；
- 指标从原始 Run 独立重算；
- pass@k/pass^k 手算样例；
- INFRA_FAILED/CANCELLED/N/A 分母测试；
- 修改版本字段，Gate 拒绝旧结果；
- 四 Baseline 等总预算/等并行时间；
- README/简历 Claim 反查 BenchmarkRun。

---

## 19. 高频问题与标答

### Q1：为什么 24 个 Case 足够？

它不是统计意义上的完整行业覆盖，而是两周 MVP 的固定回归基线，用来覆盖三类规则和关键故障类型。需要诚实说明局限，后续根据 Bad Case 扩展。

### Q2：hidden 如何保证不泄漏？

通过存储、loader、权限和数据流隔离，确保 Runtime、Prompt、Trace 和 API 无访问路径。开源作者知道内容无法完全避免，所以同时保留版本历史和不根据结果改题的治理约束。

### Q3：为什么 normal 误报要求 0？

Confirmed 会影响发布决策，正常规则被阻断代价高。普通 Candidate 可以存在，但 Confirmed 必须经过真实 Replay 和确定性 Oracle，因此应该保持高精度。

### Q4：怎样证明 Multi-Agent 有价值？

在相同 Case、模型和总预算下，与 BFS 和 Single Agent 比较 hidden 发现率、normal 误报、确认率、延迟和单位缺陷成本；只多花 Token 获得提升不能视为纯架构优势。

### Q5：为什么指标必须从原始 Run 重算？

前端或汇总表可能有公式错误、筛选和版本漂移。保留原始 Run 才能独立复核分母、失败类型和具体 Case。

### Q6：LLM Judge 在项目里完全没用吗？

不是。它可评估风险解释、报告可读性和修复建议，但不能裁决金额、状态和发布 P0 invariant。

### Q7：pass@k 很高为什么还不够？

它说明多试几次可能成功，不说明每次稳定。生产可靠性还要看 pass^k、误报、成本和失败率。

### Q8：发现率提升但 Candidate 确认率下降怎么办？

说明搜索更激进但噪声增加。需要比较每个 Confirmed 的 Replay/Token 成本，并优化策略或候选预筛，不能只看发现率。

---

## 20. 3 分钟标答

> 我没有用一个黄金 Demo 来证明多 Agent 有效，而是设计了 24 个版本化 Case，其中 16 个 development、8 个 hidden，覆盖优惠、退款积分、会员权益，以及正常、缺陷、幂等、顺序和价值守恒场景。每个 Ground Truth 入集前都要在指定 Sandbox 和 Oracle 版本上重放 3/3。评测比较 Random、BFS、Single Agent 和三个隔离策略，既做等总预算，也报告并行时间，避免 Multi-Agent 只是花了更多 Token。指标包括漏洞发现率、normal Confirmed 误报、Candidate 确认率、重放稳定率、延迟、Token 和单位确认漏洞成本，并同时看 pass@k 和 pass^k。所有指标从原始 AttackRun、Replay 和 OracleResult 重算，分母为零返回 N/A，基础设施失败单独统计。Release Gate 绑定 Rule、Scenario、Sandbox、Oracle、Runtime、模型、Prompt、seed 和预算的完整版本元组，任何版本变化都会让旧结果失效。hidden 数据只由 Evaluation Runner 读取，不能进入 Runtime、Prompt、Trace 或公共 API。如果多策略没有在公平预算下优于 BFS 或单 Agent，我会如实降低 Multi-Agent 的价值主张，而不是修改 Case 制造提升。

关键词：

```text
16 dev + 8 hidden
Ground Truth 3/3
Random/BFS/Single/Multi
equal budget
false positive + confirmation rate + cost
pass@k vs pass^k
raw Run recompute
version tuple Gate
leakage 0
```

