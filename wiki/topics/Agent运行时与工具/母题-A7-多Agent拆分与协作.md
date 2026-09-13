---
type: topic
topic: Agent运行时与工具
created: 2026-09-12
updated: 2026-09-13
status: candidate
human_reviewed: false
level: A
---

# 母题 A7 · 多 Agent 拆分与协作

> **模块**：Agent 运行时与工具 / 复杂度
> **所属主线**：三 · 风险与复杂度怎么管（边界）
> **层级**：A · 教材级（"多 Agent 有效是因为多了 token 和并行度"有实测支撑（80% 方差）；成本与收益都能算）
> **关联母题**：[[母题-A5-上下文压缩与记忆]]（子 agent 只回传 1–2K 就是压缩）· [[母题-C1-上下文组装与窗口预算]]（隔离 = 四种手段之一）· [[母题-A1-计划执行循环与停止条件]]（effort 分档 = 预算思维）· [[母题-G5-RAG评测与幻觉率]]（多 Agent 的评测更麻烦：不能只测单个 agent）
> **素材来源**：**Anthropic《How we built our multi-agent research system》**（2026-09-12 联网核实：**90.2% 提升、token 用量解释 80% 方差、三因素合计 95%、15× token、effort 分档、并行降 90% 时间、"大多数编码任务的可并行部分比研究少"、同步执行的瓶颈**）+ **Anthropic《Effective context engineering for AI agents》**（2025-09-29——**"子 agent 探索用几万 token、只回传 1,000–2,000 token 浓缩结论"这句出自这篇，不在多 agent 那篇里**）+ `study/06-Workflow-多Agent与长任务.md`。**三组算式为本次新增（待你核对）**

**导读**：必懂 3 件事（① 它有效的原因不是"更聪明" ② effort 必须分档 ③ 有些任务天生不适合拆）· 读完约 12 分钟 · 需要先懂：[[母题-A5-上下文压缩与记忆]]

**题目**：面试官问——"什么时候该用多 Agent？你们为什么用它 / 为什么不用它？"

**母题**：**一个 Agent 不够用的时候，加一个 Agent 就能解决吗——"多 Agent"到底买到了什么，又付出了什么？**

**为什么重要**：这道题**最容易答成口号**（"多 Agent 更强大"）或者**过度否定**（"多 Agent 就是噱头"）。**正确答案在中间且可量化**：Anthropic 的实测是**多 Agent 比单 Agent 高 90.2%**，但**token 消耗是普通对话的 15 倍**——**所以它是一个"用钱买性能"的架构决策**，而判据是**"任务价值够不够高 + 能不能并行拆开"**。

---

## 一、教材

### 1. 前提：它有效的原因，不是"多个模型更聪明"

【事实】Anthropic 的实测结论（**这句是这道题的题眼**）：

> **"Multi-agent systems work mainly because they help spend enough tokens to solve the problem."**

而且他们做了归因分析（BrowseComp 评测）：

```text
三个因素解释了 95% 的性能方差：
  · token 用量【单独】就解释了 80%
  · 工具调用次数
  · 模型选择
```

【推论】**这说明"多 Agent"买的其实是两样东西**：

```text
① 更多的 token 预算    （每个子 agent 有自己的上下文窗口）
② 并行度              （它们同时干活）
```

【推论】**而不是"多个模型投票更准"**——**理解这一点很重要，因为它直接决定了"什么时候不值得"**：**如果你的任务无法通过"多花 token"来变好，那多 Agent 就没用。**

【事实】**效果有多好**：

> **"…a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."**

【事实】**原文举的那个例子**：让它找出"标普 500 信息技术板块所有公司的董事会成员"——**多 Agent 通过把任务分解给子 agent 找到了正确答案，而单 Agent 用"缓慢的串行搜索"失败了**。

::figure multi-agent-when.svg | 多 Agent：什么时候值得，以及 effort 该怎么分档 | orchestrator-worker 结构；effort 三档；底部是 1× / 4× / 15× 的 token 代价

**到这里你应该能回答**：为什么"多 Agent 更强大"是一个不准确的说法？

---

### 2. 代价：15 倍 token【推导】

【事实】原文给的实测对比：

```text
普通对话             = 1×
单 agent             ≈ 4×
多 agent 系统        ≈ 15×
```

