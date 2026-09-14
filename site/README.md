# site · 学习界面

> **md 是工作台**（素材、讨论、推导、正本，允许乱）；
> **html 是学习界面**（表征、训练、诊断、交付，精炼）。
> 两者之间只有一条单向流：md → build.py → html。**html 永不回写 md。**
>
> 方案正本见 [`PLAN.md`](PLAN.md)。本文件是实现与用法说明。

## 目录

```text
site/
  index.html          唯一入口：房间直达 + 今日复训 + 作业入口（计时器在弹窗里）
  progress.html       进度页（手写，数据存 localStorage）：五板块派单（复训/抽检/主线新学/项目线/日课）+ 依赖门控 + 闭卷自评 + 断点回流 + 欠账减负 + 近 7 天回顾 + 热力图
  _data/clusters.js   进度页数据源：10 个能力簇（含项目线）+ 日课母题清单 + 跨簇前置 after（M3 起计划改由 build.py 生成）
  _data/breaks.js     断点回流数据（build 生成）：母题页路径 → 上次断点 / 一句话结论 / 恢复关键词 / 追问
  _tests/             派单引擎回归测试（手跑，build 不管）：node site/_tests/test_dispatch.js 等三个
  modules/            模块学习页（build 生成，勿手改）：{模块}.html 概览 + {模块}-NN-{主线}.html 子页
  topics/             母题页（build 生成，勿手改）
  reviews/            诊断页（build 生成，勿手改）
  PLAN.md             方案正本
  build.py            构建器：按格式选 adapter → 视图 + 牌组数据
  cards/              补充卡草稿区（::card 也可直接写进任何 md）
  figures/            图（.svg），md 里用 ::figure 引用
  _data/              构建产物 decks.json / modules.js / reviews.js（数据）+ .js（file:// 用）
  _components/        marvis.css + marvis.js，10 个原生 Web Components
```

## 页面导航（三层，双向可达）

```text
index.html（训练台）
  ├─ progress.html              进度与作业：五板块派单（复训/抽检/主线新学/项目线/日课）+ 加餐 + 闭卷自评 + 近 7 天回顾 + 连续性热力图
  ├─ modules/{模块}.html        模块概览：主线 + 一句话结论 + 边界 + 项目映射
  │    └─ modules/{模块}-NN-….html   主线子页：母题（先答后看）+ 本主线题
  │         └─ topics/{模块}-母题-….html  单卡视图（每个母题右上「单卡 →」）
  ├─ topics/*.html              母题页（复训牌组里的卡也能直接点进）
  └─ reviews/*.html             诊断页
```

**规则**：每个页面左上角都有返回链；主线子页顶部还有「训练台 / 上一条 / 下一条」。
**新增页面必须接进这条链**——孤页等于死页。构建后跑一次死链检查（见下）。

## 死链检查（改完 build 跑一次）

```bash
python - <<'PY'
import re, pathlib, urllib.parse
SITE = pathlib.Path("site")
bad = []
for p in sorted(SITE.rglob("*.html")):
    for href in re.findall(r'href="([^"]+)"', p.read_text(encoding="utf-8")):
        if href.startswith(("obsidian:", "http", "#", "mailto:", "data:")) or "+ " in href:
            continue
        t = urllib.parse.unquote(href.split("#")[0])
        if t and not (p.parent / t).resolve().exists():
            bad.append((str(p), href))
print("✅ 无死链" if not bad else "\n".join("%s -> %s" % b for b in bad))
PY
```

## 母题互链检查（新增母题卡后跑一次）

母题卡之间的 `[[母题-XX-名称]]` 是**按文件名**引用的，所以**编号错位或名称不一致会导致静默失效**（Obsidian 里显示为未解析链接，页面上看不出来）。
注意：**跨模块引用是允许的**（MySQL 卡可以引 PG 卡），所以检查要**全库搜索文件名**，不能只查本模块目录。

```bash
python - <<'PY'
import re, pathlib
all_md = {p.stem: p for p in pathlib.Path("wiki/topics").rglob("母题-*.md")}
print("母题卡总数:", len(all_md))
bad = {}
for p in all_md.values():
    for m in re.findall(r"\[\[(母题-[^\]]+)\]\]", p.read_text(encoding="utf-8")):
        if m not in all_md:
            bad.setdefault(m, set()).add(p.stem)
print("✅ 互链全部可对上" if not bad else "\n".join("❌ %s <- %s" % (k, ",".join(v)) for k, v in bad.items()))
PY
```

