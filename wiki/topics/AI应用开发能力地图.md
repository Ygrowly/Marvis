---
type: topic
created: 2026-09-01
updated: 2026-09-06
status: integrated
human_reviewed: true
aliases: [AI开发, AI应用, 能力台账]
---

# AI 应用开发 + Python 后端能力地图与掌握度台账

> 适用对象：刘宇广｜2027 届｜目标岗位：AI 应用开发 / Agent 后端工程师（Python）  
> 地域：广州、深圳优先，上海其次  
> 调研日期：2026-09-01  
> 文档性质：岗位要求基线 + 学习导航 + 掌握度台账，持续更新，不是一次性学习路线

---

## 0. 结论先行

当前岗位市场真正需要的是下面这条完整能力链，而不是孤立地“会 Prompt、会 LangChain”或“背完后端八股”：

> **理解真实业务 → 设计 AI/确定性程序边界 → 构建 RAG / Agent → 接入 Python 后端和数据系统 → 控制权限与副作用 → 建立评测、观测和失败恢复 → 用可运行项目证明结果。**

对你的最优定位是 **AI 应用工程能力为主、Python 后端能力为底座**，形成 T 型结构：

- 纵向深度：Agent Harness、RAG、Tool/MCP/Skill、评测与可靠性；
- 横向底座：Python、FastAPI、PostgreSQL、Redis、异步任务、测试、Linux、Docker、计算机基础；
- 业务差异化：企业数据、规则系统、权限审计、可解释证据链和真实交付。

优先级判断：

| 级别 | 含义 | 学习策略 |
| --- | --- | --- |
| P0 | 目标岗位和面试的共同门槛 | 必须能独立实现、讲清原理和处理边界 |
| P1 | 明显拉开差距或部分岗位常见 | P0 稳定后补齐，至少有一次实践 |
| P2 | 特定岗位才要求 | JD 命中后再学，不提前占用主线时间 |
| P3 | 当前方向暂不投入 | 只知道边界，不作为秋招前主线 |

最重要的取舍：

- **必须深挖**：Python 工程、后端基本盘、Agent/RAG 全链路、评测、可靠性、权限安全、项目证据、算法与计算机基础。
- **了解并做最小实验**：模型服务、vLLM、Embedding、LoRA、Kubernetes、前端联调。
- **暂不主攻**：从零预训练大模型、分布式训练/CUDA 内核、纯算法论文路线、同时精通 Java/Go、复杂前端工程。

---

## 1. 岗位边界：投什么，不投什么

### 1.1 主投岗位

检索 JD 时优先使用这些名称：

- AI 应用研发工程师
- 大模型应用开发工程师
- AI Agent 研发工程师 / Agent 后端工程师
- Python 后端工程师（AI / Agent 方向）
- LLM Application Engineer / GenAI Software Engineer
- AI 平台软件研发 / Agent 平台研发
- AI Native 工程师
- FDE / AI Solution Engineer（偏研发交付）
- 企业智能化 / AI 业务技术研发

### 1.2 可投但需要核对边界

- AI 应用算法工程师：若核心是 RAG、Agent、评测和业务落地，可以投；若核心是 SFT/RL、训练框架、论文，则降级。
- Agent Infra：若偏上下文、工具运行时、调度、观测和服务工程，可以投；若偏 GPU、分布式训练、推理内核，则不是当前主线。
- AI 全栈：后端占主体、前端只要求能联调时可以投；强前端岗位不优先。
- 普通 Python 后端：业务和成长空间合适时可作为保底，但需要避免岗位过度偏脚本、爬虫或测试。

### 1.3 当前不主投

- 大模型预训练、强化学习、纯 NLP/CV 算法研究岗；
- 要求顶会论文、博士背景、Megatron/DeepSpeed/CUDA 深度经验的岗位；
- 纯数据分析、纯数据仓库、纯爬虫、纯低代码搭建；
- 主要职责是售前、销售或无研发闭环的“AI 解决方案”岗位。

---

## 2. 全网岗位调研口径与共同信号

### 2.1 调研口径

本轮以 2026 年 8 月至 9 月仍可检索的 2027 届校招、实习岗位为主，同时加入少量初级/社招岗位，用于观察生产级要求。来源优先级：

1. 公司官方招聘页；
2. 高校就业网中的企业招聘公告；
3. 牛客、BOSS、智联、猎聘、LinkedIn 等平台的完整 JD；
4. 第三方转载只用于补充，不用于薪资、HC 或市场规模结论。

这些样本不是“全市场统计”，岗位也会下线；其价值是识别反复出现的能力信号。投递前仍应重新核验原 JD。

### 2.2 岗位信号分层

| 信号等级 | 反复出现的要求 | 对你的含义 |
| --- | --- | --- |
| A：几乎所有目标岗 | 主流语言/Python、数据结构与算法、计算机基础、工程质量、真实项目 | AI 岗并没有取消后端和 CS 基础 |
| A：几乎所有 AI 应用岗 | 业务理解、LLM API、Prompt、RAG、Agent、工具调用、业务落地 | 必须能讲完整链路，而不是框架名词 |
| A：高价值共同项 | 评测、失败案例、效果迭代、可观测、稳定性 | 这是从 Demo 到生产系统的分水岭 |
| B：常见 | FastAPI/后端服务、数据库、缓存、异步任务、Linux、Docker、CI/CD | Python 后端是应用落地载体 |
| B：常见 | MCP/Skill、工作流、状态管理、记忆/上下文、多 Agent | 要理解边界和适用条件，不能只会编排 |
| B：常见 | 高可靠、高扩展、权限、安全、成本、延迟 | 需要系统设计和可靠性案例 |
| C：加分与区分度 | GitHub 可运行项目、开源贡献、技术博客、AI Coding 熟练度 | 作品必须可验证，博客服务于证据展示 |
| C：部分岗位 | vLLM/Ollama、向量库、模型部署、LoRA/SFT、K8s | 先建立工程全景，再按 JD 分流 |
| D：算法岗专属 | PyTorch 深度、训练/RL、DeepSpeed、论文 | 不应反向绑架应用开发主线 |

