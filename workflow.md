# Workflow

> 按文章捕获，按主题加工，按问题深读，按知识沉淀。

## 1. 随时捕获

所有外部信息统一进入：

```text
raw/
```

链接使用 `raw/YYYY-MM-DD.md` 记录，至少保留标题和 URL，推荐补一句收藏原因：

```md
- [文章标题](URL)
  - why: 可能解决什么问题
```

收藏后关闭标签页，不在此时分类、总结或决定目录。

## 2. 批量粗加工

需要快速了解或 `raw/` 中同类内容增多时，让 AI 批量处理：

```text
raw/ → 聚类 → 去重 → 价值判断 → 主题综述
```

AI 输出：

- 每批内容有哪些主题
- 每个主题的共同观点和差异
- 哪些只是重复信息
- 相对现有 wiki 新增了什么
- 哪些主题值得继续
- 每个高价值主题推荐 1—3 个代表来源

高价值主题写入：

```text
wiki/sources/YYYY-MM-DD-主题.md
status: candidate
```

不要默认给每篇文章建立独立摘要。个别需要快速了解的单篇素材，可生成独立摘要写入 `summaries/`，同样标记 `status: candidate`。

## 3. 选择深读

只有以下内容进入 `reading/`：

- 当前项目马上要用
- 面试高频且存在理解缺口
- 能改变重要判断
- 同一主题中最系统、有实践证据或代表反方观点的来源

同时进行的深读材料最多 3 个。

```text
candidate → reading/notes → reading/discussions
```

阅读前先看主题综述，并写下要验证的问题。

## 4. 讨论巩固

深读后先写自己的理解，再让 AI：

- 检查理解偏差和遗漏
- 分析作者前提、证据和适用边界
- 提供反例
- 追问并要求二次复述
- 连接项目、面试和行动

需要保留独立阅读结论时，可生成：

```text
reading/conclusions/
```

## 5. 沉淀知识

阅读完成不等于流程完成。将新增理解更新到：

```text
wiki/topics/
wiki/projects/
wiki/interview/
wiki/thinking/
```

形成自己的知识、表达、判断或行动规则后，状态标记为：

```yaml
status: integrated
human_reviewed: true
```

## 状态速查

```text
captured → candidate → reading → integrated
```

| 状态 | 判断标准 |
|---|---|
| `captured` | 已进入 `raw/` |
| `candidate` | AI 粗加工后值得继续关注或深读 |
| `reading` | 正在阅读、验证、讨论和复述 |
| `integrated` | 已进入自己的知识体系并能用于具体场景 |

`raw/` 素材默认隐含为 `captured`，不强制写状态。

## 建议节奏

- 随时：保存到 `raw/`，关闭标签页
- 按需或每周：批量聚类和粗加工
- 每周：选择 1—3 个代表来源深读
- 遇到项目或面试问题：优先处理相关主题
- 深读完成：更新稳定知识页

系统不要求 Inbox 清零，也不要求每天处理所有收藏。