## 日常动线

| 时段 | 做什么 | 在哪 |
|---|---|---|
| 早上 5–10 分钟 | 今日到期的母题，先说后翻，点过关/忘了 | `site/index.html` |
| **每天开工** | **领今日作业（系统派单），做完点开走闭卷自评**；当天想多学 → 各板块「+ 继续派」按钮 | **`site/progress.html`** |
| 学完一条 | 闭卷自评「命中」即进复训阶梯（等级三档：未接触 / 会了 / 常练） | `site/progress.html` |
| 每 7 天 | 抽检轮：5 题连答 · 每题 60 秒 · 中途不给反馈（进度页「开始抽检」按钮） | `site/progress.html` |
| 学完一个母题 5 分钟内 | 在这张卡上自评一次（遗忘曲线最陡的一段在这） | `site/progress.html` |
| 掉档（部分/忘了）之后 | 让 AI 把这次的断点写进母题卡「本次断点」——下次复训会带着它回来 | Obsidian |
| 晚上 | 只清当日作业与欠账，不学新的 | `site/progress.html` |
| 白天 | 写笔记、讨论、推导 | Obsidian |
| 讨论完 | `python site/build.py` | 终端 |
| 要系统学一个模块 | 训练台 → 模块概览 → 进某一条主线 | `modules/` |
| 要深看某个母题 | 主线页里点「单卡 →」，或直接开 `topics/*.html` | 母题页 |
| 面试前 | 计时器（弹窗）+ 一页纸作战卡 | `site/index.html` |

## 内容怎么进 html（四种来源）

### 1. 母题卡 —— 自动抽取，零标记（主力）

按 `templates/母题卡模板.md` 写好就行，build 自动抽。**卡分三层：学（教材）→ 测（自测）→ 说（面试输出）**。

| 卡面 | 来自字段 | 是否折叠 |
|---|---|---|
| 导读条 | `**导读**` | 展开 |
| 题目 | `**题目**` | 展开 |
| **一 · 教材** | `## 一、教材` 整段（含就地图） | **展开** |
| **二 · 自测** | `## 二、自测` 里的 `**Qn（类型）**` / `**An**` → 翻转卡 | 展开，答案靠翻面 |
| **三 · 面试输出** | 主卡 Q/A = `**母题**` / `**一句话结论**`；关键词 = `**恢复关键词**` | 展开（**主卡是唯一进复训调度的单位**） |
| 展开组 | `**追问**`、`**同类变体**`、`**可迁移场景**`、`**完整回答骨架**`、`**核心不变量 / 主线**`、`**本次断点**`、`**通过证据**` | 折叠 |

**就地图**：在教材里写 `::figure 文件名.svg | 标题 | 说明`，图就插在那句话后面（svg 放 `site/figures/`）。**没被就地的图**会集中渲染到「图」区块。

**旧体裁兼容**：没有 `## 一、教材` 的卡，`---` 之后到 `## 二、` 之间的内容折叠在「讲解」面板（44 张老卡仍在用这条路径）。

字段缺失不报错，跳过即可——不因为格式不全卡住整条流水线。

**写作规范看 `templates/母题卡模板.md` 的六条**（首次使用必定义 / 比较前先介绍双方 / 同一指标才可比 / 量化给算式 / 结论标类型 / 节点小结）。**M1 是 A 级样板卡，改别人的卡前先读它。**

### 2. 面试手册 → 牌组（AI 母题 / 项目口述）

正本 `wiki/interview/面经-字节AI-Agent.md`，**按标题结构自动拆卡，零标记**：

| 牌组 | 来源 | 卡数 |
|---|---|---|
| AI 母题 | `## N. 母题 XX：<问题>` 的「15 秒」+「60 秒标准回答」 | 17 |
| 项目口述 | `## 20. 三个项目的定向回答卡` 下的 `### 20.N <项目>：<版本>` | 3 |

新写一篇面经时，只要沿用这两个标题格式，跑 build 就自动进相应牌组。
**没有「60 秒标准回答」小节的母题会被跳过**（比如母题 18 是计算机基础，已由后端教材覆盖）。
想加第二本手册，改 `build.py` 里的 `INTERVIEW_MANUAL`。