【推导】**把它换算成钱**（Opus 5，输入 $5/MTok）：

```text
假设一次对话的上下文规模是 10K token：
  普通对话   ≈ 10K       → $0.05
  单 agent   ≈ 40K       → $0.20
  多 agent   ≈ 150K      → $0.75

相对普通对话：15 倍
```

【事实】**原文对经济性的判断很直接**：

> **"For economic viability, multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance."**

【推论】**所以多 Agent 的判据不是技术先进性，是"任务价值 / 成本"的比值**——**一次研究型任务值 100 块，花 15 倍 token 换 90% 的质量提升，划算；一次简单的格式转换，同样 15 倍就是纯浪费。**

【取舍】**这也是"effort 分档"必须存在的原因**（下一节）。

**到这里你应该能回答**：为什么"我们上了多 Agent"这句话，必须先说清楚"任务价值有多高"？

---

### 3. effort 必须分档【事实】

【事实】原文给的失败模式与对应的分档规则：

```text
早期错误：为简单查询派出 50 个子 agent、无止境地找不存在的来源、
        互相用过多更新互相干扰

分档规则（写进 prompt）：
  简单事实查找  → 1 个 agent，3–10 次工具调用
  直接对比      → 2–4 个子 agent，各 10–15 次调用
  复杂研究      → >10 个子 agent，职责明确分开
```

【推导】**不分档有多浪费**：

```text
一个"简单事实查找"实际需要：1 个 agent × 约 5 次调用
若统一按"复杂研究"配置跑：10 个子 agent × 各 12 次调用 = 120 次调用

浪费 = 120 / 5 = 24 倍
```

【结论】**分档能避免约 24 倍的浪费**——**而且这还只是调用次数，token 的差距更大**（每个子 agent 有自己的上下文）。

【事实】**原文点出的根因**：

> **"Agents struggle to judge appropriate effort for different tasks, so we embedded scaling rules in the prompts."**

【推论】**注意这句话的措辞**：**"模型不擅长判断该用多大力，所以把规则写进 prompt"**——**这是一个很典型的 Harness 思路：模型判断不了的地方，用显式规则兜住**（[[母题-A1-计划执行循环与停止条件]] 的"复杂度放可测试的边界组件"）。

**到这里你应该能回答**：为什么"该派几个子 agent"这件事不能让模型自由决定？

---

### 4. 并行：两级并行降 90% 时间【推导】

【事实】原文的做法与实测：

```text
两级并行：
  ① lead agent 并行派出 3–5 个子 agent（而不是一个一个来）
  ② 子 agent 内部并行使用 3+ 个工具

实测："These changes cut research time by up to 90% for complex queries"
```

【推导】**账很好算**：

```text
串行：5 个搜索 × 每个 60 秒 = 300 秒
并行：5 个搜索同时跑      = 60 秒

降到 20%（省 80%）

若子 agent 内部再并行 3 个工具：
  单个子 agent 的 3 个串行检索（3 × 20 秒）→ 20 秒
  → 叠加后总降幅接近原文的 90%
```

【结论】**两级并行的收益是乘出来的**（lead 级的并行 × subagent 级的并行）。

【事实】**子 agent 的另一个结构性收益**（原文的表述很准）：

> **"The essence of search is compression… Subagents facilitate compression by operating in parallel with their own context windows… before condensing the most important tokens for the lead research agent."**

【推论】**这句话把"隔离"讲透了**：**子 agent 在自己的干净窗口里可能烧掉几万 token 去探索，但只回传 1,000–2,000 token 的浓缩结论**——**搜索过程的噪声全部留在子 agent 里**（[[母题-C1-上下文组装与窗口预算]] 的 Isolation，[[母题-A5-上下文压缩与记忆]] 的压缩）。

**到这里你应该能回答**：子 agent 省的不是"总 token"，是什么？

---

### 5. 有些任务天生不适合拆【推导】

【事实】原文明确列了不适用的场景：

```text
"…some domains that require all agents to share the same context or involve
 many dependencies between agents are not a good fit for multi-agent systems today.

 For instance, most coding tasks involve fewer truly parallelizable tasks than
 research, and LLM agents are not yet great at coordinating and delegating to
 other agents in real time."
```

【推导】**判据可以收成两条**：

