---
type: source_synthesis
created: 2026-08-13
updated: 2026-08-13
status: candidate
human_reviewed: false
topic: 生产级 Agent 工程实践（得物 12 篇）
sources:
  - "raw/Claude Code Harness 工程：数仓侧落地方案｜得物技术.md"
  - "raw/从 Coder 到 Designer ：电商团队数据研发的 Harness Engineering 实践.md"
  - "raw/财务数仓 Claude AI Coding 应用实战｜得物技术.md"
  - "raw/从埋点需求到规则资产：Hermes Agent 重构得物数仓工作流.md"
  - "raw/从表单到 Agent：得物社区活动搭建的 AI 实践之路.md"
  - "raw/BP Claw 破解 AI 编码输入难题 ——FlinkSpec 需求智能化实践｜得物技术.md"
  - "raw/AI驱动：从运营行为到自动化用例的智能化实践｜得物技术.md"
  - "raw/日志诊断 Skill：用 AI + MCP 一键解决BUG｜得物技术.md"
  - "raw/通用 AI Agent 驱动网关路由安全审计实践｜得物技术.md"
  - "raw/AI Native 交易核心系统的研发范式｜得物技术.md"
  - "raw/2026-08-04T111743+0800 - 从机械应答到服务伙伴：得物高可控智能客服的 Agent 工程实践｜AICon 演讲整理.md"
  - "raw/OpenSandbox 再进化：Credential Vault 让真实密钥不再进入沙箱.md"
related:
  - "[[2026-06-24-agent-loop-harness-review]]"
  - "[[MetricOps Agent]]"
  - "[[AI BI Text-to-SQL]]"
  - "[[04-Agent-Runtime与Harness]]"
  - "[[金山能源管理系统]]"
---

# 主题：生产级 Agent 工程实践（得物 12 篇）

## 一句话结论

12 篇得物生产实践共享同一工程范式：把确定性动作（规范检查、危险拦截、门禁）从 LLM 推理循环中剥离给 hooks 和结构化接口，「规范执行是 AI 长板、业务判断是人长板」——上下文管理、受控执行、评测闭环、知识资产化四大支柱反复出现。

## 本批来源

| 来源 | 主要内容 | 是否重复 | 推荐动作 |
|---|---|---|---|
| Harness 数仓侧落地方案 | 五层防御：compact 后重注入约束、PostToolUse hook 自动校验（exit 2 才阻断）、subagent 隔离高 token 操作、path-scoped rules | 否，可操作细节最全 | 深读 |
| 从 Coder 到 Designer | 知识工程 + Harness 双支柱；7-Agent NL2SQL 编排；幻觉检测 Hook；「以 Agent 养 Agent」心跳机制 | 部分重复（编排视角独立） | 深读 |
| 财务数仓 AI Coding | 规范即 Prompt × 迭代收敛 × 海量文件阅读；AI 生成测试 SQL（正向−冲销=冲销之后等）；口径分级 | 部分重复，方法论最浅 | 按需查阅 |
| Hermes 埋点需求 Agent | 单 Agent 编排 + 多能力模块防提示词漂移；上线前三道门（事实源/预演/责任）；刻意不报未验证数字 | 否，受控 Agent 面试素材首选 | 深读 |
| 从表单到 Agent | interrupt/resume 作前后端交互语言；初始化阶段禁止副作用（真实 bug 案例）；读写发布三级最小权限 | 否，HITL 设计细节 | 按需查阅 |
| BP Claw FlinkSpec | 需求转化「忠实原文、绝不捏造」；PRD 质量评分一票否决；口径歧义显式化 | 否，输入质量治理 | 按需查阅 |
| 运营行为到自动化用例 | 行为日志→Midscene 结构化用例；代码覆盖率作硬指标识别低价值用例 | 部分重复（质量闭环思路相通） | 按需查阅 |
| 日志诊断 Skill | 日志平台 MCP + /log-diagnosis SKILL 固化 SOP（分页拉全、跨服务交叉验证）；真实 SQL bug 案例 | 否，Agent 后端基本功 | 深读 |
| 网关路由安全审计 | 「通用 Agent + 业务 Skill」分层；Token 成本三层优化降 95%+；误报归因治理 | 否，唯一给出成本模型 | 深读 |
| AI Native 交易核心系统 | BDD/Gherkin 硬契约、五道关口流水线、门禁 JSON 机器判定、埋点驱动知识库补充 | 否，最完整研发流水线 | 深读 |
| 高可控智能客服 | Multi-Agent→Harness 演进；PE 自动化流水线；DPO/GRPO 飞轮与防灾难性遗忘；半双工消息流 | 部分重复（训练维度独特） | 按需查阅 |
| OpenSandbox Credential Vault | egress sidecar 出站凭据代理，密钥不进沙箱 | 否，安全基础设施视角 | 按需查阅 |

## 共同结论

