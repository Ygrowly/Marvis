---
title: "通用 AI Agent 驱动网关路由安全审计实践｜得物技术"
source: "https://mp.weixin.qq.com/s/b468fvlCr_PJ9UY26kbzSQ"
author:
  - "[[炁源]]"
published:
created: 2026-08-08
description: "本项目构建网关路由 AI 安全审计系统，采用\x26quot;通用 Agent + 业务 Skill\x26quot;分层设计，支持增量日检与存量月检。通过 AI 批量筛查 + 人工深度验证的人机协同模式，落地 Open 网关越权漏洞检测，为大规模 API 安全审计提供可复用的智能化解决方案。"
tags:
  - "read/new"
---
炁源 *2026年4月29日 18:30*

![图片](http://mmbiz.qpic.cn/mmbiz_gif/AAQtmjCc74DZeqm2Rc4qc7ocVLZVd8FOASKicbMfKsaziasqIDXGPt8yR8anxPO3NCF4a4DkYCACam4oNAOBmSbA/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

**目录**

一、背景与技术方案

1.安全审计的核心挑战

2.技术选型与建设契机

二、技术架构

1.整体架构设计

2.架构设计原则：通用 Agent + 业务 Skill 分离

3.Skill 层核心组成

4.MCP 工具集设计

三、漏洞检测方法论（以越权为例）

1.越权漏洞精细化分类

2.检测决策流程

3.精细化危害评估机制

四、技术优化：Token 成本降低 95%+

1.问题诊断

2.优化策略与效果

五、模型选型原则与决策框架

六、方法论沉淀

七、误报分析与改进方向

1.误报根因分析

2.针对性改进方案

3.后续规划

八、小结

九、附录

本项目构建了一个网关路由 AI 安全审计系统，采用"通用 Agent + 业务 Skill"分层设计，增量日检/存量月检。落地 Open 网关路由越权漏洞检测流程，通过 AI 批量筛查 + 人工深度验证的人机协同模式，为大规模 API 安全审计提供了可复用的智能化解决方案。充分发挥通用 Agent 能力，业务逻辑在 Skill 中快速迭代。

**一**

**背景与技术方案**

**安全审计的核心挑战**

随着平台 API 规模持续扩张，安全审计面临新的规模化挑战：

**主要挑战：**

- 覆盖面不足：抽样审计约覆盖 ~20%。
- 时效性压力：新接口需要更快的安全评估。
- 规则一致性：标准化检测规则难以沉淀。

**技术选型与建设契机**

当前，以大型语言模型为基座的 AI Agent 在代码语义理解、逻辑推理与自动化执行等维度的能力已超预期成熟，工程落地准确率与稳定性得到大规模验证。这一技术跃迁使全量自动化安全审计从概念验证走向可靠实践。传统人工抽样模式在数万条 API、数百个微服务的规模下已难以为继，而基于 AI Agent 的方案可实现 100% 路由覆盖与分钟级检测响应。本文将围绕这一契机，阐述如何构建贯穿全链路调用链的智能审计体系，解决覆盖面、时效性与规则一致性三大核心挑战。

**二**

**技术架构**

**整体架构设计**

架构说明：常规代码负责任务调度与结果存储，所有 AI 分析工作由超级 Agent 完成。

具体项目分析告警时采用 AI批量筛查 + 人工深度验证 的人机协同模式：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

场景化应用：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**架构设计原则：通用 Agent + 业务 Skill 分离**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**设计优势：**

通用 Agent 能力最大化：充分利用 Claude Code/OpenCode 的代码理解、推理分析、上下文管理、会话恢复等标准能力，不重复造轮子。业务逻辑快速迭代：检测规则、分析流程、报告格式等业务逻辑全部沉淀在 Skill 中，可随时调整优化。任务可追溯可复现：通过 --resume 恢复会话现场，任何分析过程都可回溯、可验证。

**Skill层核心组成**

```bash
gateway-route-vuln-analyzer/├── SKILL.md                        # 核心：漏洞分析主流程│   ├── 检测决策树（Step 1-4）│   ├── 危害评估规则│   └── 报告输出模板├── references/│   ├── unauthorized_patterns.md    # 越权漏洞模式库│   ├── logic_flaws.md              # 逻辑漏洞检测指南│   ├── data_classification.md      # 数据敏感性分级│   └── report_template.md          # 标准化报告模板└── scripts/    └── mcpcli-gateway              # CLI入口（Token优化）
```

**MCP 工具集设计**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**三**

**漏洞检测方法论（以越权为例）**

**越权漏洞精细化分类**

基于公开漏洞案例库分析，细分越权：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**检测决策流程**

检测分四步，前两步设有短路退出以降低成本。 **路由配置检查：** 检查 auth\_config.public 和 required\_scopes，配置无异常则跳过后续审计； **登录态识别：** 遍历调用链查找认证节点，标准认证路由直接信任，跳过代码审计； **代码审计** **（三维检测）：** 检查权限注解（@PreAuthorize）、用户 ID 来源（登录态 vs 请求参数）、所有权校验（DB 过滤 vs 代码显式校验）； **精细化危害评估：** 区分越权读取（数据敏感性）和越权操作（利益流向），输出风险等级与修复建议。

**精细化危害评估机制**

**越权读取 - 数据敏感性评估**

依据《数据安全法》确立的数据分类分级保护制度及《网络安全法》关于网络运营者数据安全管理义务的相关要求，通过 AI Agent 对源代码文本分析（基于变量名、字段类型、接口定义等代码特征进行技术推断），对路由功能返回涉及的数据资产进行分级评估。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**越权操作 - 利益流向评估**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**四**

**技术优化：Token 成本降低 95%+**

**问题诊断**

通过对多个会话日志的深入分析，识别出 Token 消耗的关键问题：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Token 消耗热点：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**优化策略与效果**

**MCP → CLI 转换（mcp2cli）：核心优化**

***原理：*** 将 MCP 工具暴露为 CLI 命令，避免每次会话加载 MCP 上下文。

```nginx
# 优化前：MCP调用（需加载完整MCP上下文）Claude → MCP Server → 工具执行# 优化后：CLI调用（直接执行，无额外上下文）Claude → Bash → mcp2cli → 工具执行
```

**效果：** 节省 61% Token 消耗。

**工具返回值优化 ：关键优化**

**问题：** 无参数调用返回完整文件（最大 1.47MB ≈ 500K tokens）。 **解决方案：** 为 gitlab\_file 添加精准参数，实现按需提取。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**效果：** v2 vs v1 再节省 88%。

**Early-Exit模式**

**原理：** 标准认证路由直接信任，跳过冗余代码审计。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**效果：** 标准认证场景节省 50-70%。

**AI友好返回格式 YAML**

**原理：** YAML 天然比 JSON 的 Token 量更少，对 AI 阅读更友好，降低模型解析成本。

**五**

**模型选型原则与决策框架**

在路由安全审计场景下，模型选型需围绕准确率（Precision）与召回率（Recall）两大核心指标建立决策矩阵：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

最终选型：满足 P0/P1/P2 三重约束的最优模型。选型理由：在召回率 100% 的候选模型中，qwen3.5-plus 以更低的单位成本实现可接受的准确率，是批量场景下的最优解。

**局限性说明:**

测试集局限性：上述结论基于独立手工标注测试集（100 + 样本），与生产告警数据相互隔离，仅可作为基线参考依据。模型迭代风险：大模型迭代更新速度极快，市场中或存在性能更优、成本更低的全新模型，暂未纳入本次评测范围。

AI不是替代人工，而是放大安全工程师的能力：AI处理重复性筛查，人工聚焦深度分析和复杂判断。

**六**

**方法论沉淀**

**定制化漏洞分析能力沉淀：** 针对 API 越权漏洞场景，构建专属漏洞分析技能体系，持续沉淀检测规则与标准化分析流程，保障规则具备落地实战有效性。

**精细化危害评估体系：** 严格区分越权读取与越权操作两类风险行为，引入利益流向分析维度，规避一刀切式风险评级，评估更贴合业务实际风险。

**Token 成本系统化优化：** 通过 MCP→CLI 格式转换 + 代码精准按需提取 + Early-Exit 提前终止 三层优化方案，整体实现 Token 成本降幅 95%+。

**场景化分层模型选型：** 批量例行场景采用高性价比模型，核心关键场景启用高精度模型，在检测效果与使用成本之间实现最优平衡。

**七**

**误报分析与改进方向**

**误报根因分析**

基于已完成的复核告警深度分析，识别出以下主要误报原因及改进方案。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**针对性改进方案**

**强化信任边界追踪（解决 35% 误报）**

**问题：** AI 发现中间层没校验就停止，直接认为存在漏洞，未追踪到最终数据操作层。 **方案：** 在 Skill 中增加指导规则。

```js
发现校验就停止，发现缺失就继续必须追踪到信任边界，中间层不能下结论
```

**上下游参数一致性校验（解决 25% 误报）**

**问题：** 下游方法参数有越权可能，但上游调用时未传入资源ID。 **方案：** 分析Controller层Request对象，确认是否包含资源ID字段。如果上游Request中无资源ID字段，判定为"仅操作当前用户数据"。 **实施：** 在Skill中增加规则："优先检查Controller层入参，无资源ID则跳过越权分析"。

**Dubbo 配置信息补充（解决 10% 误报）**

**问题：** 内部网关转 Dubbo 传参信息 AI 无法获取，导致认证判断错误。 **方案：** 引入 Open 网关 Dubbo 配置信息（通过内部管理平台获取），新增 MCP 工具 get\_dubbo\_config，获取路由的 Dubbo 调用配置。 **实施：**

```bash
# 新增工具"get_dubbo_config": {    "description": "获取路由的Dubbo调用配置和参数映射",    "inputSchema": {"route_path": "string", "service_name": "string"}}
```

**代码内的响应体价值预判优化（解决 10% 误报）**

**问题：** AI 将无敏感信息的读操作误判为越权。 **方案：** 细化响应体敏感性判断规则。

```bash
不敏感（可忽略）： 纯状态码返回（code/msg/status） 通用配置信息（活动名称、时间、状态） 流程节点信息（taskId、nodeName）
```

**后续规划**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

八

**小结**

网关路由 AI 驱动审计是一个面向 API 安全场景的智能化交付范式，将规模化安全审计升级为 AI 自动化检测 + 精细化危害评估 + Token 成本优化的标准化机制。

**它回答的问题：** 如何在网关路由规模快速扩张的背景下，实现安全漏洞的全量自动化检测，同时将成本控制在可接受范围。

**它证明的事：** 多个高危外网漏洞的实际发现，验证了 AI 在代码审计场景的有效性。单条成本 ¥0.23，某大型业务集群全量扫描一轮不到 1 万元，成本完全可控。人机协同模式有效：AI 批量筛查 + 人工深度验证，既保证效率又确保准确性。

**它沉淀的方法：** MCP→CLI 转换、精准代码提取、Early-Exit 优化，可复用于其他 AI 安全审计场景。

**九**

**附录**

**标准化告警报告模板**

本项目输出标准化的漏洞分析报告，以下是模板结构：

```shell
## 漏洞分析报告
### 1. 路由信息 路由ID: [必填：从 analyze_route 返回的 route_id] 路径: [必填：分析的路由路径] 目标服务: [必填：目标服务名称] 描述: [必填：路由描述，如无则填"无"]
### 2. 接口功能分析 接口用途: [必填：简要说明接口用途] 业务场景: [必填：业务场景描述] 调用方: [必填：H5前端/APP客户端/小程序/其他服务] 数据敏感性评估:  - 涉及数据类型: [必填：PII/金融数据/订单信息/配置信息等]  - 敏感等级: [必填：critical/high/medium/low]  - 影响用户范围: [必填：全平台用户/特定用户群/内部用户等]

### 3. 调用链分析[必填：调用链树形展示，使用缩进表示层级关系，标记漏洞点]
示例格式：[网关入口] (总耗时)  └─ [认证服务]: [认证接口] (耗时) [认证节点]  └─ [业务服务A]: [业务接口] (耗时) [漏洞点]     └─ [业务服务B]: [数据库查询] (耗时)
关键中间件操作（只写与漏洞分析直接相关的部分）: SQL: [可选：列出执行的 SQL 操作类型，如 SELECT/INSERT/UPDATE/DELETE] Redis: [可选：如有 Redis 操作则填写] MQ: [可选：如有 MQ 操作则填写]
### 4. 漏洞详情
⚠️ 说明：- 如果发现漏洞，必须填写此章节- 如果未发现漏洞，填写"未发现漏洞"并跳过后续小节
#### 漏洞 1: [必填：漏洞标题]- 严重等级: [必填：critical/high/medium/low]- 类型: [必填：越权读取/越权操作/逻辑漏洞/竞争条件]- 漏洞位置:  - 服务: [必填：漏洞所在服务名称]  - 方法: [必填：漏洞所在方法名]  - 文件: [必填：文件路径:行号]  - 仓库链接: [必填：GitLab 代码链接]  - Trace ID: [必填：对应的 trace_id] 问题描述: [必填：详细描述漏洞原因和利用机制] 调用链位置: [必填：标注漏洞在调用链中的位置] 问题代码:  [必填：漏洞代码片段，包含行号] 漏洞危害:  1. [必填：直接危害]  2. [必填：间接危害]  3. 潜在连锁攻击: [必填：可能的连锁攻击场景]  4. 合规风险: [必填：法律合规风险] 修复建议:  1. [必填：具体修复方案]  2. [必填：具体修复方案]  3. [可选：额外加固建议]
### 5. 分析置信度- 置信度: [必填：高/中/低]- 依据: [必填：说明置信度的判断依据]
### 6. 局限性⚠️ 数据获取不全说明:| 限制类型 | 说明 | 影响范围 | 建议操作 ||----------|------|----------|----------|| [限制类型] | [说明] | [影响范围] | [建议操作] |
### 7. 二方包依赖- 涉及的二方包: [必填：group_id:artifact_id:version - 用途说明，如无则填"无"]- 源码获取: [必填：已获取/未获取/不需要]
### 8. 涉及的微服务⚠️ 重要：必须包含 commit_id 和 project_path
- [service_name1] (commit: [commit_id], project: [project_path])- [service_name2] (commit: [commit_id], project: [project_path])
```

**往期回顾**

1.[AI驱动：从运营行为到自动化用例的智能化实践｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544174&idx=1&sn=b87982ec3a52d256511e71ac0691c490&scene=21#wechat_redirect)

2.[生成式召回在得物的落地技术分享与思考](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544067&idx=1&sn=6dfd6e3f1948f4a36d30abf1e79ef6ef&scene=21#wechat_redirect)

3.[立正请站好：一个组件复用 Skill 的工程化实践｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544056&idx=1&sn=18bd6749a8e9b8ff2dde91b066a2526a&scene=21#wechat_redirect)

4.[财务数仓 Claude AI Coding 应用实战｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544050&idx=1&sn=ff7efc6c5e38359470b157514a275f89&scene=21#wechat_redirect)

5.[日志诊断 Skill：用 AI + MCP 一键解决BUG｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544017&idx=1&sn=eaceee1d1f4f672b2dd630a1b235eda3&scene=21#wechat_redirect)

文 /炁源

关注得物技术，每周三更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。

“

**扫码添加小助手微信**

如有任何疑问，或想要了解更多技术资讯，请添加小助手微信：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

安全 · 目录