```text
适合多 Agent：
  ① 重并行（子任务之间独立）
  ② 信息量超出单个上下文窗口
  ③ 要对接很多复杂工具

不适合：
  ① 所有 agent 必须共享同一份上下文
  ② 子任务之间依赖很密（A 的结论决定 B 怎么做）
  ③ 需要实时协调与委派
```

【推论】**"重并行"是关键**：**研究任务天然可拆（查 A 公司、查 B 公司、查 C 公司互不影响）；而大多数编码任务不行**（改一个函数会影响调它的所有地方）——**原文明确说"most coding tasks involve fewer truly parallelizable tasks than research"**。

【取舍】**还有一个原文承认的工程限制**：

> **"Currently, our lead agents execute subagents synchronously… this simplifies coordination, but creates bottlenecks… the lead agent can't steer subagents, subagents can't coordinate, and the entire system can be blocked while waiting for a single subagent to finish searching."**

【推论】**同步执行是个真实的瓶颈**——**整个系统会被最慢的那个子 agent 卡住**。**异步能提升并行度，但会带来结果协调、状态一致性和错误传播的新问题**——**这是一次典型的"用复杂度换性能"的取舍。**

**到这里你应该能回答**：为什么"两个 Agent 一起改同一份代码"通常不如一个 Agent 干？

---

### 6. 多 Agent 的评测更难【推导】

【事实】原文的一句话点出了本质困难：

> **"Multi-agent systems have emergent behaviors, which arise without specific programming… small changes to the lead agent can unpredictably change how subagents behave. Success requires understanding interaction patterns, not just individual agent behavior."**

【推导】**这意味着评测的对象变了**：

```text
单 Agent：评"这个 agent 在任务上表现如何"
多 Agent：还要评"它们之间的交互模式"
  → 改 lead 的 prompt 可能不可预测地改变子 agent 的行为
  → 所以"每个 agent 单独都好"不等于"系统整体好"
```

【推论】**因此原文的结论是**：

> **"…the best prompts for these agents are not just strict instructions, but frameworks for collaboration that define the division of labor, problem-solving approaches, and effort budgets."**

【推论】**prompt 从"指令"变成"协作框架"**——**要定义分工、解题方法和预算**。**这是多 Agent 和单 Agent 在工程上最大的差别。**

**到这里你应该能回答**：为什么"每个子 agent 单独测都很好，合起来却不行"是一件可能发生的事？

---

### 7. 边界与常见误解

| 常见说法 | 修正 |
|---|---|
| "多 Agent 更强大，能用就用" | **它有效的原因是"多花了 token + 并行"**（token 用量单独解释 **80%** 的性能方差），**不是"多个模型更聪明"**。而且**代价是 15× token**（普通对话 1×、单 agent 4×）——**只有任务价值足够高才划算** |
| "加一个 Agent 就行" | **要看任务能不能并行拆开**。**研究类天然可拆**（查 A 公司、B 公司互不影响）；**大多数编码任务不行**（改一个函数影响所有调用方）——原文明确说了这一点 |
| "让模型自己决定派几个 agent" | **模型不擅长判断该用多大力**（原文原话），所以要**把分档规则写进 prompt**：简单查找 1 个 / 直接对比 2–4 个 / 复杂研究 >10 个。**不分档会浪费约 24 倍**（简单查询按复杂配置跑） |
| "多 Agent 就是并行跑几个实例" | **并行只是它的一半**。另一半是**上下文隔离**：子 agent 可能烧几万 token 探索，**但只回传 1,000–2,000 token 的结论**——**噪声留在子 agent 里**。这才是"压缩"的本质 |
| "子 agent 越多覆盖越全" | **早期错误就是"为简单查询派 50 个子 agent"**，还有"无止境找不存在的来源""互相用过多更新干扰"。**数量要按复杂度分档，不是越多越好** |
| "多 Agent 一定比单 Agent 快" | **要看任务**。**重并行的任务快得多**（实测降 90% 时间）；**依赖密集的任务反而更慢**——因为**同步执行下，整个系统会被最慢的子 agent 卡住**，而且 lead 不能中途调整子 agent |
| "每个子 agent 都测好就行了" | **不够**。多 Agent 有**涌现行为**：**改 lead 的 prompt 可能不可预测地改变子 agent 的行为**。**所以要评"交互模式"，不只是单个 agent 的表现** |

