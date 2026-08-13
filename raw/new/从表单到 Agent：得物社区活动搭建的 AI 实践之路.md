---
title: "从表单到 Agent：得物社区活动搭建的 AI 实践之路"
source: "https://mp.weixin.qq.com/s/hiOqwjA7Hb7LfJfJyYirnw"
author:
  - "[[航飞]]"
published:
created: 2026-08-08
description: "一场营销活动从策划到上线，运营要在三个系统间跳转 10 + 次、填写 40 + 个字段。我们用 AI 重新设计了这条链路 —— 从 “AI 帮你填表单” 到 “两阶段 Agent + 聚合工作台”。这篇文章记录的不是技术细节，而是这条路上的选择和反思。"
tags:
  - "read"
---
航飞 *2026年6月24日 18:30*

![图片](http://mmbiz.qpic.cn/mmbiz_gif/AAQtmjCc74DZeqm2Rc4qc7ocVLZVd8FOASKicbMfKsaziasqIDXGPt8yR8anxPO3NCF4a4DkYCACam4oNAOBmSbA/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

**目录**

一、项目背景

二、第一版探索与Agent CLI可行性评估

1.让 AI 帮你填表——但人还是主角

2.Agent CLI方案的可行性评估

三、第二版实现与组件模块协议

1.从"填表"到"审卡片"

2.选择 LangGraph 作为编排引擎

3.Interrupt / Resume：前后端的交互语言

4.运营视角：一场活动怎么搭

5.Capability Registry：一个壳装所有场景

6.组件模块协议：把差异封进模块

四、第三版设计与工程实践

1.从"我有文档"到"帮我写文档"

2.两阶段架构

3.Stage 1：活动方案生成 Skill

4.Stage 2：聚合工作台

5.表单托管runtime：一个务实的工程妥协

五、架构全景

六、实践中的取舍

七、总结与展望

**一**

**项目背景**

一场营销活动从策划到上线，运营要在三个系统间跳转 10 + 次、填写 40 + 个字段。我们用 AI 重新设计了这条链路 —— 从 “AI 帮你填表单” 到 “两阶段 Agent + 聚合工作台”。这篇文章记录的不是技术细节，而是这条路上的选择和反思。

想象你是得物社区运营，下周要上一场 “夏季户外好物推荐” 活动，你需要打开 A 系统创建话题、切到 B 系统填写活动配置、再打开会场搭建系统配置组件，最后提交审核。三个系统各自独立，但字段高度耦合。活动名称改了一个字，A 系统和会场里也要跟着改，其中大量是重复录入。

**二**

**第一版探索与Agent CLI可行性评估**

**让 AI 帮你填表——但人还是主角**

我们的第一反应是：让 AI 帮运营填字段。做法是一个 5 步表单向导，AI 在第一步解析策划文档，后续步骤中预填字段：AI 的能力来自两个 Dify Workflow（Dify：开源的 LLM 应用开发平台）。第一个负责把策划文档解析成结构化字段，第二个负责把解析结果与系统的下拉选项做语义匹配。效果上，运营从 “全部手填” 变成了 “AI 预填 + 人工校验”。

上线后发现，操作时间缩短了，但远没有达到 “质的飞跃”。 **原因很简单：范式没有变。** 运营仍然是流程的主体，AI 只是预填了一部分字段，你还是得理解每个字段、按顺序走完 5 步、在三个系统间跳转、自己判断 AI 填得对不对。更具体的问题：

- **不可逆** —— 文档解析错了就得从头来；
- **AI 是黑盒** —— 调用需要 5-15 秒等待，过程中没有真实反馈；
- **组件硬编码** —— 只支持一个模板、5 个组件；
- **没有持久化** —— 刷新浏览器进度丢失。

**第一版给了我们一个重要认知：如果 AI 的角色只是 “帮你填字段”，它永远不会带来质变。** 真正的变化应该是 ——AI 来驱动流程，人只在关键节点做确认。这个认知和 AI 产品领域的规律一致：AI 产品的价值跃迁，几乎都发生在 “AI 从辅助工具变成流程主体” 的那个拐点上。GitHub Copilot 从 “行级补全” 进化到 “Copilot Workspace”，ChatGPT 从 “对话” 进化到 “GPTs+Actions”，都是同一个拐点的不同表现。

**Agent CLI方案的可行性评估**

在决定重写之前，我们评估了一个更激进的方向：Agent CLI。OpenCode CLI、Cursor、Claude Code 这类工具展示了另一种可能 —— 用自然语言指导 AI Agent 完成整个开发流程。理论上，会场搭建也可以用类似方式：运营说 “我要做一个夏季户外主题活动”，Agent 自主完成话题创建、活动配置、组件搭建，完全不需要结构化的 UI 卡片。

我们坚信这是未来，但当前落地有三个硬性障碍：第一，Agent 对会场的业务约束没有 “体感”；第二，Agent 无法获取实时状态；第三，Agent 的操作缺少审计与可解释性。这让我们意识到：需要在 “完全自主的 Agent” 和 “纯人工操作” 之间找到合适的位置。

Anthropic 的 Agentic 系统复杂度光谱正好提供了这个框架 —— 它将 AI 系统的自主性从低到高分成多个层级。我们的工作流大致对应光谱中间的 Prompt Chaining + Routing + Human-in-the-loop 组合。这不是光谱上最复杂的位置，但对我们来说是最合适的位置。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**三**

**第二版实现与组件模块协议**

**从"填表"到"审卡片"**

第二版是一次架构级的重写。核心理念用一句话概括：把运营从 “流程执行者” 变成 “流程监督者”。运营要做的事情缩减为两件：提供信息 —— 粘贴一份飞书策划文档链接；关键确认 —— 在 AI 弹出的结构化卡片上做校验和微调，其他所有事情（抓取文档、解析字段、创建话题、创建活动、复制会场模板、配置组件）全部由工作流驱动完成。在选技术方案之前，有一个更根本的问题需要先回答：我们需要的是一个 Workflow（工作流）还是一个 Agent（智能体）？

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

我们的会场搭建流程有明确的步骤（解析 → 选组件 → 补字段 → 确认 → 构建），每步的完成条件是确定的，而且对正确率有极高要求。这显然更适合 Workflow 模式。但这不意味着完全不用 Agent 能力。在局部场景中 —— 比如 AI 改写规则文案、理解自然语言修改组件配置 —— 我们使用了 Agent 式的 LLM 调用（给 LLM 工具，让它自主决定如何完成这个局部任务）。

**一个实用的经验法则** **：** 如果你的业务流程可以被画成一张有限状态机图，那就用 Workflow；如果它更像 “给定一个目标，让 AI 自己想办法达到”，那就用 Agent。大多数企业级场景是两者的混合 —— 大框架用 Workflow 保证可控，局部节点用 Agent 提供灵活性。

这个区分在行业中越来越被重视。LangChain 的创始人 Harrison Chase 在多个场合强调过：当前大部分成功的 AI 应用都是 Workflow 而非 Agent。Klarna 的 AI 客服系统被广泛报道为 “Agent”，但从架构上看，它更接近一个精心设计的 Workflow—— 有明确的意图分类路由、有标准化的工具调用流程、有人工升级（escalation）机制。真正在生产环境中跑 “完全自主 Agent” 的案例仍然非常少。

**选择 LangGraph 作为编排引擎**

明确了需要 Workflow 之后，我们评估了多个方案，最终选择了 LangGraph 作为编排引擎。LangGraph 是 LangChain 团队推出的状态编排引擎，MIT 开源。它用有向图定义 AI 工作流：每个节点是一个处理步骤（可以是 LLM 调用、工具调用或人工确认），边定义了步骤之间的流转条件。内置 Checkpointer 机制可以持久化每个会话的完整状态，支持中断后恢复。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

在我们的系统里，LLM 不是 “决策者”，而是 “节点内的执行者”—— 在明确定义的节点里做信息解析和文案生成，不参与流程路由。

**Interrupt / Resume：前后端的交互语言**

整个前后端的交互基于 LangGraph 的 interrupt/resume（中断 / 恢复）机制。 **Interrupt / Resume 是什么？** 可以把它理解为 “程序的暂停和继续”。当后端流程执行到需要人类输入的步骤时，调用 interrupt () 暂停整个图的执行，同时把一个结构化的数据包（payload）发给前端。前端根据数据类型渲染对应的 UI 卡片。用户操作完后，前端通过 Command (resume=value) 把结果推回去，图从断点处继续执行。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

结合 LangGraph 的 interrupt 机制和 LangChain 的 Human-in-the-loop 文档，人工介入通常覆盖几类动作：Approve / Reject：审批或拒绝——适合高风险操作前的确认，Edit：编辑 Agent 的动作、状态或中间结果——适合人工修正 AI 的输出，Respond / Input：提供额外信息或补充反馈——适合 AI 无法自行获取的数据，我们的 6 个中断点对应了这几类模式的混合：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**运营视角：一场活动怎么搭**

以"夏季户外好物推荐"活动为例：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

全程在同一个对话界面完成，不需要跳转到其他系统。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**Capability Registry：一个壳装所有场景**

前端没有把 “会场场景” 写死，而是通过一套能力注册表（Capability Registry）来动态挂载不同场景的 UI。什么是 Capability Registry？类似于插件系统 —— 每个业务场景是一个 “能力模块”，向统一的交互壳注册自己的 UI 贡献（欢迎态、中断卡片、结果展示等）。交互壳不关心具体业务，只负责调度和渲染。新增场景时只需要注册一个新模块，不需要改壳的代码。这个设计思路与微前端架构中的 Module Federation 有相似之处 —— 都是将 “壳” 和 “能力” 解耦，让新能力可以独立开发、独立注册。不同之处在于我们的粒度更细：不是整个页面模块的联邦，而是 UI 贡献点（欢迎态、卡片、结果展示）级别的注册。

第二版把体验从 “填表单” 推进到 “审卡片”：AI 从 “帮你填字段” 升级为 “驱动整个流程”，支持中断恢复 —— 关掉浏览器再打开可以继续。能力注册表的设计让系统具备良好扩展性，当前已接入会场搭建、动态筛选和通用聊天三个场景，未来新场景只需实现对应的能力模块即可。但第二版仍有一个前提：运营已经有一份策划文档。很多真实业务场景里，运营一开始并没有文档，只有一个活动想法。这直接推动了第三版。

**组件模块协议：把差异封进模块**

**为什么需要一套协议**

在进入第三版之前，需要先讲第二版里最重要的一层设计 —— 组件表单模块协议。它解决了一个核心的业务扩展性问题。会场由多个组件构成：头图、动态 Feed、活动任务、规则说明、Banner、瓜分激励等。每个组件的配置逻辑差异很大。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

第一版的做法是在一个文件里写条件判断分发。每加一个组件就要改中心调度文件，组件的业务逻辑散落各处。5 个组件时还能接受，16+ 个组件就不可行了。

**生命周期：每个组件的统一节奏**

我们把每个组件抽象成独立模块，定义统一的生命周期：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

最重要的规则是初始化阶段不产生副作用（比如调后端创建资源）。真正会产生写操作的动作必须放在 “构建前” 阶段，即用户明确点了 “构建会场” 之后。这个规则避免了一个真实 bug：有组件在初始化时偷偷调了后端保存接口，导致用户只是打开卡片看了一眼，系统就已经创建了活动数据。

**双轨注册：显式选择 + 条件注入**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

新增组件时只需要实现模块接口并注册到对应轨道，不需要改任何调度逻辑。这是协议级设计的核心优势 —— **开闭原则** （Open-Closed Principle）：对扩展开放，对修改关闭。这种 “根据上下文自动注入，用户不感知” 的模式，在软件架构中其实很常见： **把 “是否需要某个组件” 的决策从使用者手中拿走，交给系统根据规则自动判断。** 好处是使用者的心智负担更低，坏处是系统行为变得更难预测 —— 所以我们的条件注入轨道会在工作台上展示 “已自动注入” 的提示，让运营知道系统替她做了什么决定。

**声明式位置编排**

组件输出的不只是配置数据，还可以声明位置意图 ——“我希望被放在哪个组件的前面或后面”。以 Feeds 组件为例，一个活动可能有多条 Feed，其中 “竖向那条” 要放到页面底部。Feeds 模块不需要知道 “底部在哪里”，只需要声明 “这条竖向 Feed 想放在页面末尾”。三层关注点分离，每层只关心自己的事。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**四**

**第三版设计与工程实践**

**从"我有文档"到"帮我写文档"**

第二版解决了 “会场搭建流程如何被 AI 驱动” 的问题，但它有一个隐含前提：运营已经有一份策划文档。实际业务中，很多运营连文档都没有 —— 只有一个模糊的想法，就被要求先写一份结构化的飞书文档，再粘贴到 Agent 里。策划生成和会场搭建是两种不同范式：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这两种范式的差异，决定了我们需要一个两阶段架构来分别承载：第一阶段解决"从想法到策划文档"，第二阶段解决"从策划文档到会场配置"。

**两阶段架构**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**Stage 1：活动方案生成 Skill**

Stage 1 Skill 的核心约束是只读不写 —— 只查询候选数据（预算池、类目、标签、历史会场），不做任何写操作。所有写操作（创建话题、创建活动、复制会场、提交审核）全部由 Stage 2 闭环。这个 “只读” 约束不是技术限制，而是权限模型的设计选择。在 Agent 系统中，一个反复出现的架构决策是：AI 的能力边界应该在哪？

- **读权限：** AI 可以查询任何数据 —— 风险低，最多是查到不相关的结果；
- **写权限：** AI 可以创建 / 修改数据 —— 风险中等，可能产生脏数据；
- **发布 / 审批权限：** AI 可以影响线上 —— 风险高，直接影响真实用户。

Stage 1 只给读权限，Stage 2 逐步开放写权限，发布权限则要求人工确认后触发。这个分级和 AWS 的 IAM 最小权限原则（Principle of Least Privilege）是一脉相承的：每个主体只拥有完成当前任务所必需的最小权限集。

引导策略是渐进式的，不一次性要求填完整表单：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E) ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