### 3. 补充卡 —— `::card`（模板覆盖不到时）

```md
::card id=lru-01 tag=算法
Q: 问题
A: 答案，可以换多行
::end
```

写在任何被扫描的 md 里：`site/cards/`、`output/算法/`、`study/`、`wiki/interview/`、`wiki/thinking/`、`projects/`。
`id` 全库唯一，重复跳过。想加扫描目录改 `build.py` 的 `CARD_DIRS`。

### 4. 图 —— `::figure`（AI 生成，人审图）

```md
::figure lru-two-views.svg | 标题 | 说明文字
```

文件放 `site/figures/`。build 会把 SVG 内联进页面（多图时自动加 id 前缀防冲突）。
流程：**md 里描述需要什么图 → AI 生成 svg → 人看图对不对**。人不需要会写 SVG。

### 4. 模块卡 —— 生成模块学习页

正本 `wiki/topics/{模块}/{模块}模块深挖卡.md`，按 `templates/模块深挖卡模板.md` 写。build 按**标题**取节（不是硬编码序号），产出：

| 节 | 变成 |
|---|---|
| 一句话结论 / 模块边界 | 概览页顶部 |
| 第 2 节 主线拆解 | 概览页的主线列表 → 每条一个子页 |
| 第 3 节 母题清单 | 子页的母题块（配合 `母题-NN-*.md` 出讲解） |
| 第 4 节 题单 | 按「归属主线」分发到各子页的题卡区 |
| 第 5 节 项目映射 | 概览页底部（每个项目一个折叠块） |
| 第 6 节 验收门 | 解析为清单（当前不在页面显示） |

**用标题找节的原因**：硬编码「第 N 节」在章节顺序调整后会静默取空——不报错，只是悄悄失效，很难发现。

## 组件（10 个，已封顶）

| 标签 | 用途 | 关键属性 |
|---|---|---|
| `flip-card` | 翻转卡，先说后翻 | `q` `a` `tag` `gradable` `card-id` |
| `timer-ring` | 限时输出计时 | `seconds` `label` `note` |
| `check-list` | 待办，`reset="daily"` 每日清零 | `key` `title` `reset` |
| `review-deck` | 间隔复训，多牌组切换 | `title`（数据取 `window.MARVIS_DECKS`） |
| `palace-map` | 房间导航，Obsidian URI 跳正本 | `vault` `layout="bar\|grid"` |
| `stat-bars` | 多维评分条 | `title` `data="标签:值,..."` `max` |
| `metric-strip` | 指标条 | 子 `<li data-label data-value>` |
| `collapse-panel` | 折叠分组 | `title` `open` |
| `figure-box` | 图容器 | `num` `title` `note` |
| `topic-view` | 母题页组装器（由 build 拼接，非运行时） | — |

**10 个封顶。要加第 11 个，说明结构设计错了。**

进度存 `localStorage`（键名 `mv.`）。换机器不迁移——进度不是资产，脑子里的才是。

## 规则（违反任何一条，系统会死）

1. **单向流**：md → build → html。html 永不回写 md。
2. **卡片不手写进 html / json**：必须由 adapter 抽取。
3. **组件库封顶 10 个**。
4. **入口只放每日必需**：其余进弹窗或子页。首页是「5 秒内开始练」的地方，不是展厅。
5. **规则只写在本文件与 PLAN.md**：不复制进 html，否则必然两边不一致。
6. **判据**：视图的价值 = 是否增加了**编码通道**（图/动/交互）或**提取动作**。只改排版 = 不做。
7. **只有 `status: integrated` 的正本才生成视图**；`candidate` / `reading` 停在 md。

## 死法预警

| 信号 | 含义 |
|---|---|
| 做页面的时间 > 练知识的时间 | 搬运取代训练（最阴险） |
| 页面数 > 每周打开次数 | 沦为第二个 `raw/` |
| 开始问「以哪个为准」 | 同步地狱 |
| 加第 11 个组件 | 结构设计错了 |
| md 里手写卡片数据 | 应当由 adapter 抽取 |
| 需要搜索才能找到房间 | 宫殿变迷宫 |
