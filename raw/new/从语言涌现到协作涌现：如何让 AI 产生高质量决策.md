---
title: "从语言涌现到协作涌现：如何让 AI 产生高质量决策"
source: "https://mp.weixin.qq.com/s/pV-f8WzoYSDxpEUk0uQdFw"
author:
  - "[[吕若凡]]"
published:
created: 2026-08-08
description: "AI NATIVE组织/业务自迭代 由AI 能否产生高质量决策决定。"
tags:
  - "read"
---
吕若凡 *2026年5月27日 18:30*

这是2026年的第17篇文章

（ 本文阅读时间：约20分钟 ）

## 前言

“涌现”不是一个玄学词。在复杂系统里，涌现指的是：系统整体表现出某种单个组成部分并不具备、也没有被直接写死的性质。

这种性质来自大量局部单元之间的交互。水分子本身没有“波浪”，神经元本身没有“意识”，单只蚂蚁没有“城市规划”，但当它们以某种密度、规则和反馈连接起来，整体就会出现新的层级。大模型的智能，本质上也可以这样理解。

单个 token 没有智能，单句话也没有智能。但当海量文本、语义结构、知识关系、推理痕迹、行动描述被压缩进一个语言模型里，模型通过预测下一个词学到的就不只是语法，而是世界在语言中的投影。

它没有被显式编程去“理解业务”“做产品判断”“写代码”，但在足够规模的语言训练之后，这些能力从语言结构中长了出来。这就是第一层涌现：文字规模足够大，语言模型中涌现出智能。

这篇文章想讨论的是第二层：当智能体之间的上下文交互足够充分，群聊里会不会长出更高质量的协作判断和决策。

前置观点：AI Native 组织/业务自迭代 由 AI 能否产生高质量决策决定。Agent 集成再多的 skill 和 CLI 也只是流程自动化，而非业务自迭代。希望本文能为「 AI 产生高质量决策」这一目标的前进迈一小步。

借用吴妈的AI Native 组织的定义：任何应用、任何任务，都要拆解到一个全链路AI驱动的流程中。如果中间有个环节要人去介入控制，那么就不叫AI Native。

业务自迭代：浅薄地定义一下：人只需要给出目标（非需求），AI 围绕目标产出方案、拆解、执行、完成；并不断地根据产品推出效果，优化，直至达到目标。

## 01

这篇文章从哪里开始

我对 AI 研发的理解，不是一开始就走到“协作涌现”。 中间经历过几次明显的转向。

第一阶段，大约在 2025 年 11 月，我们基于 Aone Agent 做了一套研发流程页面。那套系统的重点是把软件研发拆成明确阶段：PRD 输入、任务澄清、技术方案、生码执行、代码评审、知识沉淀。每个阶段可以创建一个 Aone Agent 会话，由 Agent 生成阶段产物。

这套系统的本质是“流程自动化”。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这套方式比纯人工流程、vibe coding 和 spec coding 都往前走了一步。它把阶段、产物、状态推进、会话链接、模板配置都做成了产品能力，解决的是“每一步怎么自动化生成”的问题。

但它仍然有一个明显前提：流程必须先被人定义好。

系统知道下一阶段是什么，知道每个阶段应该产出什么字段，知道什么时候推进，知道哪个模板负责哪类内容。AI 在这里更像某个阶段里的增强执行器。它可以提升效率，但它不真正参与流程本身的生成、修正和重组。

第二阶段，是 2026 年年初 OpenClaw 这类 Agent 框架出现之后，我们发现模型和 Agent 能力已经足够强，不一定要继续用代码把研发流程一格一格写死。于是我们基于 OpenClaw 框架做了一套 AI 多 Agent 协同开发系统（ agent调度方式是 Supervisor / Router，后面会对比各种 agent 调度方式）。

这一步的变化很大。

它不再只是“点一个按钮，生成某阶段产物”，而是可以让 Agent 自己读取需求、识别多应用仓库、推断技术栈、生成配置、拆解跨应用 Spec、调度代码修改和验证。全链路自动化开始成立。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

