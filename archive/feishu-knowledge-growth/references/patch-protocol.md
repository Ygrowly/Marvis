# 知识补丁协议

## 目的

Knowledge Patch 只描述“这次新信息让现有认知发生了什么变化”。它不是来源摘要，也不是整篇 Wiki 正文。

## 允许的产物

| 产物 | 使用条件 |
|---|---|
| `KnowledgePatch` | 已有或新知识节点需要改变 |
| `CapabilityGap` | 目标标准与现有证据之间出现差距 |
| `BehaviorExperiment` | 对重复行为机制有可检验假设 |
| `DecisionProtocol` | 可把反复纠结转成预先规则 |
| `NoOp` | 只有重复、噪声或与当前系统无关 |

一个处理回合可以产生一份主补丁和一个行动型产物。不要为了完整而五种都产出。

## Patch 字段

```yaml
patch_id: PATCH-YYYYMMDD-NNN
route: learning | capability | growth
operation: add | extend | correct | merge | split | deprecate | noop
status: draft | pending_confirmation | approved | applied | rejected | needs_evidence
trigger: 为什么现在处理这条材料
source_ids: []
target_node_ids: []
existing_belief: 原结论；新增节点时为 null
delta: 本次真正新增或改变的内容
tension: 与旧结论、其他证据或目标的矛盾
synthesis: 合并后的简洁结论
boundary: 适用条件、失效条件、反例
evidence:
  quality: weak | medium | strong
  basis: 直接事实、来源主张、用户经历、实验或推断
confidence: 1-5
user_contribution: 用户的连接、选择、反例或承诺
next_action:
  hypothesis: null
  smallest_step: null
  success_signal: null
  review_at: null
created_at: ISO-8601
```

飞书表中不必逐字保存 YAML；按 `feishu-schema.md` 映射到字段。交互预览必须包含 `operation`、`delta`、`synthesis`、`boundary` 和证据质量。

## 操作判定

### add

系统中没有回答同一稳定问题的节点，且内容对当前目标有足够价值。新节点标题用问题或可复用主题命名，不以来源标题命名。

### extend

旧结论仍成立，新材料增加机制、例子、边界、证据或可执行方法。

### correct

新证据直接削弱旧结论。必须保留旧结论和修正理由，不把修正伪装成自然补充。

### merge

两个节点回答同一对象、同一抽象层级、且合并不会抹掉适用边界。若只是在相关，不合并，建立关联。

### split

一个节点混合了多个问题、条件或抽象层级，导致结论互相冲突或难以调用。

### deprecate

节点已被更好解释取代、长期无效或问题本身不再有价值。保留重定向和废弃原因，不删除历史。

### noop

满足任一条件：

- 与已有结论同义，没有新增证据或边界；
- 仅有情绪化观点，不能支持判断；
- 与当前或长期模型关联极弱，处理成本明显高于收益；
- 无法获得必要内容，当前只能保留来源。

`NoOp` 不是失败，而是控制系统熵增。

## 融合规则

1. 先比较命题，不比较标题。
2. 将“事实、来源解释、AI 推断、用户判断”分开。
3. 矛盾优先转化为条件：在 A 情境成立，在 B 情境失效。条件仍无法解释时保留争议。
4. 频繁出现只提高“岗位/舆论中常见”的置信度，不直接提高真理置信度。
5. 单条个人经历只能产生暂定模式，至少需要重复观察或行为实验才能进入稳定自我模型。
6. 置信度 1–5：1=猜想，2=有限线索，3=多条一致证据，4=高质量证据且经实践，5=多情境反复验证。默认不轻易给 5。

## 状态机

```text
draft -> pending_confirmation -> approved -> applied
   |              |                 |
   |              +-> rejected      +-> needs_evidence
   +-> noop
```

- 创建来源记录可自动执行。
- 创建补丁草稿可自动执行，但必须让用户看到预览。
- 用户说“确认这个补丁”“按这个更新”后才进入 `approved`。
- Wiki 更新并读回成功后才进入 `applied`。
- 写入失败时保留 `approved`，记录错误，不重复制造补丁。

## Wiki 应用模板

每个知识节点建议保持以下短结构：

```markdown
# 节点标题

## 当前结论
一到三段能直接调用的结论。

## 为什么成立
关键机制与最强证据。

## 边界与反例
何时不成立、仍有哪些争议。

## 如何使用
决策规则、项目应用或表达方式。

## 待验证
尚未解决的问题或实验。
```

应用补丁时只更新受影响小节。来源明细和补丁历史保留在 Base，不在 Wiki 堆积长流水账。

## 行动判定

只有满足以下三项才创建行动：

- 有明确要降低的不确定性或要补的缺口；
- 最小动作可在具体时间或触发条件下执行；
- 有能观察的完成/成功信号。

行动应优先产出证据，例如：“用 20 分钟白板讲清项目核心链路并录音，能在 3 分钟内说明权衡”，而不是“学习项目”。