### 2.3 代表性岗位证据

| 公司/来源 | 岗位 | 代表性要求 |
| --- | --- | --- |
| [字节跳动](https://jobs.bytedance.com/campus/m/position/detail/7667098583514024245) | AI Agent 服务端研发 | Agent、RAG、MCP/工具、主流语言、应用全流程 |
| [字节跳动](https://jobs.bytedance.com/campus/position/7452318081927350546/detail) | AI Agent 研发（开发套件） | RAG、Tool Use、上下文、MCP、多 Agent、产品意识 |
| [字节跳动](https://jobs.bytedance.com/campus/m/position/detail/7676057466433521973) | Agent Harness 研发 | 编程基础、Harness、工具执行与系统工程 |
| [字节跳动](https://jobs.bytedance.com/campus/position/7667142530726906117/detail) | AI Agent 开发（抖音研发） | 推理、环境交互、轨迹、工具调用、编程能力 |
| [腾讯校招](https://join.qq.com/post_detail.html?postid=1282707395466077184) | Agent 相关研发 | Python/TypeScript/Go、算法、Planning、Memory 等 Agent 架构 |
| [腾讯](https://careers.tencent.com/jobdesc.html?postId=2056998436447895552) | AI Agent 开发（游戏研发） | Python/C++、代码设计、调试、系统集成 |
| [美团](https://zhaopin.meituan.com/web/position/detail?highlightType=campus&jobUnionId=4697320043) | 大模型应用开发 | Prompt、RAG 管线、Agent 工作流、Python/Java/TypeScript |
| [小米](https://xiaomi.jobs.f.mioffice.cn/toptalent/position/7646709448982972713/detail) | 大模型应用开发 | Python asyncio、Rust/Go、RAG、Agent、IoT 智能体 |
| [阿里巴巴 2027 秋招](https://campus-talent.alibaba.com/campus/position/199907620013) | AI 应用研发 | 业务问题、Agent 落地、RAG、多 Agent、MCP/Skill、项目证据 |
| [阿里云 2027](https://www.nowcoder.com/jobs/detail/439325) | 大模型应用开发 | Prompt、Agent 核心模块、RAG 优化、LLMOps、MCP、高可靠架构 |
| [百度 2027 校招](https://talent.baidu.com/jobs/list?recruitType=GRADUATE) | 后端/智能体研发 | AI 集成、稳定性、故障排查、Planning/Tool/Memory、并发与容错 |
| [小红书岗位抽样与官方链接索引](https://gitee.com/memorin/agent-study/blob/master/research/2026-08-14-agent-internship-jd-sample.md) | Agent/Coding Agent 实习 | Python、代码库 RAG、测试、Eval、Trace、CI/CD、可运行项目 |
| [蔚来](https://nio.jobs.feishu.cn/) | AI 平台软件研发 | Python/Java/Go、数据结构算法、平台工程 |
| [平安银行 2027 深圳](https://www.nowcoder.com/jobs/detail/464035) | AI 应用研发 | CS 基础、LLM 边界、确定性兜底、RAG、多 Agent、MCP/Skill |
| [启云方 2027 深圳](https://myjob.dlmu.edu.cn/campus/view/id/868418) | AI Agent 工程师 | Skill/Tool、状态、异常、权限、日志、结果校验、Python/Linux |
| [江苏国泰华盛 2027](https://www.shushuqiuzhi.com/position/453523) | AI 应用开发 | 业务流程、Python/Java、数据分析、Agent、上线运维和复盘 |
| [TCL 岗位索引](https://www.zhipin.com/zhaopin/466c15ede7339b2c0nV62Nm7EQ~~/) | Python 后端（AI Agent） | Python 服务、对话、工具调用、任务编排、AI 后端 |
| [盯盯拍深圳](https://www.zhaopin.com/jobdetail/CC611941820J40876941605.htm) | AI Agent 应用开发 | Harness 评测、RAG、插件安全、上下文、复杂编排、并发调度 |
| [广州/深圳市场代表 JD](https://cn.linkedin.com/jobs/view/ai-development-engineer-at-%E5%B9%BF%E5%B7%9E%E8%83%A1%E5%B7%B4%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8-4452338171) | AI Development Engineer | FastAPI、异步、LangGraph、向量库、SLA、CI/CD、数据库/缓存 |
| [小红书后端样本](https://www.nowcoder.com/jobs/detail/408253) | 后端开发 | 算法、网络、OS、主流语言、多线程、微服务、消息队列、MySQL |

### 2.4 第一性原理解释

一个 AI 应用上线后，企业承担的不是“模型是否能回答一次”，而是以下责任：

- 输入不完整、模型不稳定时仍要给出可控结果；
- 调错工具、重复执行、越权访问不能造成真实损失；
- 知识变化后要能更新，回答必须绑定证据；
- 延迟、Token、并发和第三方模型故障需要预算与降级；
- 结果好坏必须能测量，失败必须能复现；
- 系统要能部署、监控、审计和持续迭代。

因此，“AI 应用开发 + 后端能力”不是两个方向叠加，而是一条生产链路的上下两层。

---

## 3. 掌握度标准：避免“看过 = 会了”

### 3.1 五级掌握度

| 等级 | 定义 | 是否算掌握 |
| --- | --- | --- |
| M0 未接触 | 不知道核心概念 | 否 |
| M1 能识别 | 能用一句话解释，无法独立应用 | 否 |
| M2 能复现 | 看资料能实现标准案例 | 否 |
| M3 能独立解决 | 能独立实现、解释设计、处理常见边界 | **是，核心项最低线** |
| M4 有工程证据 | 在真实/高仿业务中验证，有测试、指标、失败复盘 | **是，简历重点** |

### 3.2 单项验收四件套

一个能力只有同时满足下面条件，才能从“学过”改成“已掌握”：

1. **60 秒主线**：不用背稿讲清它解决什么问题、处于哪条链路；
2. **关键实现**：能现场写核心代码、SQL、伪代码或架构；
3. **追问边界**：能回答失败场景、替代方案和取舍；
4. **证据定位**：能指向项目、测试、指标、Commit、文档或可复现 Demo。

### 3.3 当前状态标记

| 标记 | 含义 |
| --- | --- |
| E | 已有项目使用证据，但还需口述/实现验收，不能直接视为掌握 |
| G | 已知需要补齐 |
| U | 尚未核对 |
| M3 | 已通过独立实现与追问验收 |
| M4 | 已有可核验工程证据 |

建议写法：`E/M2`、`G/M1`、`M3`、`M4`。不要只写“会/不会”。

---

## 4. P0：AI 应用与 Agent 核心能力台账

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 最适合的项目证据 |
| --- | --- | --- | --- | --- |
| A01 | 业务问题定义与 AI 适用性 | 能区分模型、规则程序、人工审批各自边界，并定义业务指标 | E/M2 | EnergyOps、RuleArena |
| A02 | LLM 能力与局限 | 讲清概率生成、幻觉、上下文限制、非确定性及应对方式 | G/U | RuleArena、数驭穹图 |
| A03 | 模型 API 接入 | 独立完成鉴权、超时、重试、流式输出、错误映射、限流 | E/M2 | 任一在线 Demo |
| A04 | Token、上下文与成本 | 能估算上下文、输出和重试成本，设计预算与截断策略 | G/U | RuleArena |
| A05 | Prompt 与结构化输出 | 会角色/约束/示例/上下文组织；用 Schema 校验并处理失败 | E/M2 | 数驭穹图、RuleArena |
| A06 | Tool / Function Calling 生命周期 | 讲清 tool call、参数校验、执行、tool result、继续推理的完整循环 | E/M2 | EnergyOps MCP、RuleArena |
| A07 | Agent Loop | 能实现 ReAct 或 Plan-Execute 最小内核，定义终止与最大步数 | G/M2 | RuleArena、Pi-Agent 学习 |
| A08 | Harness 架构 | 讲清 model + context + tools + constraints + verify/correct | E/M2 | RuleArena、Pi/Claude Code 学习 |
| A09 | 上下文管理 | 区分系统指令、会话、检索、工具结果、状态；会压缩、裁剪和排序 | G/M2 | RuleArena |
| A10 | State / Memory / Context | 区分权威业务状态、Agent 状态、短期上下文和长期记忆 | G/M2 | RuleArena、EnergyOps |
| A11 | Workflow / 状态机 | 能用显式节点、状态、条件和失败分支表达稳定业务流程 | E/M2 | EnergyOps、RuleArena |
| A12 | MCP / Skill / Tool 设计 | 会定义职责、Schema、权限、错误语义、幂等性和可观测字段 | E/M2 | EnergyOps 25 个 MCP 工具 |
| A13 | 多 Agent 取舍 | 能说明何时单 Agent/Workflow 足够，何时需要角色分工和并行 | G/U | RuleArena |
| A14 | 副作用与幂等 | 区分 ToolCallID 与业务幂等键；处理重试、重复执行、未知结果 | E/M2 | EnergyOps、Pi-Agent 学习 |
| A15 | Checkpoint 与恢复 | 能设计 checkpoint 时机、权威状态查询、恢复与重复副作用防护 | E/M2 | EnergyOps、Pi-Agent 学习 |
| A16 | 人在回路 | 根据风险等级设计确认、审批、撤销、超时和审计 | E/M2 | EnergyOps R0/R1/R2、RuleArena |
| A17 | Agent 评测集 | 从真实任务构造 golden/bad case/holdout，版本化输入和预期 | G/M1 | RuleArena |
| A18 | Agent 评测指标 | 至少覆盖任务成功率、工具准确率、步骤、延迟、成本和安全违规 | G/M1 | RuleArena |
| A19 | 轨迹与失败归因 | 保存可复现轨迹、终止原因、工具输入输出和失败分类 | G/M2 | RuleArena、EnergyOps |
| A20 | 证据绑定与可信输出 | 结果能追溯到来源、计算或工具；证据不足时拒答/降级 | E/M2 | 数驭穹图、RuleArena |
| A21 | Prompt Injection 与工具安全 | 识别不可信内容、数据泄露、越权工具、命令/SQL 注入并隔离 | G/U | RuleArena、数驭穹图 |
| A22 | LLMOps 版本与实验 | 管理模型/Prompt/知识库/工具版本，支持回放和对比实验 | G/U | RuleArena |
| A23 | 模型降级与故障策略 | 区分可重试、不可重试、降级、转人工；避免掩盖错误 | G/U | RuleArena |
| A24 | 框架使用与解耦 | 会用 LangGraph/LangChain 等，但核心状态、工具和评测不被框架绑死 | G/U | RuleArena |

---

## 5. P0：RAG 与企业知识能力台账

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| R01 | 数据源与知识边界 | 定义来源、权限、时效、权威级别和不可回答范围 | E/M2 | 数驭穹图、RuleArena |
| R02 | 文档解析 | 处理 PDF/Markdown/HTML/表格、元数据、失败与增量更新 | G/U | RuleArena 知识库 |
| R03 | Chunking | 能按语义、标题、窗口或结构切分，并解释召回与上下文取舍 | G/M1 | RuleArena |
| R04 | Embedding | 理解向量语义、维度、相似度、模型选择和版本变更影响 | G/M1 | RuleArena |
| R05 | 向量索引 | 会使用 pgvector/Milvus 等一种方案并解释索引和过滤 | G/U | PostgreSQL + pgvector 优先 |
| R06 | 检索策略 | 能实现关键词 + 向量混合检索、元数据过滤、Query Rewrite | G/M1 | RuleArena、数驭穹图 |
| R07 | Rerank | 知道何时重排，能权衡质量、时延和成本 | G/U | RuleArena |
| R08 | 上下文组装 | 去重、排序、控制 Token，避免相互冲突的证据污染回答 | G/U | RuleArena |
| R09 | RAG 生成与引用 | 答案逐项绑定证据，证据不足时明确不确定或拒答 | E/M2 | 数驭穹图 |
| R10 | 离线评测 | 构造问题集，评估 Recall@K/MRR、faithfulness、answer correctness | G/M1 | RuleArena |
| R11 | 在线评测 | 记录用户反馈、无答案率、延迟、成本、Bad Case 并回流 | G/U | RuleArena Demo |
| R12 | 权限检索 | 在检索前过滤权限，不依赖生成后脱敏 | E/M2 | 数驭穹图 |
| R13 | 知识更新与版本 | 增量索引、删除传播、版本兼容、回滚和过期检测 | G/U | RuleArena |
| R14 | RAG 与微调取舍 | 能根据“知识更新/行为格式/领域能力”选择 RAG、Prompt 或微调 | G/M1 | 面试设计题 |

---

## 6. P0：Python 工程能力台账

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| P01 | Python 数据模型 | 熟悉可变/不可变、引用、浅深拷贝、hash、`__eq__`、对象生命周期 | G/U | 现场编码 |
| P02 | 函数与作用域 | 参数传递、闭包、装饰器、LEGB、默认可变参数陷阱 | G/U | 现场编码 |
| P03 | 迭代器/生成器/上下文管理器 | 能独立实现并说明节省内存和资源释放场景 | G/U | 现场编码 |
| P04 | 类型系统 | 使用 typing、Protocol/Generic、mypy/pyright，设计清晰边界 | E/M2 | FastAPI 项目 |
| P05 | Pydantic v2 | Validator、序列化、配置、错误结构、DTO 与领域对象边界 | E/M2 | EnergyOps |
| P06 | 异常设计 | 错误尽早暴露、分层传播、统一转换，不吞异常 | E/M2 | EnergyOps、RuleArena |
| P07 | asyncio | 讲清 event loop、coroutine/task、gather、取消、超时和背压 | G/M1 | AI 流式服务实验 |
| P08 | 线程/进程/GIL | 能按 IO/CPU 任务选择 asyncio、线程池、进程池 | G/M1 | 性能实验 |
| P09 | 并发安全 | 识别竞态、共享状态、锁、连接池耗尽和同步阻塞异步循环 | G/U | 压测实验 |
| P10 | 包与依赖 | pyproject、虚拟环境、锁文件、配置分环境、可复现构建 | E/M2 | RuleArena / 在线 Demo |
| P11 | 日志 | 结构化日志、request/task/trace ID、敏感信息脱敏 | E/M2 | EnergyOps |
| P12 | 测试工具 | pytest fixture/parametrize/mock、覆盖率、确定性测试 | E/M2 | EnergyOps 92+ 测试 |
| P13 | 代码质量 | lint/format/type check、模块边界、Code Review、复杂度控制 | G/U | GitHub 仓库 |
| P14 | 性能定位 | profiling、内存、CPU、I/O、N+1、连接池和热点分析 | G/U | EnergyOps 查询优化 |

---

## 7. P0：Web、API 与 FastAPI 台账

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| W01 | HTTP 基础 | 方法、状态码、Header、Cookie、缓存、幂等、连接复用 | G/M1 | API 面试题 |
| W02 | REST API 设计 | 资源建模、版本、分页、过滤、错误码、幂等键、OpenAPI | E/M2 | EnergyOps |
| W03 | FastAPI 核心 | 路由、依赖注入、中间件、生命周期、异常、BackgroundTasks | E/M2 | EnergyOps |
| W04 | 同步/异步边界 | 知道 async handler 中阻塞调用的影响和隔离方法 | G/U | 压测实验 |
| W05 | 鉴权 | Session/JWT/OAuth2 基本流程，Access/Refresh Token 与撤销 | G/U | Ovanta / RuleArena |
| W06 | 授权 | RBAC、ABAC、资源级权限、租户隔离、最小权限 | E/M2 | 数驭穹图、RuleArena |
| W07 | 输入安全 | Schema、文件大小/MIME、SQL/命令注入、SSRF、路径穿越 | G/U | RuleArena |
| W08 | SSE / WebSocket | 流式响应、断线、心跳、取消、代理缓冲和恢复策略 | E/M2 | Agent 对话接口 |
| W09 | 文件与大结果 | 对象存储、授权下载、异步导出、过期和审计 | E/M2 | EnergyOps、数驭穹图 |
| W10 | Webhook/第三方 API | 签名、重放防护、超时重试、幂等和状态查询 | E/M2 | 通知/支付类案例 |
| W11 | 限流与配额 | 用户/租户/模型维度限流，429、漏桶/令牌桶和预算 | G/U | RuleArena |
| W12 | API 测试 | 单元、集成、契约和 E2E；测试错误与权限路径 | E/M2 | EnergyOps |

---

## 8. P0：数据库、缓存、任务与一致性台账

### 8.1 PostgreSQL / SQL

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| D01 | 数据建模 | 实体、关系、范式/反范式、主外键、唯一约束、审计字段 | E/M2 | EnergyOps、Ovanta |
| D02 | SQL | JOIN、聚合、窗口、CTE、子查询、NULL、去重和分页 | E/M2 | EnergyOps、数驭穹图 |
| D03 | 事务 ACID | 能解释原子性、一致性、隔离性、持久性及业务落点 | G/M2 | 账单/状态变更 |
| D04 | 隔离与并发 | 脏读/不可重复读/幻读、MVCC、锁、丢失更新、死锁 | G/M1 | 状态更新实验 |
| D05 | 索引 | B+Tree、联合索引、最左匹配、选择性、覆盖索引、写放大 | G/M1 | EnergyOps 优化 |
| D06 | EXPLAIN | 看扫描、行数估计、Join、排序、聚合，定位慢查询 | G/M1 | 查询 P95 优化 |
| D07 | SQLAlchemy | Session/事务边界、关系加载、N+1、连接池、Unit of Work | E/M2 | EnergyOps |
| D08 | Alembic | 可回滚迁移、数据迁移、兼容发布、线上锁风险 | E/M2 | EnergyOps |
| D09 | 大结果 | Keyset 分页、流式读取、行数预估、截断/异步导出边界 | E/M2 | 数驭穹图 |
| D10 | 数据质量 | 唯一性、完整性、时效性、口径、血缘、可追溯与修正 | E/M4 候选 | EnergyOps 数据链路 |

### 8.2 Redis / 缓存

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| C01 | Redis 数据结构 | String/Hash/List/Set/ZSet/Stream 的典型场景 | G/M1 | 小实验 |
| C02 | Cache Aside | 读写流程、TTL、失效、最终一致性和失败窗口 | G/M1 | RuleArena |
| C03 | 缓存风险 | 穿透、击穿、雪崩、热 Key、大 Value 的识别和处理 | G/U | 系统设计题 |
| C04 | 原子操作 | SET NX EX、Lua、CAS 思路；理解分布式锁边界 | G/U | 幂等实验 |
| C05 | 去重与状态 | dedup key、TTL、状态机与数据库权威状态的关系 | E/M2 | EnergyOps 告警 |
| C06 | 限流/会话/队列 | 能选择 Redis 的合适结构，并解释可靠性限制 | G/U | Agent 服务 |

### 8.3 异步任务、消息与调度

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| Q01 | Celery/任务队列 | 生产、消费、ack、重试、超时、并发、结果存储 | E/M2 | EnergyOps / AI 任务 |
| Q02 | 消息语义 | 至多一次/至少一次/效果一次；不存在轻易获得的端到端 exactly-once | G/M2 | 面试场景题 |
| Q03 | 幂等消费 | 业务幂等键、唯一约束、状态查询、条件更新 | E/M2 | EnergyOps、Pi-Agent |
| Q04 | Outbox | 业务状态和事件同事务，可靠投递与重复消费 | G/M1 | RuleArena 状态事件 |
| Q05 | 重试策略 | 指数退避、抖动、最大次数、死信、人工处理 | E/M2 | 通知与第三方调用 |
| Q06 | 调度 | 墙钟、重入、补偿、错过执行、时区、分布式重复调度 | E/M3 候选 | EnergyOps APScheduler |
| Q07 | 长任务 | 接收任务、返回 ID、进度、取消、恢复、结果过期和下载 | G/M2 | 导出/Agent 任务 |
| Q08 | 顺序与乱序 | 序号/版本、事件时间、延迟到达、去重和重算 | E/M3 候选 | EnergyOps 补数 |

---

## 9. P0：测试、可靠性、安全与可观测性台账

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| O01 | 测试金字塔 | 能分配单元、集成、契约、E2E，不把所有测试塞进一个层级 | E/M2 | EnergyOps |
| O02 | 失败优先测试 | 测试先证明缺陷存在，覆盖边界和回归，不只验证 happy path | E/M2 | EnergyOps 黄金对账 |
| O03 | 测试替身 | 正确区分 fake/stub/mock；不 mock 掉真正要验证的边界 | G/U | Agent 工具测试 |
| O04 | Golden / 回放 | 固定输入、依赖和版本，能复现业务与 Agent 输出 | E/M2 | 账单黄金数据、RuleArena |
| O05 | 超时 | API、DB、模型、工具分层超时并正确取消/回收资源 | G/U | RuleArena |
| O06 | 重试 | 只重试瞬时错误；考虑副作用、退避、预算和重试风暴 | E/M2 | 通知、工具调用 |
| O07 | 熔断/隔离/降级 | 解释何时使用，设计明确可观测的降级结果 | G/U | 系统设计题 |
| O08 | 限流与背压 | 入口、队列、模型并发和下游容量一致，不无限堆积 | G/U | Agent 压测 |
| O09 | 健康检查 | liveness/readiness、依赖检查和启动顺序 | G/U | Docker 部署 |
| O10 | 日志 | 结构化、关联 ID、错误栈、敏感字段和保留周期 | E/M2 | EnergyOps |
| O11 | Metrics | QPS、错误率、P95/P99、队列积压、模型 Token/成本/成功率 | G/M1 | RuleArena |
| O12 | Trace | API→Agent→Tool→DB/模型全链路追踪与耗时拆解 | G/M1 | RuleArena / OTel |
| O13 | 告警 | 基于用户影响和 SLO，避免告警风暴，支持恢复通知 | E/M2 | EnergyOps |
| O14 | 故障定位 | 从现象到日志/指标/Trace/数据，提出并验证假设 | E/M2 | EnergyOps 复盘 |
| O15 | 认证与权限 | 默认拒绝、最小权限、资源级鉴权、服务身份 | G/M2 | 数驭穹图、RuleArena |
| O16 | Secret 管理 | 不入库、不写日志，分环境、轮换、撤销和最小暴露 | G/U | 部署配置 |
| O17 | 常见 Web 风险 | OWASP 基本项，尤其注入、SSRF、越权、上传和依赖风险 | G/U | 安全审查 |
| O18 | AI 安全 | Prompt Injection、数据泄露、越权 Tool、恶意文档和输出执行 | G/U | RuleArena |
| O19 | 审计 | 谁在何时以何权限做了什么，输入、决策、结果和版本可追溯 | E/M2 | EnergyOps、RuleArena |
| O20 | SLO/SLA | 定义可用性、延迟、正确率和预算，知道 99.9% 的含义 | G/U | 系统设计题 |

---

## 10. P0：Linux、网络、部署与系统设计台账

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| I01 | Linux 日常 | 进程、端口、文件、权限、日志、磁盘、内存、信号和常用排查命令 | G/M1 | 部署排错 |
| I02 | 进程/线程/协程 | 区分资源、调度、通信和适用场景 | G/M1 | Python 并发题 |
| I03 | 内存与 I/O | 虚拟内存、页、文件描述符、阻塞/非阻塞、缓冲 | G/U | 后端面试 |
| I04 | TCP/UDP | 握手、可靠传输、重传、流量/拥塞控制的业务影响 | G/U | 网络面试 |
| I05 | DNS/HTTP/HTTPS | 从域名到服务完整链路，TLS、连接复用、代理和超时 | G/M1 | 请求链路题 |
| I06 | Nginx | 反向代理、TLS、负载均衡、超时、上传和流式缓冲 | E/M2 | EnergyOps |
| I07 | Docker | 镜像层、容器网络/卷、健康检查、非 root、Compose | E/M2 | EnergyOps / Demo |
| I08 | CI/CD | lint/test/build/migrate/deploy/rollback 的最小流水线 | G/U | GitHub Actions |
| I09 | 云部署 | 配置、数据库、对象存储、域名/TLS、日志、备份和成本 | E/M2 | Railway/云端 Demo |
| I10 | 容量估算 | 从用户/QPS/数据量/Token/模型并发推导资源与瓶颈 | G/U | 系统设计题 |
| I11 | 水平扩展 | 无状态服务、共享状态、连接池、任务调度和会话处理 | G/U | Agent 服务设计 |
| I12 | 高可用 | 单点识别、冗余、健康检查、故障转移、备份恢复 | G/U | 系统设计题 |
| I13 | 单体/模块化/微服务 | 根据团队、变化和一致性成本选择，不为“架构感”拆分 | E/M2 | RuleArena 架构 |
| I14 | 读写/异步拆分 | 知道何时缓存、异步、批处理、预计算和物化视图 | E/M2 | EnergyOps |
| I15 | 一致性取舍 | 强一致/最终一致、事务边界、补偿与对账 | E/M2 | 月度账单、通知 |
| I16 | 性能测试 | 设计基线、负载、压力、稳定性测试并读 P95/P99 | G/U | Agent/API 压测 |
| I17 | Kubernetes 基础 | 能读 Deployment/Service/Config/Secret，理解滚动发布即可 | G/U（P1 深度） | 最小部署实验 |

---

## 11. P0：算法与计算机基础台账

算法目标不是刷完题库，而是稳定通过笔试、手撕并展示清晰工程思维。

| ID | 母题组 | 最低掌握判据 | 当前初始判断 |
| --- | --- | --- | --- |
| K01 | 复杂度与边界 | 准确分析时空复杂度，主动覆盖空、重复、极值、溢出 | E/M2 |
| K02 | 哈希/集合 | 两数之和、分组、去重、频次、前缀和 | E/M3 候选 |
| K03 | 双指针 | 移动零、三数之和、盛水、接雨水 | E/M3 候选 |
| K04 | 滑动窗口 | 无重复子串、异位词、最小覆盖、单调队列 | E/M3 候选 |
| K05 | 链表 | 反转、环、合并、相交、LRU | G/M2 |
| K06 | 栈/队列/堆 | 括号、单调栈、TopK、优先队列 | G/U |
| K07 | 二叉树 | 遍历、层序、深度、路径、BST、最近公共祖先 | G/M1 |
| K08 | 二分 | 有序查找、边界、答案二分 | G/U |
| K09 | 图 | DFS/BFS、拓扑排序、并查集、最短路基本思想 | G/U |
| K10 | 回溯 | 子集、排列、组合、剪枝 | G/U |
| K11 | 动态规划 | 背包、子序列、路径、状态与转移 | G/U |
| K12 | 区间/贪心 | 合并区间、跳跃、调度类问题 | E/M2 |
| K13 | SQL 手写 | JOIN、聚合、窗口、TopN、连续/留存类问题 | E/M2 |
| K14 | 现场表达 | 先澄清→朴素解→不变量→编码→样例→复杂度 | G/M2 |

你已经完成的数组、哈希、双指针、滑动窗口、前缀和、区间等母题应进入“复习与随机手写”，而不是重新从头学。树、图、堆、二分、回溯和 DP 需要按高频核心题补齐。

---

## 12. P0/P1：业务交付、FDE 与协作能力

| ID | 能力项 | 最低掌握判据 | 当前初始判断 | 证据载体 |
| --- | --- | --- | --- | --- |
| F01 | 需求澄清 | 从模糊诉求识别用户、输入、输出、规则、异常和验收指标 | E/M3 候选 | EnergyOps、Ovanta |
| F02 | 领域建模 | 实体、状态、事件、不变量、权限和系统边界 | E/M2 | RuleArena、EnergyOps |
| F03 | 技术方案 | 能写背景、目标/非目标、方案、接口、数据、风险、测试、上线 | E/M2 | 项目 Spec |
| F04 | 逆向失败设计 | 从最坏结果反推权限、验证、审计、恢复和人工兜底 | E/M2 | RuleArena |
| F05 | 指标闭环 | 技术指标映射业务结果，定义基线、目标和复盘 | E/M2 | EnergyOps |
| F06 | 演示与讲解 | 3 分钟完整主线，能用黄金案例展示成功与失败路径 | G/M2 | RuleArena Demo |
| F07 | 跨团队协作 | 与产品/前端/测试/业务对齐接口、口径、风险和时间 | E/M3 候选 | 实习经历 |
| F08 | 文档 | README、架构、开发、Review、Runbook、ADR 简洁一致 | E/M2 | RuleArena 材料 |
| F09 | Git 协作 | 分支、Commit、PR、Review、rebase/冲突、回滚 | G/M2 | GitHub 项目 |
| F10 | AI Coding | 用 AGENTS.md/Spec/测试/Review 驱动 AI，同时能审查结果 | E/M2 | RuleArena 开发流程 |
| F11 | 开源证据 | 仓库可运行、README 清楚、Demo 在线、Issue/Commit 可信 | G/U | RuleArena |
| F12 | 技术英语 | 能读官方文档/JD，写英文 README 摘要并做基础英文介绍 | G/M1 | 个人网站/GitHub |

---

## 13. P1 能力：补齐工程全景，但不抢占 P0

| ID | 能力项 | 达标方式 | 何时升级为 P0 |
| --- | --- | --- | --- |
| X01 | Transformer 基础 | 讲清 Token、Embedding、Attention、位置编码、推理生成 | 多个目标 JD 明确追问模型原理 |
| X02 | PyTorch 基础 | 能写 Dataset/DataLoader、训练循环，理解反向传播和 eval | 主投 AI 应用算法岗 |
| X03 | LoRA/SFT | 做一个小型可复现实验，比较前后效果和成本 | JD 要求微调或现有方案确有行为适配需求 |
| X04 | 模型服务 | 本地运行 vLLM/Ollama，理解 batching、KV Cache、量化、流式 | 主投 Agent Infra/私有化部署 |
| X05 | 向量数据库运维 | 深入索引参数、扩缩容、备份和大规模性能 | RAG 平台/搜索工程岗位 |
| X06 | Kubernetes | 能部署服务、配置资源、滚动发布、看日志与探针 | 岗位明确云原生/K8s |
| X07 | Go | 能读写基础服务，理解 goroutine/channel | 深圳目标岗大量明确要求 Go，且 Python 岗不足 |
| X08 | 前端 | React/Vue 基本联调、状态和流式 UI | AI 全栈岗位占主投比例上升 |
| X09 | 多模态 | 文档/图片/音频输入、解析和评测最小实践 | 项目或岗位明确需要 |
| X10 | 搜索/NL2SQL 深度 | Schema Linking、IR/AST、检索/执行计划、安全验证 | 数驭穹图进入主简历重点 |

---

## 14. P2/P3：当前不要过度投入

| 方向 | 当前策略 | 原因 |
| --- | --- | --- |
| 从零预训练大模型 | P3，仅理解流程 | 算力、数据和岗位画像不匹配 |
| RLHF/RLAIF/大规模强化学习 | P3 | 主要属于算法训练岗 |
| Megatron/DeepSpeed/CUDA/算子优化 | P3 | AI Infra/训练基础设施专属 |
| 同时精通 Java、Go、Python | P3 | 稀释 Python 主线；其他语言只做阅读/基础 |
| 深度 Kubernetes 运维 | P2 | 当前只需会部署和排障基础 |
| 复杂微服务治理 | P2 | 先掌握模块化单体、一致性和可靠性 |
| 纯前端视觉工程 | P3 | 只保证 Demo 和接口联调 |
| 追逐每个新 Agent 框架 | P3 | 框架变化快，Harness 原理和评测更稳定 |
| 证书堆叠 | P3 | JD 更看重可运行项目、实习、开源和面试表现 |

---

## 15. 你的现有能力证据映射

这里记录“已有证据”，不是直接宣布“已经掌握”。下一步应通过口述、现场实现和追问把 E 转成 M3/M4。

### 15.1 EnergyOps：后端与真实业务主证据

- Python、FastAPI、SQLAlchemy、Pydantic v2、PostgreSQL、Redis、Alembic、pytest；
- 外部平台数据接入，`raw → interval → hourly → daily` 数据链路；
- 质量状态、乱序补数、partial 透明度、checkpoint、自愈；
- APScheduler 调度、异常规则、告警、通知、重试和状态查询；
- 25 个 MCP 工具、R0/R1/R2 风险等级、真实业务闭环；
- 月度水电费黄金对账、年度看板、逐单元格回归；
- 适合证明：B/Python、数据库、数据质量、任务调度、测试、可靠性、业务交付。

### 15.2 数驭穹图：可信 AI 数据查询证据

- 意图识别、领域路由、Schema Linking、SemQL/SQL 生成；
- SQL AST、只读事务、扫描量、大结果异步导出、JOIN 膨胀；
- 权限前置、查询验证、证据绑定；
- 适合证明：AI 与确定性程序边界、NL2SQL、权限、SQL 安全、可信输出。

### 15.3 Ovanta：业务后端与跨境场景证据

- 国内/海外登录、草稿/审核/发布/版本/来源；
- 会员权益、顾问服务、订单/支付/权益链路；
- 适合证明：业务建模、鉴权、状态流转、跨团队交付和国际化业务理解。

### 15.4 RuleArena：未来补齐 Agent 工程上限

RuleArena 不应只是“多 Agent 审查 Demo”，而应专门补齐这些能力：

- Harness：上下文、工具、约束、验证、纠正；
- 显式状态机、不变量和非法状态；
- 工具副作用、权限、幂等、checkpoint 和恢复；
- Golden/Bad Case、任务级 Eval、轨迹回放与失败归因；
- 可解释证据链、修复建议和确定性验证；
- 在线 Demo、可复现仓库、评测卡和系统设计文档。

### 15.5 组合后的简历能力叙事

> 我不是只会调用大模型 API，而是能从真实业务和数据出发，用 Python 后端承载 Agent/RAG，通过权限、确定性规则、证据、评测、观测和恢复机制，把非确定模型变成可上线、可验证的业务系统。

---

## 16. 近期核对顺序：先审计，再决定学什么

不要把整份地图同时开工。按下面顺序逐项验收，未通过才进入学习：

1. 四个项目的一条业务主线、边界、关键设计、失败场景和个人贡献；
2. Python 语言核心、asyncio、线程/进程/GIL、异常与类型；
3. HTTP、FastAPI、鉴权、SSE、第三方 API；
4. PostgreSQL 事务/锁/索引/EXPLAIN 与 SQLAlchemy Session；
5. Redis 缓存、去重、原子操作与分布式锁边界；
6. 异步任务、至少一次、幂等、Outbox、重试和恢复；
7. OS、网络、Linux、Docker 和常见线上排错；
8. 高频算法母题：已学内容随机手写，补齐树/堆/图/二分/DP；
9. Agent Loop、Harness、Context/State/Memory、Tool 生命周期；
10. Agent 副作用、权限、checkpoint、终止与失败恢复；
11. Agent Eval、轨迹、Bad Case、指标和回归；
12. RAG 解析→切分→检索→重排→引用→离线/在线评测；
13. 可观测、SLO、超时/重试/限流/背压、成本与容量估算；
14. Transformer/vLLM/LoRA 的工程全景和一个最小实验；
15. RuleArena 在线 Demo、GitHub、README、评测卡和 3 分钟演示。

---

## 17. 每周维护方法

### 17.1 新 JD 进入时

把 JD 拆成能力 ID，不再新建一套学习路线：

```text
岗位：
公司/城市/链接：
硬门槛：
命中能力 ID：A__ / R__ / P__ / W__ / D__ / ...
当前缺口：
是否值得为它调整优先级：是 / 否
投递结论：主投 / 可投 / 放弃
```

只有同一新能力在 **3 个以上高匹配 JD** 中反复出现，或目标公司明确要求，才加入 P0/P1。不要被单个 JD 带偏。

### 17.2 学完一个能力时

```text
能力 ID：
日期：
掌握度：M0 / M1 / M2 / M3 / M4
60 秒答案：
独立实现：
失败/边界：
项目证据或链接：
仍答不好的追问：
下次复习日期：
```

### 17.3 面试后

```text
问题原文：
对应能力 ID：
卡住类型：不知道 / 关系混乱 / 说不清 / 无项目证据 / 现场写不出
正确答案主线：
需要补的最小知识：
新增测试/代码/文档证据：
是否更新掌握度：
```

### 17.4 每周只看四个数字

- P0 总项中 M3/M4 的比例；
- 本周新增 M3/M4 数量；
- 随机抽查失败数量；
- 模拟/真实面试新增断点数量及关闭数量。

不要用“看了多少小时、收藏多少文章”作为主指标。

---

## 18. 个人掌握度总表

每完成一个模块验收，在这里更新。初始值不要凭感觉填写。

| 模块 | P0 项数 | M3 | M4 | 最大断点 | 最近验收 | 下次复习 |
| --- | ---: | ---: | ---: | --- | --- | --- |
| AI/Agent | 24 | 0 | 0 | 待首次系统验收 |  |  |
| RAG | 14 | 0 | 0 | 待首次系统验收 |  |  |
| Python | 14 | 0 | 0 | 待首次系统验收 |  |  |
| Web/FastAPI | 12 | 0 | 0 | 待首次系统验收 |  |  |
| PostgreSQL/SQL | 10 | 0 | 0 | 待首次系统验收 |  |  |
| Redis | 6 | 0 | 0 | 待首次系统验收 |  |  |
| 任务/消息 | 8 | 0 | 0 | 待首次系统验收 |  |  |
| 测试/可靠性/安全/观测 | 20 | 0 | 0 | 待首次系统验收 |  |  |
| Linux/网络/部署/系统设计 | 17 | 0 | 0 | 待首次系统验收 |  |  |
| 算法 | 14 | 0 | 0 | 树/图/堆/DP 待补 |  |  |
| 业务交付/FDE | 12 | 0 | 0 | 待口述验收 |  |  |

> 说明：这里暂时全部记 0，是为了避免把“项目里出现过”误判为“个人已经稳定掌握”。首次验收后，EnergyOps 对应的数据库、调度、数据质量、测试与业务交付项很可能可以快速转成 M3/M4。

---

## 19. 一页复习索引

面试前只记住下面 12 条主线：

1. **业务**：谁遇到什么问题，输入、输出、约束和成功指标是什么；
2. **边界**：模型负责理解与生成，程序负责规则、权限、计算和最终验证；
3. **Agent**：Context → Model → Tool → Result → Verify/Continue/Stop；
4. **状态**：上下文不是权威状态，Memory 不是数据库，Checkpoint 不是幂等；
5. **RAG**：解析→切分→索引→召回→重排→上下文→引用→评测；
6. **副作用**：权限 + 参数校验 + 业务幂等键 + 状态查询 + 审计 + 恢复；
7. **后端**：API→服务→事务→缓存/消息→异步任务→部署；
8. **数据库**：约束保正确，事务保原子，并发靠锁/MVCC，索引与 EXPLAIN 保性能；
9. **可靠性**：超时、重试、幂等、限流、背压、隔离、降级、恢复；
10. **可观测**：日志回答发生了什么，指标回答影响多大，Trace 回答慢/错在哪里；
11. **评测**：Golden + Bad Case + Holdout，测效果、效率、成本、安全并持续回归；
12. **证据**：真实项目、测试、指标、失败复盘、仓库和在线 Demo 比框架清单更有说服力。

---

## 20. 文档更新规则

- 本文只维护目标能力和掌握证据，不堆积大段学习笔记；
- 具体知识放到对应专题资料，本文只保留链接和结论；
- 每个能力只保留一个权威状态，避免多个表互相冲突；
- JD、面试问题、项目 Review 都通过能力 ID 回写；
- 每两周删除不再服务目标岗位的学习任务；
- 任何“已掌握”必须有验收日期和证据；
- 调研来源超过 60 天或岗位下线时，标记“待重新核验”，不静默沿用。

## 关联页面

- [[FDE能力地图]]
- [[Python后端工程]]
- [[Agent-RAG-MCP]]
- [[秋招面试地图]]