再往后看，基建团队提供了越来越强的 AI 基建工具，离线表cli、。一个团队只要写出足够完整的提示词，就可以让 AI 接管大量日常重复手工流程。

以我们团队自建的一些技能为例，它已经可以覆盖很多高频单点场景：

\-通过自然语言或页面截图识别业务域、业务线和具体页面。

\-根据问题类型自动路由到代码仓库、SLS 日志、MySQL 在线库、ODPS 离线表、钉钉文档。

\-用 A1 发现应用、仓库、研发信息，用 normandy-cli 查询运维资源和日志，用 mw-cli-skill 查询 Diamond、HSF、MetaQ 等中间件配置。

\-自动初始化业务域知识图谱仓库，沉淀业务线、页面、日志、数据库、离线表和问题案例。

\-排查问题后通过 DMS 查询在线数据，验证代码修改或接口逻辑是否真实正确。

\-在多应用研发场景下克隆仓库、推断技术栈与应用拓扑、生成协同开发配置和跨应用 Spec 。

这些能力已经很强。它们证明了一件事：只要工具足够完整，提示词足够具体，AI可以接管很多重复、稳定、可描述的手工流程。

即便很多人宣称，已经完成了7\*24H写代码，但这还不是 AI Native 组织。也不是业务自迭代，这只是流程的自动化。

因为这些场景大多还是单点自动化。它们能完成一个动作，能跑通一条流程，能替代一段人工操作，却还没有形成组织级的自迭代能力。真正难的不是“怎么使用工具”，而是“系统如何长出脑子,给出决策”。他不能由一个目标，拆解成可落地的完整能力和实现，这些都依赖于 Agent 持续的高质量决策。

今天这篇文章的重点就在这里： 不是讲怎么查日志、怎么写 skill、怎么跑代码生成。 而是讲：当多个智能体共享上下文、互相修正、沉淀任务、执行验证、保留记忆时，一个系统如何从“会用工具”走向“会形成判断”。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

所以，Agent Room 不是从“多弄几个 Agent 聊天”开始的。 它是从几次反思里长出来的：流程自动化不等于智能组织；全链路自动化不等于协作涌现；工具接管不等于业务自迭代。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

概念先放一放。先看两个现场，看看“涌现”到底表现成什么样。

下文把这个形态称为 Agent Room。它不是 Codex 或 Claude 里那种预设好的专家团，而是把多个角色放进同一个上下文场里，让它们自己判断是否该介入、该沉默、该推进。(目前基于codeX cli实现，请先忽略丑陋的UI!)

## 02

## 两个现场：协作涌现长什么样

## 示例 1：需求自迭代，不止是研发流程自动化

## 一类现场是需求自迭代。

## 通过集成集团的基础设施，系统可以自动创建变更、创建分支、创建项目环境，并完成前后端应用部署。如下图的任务拓扑所示，这些能力主要依赖 DAG 编排，也离不开中间件团队提供的基础建设。

但这篇文章的重点不在“AI Agent 能跑完整条流程”。这只是地基。

真正值得讨论的是agent room里发生的那条暗线。如果只是流程自动化，系统很容易进入“产品提需求 -> 开发改代码 -> QA 测试”的直线。但 Agent Room 不是这么走的。产品先把核心边界和非目标钉住：这次只解决当前主路径问题，不扩展到历史修复、旁路流程和其他非目标场景。QA 也没有等开发完成才进场，而是提前把正确性、幂等性、并发风险、异常状态和重复操作变成发布前置。架构也没有顺着“复用现有逻辑”往下走，而是指出直接复用旧路径可能带来状态错乱、重复处理或边界失控，要求新增更明确、更可验证的专用实现路径。

这就是协作涌现开始出现的地方：没有一个角色单独拥有完整答案。产品给出业务边界，QA 把验证风险前置，架构修正实现方向，全栈在门禁不满足时主动停下来，要求先补执行 DAG、变更记录、研发分支和契约冻结。后面系统又继续把多仓代码改动、前后端变更、依赖版本、CI 构建、预发环境、部署状态和验证证据都纳入同一个房间状态里。