最低三件套：活动名称 + 活动时间 + 至少一个话题。其他信息按对话进度逐步追问。 **渐进式信息收集：一个 UX 模式。** 这种 “不一次问完所有问题，而是按对话进度逐步追问” 的策略，在 UX 设计中叫做 Progressive Disclosure（渐进式披露）。Nielsen Norman Group（NNG）对这一经典 UX 模式做过系统阐述和案例推广，但它并不是由 NNG 首次提出的概念。核心思想是：不要一次给用户太多信息或太多选择。在用户需要的时候、以用户能理解的方式、提供恰好足够的信息。

**Stage 2：聚合工作台**

Stage 2 是一个独立的页面，不是聊天壳里的一个面板。它承载的是更偏生产操作的密集交互。中栏预览是核心升级。它复用了搭建器已有的 H5 编辑页面，在上面覆盖了一层可交互的遮罩。运营可以点击预览里的任何组件，右侧自动展示该组件的配置表单。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E) ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这个设计的关键在于 “不重新实现预览器”—— 搭建器已经有完整的会场渲染能力，我们只是在外层加了交互层。草稿实时同步保证操作不丢失：每次组件增删改或属性修改都会即时更新预览，同时异步持久化到后端。

组件级 AI 改造有两个层次： **显式 AI 辅助面板** ——部分组件支持在 “AI 辅助” 和 “原表单” 之间切换，运营可以用自然语言描述想要的效果； **通用自然语言编辑** ——在工作台对话里输入修改需求，系统把当前选中的组件上下文交给后端的编辑子流程处理。

