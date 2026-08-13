---
title: "阿里云发布 AgentTeams 与 AgentLoop"
source: "https://mp.weixin.qq.com/s/BPEXEK0k4oayTTLCrLz4qg"
author:
published:
created: 2026-07-20
description: "针对企业智能体规模化落地两大难题"
tags:
  - "read"
---
*2026年7月9日 18:08*

**近日，阿里云正式发布两款面向企业 AI 落地的核心产品——多智能体协作治理平台 AgentTeams 与智能体观测优化平台 AgentLoop。** 两款产品分别解决企业在大规模部署 AI 智能体时面临的两大难题，即如何让多个智能体有序配合完成复杂任务，以及如何让智能体在实际运行中越用越好。目前，两款产品已全面开启公测。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/bvDbzNRia8j2HmX2SzysOSBUjSPV3avpgW3dNpicfzTzzic66WHDwBdJrLvszofR7Mvjia54GdGwzdPfQPX8bIblHx8ibGbupHq9w2HWWChKELoE/640?wx_fmt=png&from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

当企业开始用 AI 智能体替代重复性工作时，最先遇到的问题往往不是 AI 够不够聪明，而是多个 AI 之间怎么配合。一个复杂业务流程需要多个 Agent 各司其职：有的负责理解需求，有的负责执行操作，有的负责审核结果。如果缺乏统一协作机制，这些“数字员工”很容易各干各的，甚至相互矛盾。

AgentTeams 就像是给 AI 团队配备了一套完整的组织管理体系：岗位说明书明确每个智能体的职责边界，审批流程规定关键节点必须经过人类确认，工作群让人类员工随时看到 AI 之间在聊什么、做什么，门禁和公章制度保证每个智能体只能进该进的门、盖该盖的章。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

在分工模式上，AgentTeams 采用 Leader-Worker（主管+执行者）分工架构——由 Leader Agent（主管智能体）负责理解任务、拆解步骤，再分配给不同的 Worker Agent（执行智能体）完成。整条任务链路清晰可查，谁在什么时间做了什么一目了然。整条任务链路可声明、可审计。产品原生集成钉钉、飞书，业务人员可在熟悉的聊天窗口实时洞悉 Agent 之间的交流，随时干预纠偏。

安全性是企业最敏感的关切。很多场景中，智能体需要调用数据库、支付接口等敏感系统，必须持有访问密钥。AgentTeams 采用钥匙集中托管机制：Agent 本身看不到也留不下任何密钥，需要时由平台按需发放，用完即收。无论自研 Agent 还是开源框架搭建的 Agent，都能统一纳入平台管理，调用记录、资源消耗、运行成本全程可审计，满足金融、政务等行业的严苛合规要求。

如果说 AgentTeams 解决的是让 AI 团队稳定工作，AgentLoop 要回答的是更深一层的问题——让 AI 越用越聪明。

AI 智能体上线后最大的挑战是效果黑盒：它跑得好不好？哪里出了问题？靠人工抽查既低效也不现实。AgentLoop 把智能体每一次的思考过程、工具调用、资源消耗自动记录下来，还原为清晰的执行轨迹。开发者不用改动代码就能接入，打开平台即可看到每个智能体的工作日志，快速定位哪个环节拖慢了速度、哪个步骤花了太多钱。

更关键的是评估能力。AgentLoop 引入 AI 评估 AI 的方法（"Agent-as-a-Judge" 范式）——由一个专门的评估智能体基于执行轨迹做深度分析，自动发现回答跑题、信息编造等典型问题。发现的问题自动沉淀为经验教训，反馈回知识库，让智能体下次不再犯错。这套观测—评估—优化—再观测的循环机制，让智能体在真实业务中持续学习、持续进步，而不是上线后一成不变。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

此外，阿里云全域智能运维平台 STAROps 正式商业化，并上架 Qoder Desktop 插件市场。用户可直接在 Qoder 中用日常对话完成指标查询、日志检索、链路追踪和告警诊断。