更让我惊讶的是，QA 会主动做判断：当开发完成事实不足以进入测试时，它会拒绝验收，并 @开发补充更完整的测试准入证明。这不是人工在旁边提醒，而是多 Agent 在共享上下文中形成的协作闭环。

所以 Agent Room 的价值不只是“自动创建了变更、分支和环境”。真正重要的是：这个房间能在共享上下文里不断改写自己的判断。

这些判断不是某个预设流程节点提前写死的，而是多个角色在同一份上下文里反复修正出来的。DAG 负责把共识沉淀成依赖，Memory 负责让旧阻塞不反复污染新决策，Runtime 负责真实执行，Artifacts 负责留下证据。这个闭环，才是从工具自动化走向协作涌现的关键。

示例 2：工单排查-单case修复-产品确认-代码修复的自驱动

一次普通工单排查里，技术支持 Agent 先查 SLS，发现日志报错符合预期。它没有停在“日志正常”的结论上，而是继续把问题交给开发 Agent，核对代码逻辑和历史事件。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

开发 Agent 看完代码之后，直接把产品拉进房间。这个动作出乎我意料：我配置的初始角色只有技术支持和开发，提出的问题也只是“排查工单”，没有要求改代码。但它判断这里可能会涉及代码改动，而且也不能直接进入开发，需要产品确认是否作为需求迭代。也就是说，系统自己补上了“问题排查-单case修复-产品确认-代码修复”这一层自闭环。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

后续几个角色明确分工，重新还原现场，最后得到的结论和工程师判断一致。

## 03

## 涌现的形式化定义

设一个系统由多个局部单元组成：

每个局部单元有自己的状态 ，系统整体有一个宏观状态 。如果整体状态 中存在某些性质，无法由任意单个 单独解释，而必须依赖多个单元之间的关系 ，我们就说这个性质是涌现的。

可以用一个简单的信息论形式描述：

这里 是互信息。

互信息可以简单理解成：知道一个变量之后，能减少你对另一个变量多少不确定性。

比如有两个变量： `X` 是某个 Agent 的观点、证据、观察， `Y` 是最终正确决策。如果你知道 `X` 之后，对 `Y` 更有把握了，那么 `X` 和 `Y` 之间就有互信息。

用公式说，就是 `I(X;Y)=H(Y)-H(Y|X)` 。它的意思是：互信息 = 原本对 `Y` 的不确定性 - 知道 `X` 之后对 `Y` 剩下的不确定性。

如果 `X` 和 `Y` 完全无关，知道 `X` 对判断 `Y` 没帮助，互信息就是 0。如果 `X` 能完整决定 `Y` ，互信息就很高。如果 `X` 只能提供一点线索，互信息就是一个中间值。

放到 Agent Room 里，产品、架构、开发、QA 各自的观点，和最终好决策之间分别有一定互信息；但当它们在共享上下文里交互后，整体系统可能产生比任意单个角色更多的有效判断信息。

如果整体对的解释力显著大于任何单个部分，说明系统存在整体层面的新增信息。更严格一点，可以看协同信息：

这个公式不是为了把产品做成数学游戏，而是为了说明一件事：涌现不是“组件很多”本身，而是组件之间的关系产生了额外信息。

这正是 Agent Room 关心的问题。

如果每个 Agent 只拿到自己的小任务，它们就是孤立变量 。如果所有 Agent 看到同一个上下文，并持续把自己的专业判断写回公共空间，它们就构成了一个交互系统：

其中：

\- 是角色集合，例如产品、架构、全栈、QA、运维、数据研发。

\- 是第 轮的消息交互关系。

\- 是当前共享上下文。

\- 是任务账本，包括 owner、状态、依赖和验收口径。

Agent Room 的核心目标，就是让足够完整、足够有约束、足够可执行，从而让整体判断好于任意单个 Agent 的判断。