工作台中 “用自然语言修改组件” 的能力 —— 比如 “把这个 Banner 的标题改成夏季清凉风格”—— 是当前 AI 辅助设计（AI-Assisted Design）领域的一个缩影。这个领域正在快速发展。几个值得关注的产品和方向：Figma AI：Figma 正在将 AI 能力嵌入设计工具 —— 自动布局建议、文案生成、设计稿搜索。它的做法和我们类似：AI 做建议，设计师做决定。Vercel v0：用自然语言描述生成 React UI 组件代码。它走的是更激进的路 ——AI 直接生成完整代码，而不是修改已有组件的属性。Adobe Firefly：Adobe 在 Photoshop 和 Illustrator 中嵌入的生成式 AI，走的是 “AI 在画布内局部生成，人工在全局把控” 的路线。

这些产品的共同模式是：AI 做局部生成 / 修改，人做全局决策。完全用 AI 替代设计师的产品（如一些 “AI 自动建站” 工具）目前还很难在专业场景中落地 —— 和我们的会场搭建面临同样的问题：正确率和品牌一致性要求太高。

**表单托管runtime：一个务实的工程妥协**

工作台右侧的组件表单运行在一个独立构建的子项目中。原因是搭建器的组件表单依赖特定的运行时环境和 Formily 表单引擎，与我们的前端技术栈不兼容。我们没有重新实现几十个组件表单，而是做了一个独立构建，复用搭建器原版的运行时，通过消息协议与主页面通信。这是 “避免重复开发” 的工程妥协 —— **虽然增加了架构复杂度，但把有限的开发精力放在了真正新增的价值上（预览交互、AI 辅助、草稿同步），而不是重造已有的轮子。**