【取舍】读成一句话：**多 Agent 是一个"用钱买性能"的架构决策——先问"任务价值够不够高"，再问"能不能并行拆开"，两个都 yes 才值得。**

---

## 二、自测

**Q1（计算）**：某系统一次普通对话的上下文规模约 **10K token**。实测数据是：**单 agent ≈ 4×、多 agent ≈ 15×**。模型 Opus 5（输入 $5/MTok）。

问：**三种形态的单次成本各是多少？**这对"该不该上多 Agent"意味着什么？

**A1**：

```text
普通对话：10K  × $5/MTok = $0.05
单 agent：40K  × $5/MTok = $0.20   （4×）
多 agent：150K × $5/MTok = $0.75   （15×）
```

【结论】**多 Agent 是普通对话的 15 倍成本。**

【推论】**它是一个"用钱买性能"的决策**：原文的实测是**质量高 90.2%**，而**token 用量单独就解释了 80% 的性能方差**——**两者是同一件事的两面**。

【判据】**所以要先问任务价值**：

```text
值 100 块的任务：花 15 倍换 90% 质量提升 → 划算
值 1 块的任务：　同样 15 倍 → 纯浪费
```

**关键词是原文那句**："**multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance**"。

**Q2（计算）**：一个"简单事实查找"实际需要 **1 个 agent × 约 5 次工具调用**。

问：**如果统一按"复杂研究"的配置跑**（10 个子 agent，各 12 次调用），**浪费多少倍？**这解释了原文的哪个失败模式？

**A2**：

```text
简单查询按正确配置：1 × 5 = 5 次调用
按复杂配置跑：      10 × 12 = 120 次调用

浪费 = 120 / 5 = 24 倍
```

【结论】**不分档会浪费约 24 倍的调用次数**——而 **token 的差距更大**（每个子 agent 有自己的完整上下文窗口）。

【原文的失败模式】**正是"early agents made errors like spawning 50 subagents for simple queries"**。

【推论】**分档规则要写进 prompt**，因为（原文原话）"**Agents struggle to judge appropriate effort for different tasks**"——**模型判断不了的地方，用显式规则兜住**（[[母题-A1-计划执行循环与停止条件]] 的同一思路）。

**Q3（判读）**：下面两个任务，**哪个适合用多 Agent？为什么？**

```text
任务 A：调研"2026 年国内做 AI Agent 的十家公司"，分别整理它们的产品、融资、团队
任务 B：给一个 5 万行的代码库统一加上日志埋点
```

**A3**：

**任务 A 适合，任务 B 不适合。**

```text
任务 A：
  ✓ 重并行（十家公司互不影响，可以分给多个子 agent）
  ✓ 信息量超出单个上下文窗口（十家 × 各自的资料）
  ✓ 天然可分——查 A 公司的结论不影响查 B 公司

任务 B：
  ✗ 子任务之间依赖很密——加日志点会改动函数签名/调用处，
    改一处影响多处，"哪一行该加"需要全局视野
  ✗ 所有 agent 必须共享同一份上下文（否则各自改出不一致的代码）
```

【结论】**判据是"能不能并行拆开"**，而原文对编码任务有明确判断：**"most coding tasks involve fewer truly parallelizable tasks than research"**。

【补充】**而且同步执行会放大这个问题**：原文承认"**the entire system can be blocked while waiting for a single subagent to finish**"——**依赖密集的任务里，一个子 agent 卡住，整个系统都停**。

**Q4（纠错）**：下面这段话哪里不准确？

> "多 Agent 比单 Agent 强很多，所以我们的系统能拆就拆成多 Agent。"

**A4**：三处问题。

1. **"强很多"有前提**：实测的 90.2% 提升是**在内部研究评测上**——而**研究类任务恰好是"天然可并行"的代表**。**原文明确说了"大多数编码任务的真正可并行部分比研究少"**，所以不能推广。
2. **"强很多"的机制被说错了**：它有效的原因是**"多花了 token + 并行"**（**token 用量单独解释 80% 的性能方差**），**不是"多个模型更聪明"**。**理解这一点才知道什么时候不该用。**
3. **漏了代价**：**多 Agent 是 15× token**（普通对话 1×、单 agent 4×）。**"能拆就拆"会让成本失控**——原文的判据是"**任务价值高到足以支付这个性能提升**"。