我们希望得到的是：

其中，表示第个 Agent 在局部上下文中独立形成的判断， 表示协作室在共享上下文、任务账本和多角色交互之后形成的整体判断。

也就是说，房间里的集体判断质量，要高于任何单个 Agent 在局部上下文中的判断质量。

## 04

## 传统 Agent 编排在编排什么

现在常见的 Agent 编排，大多是在编排任务，而不是编排上下文。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这些方式并不是错。它们让系统更可控，也更容易工程化。但它们有一个隐含前提：任务可以被提前正确拆解，输入输出边界可以被提前定义清楚。

不过，需要注意的是，真实的软件开发往往并非如此。 需求在讨论中变清晰，风险在实现中暴露，验收口径在测试前才被补齐，发布路径在环境里才显出阻塞。很多关键判断不是来自“下一步该谁做”，而是来自“谁看到了同一份上下文，并从自己的角度发现了别人没看到的问题”。

这就是任务编排和上下文编排的分界。

| 编排方式 | 典型运行方式 | 它擅长什么 | 主要风险 |
| --- | --- | --- | --- |
| 流水线 / DAG | 像发布流水线： `拉代码 -> 编译 -> 单测 -> 部署日常 -> 部署预发 -> 回归 -> 发布` 。每一步完成后，才触发下一步。 | 明确流程、  稳定执行、  可追踪 | 前期拆错后很僵硬 |
| Planner-Executor | 用户说“把登录页改成中文”，Planner 先拆成“找页面、改文案、调样式、跑测试”，再把这些子任务交给 Executor 执行。 | 开放任务拆解、  单点规划 | planner 误判会传导到所有执行者 |
| Supervisor / Router | 用户问“线上机器 CPU 高”，Router 判断交给运维；用户问“按钮样式错了”，Router 判断交给前端。未被路由到的角色通常看不到完整问题。 | 入口清晰、  降噪 | 调度者决定谁能看见什么，容易漏掉跨角色洞察 |
| Manager-Worker | Manager 把一个大重构拆成 10 个文件修改任务，分给多个 worker 并行处理；worker 只回报自己的 diff，最后由 Manager 汇总。 | 并行执行、  规模化产出 | worker 间上下文弱，集成压力回到 manager |
| 辩论 / 多专家投票 | 多个专家分别评价“方案 A / B / C 哪个更好”，各自给理由，最后由裁判总结或投票。 | 方案比较、  风险评估 | 容易停留在观点层，没有执行和验收闭环 |
| Agent Room | 用户只 @ 产品提出需求；产品冻结边界，QA 在同一上下文里补验收风险，架构修正实现路径，全栈开发接任务真实改代码，DAG/Memory/Artifacts 把共识、依赖和证据沉淀下来。 | 共享上下文、  多视角修正、  任务沉淀、  真实执行 | 需要强约束控制噪音和轮次 |

这里不是说 DAG、Router、Worker 这些方式没价值。相反，Agent Room 里面仍然需要 DAG 来执行确定流程，需要 Router 来做提醒，需要 Worker 去落地代码。区别在于：传统编排通常先决定“谁做哪一步”，Agent Room 先让相关角色看到同一份上下文，让判断在公共空间里被修正，然后再把已经收敛的共识沉淀成 DAG、任务和产物。

传统编排问的是：

`Who should do the next step?`

Agent Room 问的是：

`Who should see the same context, and what new judgment emerges?`

## 05

## 上下文损耗：为什么中心化编排会变窄

在 manager-worker 或 planner-executor 结构中，中心节点会对上下文做裁剪。裁剪是必要的，否则每个 worker 都会被信息淹没。但裁剪同时带来上下文损耗。

设完整上下文为 ，第个 Agent 实际拿到的上下文为 ：

上

上下文损耗可以表示为：

其中是条件熵。越大，说明 Agent 越不知道完整上下文里被裁掉了什么。

条件熵是指已经知道一部分信息之后，对完整信息还剩多少不确定性。