**五**

**架构全景**

**系统分层**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**六**

**实践中的取舍**

- **AI与人的分工边界**

"全 AI 控制"现阶段不现实。会场组件业务约束复杂：字段来自多个外部系统，规则有优先级，部分组件会触发真实资源创建。最终方案是 AI 负责信息提取、草稿生成、字段改写和推荐，代码负责流程、结构、校验和副作用时机。

- **交互方式的选择**

结构化 UI 不是"不够 AI"，而是对运营认知负担的尊重。让运营在下拉列表里选预算池，比用自然语言描述然后让 AI 去猜更高效准确。最好的交互方式是混合的：自然语言描述意图、结构化 UI 确认细节、可视化预览检查结果。

- **副作用控制的时机**

组件模块协议最重要的规则之一：初始化阶段不产生副作用，只有用户明确确认后才允许写操作。这是 LangGraph 的 Edit Action 保护机制，决定了系统是否会在用户未确认时产生脏数据。

- **工程妥协的边界**

Form Host 是工程妥协但必要。完全重写成本高且容易引入行为差异。复用旧生态让工作台能把有限的开发精力放在真正新增的价值上。

- **信任建立的方式**

假进度条是过度承诺。AI 产品的信任是慢慢建立的，每一个"假反馈"都在消耗信任。Microsoft 的 HAX 设计指南建议让用户清楚系统为什么做了它做的事——我们的每张中断卡片都在做这件事，不只是给运营一个表单，还解释了"为什么需要你填这些字段"和"AI 已经做了什么、还缺什么"。