【准确说法】"**先用两条判据筛**：**① 任务价值够不够高（付得起 15× token）② 能不能并行拆开（子任务独立性）**。**两条都满足才用多 Agent**；依赖密集的任务（比如大多数编码任务）应该用单 Agent + 好的上下文管理。"

**Q5（纠错）**：下面这段话哪里不准确？

> "我们把任务拆给三个 Agent 并行跑，比一个 Agent 串行快了三倍。"

**A5**：三处问题。

1. **"快了三倍"要看哪一部分**。原文的实测是**复杂查询的研究时间降低最多 90%**——**但那是"两级并行"的结果**：**lead 并行派 3–5 个子 agent** + **子 agent 内部并行用 3+ 个工具**。**只做一级并行拿不到这个降幅。**
2. **同步执行下，整个系统会被最慢的子 agent 卡住**（原文承认的瓶颈）。**所以"三个并行"的实际耗时是 max(三个) 而不是 sum/3**——**如果三个子任务耗时严重不均，收益会远小于 3 倍。**
3. **"拆给三个 Agent"没说清它们的上下文关系**：**如果三者需要共享同一份上下文，那它们会各自维护一份，反而更容易不一致**——原文说这类任务"**not a good fit for multi-agent systems today**"。

【准确说法】"**快多少取决于两件事**：**① 并行的层级（lead 级 + 子 agent 级，两级才有 90% 量级的降幅）② 子任务耗时的均衡度（同步执行下由最慢的那个决定）。** 而**收益的另一半不在速度，在上下文隔离**——**子 agent 只回传 1–2K 的结论，噪声留在它自己的窗口里。**"

---

## 三、面试输出（学完再看）

**一句话结论**：**多 Agent 有效的原因不是"多个模型更聪明"，是"多花了 token + 并行"**——Anthropic 的归因分析显示，**token 用量单独就解释了 80% 的性能方差**（三个因素合计 95%）。效果实测是**比单 Agent 高 90.2%**（Opus 4 做 lead + Sonnet 4 做子 agent，对比单 Opus 4）。**代价是 15× token**（普通对话 1×、单 agent ≈ 4×、多 agent ≈ 15×），所以它的判据是"**任务价值高到足以支付这个性能提升**"。**适用的任务有三类特征**：**重并行、信息量超出单窗口、要对接很多复杂工具**；**不适合的是"所有 agent 必须共享同一份上下文"或"子任务依赖很密"**——**原文明确说大多数编码任务的真正可并行部分比研究少**。**effort 必须分档**（简单查找 1 个 agent/3–10 次调用、直接对比 2–4 个子 agent、复杂研究 >10 个），因为模型判断不了该用多大力，不分档会浪费约 **24 倍**。**并行的收益来自两级**（lead 派 3–5 个子 agent + 子 agent 内部并行 3+ 工具），实测**降 90% 时间**；而另一半收益是**上下文隔离**——子 agent 烧几万 token 探索，**只回传 1,000–2,000 token 的结论**。最后，**多 Agent 的评测更难**：它有**涌现行为**，改 lead 的 prompt 会不可预测地改变子 agent 的行为，**所以要评交互模式，不只是单个 agent**。

**恢复关键词**：**有效原因是"多花 token + 并行"**（token 解释 **80%** 方差）/ 实测高 **90.2%** / 代价 **15×**（对话 1×、单 agent 4×）/ 判据 = **任务价值 + 能否并行拆开** / 适用：重并行 · 超单窗口 · 多复杂工具 / 不适：共享上下文 · 依赖密集（**大多数编码任务**）/ **effort 分档**（1 个 / 2–4 个 / >10 个），不分档浪费 **24 倍** / **两级并行降 90% 时间** / 子 agent 只回传 **1–2K**（噪声留在它自己窗口）/ **同步执行是瓶颈**（被最慢的卡住）/ 涌现行为 → 评交互模式 / prompt 从"指令"变成"协作框架"

**核心不变量 / 主线**：
**多 Agent 买的是"token 预算 + 并行度 + 上下文隔离"，不是"集体智慧"。**
所以判据从来不是"这个任务难不难"，而是"**这个任务值不值得多花 15 倍的钱**"和"**它能不能被并行拆开**"。