当任务是确定性的，不一定有害。比如“把 CSV 转成 JSON”，worker 不需要知道公司战略。但当任务包含需求取舍、架构边界、验收风险、线上约束时， 会直接降低判断质量。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Agent Room 不是取消裁剪，而是改变默认值。

传统系统默认“只给你该看的”。Agent Room 默认“你可以看到完整上下文，但你要克制发言”。这两个默认值，会导向完全不同的协作结构。

## 06

## Agent Room：

## 把智能体放进同一个上下文场

Agent Room 的基本单位不是 pipeline step，也不是 manager 派发的 job，而是一条群聊消息。所有 Agent 都在同一个房间里看到完整上下文。

产品能看到开发的实现顾虑，开发能看到 QA 的验收口径，架构能看到用户真正关心的取舍，QA 能看到决策为什么这样定。运维能提前发现发布路径、机器资源、中间件配置的风险；数据研发能从表、口径、离线链路判断业务结论是否可验证。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

关键在这里：同一份上下文，会被多种专业视角同时阅读。

产品看到目标和边界，架构看到结构和风险，开发看到实现路径和成本，QA 看到可验证性和回归缺口。运维能提前发现发布、资源、日志和线上风险；数据研发能从口径、表结构、上游任务和离线链路里判断业务结论是否站得住。

协作智慧不是从某个“更聪明的总控 Agent”里冒出来的，而是从这些视角在同一个上下文场里的相互修正中长出来的。

## 07

## 群聊不是无限发言系统

如果所有 Agent 都看到完整上下文，又都积极发言，系统会很快变成噪音机器。所以 Agent Room 的关键不是“让更多 Agent 说话”，而是让 Agent 知道什么时候不说话。

我们把 Agent 的发言看成一个带成本的动作。第 个 Agent 在第轮是否发言，取决于它预期带来的增益是否大于噪音成本：

其中：

●是这次发言带来的预期收益，例如新增事实、纠偏、冻结决策、推进任务。

●是噪音成本，例如重复、抢话、无效转述、制造额外队列。

●是噪音惩罚系数。

● 是发言阈值。

这条规则听起来简单，但非常重要：沉默是一等行为。

Agent Room 的设计里，所有人都能看见，但不是所有人都必须说话。@ 是提醒，不是权限。没有新增价值，就应该输出 `NO_REPLY` 。

## 08

## 讨论必须落到任务账本

群聊负责形成共识，但共识不能只停在文字里。否则系统会出现一种常见错觉：大家都觉得“聊完了”，但没有任何东西真正进入可执行状态。

所以 Agent Room 需要任务账本：

任务状态转移必须显示：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这套账本解决几个问题：

● 未指派任务不会被误认为正在执行。

● 已完成任务不会因为旧消息被反复阻塞。

● 依赖未完成时，Agent 不会越权实现。

● QA 可以提前设计用例，但正式回归要等实现完成。

● 用户可以看到“谁在做什么、卡在哪里、下一步是什么”。

群聊提供上下文，任务账本提供状态，运行时提供执行。 三者缺一不可。

## 09

## Memory 系统：

## 让房间有连续性，但不被旧话绑架

群聊如果没有记忆，每次刷新、重启、进入下一轮迭代，都会退回“重新解释一遍”的低效状态。

但群聊如果只有“一坨”历史消息，又会出现另一个问题：旧判断、旧任务、旧阻塞会反复污染当前决策。比如一个任务已经完成，但 Agent 仍然记得“它还没完成”；一个发布前置已经被用户改口径取消，但后续角色仍然拿旧口径当 blocker。

所以 Memory 系统不是简单的聊天记录存档，而是分层、可检索、可失效的房间记忆。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

可以把房间记忆表示为：

每次 Agent 被调度时，不应该把所有历史消息都塞进 prompt，而应该根据当前目标做检索：

检索排序不能只看语义相似度。房间协作里的记忆有“权威性”和“新鲜度”。一个用户最新确认的 `[Decision]` ，应该压过三小时前某个 Agent 的 `[Proposal]` ；一个已经 `done` 的任务状态，应该压过旧消息里的“待完成”描述。

