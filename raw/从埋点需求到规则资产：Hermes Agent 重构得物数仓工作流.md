---
title: "从埋点需求到规则资产：Hermes Agent 重构得物数仓工作流"
source: "https://mp.weixin.qq.com/s/hGma3I1jMF5KsDZQK_6X4Q"
author:
  - "[[小诘、博温]]"
published:
created: 2026-08-08
description: "埋点和指标需求中，消耗数据承接方的不是生成答案，而是补齐证据链、对齐历史口径、识别下游影响，并在生产写入前留下可追溯的确认记录。本文数据承接方指承接业务需求的数据同学或业务合作伙伴；后文讨论内部研发、元数据、查询和门禁能力在流程中的角色。"
tags:
  - "read"
---
小诘、博温 *2026年6月17日 18:30*

![图片](http://mmbiz.qpic.cn/mmbiz_gif/AAQtmjCc74DZeqm2Rc4qc7ocVLZVd8FOASKicbMfKsaziasqIDXGPt8yR8anxPO3NCF4a4DkYCACam4oNAOBmSbA/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

**目录**

一、Hermes Agent 让流程可控

二、用单 Agent 串流程，用能力模块沉淀可复用能力

1.固化流程契约

2.可复用能力模块设计：从埋点链路迁移到更多数据研发场景

三、总体工作流：从一次对话变成一条可回放链路

四、能力底座：把规则、上下文和命令资产化

1.规则资产化：先决定什么值得记住

2.协作可见：让 AI 不在后台默默跑完

3.上下文与事实源：下一任务读什么，最终相信什么

4.结构化工具接口：把生产动作变成可验证接口

五、风险治理：可验证执行、人工确认点与审计留痕

六、结论

在埋点和指标需求里，最消耗数据承接方的往往是 **把分散的信息重新拼起来：需求文档里的动作到底要不要采集，历史上有没有类似点位，指标口径有没有被下游使用，新增字段要改哪几层表，发布前又该由谁确认。** 我们选择Hermes Agent而不是OpenClaw是因为它具备持续在线、持久记忆和技能沉淀能力。对数据团队来说，下面几个原生能力正好对准了这类流程痛点：

- **分层持久记忆：** 短期会话/中期交互/长期知识/技能库四层结构，本地SQLite+FTS5全文检索。"关掉窗口就失忆"，在需要反复回溯历史口径的数仓场景是不可接受的；
- **技能自动沉淀：** 任务完成后能把经验提炼成Markdown技能文档并持续优化。这正是"专家经验资产化"的框架级支撑，本文反复出现的"规则包"就构建在这套技能机制之上；
- **多平台统一网关：** 原生接入飞书、钉钉、企业微信等协作平台，智能体直接嵌进团队已有的沟通现场，不用另建工作台；
- **工具与扩展生态：** 终端执行、定时任务、浏览器自动化等内置工具，企业内部系统经MCP命令封装稳定接入。

在这套框架之上，我们把一次埋点需求承接拆成四个可追踪的工程构件：工作区（每个需求独立空间，集中存放需求文档、历史讨论、评审结论和交付产物）、看板（状态机流转：进入、设计、预演、评审、交付，每步有责任人）、规则 + 长期记忆（把"老同学才知道"的判断写成可执行检查清单）、结构化工具接口 + 预演 + 人工确认点（高风险动作走结构化接口，写入生产前先预演、再等人放行）。

图：Hermes Agent 能力底座与 OpenClaw 对比

图：Hermes Agent 工作流主线

**一**

**Hermes Agent 让流程可控**

如果让AI直接给最终结论，确实会很快，但这种快并不让人放心。因为数仓链路里的错误通常是依据没找全、假设没说清、风险没暴露，最后带着一个“看起来完整”的方案进入评审或生产。

**所以Hermes Agent的边界是把问题整理到足够可判断。** 它负责把材料、历史、候选方案、系统预演和风险证据组织起来；人负责业务语义、指标口径、敏感字段、下游影响和生产放行。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：Hermes Agent 的能力边界与人工确认线

**Hermes Agent 真正承担的是判断前的工程化准备**

在这条链路里，Hermes Agent 更像一个流程编排者，而不是一个埋点生成器。它把一次需求拆成几件能被检查、能被追踪、能被恢复的事，所做的准备如下图所示：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：Hermes Agent 判断前准备四步

要从流程侧切入：这不是弱化数据承接方的判断，恰恰相反，是把数据承接方从反复翻材料、追状态、补上下文里释放出来，让人把精力放在真正需要负责的地方：口径能不能成立，风险能不能接受，生产动作能不能放行。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：为什么先从流程侧切入与风险边界

边界说清楚后，选型的重点不在 Agent 数量，而在上下文、规则和确认点能不能在同一条链路里稳定运转。

**二**

**用单 Agent 串流程，用能力模块沉淀可复用能力**

这一类需求如果只靠一段提示词，很快会遇到两个问题：一是同一个需求换个问法，输出结构和检查重点就会漂；二是模型可以写出“看起来完整”的方案，却说不清它读了哪些事实、调用了哪些系统、哪些动作必须等人确认。所以我们没有把能力拆成一组互相独立的智能体，而是选择“单Agent编排+多能力模块+看板确认点”： **Hermes Agent 保持统一上下文，负责调度阶段；能力模块承接稳定动作，负责把工具调用、输入约束、输出产物和停顿条件固化下来。**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E) ![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：Hermes Agent 选型：单 Agent 编排 + 多能力模块

**固化流程契约**

选型确定以后， **要固化的是每个能力模块的输入、动作边界、输出产物、失败处理和经验回写。** 只有这些契约稳定，Hermes Agent才不会因为提示词换一种说法就改变检查重点

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：能力模块不是工具清单，而是流程契约

**可复用能力模块设计：从埋点链路迁移到更多数据研发场景**

这些能力模块不是只服务一次埋点需求，而是把素材采集、历史检索、变更预演、发布确认、经验沉淀抽成可复用的流程模块。换事实源和工具接口后，同一套机制也能迁移到指标发布、配置变更和数据质量排查， **可复用的SKILL就是这套机制的核心载体。**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：可复用能力模块设计地图

这一选择把 Hermes Agent 的长期记忆和能力模块 机制变成团队可复用的作业制度，也为工作区、看板、预演和确认点提供统一上下文。

**三**

**总体工作流：从一次对话变成一条可回放链路**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：Hermes Agent 埋点需求端到端工作流

下面用一个场景串联完整链路：业务希望稳定查看“昨天各体裁发布量”。如果只让模型直接写 SQL，很容易把物理字段、业务发生日期和默认过滤混在一起， **Hermes Agent 的做法是先固化事实，再预演风险，最后把需要人判断的点推到看板确认。**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

全链路把需求入口、工作区、规则包、系统预演、人工确认和交付归档串在一起；会议纪要则作为协作语境进入需求上下文，补充已确认事实、责任人和待澄清问题。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：会议纪要进入需求上下文的链路

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：周期性同步需求并写入工作看板

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：任务看板承接需求状态、推进和人工介入

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：工作区保留的事实源

**四**

**能力底座：把规则、上下文和命令资产化**

这一节聚焦“什么值得沉淀”。埋点自动化真正难的是把历史口径、下游影响、人工确认和生产状态拆成可复用资产：规则包回答“怎么判断”，工作区回答“依据在哪里”，看板回答“卡在哪里”，结构化工具接口回答“系统状态是否验证过”。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**规则资产化：先决定什么值得记住**

这里的关键不是让 Hermes Agent 记得更多，而是把材料分层：临时信息留在本轮任务，能复用的做法沉进规则包，需要人工把关的内容进入治理记忆。这样下一次相似需求到来时，系统先补证据、提醒风险，而不是让数据承接方从头解释。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：规则资产化与长期记忆闭环

**协作可见：让 AI 不在后台默默跑完**

规则资产只有进入协作流程才有价值。看板负责暴露阶段、阻断项和责任人，飞书保留澄清、驳回和确认语境，工作区承接证据和产物；三者合起来，才能让人知道AI做到了哪一步、还缺什么、哪里必须停下来等确认。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：看板 + 飞书让 AI 每一步可见

**上下文与事实源：下一任务读什么，最终相信什么**

上下文传递不能靠“多塞材料”解决，而是把任务背景、阶段结论、人工反馈和运行元数据分开保存。与此同时，聊天只能补语境，工作区负责留证，系统预演负责验证，生产系统才是最终事实源。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：上下文传递与事实源边界

**结构化工具接口：把生产动作变成可验证接口**

当智能体接近生产系统时，最不应该依赖页面识别和临场点击。结构化工具接口的作用，是把查询、绑定、发布、验证这些动作包装成参数明确、返回结构化、过程可审计的接口；越靠近写入，越要先预演、再确认、最后留痕。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：结构化工具接口把生产动作变成可验证接口

这四类资产合在一起，才让 Hermes Agent 从“会回答”变成“能交接”。越靠近生产，越要把资产和治理连起来：规则给出判断边界，命令提供验证证据，看板承接人工确认。

**五**

**风险治理：可验证执行、人工确认点与审计留痕**

Hermes Agent越靠近生产链路，越不能只追求“自动执行”。上线前只看三类硬证据：事实来源是否可信，系统预演是否通过，责任人是否已经确认。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：Hermes Agent 的能力边界与人工确认线

**上线前只过三道门** ：事实源门、预演门、责任门。任何一道门缺证据，Hermes Agent 都只能停在候选方案或待确认状态，不能继续推进生产写入。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

治理的目标不是让数据承接方把系统做过的事再手工复查，而是让系统在关键位置停下来，把证据、预演结果和责任人摆到台面上。人的精力应该留给真正的判断点：口径要不要调整，风险能不能接受，生产动作能不能放行。

**六**

**结论**

Hermes Agent值得放大的是可回放、可确认、可复用的工作流能力。当前链路已经围绕四件事形成主线：跑通需求流转，前置风险拦截，沉淀规则资产，让数据承接方把精力放到口径裁决和生产边界上。

下一步的重点不是继续堆更多自动化动作，而是把证据口径跑实：用连续样本证明准备时间、交付周期、评审通过率和返工原因的变化。只有当这些指标和看板、日志、确认记录一一对应时，这条链路才真正具备扩大使用的工程基础。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

图：Hermes Agent 规模化落地路径

**往期回顾**

1.[让 Claude Code 拥有自我进化和记忆系统｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544916&idx=1&sn=25d5c20a7a9d2b0dfed78eaf25598717&scene=21#wechat_redirect)

2.[用 LLM Agent 重构告警排查流程｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544879&idx=1&sn=4d1a92199b785d5d3d3de1758545adba&scene=21#wechat_redirect)

3.[得物技术在 AICon 关于大模型与 Agent 技术实践分享来袭！](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544742&idx=1&sn=95a1c9a7738bbda6f89f887df7767534&scene=21#wechat_redirect)

4.[HorizonVault 技术深潜：如何在 HDD 上做出 100GB/s+ 级大吞吐分布式存储｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544708&idx=1&sn=cc8d064185a5bdc27fd7748f0958182d&scene=21#wechat_redirect)

5.[Claude Code Harness 工程：数仓侧落地方案｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247544651&idx=1&sn=9a231b02a15ac5e33bd4bf41148a021d&scene=21#wechat_redirect)

文 /小诘、博温

关注得物技术，每周三更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。

“

**扫码添加小助手微信**

如有任何疑问，或想要了解更多技术资讯，请添加小助手微信：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

大数据 · 目录