**七**

**总结与展望**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这个项目的演进路径：

- **第一版：** AI 帮你填字段，人还是主角。效率有提升，但没有质变。
- **第二版：** AI 来开车，人来踩刹车。从 “填表单” 变成 “审卡片”，运营从流程执行者变成流程监督者。
- **第三版：** AI 不仅开车，还帮你规划路线。策划生成前移到 Stage 1，会场搭建落到 Stage 2 聚合工作台，运营从 “我得先写文档” 变成 “AI 帮我写文档”。

下一步可能会是什么？也许是 Agent CLI 方案的成熟，让更多操作可以通过自然语言完成；也许是更多场景的接入，让同一套架构支撑更多业务；也许是 LLM 能力提升后，“组件全 AI 控制” 变得可行。但无论如何演进，有三条原则不会变： **流程可控** —— 不能让 AI 自由发挥到不可预测的地步； **正确率优先** —— 会场配置错误直接影响线上运营； **运营负担更低** —— 技术再酷，最终要让运营觉得好用；技术形态会变，业务约束不会变。

**往期回顾**

1.[从埋点需求到规则资产：Hermes Agent 重构得物数仓工作流](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247545376&idx=1&sn=62f5170e2075ef7beaf095de749fec51&scene=21#wechat_redirect)

2.[让 Claude Code 拥有自我进化和记忆系统｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544916&idx=1&sn=25d5c20a7a9d2b0dfed78eaf25598717&scene=21#wechat_redirect)

3.[用 LLM Agent 重构告警排查流程｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544879&idx=1&sn=4d1a92199b785d5d3d3de1758545adba&scene=21#wechat_redirect)

4.[得物技术在 AICon 关于大模型与 Agent 技术实践分享来袭！](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544742&idx=1&sn=95a1c9a7738bbda6f89f887df7767534&scene=21#wechat_redirect)

5.[HorizonVault 技术深潜：如何在 HDD 上做出 100GB/s+ 级大吞吐分布式存储｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544708&idx=1&sn=cc8d064185a5bdc27fd7748f0958182d&scene=21#wechat_redirect)

文 /航飞

关注得物技术，每周三更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。

“

**扫码添加小助手微信**

如有任何疑问，或想要了解更多技术资讯，请添加小助手微信：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

AI · 目录