可以用一个加权函数表达：

这里最关键的是 authority 和 obslete 。

- 用户消息、明确的 `[Decision]` 、 `[Contract Freeze]` 、任务状态变更，权威性更高。
- 被新决策覆盖的旧结论、已完成任务的旧 blocker、失败后已重试成功的 runtime 日志，应该被标记为过期。
- `@我`
	/ `需求发起人` 只能由真实用户代表，AI 不能用用户身份生成回复；Memory 可以引用用户决策，但不能代替用户做决策。

Memory 系统的目标不是让 Agent “记得更多”，而是让 Agent 在正确的时间记得正确的东西。

更具体地说，房间里至少需要六类记忆：

| 记忆类型 | 记录什么 | 用来解决什么问题 |
| --- | --- | --- |
| 短期记忆 | 最近几轮对话 | 保持当前讨论连续 |
| 决策记忆 | `[Decision]` 、 `[Contract Freeze]` 、用户确认 | 防止旧口径反复阻塞 |
| 任务记忆 | 任务 owner、状态、依赖、验收 | 让 Agent 知道什么能做、什么已做完 |
| 运行记忆 | Codex CLI 事件、命令、文件 diff、错误 | 让执行过程可追溯、可重试 |
| 产物记忆 | DAG、验收报告、发布证据、风险清单 | 把过程沉淀成房间资产 |
| 领域记忆 | 业务域、仓库、表、应用、历史知识 | 让房间知道自己在处理哪个业务世界 |

这套系统也解释了为什么“刷新页面后上一轮会话找不到”是产品级问题。房间不是一个前端临时聊天框，而是一个有状态的协作容器。消息、任务、记忆、产物、runtime run，都应该有可恢复的持久化身份。

## 10

## DiT DAG 系统：

## 把群聊共识变成可执行拓扑

群聊负责产生判断，但判断要进入执行，必须变成结构。

DAG 系统就是这层结构化能力。它把房间里的决策、任务、依赖、执行动作、验证动作组织成一个有向无环图：

其中是节点集合， 是依赖边。一个节点可以是：

● 决策节点：例如“发布前置口径已改为 SNAPSHOT 制品”。

● 契约节点：例如“接口字段、状态枚举、错误码冻结”。

● 实现节点：例如“全栈开发修改消息持久化逻辑”。

● 验证节点：例如“QA 运行单测、浏览器 smoke、回归清单”。

● 运维节点：例如“查询预发环境、发布单、机器日志”。

● 数据节点：例如“核对离线表口径、分区、上游任务”。

● 产物节点：例如“生成验收报告、发布证据、风险清单”。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

DAG 的价值不是画图，而是解决三个很具体的问题。

第一，避免“大家都说完了，但没有人知道下一步谁来做”。

第二，避免“旧任务已经完成，但因为旧消息还在，系统不敢进入下一阶段”。

第三，避免“Agent 互相 @ 触发无限讨论”。DAG 可以明确告诉系统：当前哪些节点 ready，哪些节点 blocked，哪些节点 done，哪些节点根本不需要说话。

每个节点可以抽象成：

节点是否可运行，不取决于谁又 @ 了谁，而取决于依赖是否满足：

当节点运行完成后，它必须产生证据：

这里的 evidence 可以是测试输出、diff、命令日志、截图、发布单状态、SQL 查询结果、人工确认。没有证据的 `done` ，只能算口头完成。

DAG 还应该允许用户改口径。用户一旦确认新的 `[Decision]` ，旧 DAG 中受影响的节点不能继续作为 blocker，而应该被标记为 `waived` 或重新连边：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这就是为什么 DAG 不应该写进业务代码仓库。它是房间过程的一部分，记录的是协作路径和执行证据，而不是业务系统本身。

## 11

## 产出物系统：

## 把临时讨论变成可复用资产

房间每推进一步，都会产生东西。