1. **职责分层 Harness**：确定性动作剥离给 hooks/结构化接口，模型做语义理解，人做业务判断——第 1、2、4、10 篇反复出现。
2. **上下文管理是通用难题**：compact 失忆重注入、subagent 隔离只回摘要、渐进式披露、Token 成本工程，几乎每篇都在对抗 context 膨胀。
3. **受控执行**：人工 Gate、上线前三道门、interrupt/resume HITL、读写发布三级权限、exit 2 阻断协议。
4. **评测度量闭环**：埋点看板、覆盖率硬指标、误报归因治理、PE 自动化飞轮——没有度量就没有迭代。
5. **知识资产化**：语义层、规则包、Spec「文档即接口」——把一次性经验变成可复用资产。

## 真正的分歧

- **多 Agent vs 单 Agent 编排**：从 Coder 到 Designer 用 7-Agent 顺序协作；Hermes 刻意用「单 Agent 编排 + 多能力模块」，理由是多 Agent 易提示词漂移、难维护。生产案例各执一词。
- **量化文化**：多数文章给出量化数据（部分脱敏或标注「预计」）；Hermes 刻意不报未经验证的数字，明确下一步要用连续样本证明——对「数字可信度」的态度不同。
- **Workflow vs Agent 的判别**：从表单到 Agent 给出判别法则「能画有限状态机就用 Workflow」，与面试复盘文「无通信的编排只是 Workflow 不是多 Agent」互相印证。

## 新增或修正的知识

- **exit 2 阻断协议**：PostToolUse hook 校验失败 exit 2 才阻断、exit 1 不阻断——阻断语义的工程细节。
- **Token 成本工程三层**：MCP→CLI 转换（省 61%）+ 精准参数提取（省 88%）+ Early-Exit（省 50-70%），单条审计 ¥0.23、全量扫描 <1 万元——批处理 Agent 的成本模型。
- **BDD 硬契约**：Gherkin 场景作为需求与测试之间的硬契约，Spec 六节模板禁技术语言，「阻断兜底行为」必填。
- **幻觉检测 Hook**：对比 Agent 声称结果与实际系统状态（qwen 读文档失败却报「检查通过」的真实案例）。
- **初始化阶段禁止副作用**：真实 bug——组件初始化偷调后端导致只看一眼就建数据；写操作只在「构建前」阶段。
- **三道门**：事实源门、预演门、责任门，缺证据只能停在待确认。
- **半双工消息流**：用户可打断、Agent 不可打断，Qwen3-4B 做消息合并/切分。

## 可信度

- 有数据、代码或案例支持：
  - Harness 数仓：完整可抄的 settings.json、shell 脚本；规范遵守率 70-80%→95%+、一次通过率 50%→90%（部分为预估）。
  - 网关安全审计：成本数字、100+ 样本测试集、误报占比归因、真实高危漏洞。
  - AI Native 交易：礼品卡资损案例贯穿全程，插件设计完整。
  - 日志诊断：完整真实案例 + 可直接安装的 Skill 文件结构。
- 只有观点或二手转述：
  - 财务数仓、从 Coder 到 Designer 量化弱；智能客服数字多在图片中。
- 需要进一步验证：
  - 「规范遵守率 95%+」等自报数字的统计口径；compact 频率降 50-70% 是预估。
  - 7-Agent 编排 vs 单 Agent 编排在自己项目规模下的取舍。

## 是否值得继续

- 结论：值得深读。
- 原因：这是「Harness 理论」在生产场景的完整落地样本，与 [[MetricOps Agent]]、[[AI BI Text-to-SQL]]、EnergyOps 的工程化改造直接同构；门禁、成本模型、受控执行都是 Agent 后端面试的硬通货，且能直接回答「你做的项目为什么是生产级」。

## 推荐代表来源

1. 最完整流水线：`raw/AI Native 交易核心系统的研发范式｜得物技术.md`
2. 可操作细节最全：`raw/Claude Code Harness 工程：数仓侧落地方案｜得物技术.md`
3. 唯一成本模型：`raw/通用 AI Agent 驱动网关路由安全审计实践｜得物技术.md`
4. Agent 后端基本功：`raw/日志诊断 Skill：用 AI + MCP 一键解决BUG｜得物技术.md`

## 阅读问题

1. exit 2/exit 1 阻断协议和 compact 重注入能否直接搬到 MetricOps Agent 的 harness？哪些约束适合 hook 化、哪些适合 rules？
2. 三道门（事实源/预演/责任）在 EnergyOps 的生产操作 Agent 化改造中对应哪些环节？
3. 网关审计的成本三层优化（MCP→CLI、参数提取、Early-Exit）里，哪些对自己的批处理任务适用？
4. 「通用 Agent + 业务 Skill」的分层和 Hermes「单 Agent + 多模块」的边界在哪里？什么时候编排会变成过度设计？
5. BDD 硬契约适合哪些项目阶段？Text-to-SQL 的需求是否也能 Gherkin 化？

## 可能更新的知识页

- [[MetricOps Agent]]：补受控执行、成本模型、Skill 即 SOP。
- [[AI BI Text-to-SQL]]：补语义层、口径显式化、需求质量门禁。
- [[金山能源管理系统]]：补 Agent 化改造的 HITL 分级与副作用时机。
- [[04-Agent-Runtime与Harness]]：补 Harness 分层与「通用 Agent + 业务 Skill」模式。
