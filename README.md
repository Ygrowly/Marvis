# Marvis · SecondBrain

> 我的知识库、职业资产和阅读训练系统。

这是一个 Obsidian 知识库，围绕 2027 届秋招运转：外部素材统一进 `raw/`，按问题台账驱动加工，深读讨论后沉淀为可复述的**母题卡**与面试资产。`site/` 是 md 正本派生的**学习界面**（复训 / 派单 / 诊断 / 项目口述），发布在 GitHub Pages。

## 三条入口

| 想知道 | 去哪 |
|---|---|
| 全库规则（唯一权威） | [CLAUDE.md](CLAUDE.md) |
| 某个主题的正本在哪 | [MAP.md](MAP.md) —— 主题正本登记表 |
| 现在该做什么 | [questions.md](questions.md) —— 问题台账，加工的唯一驱动 |

库内导航（Obsidian 双链版）在 [index.md](index.md)；本 README 只面向 GitHub 访客，不承载规则正文。

## 核心流程

```text
raw/ 唯一素材入口（允许积压）
  ↓ 按活跃问题定向聚类、去重、粗加工
wiki/sources/ 候选主题综述（candidate）
  ↓ 选择代表来源深读、讨论、复述
reading/ 深读与验证
  ↓ 沉淀为可复用资产
wiki/ 知识资产（母题卡为主）+ output/ 对外成品
```

加工由 `questions.md` 的活跃问题拉动，唯一指标是每周闭环 ≥ 1 个问题。细则见 [CLAUDE.md](CLAUDE.md) 与 [workflow.md](workflow.md)，变更史见 [log.md](log.md)。

## 目录速查

| 区域 | 用途 |
|---|---|
| `CLAUDE.md` / `MAP.md` / `questions.md` | 规则权威 / 正本登记表 / 问题台账 |
| `raw/` | 唯一外部素材入口，允许积压 |
| `summaries/` | 单篇摘要候选区（默认停更，状态最高 candidate） |
| `reading/` | 深读、讨论、结论（过程区） |
| `wiki/topics/{模块}/` | 技术知识母题卡，按模块分子目录（算法 / MySQL / Redis / LLM与上下文 / …） |
| `wiki/interview/` | 面试表达、题库、面经复盘 |
| `wiki/thinking/` | 学习方法、精力与行动规则 |
| `wiki/sources/` | AI 生成的主题综述候选 |
| `study/` | 能力课程底库（已降为素材，学习入口在母题卡） |
| `projects/` | 活跃项目一目录：项目说明正本 + 编号手册 |
| `archive/` | 已移出准备范围的项目存档（只读备查） |
| `jd/` | JD 融合核对表、横向对比、参考简历 |
| `output/` | 对外成品（简历只放 `output/resume/`，证据材料在 `output/evidence/`） |
| `site/` | md 正本 → html 学习界面（build.py 派生） |
| `templates/` | 母题卡、模块卡、复盘等写作模板 |
| `data/` | 站点进度云同步落盘文件（`marvis-sync.json`） |

## site/ 学习界面

- **md 是工作台，html 是派生视图**：改内容只改 md，然后跑 `python site/build.py`（纯 Python 标准库，离线可跑）。html 永不回写 md。
- 用法与内容接入方式见 [site/README.md](site/README.md)，方案正本见 [site/PLAN.md](site/PLAN.md)。
- 回归测试：`node site/_tests/test_dispatch.js` 等 4 个 + `python site/_tests/test_ledger.py`（问题台账解析器），改动派单 / 解析器 / 数据源后须全部跑绿再提交。
- 复训进度存浏览器本机（键名前缀 `mv.`），可选云同步到 `data/marvis-sync.json`（页面右下角配置 GitHub 令牌，令牌不进仓库）。

## 部署

GitHub Pages：`.github/workflows/pages.yml` 在 push 到 `main` 且改动 `site/**` 时自动部署。`site/.nojekyll` 保证 `_data/`、`_components/` 等下划线目录可被直接访问。

## 治理约定（正本制）

1. **一个主题一个正本**，登记在 [MAP.md](MAP.md)；默认更新、不默认新建，新建必须登记。
2. **视图是派生物**：`site/` 的 html 由 `build.py` 生成，不手写（`index` / `progress` / `brain` / `rules` 四个手写页为已登记例外）。
3. **落点唯一**：技术母题卡进 `wiki/topics/{模块}/`，面试表达进 `wiki/interview/`；`output/` 只放对外成品。
4. 结构性变更追加进 [log.md](log.md)，并同步 MAP / CLAUDE / index 三处口径。

## 本地使用

用 Obsidian 打开仓库根目录即可（`.obsidian/` 已本地化配置、不入库）。行尾统一 LF（见 `.gitattributes`）；Windows 下若 git 反复误报「已修改」，先确认工作区checkout 为 LF 再看实质 diff。
