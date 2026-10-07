---
type: brain-cards
kind: ground
module: Agent运行时与工具
status: candidate
human_reviewed: false
created: 2026-10-03
updated: 2026-10-03
domain: 学识
---

## ground ground-agent · Agent 运行时与工具 地基包

**定位**：AI 主战场里最「工程」的一块，只回答三件事：Agent 怎么不失控、失败之后怎么接着干、风险怎么管住。不含框架 API。

**心智模型**：三条线 = **正常路径**（循环怎么转、何时停）、**异常路径**（中断失败怎么继续）、**边界**（权限 / 多 Agent / 计划会变）。面试区分度最高的是第二条：多数候选人「只保存消息历史，进程重启后不知道哪些写操作已经完成」——能不能讲出 checkpoint「记两次」（副作用前记 intent、后记 result），直接分档。

**必会清单**：
- Agent 五条件里「动作改变环境」是分水岭：问一次返回文本的不算 Agent [@Agent运行时与工具-1]
- 预算七种：max_steps / max_tokens / max_cost / deadline / max_tool_calls / per-tool quota / max_retries，防的是重试放大 [@Agent运行时与工具-1]
- 工具是「给模型看的界面」，不是 API 直封：list_contacts 改造成 search_contacts [@Agent运行时与工具-1]
- 幂等键必须用业务身份 run_id + action_type + 业务键；ToolCallID / 时间戳 / UUID 都会失效 [@Agent运行时与工具-2]
- 数据库唯一约束 UNIQUE(run_id, action_type, idempotency_key) 是唯一「无论如何都拦得住」的位置 [@Agent运行时与工具-2]
- checkpoint 存九项，只存聊天历史恢复不了执行状态 [@Agent运行时与工具-2]
- 隔离 = 文件系统 × 网络隔离，必须是「与」不是「或」 [@Agent运行时与工具-3]
- 多 Agent 成本约 15× token：Anthropic 实测 token 用量单独解释 80% 的性能方差 [@Agent运行时与工具-3]

**学习路径**：
1. 先学「循环怎么转、什么时候停」：会画正常 Loop，出口的工程分量比入口大 [@Agent运行时与工具-1]
2. 再攻「中断与失败之后怎么继续」：区分度所在，幂等 + checkpoint 是两大件 [@Agent运行时与工具-2]
3. 最后「风险与复杂度怎么管」：用边界替代确认，多 Agent 先算 15× 成本账 [@Agent运行时与工具-3]

**验收门**：
- 闭卷画出 Agent 主循环，标出七种预算在哪个位置生效、先到先停 [@Agent运行时与工具-1]
- 能讲出「进程重启后怎么知道哪些写操作已完成」，包含 intent/result 记两次 [@Agent运行时与工具-2]