有些东西是代码，有些东西是证据，有些东西是知识，有些东西是过程记录。没有产出物系统，这些东西会散落在聊天、终端、日志、浏览器截图和代码仓库里，最后谁也说不清“这次需求到底交付了什么”。

所以 Agent Room 需要一个明确的产出物系统：

每个产出物至少要有：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

产出物系统至少包括四类资产：

| 产出物类型 | 示例 | 归属 |
| --- | --- | --- |
| 代码产物 | 源码、测试、配置、迁移脚本 | 业务代码仓库 |
| 过程产物 | 执行 DAG、决策 DAG、发布 DAG | 房间 workspace |
| 验证产物 | 测试日志、浏览器截图、QA 报告 | 房间 workspace |
| 交付产物 | MR 链接、CR 链接、发布证据、最终总结 | 房间 workspace + 群聊摘要 |

它和 Memory / DAG 的关系是闭环的：

● Memory 负责告诉 Agent “过去发生了什么，哪些结论仍然有效”。

● DAG 负责告诉 Agent “现在应该做什么，依赖是否满足”。

● Runtime 负责真正执行。

● Artifact 负责记录“执行产生了什么证据”。

● Artifact 再反哺 Memory，让后续 Agent 不用重新猜。

可以把这个闭环写成：

也就是说，房间上下文的增长不应该只来自“又说了几句话”，还应该来自任务状态、执行证据和结构化产物。 这会把产品从“聊天界面”推进到“协作操作系统”。

## 12

三套系统的编排交互

Memory、DAG、产出物系统不是三个后台模块，而是同一个协作循环的三个面。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这套交互有几个产品含义。

第一，Agent 被 @ 之后不应该只生成“待处理”。如果房间策略允许自动执行，DAG 判断节点 ready，Runtime 就应该直接拉起本地 Codex CLI 或云端接口执行，并把结果写回群聊。

第二，Agent 不需要互相疯狂 @。所有人本来就能看见完整上下文。DAG 会告诉系统谁有 ready 的工作，Memory 会告诉 Agent 当前信息是否和自己有关。没有新增价值就 NO\_REPLY。

第三，用户需要看到的是“协作正在推进”，不是一串无法判断真假的自然语言。状态面板应该显示节点状态、运行状态、当前命令、最近文件改动、产物列表和失败重试入口。

第四，房间关闭不是简单隐藏 UI。关闭意味着：

● 冻结最终 Memory 快照。

● 关闭未完成 DAG 节点或标记取消。

● 保存产物索引和交付总结。

● 回收临时 workspace。

● 保留必要的审计和交付证据。

所以房间生命周期可以表示为：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这时，“涌现”就不是一句口号了。

它有可恢复的记忆，有可执行的拓扑，有可追溯的产出物，有真实 runtime，有用户可见的状态。

## 08

## 我们到底在做什么

所以 Agent Room 不是“多 Agent 聊天 UI”。它更像一种新的协作结构：前台是共享上下文，后台是 Memory、DAG、Runtime、Artifacts 组成的可执行任务系统，中间用状态、证据和可观测性连接。

传统编排把智能体当作流程节点。Agent Room 把智能体放进同一个上下文场。

流程节点擅长执行确定步骤。上下文场擅长处理不确定问题。真实的软件开发、产品设计、需求澄清、测试验收、预发发布，往往不是线性流程，而是不断发现信息、修正判断、冻结边界、推进实现的过程。它天然更像一场高质量会议，而不是一条流水线。

群聊恰好提供了涌现所需的条件：

● 共享上下文

● 多视角解释

● 局部自主判断

● 公开反馈

● 有限轮次

● 任务沉淀

● Memory 校正

● DAG 收敛

● 产出物沉淀

● 真实执行

● 可观测状态

当这些条件同时成立，多个 Agent 之间就不只是协作执行，而是在同一个问题空间里共同形成判断。 大模型让智能从语言中涌现。 Agent Room 让智慧从共享上下文中涌现。 这就是产品设计的底层。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E) ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

欢迎留言一起参与讨论~