**完整回答骨架**：先破"更聪明"（给 80% 方差的归因）→ 效果 90.2% 与代价 15× → **两条判据（价值 + 可并行性）** → 适用/不适用的场景 → **effort 分档**（给 24 倍浪费的算式）→ **两级并行降 90%** + 上下文隔离 → 同步执行的瓶颈 → 涌现行为与评测 → 收束到"用钱买性能"

**追问**（先说后看）

1. **什么时候该拆多 Agent，什么时候不该？** —— **该**：**重并行 + 信息超出单窗口 + 工具复杂**（研究、多源调研）。**不该**：**需要共享同一份上下文**（如大多数编码任务）、**子任务依赖很密**、**需要实时协调**。
2. **多 Agent 的上下文怎么隔离与传递？** —— **子 agent 用独立上下文窗口，只回传结构化的浓缩结论（1–2K token）**；**大产物写外部系统，只传轻量引用**——原文叫"**避免传话游戏（game of telephone）**"。**这本质上是 [[母题-A5-上下文压缩与记忆]] 的压缩，而且是"天然干净"的那种。**
3. **多 Agent 的成本怎么算？** —— **按 token 算**：普通对话 1×、单 agent 4×、多 agent 15×。**再乘上任务量**。**而且要注意"effort 分档"**——不分档会让简单查询也按复杂配置跑（浪费 24 倍）。
4. **为什么不让模型自己决定派几个子 agent？** —— **原文原话是"Agents struggle to judge appropriate effort for different tasks"**。**所以把分档规则写进 prompt**——**这是 Harness 的通用思路：模型判断不了的地方，用显式规则兜住**。
5. **多 Agent 的评测和单 Agent 有什么不同？** —— **它要评"交互模式"而不只是单个 agent**。因为有**涌现行为**：**改 lead 的 prompt 可能不可预测地改变子 agent 的行为**（[[母题-G5-RAG评测与幻觉率]] 的分层归因在这里同样成立，只是层次更多）。

**同类变体**

- 「Workflow 和 Multi-Agent 有什么区别？」——**Workflow 是固定编排**（谁在什么时候调用谁，是写死的）；**Multi-Agent 是模型动态决定派谁**。**前者更可控更便宜，后者更灵活更贵**——**能用 Workflow 解决就别上 Multi-Agent**。
- 「子 agent 失败了怎么办？」——**这是多 Agent 特有的失败模式**：**要么整个 lead 挂掉（同步执行的连锁），要么结果被静默丢弃**。所以要有**子 agent 级的超时、重试与降级**（[[母题-A3-失败恢复与幂等]]），**并且 lead 必须能分辨"子 agent 返回空"和"子 agent 失败了"**。

---

## 四、拼接

**关联母题**：[[母题-A5-上下文压缩与记忆]]（子 agent 只回传 1–2K 就是压缩的极致形态）· [[母题-C1-上下文组装与窗口预算]]（Isolation 是四种手段之一）· [[母题-A1-计划执行循环与停止条件]]（effort 分档 = 预算思维）· [[母题-G5-RAG评测与幻觉率]]（多 Agent 的评测层次更多）

**可迁移场景**：

- **RuleArena**：**显式 FSM 编排（而不是 LangGraph 的自由编排）**——**这正是"能用 Workflow 就别上 Multi-Agent"的判断**；**多角色审查是并行度较高的部分**（各角色独立审），**而合并与确定性验证必须串行**。
- **数驭穹图**：**意图路由**——**先判断意图（RAG / NL2SQL / 直接回答）再走对应链路**，比"把所有工具都给一个 agent"更可靠（[[母题-A2-工具调用与MCP边界]]）。

**本次断点**：【待填 —— 闭卷时具体卡在哪，写成事实不写评价】

**通过证据**：能说出"多 Agent 有效的原因是 token + 并行"并给出 **80% 方差**这个依据；**能算出 1× / 4× / 15× 与三档成本**；**能算出不分档的 24 倍浪费**；能说出适用/不适用各三条并解释为什么编码任务通常不适合；能说清 **effort 三档**的具体数字；能说出两级并行与上下文隔离的关系；能说清"同步执行被最慢的子 agent 卡住"；能说出多 Agent 的评测为什么要看交互模式；**且自测 5 题全对**。
