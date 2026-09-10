# site · 学习界面

> **md 是工作台**（素材、讨论、推导、正本，允许乱）；
> **html 是学习界面**（表征、训练、诊断、交付，精炼）。
> 两者之间只有一条单向流：md → build.py → html。**html 永不回写 md。**
>
> 方案正本见 [`PLAN.md`](PLAN.md)。本文件是实现与用法说明。

## 目录

```text
site/
  index.html          唯一入口：房间直达 + 今日复训 + 今日保底（计时器在弹窗里）
  topics/             母题页（build 生成，勿手改）
  PLAN.md             方案正本
  build.py            构建器：按格式选 adapter → 视图 + 牌组数据
  cards/              补充卡草稿区（::card 也可直接写进任何 md）
  figures/            图（.svg），md 里用 ::figure 引用
  _data/              构建产物 decks.json（数据）/ decks.js（file:// 用）
  _components/        marvis.css + marvis.js，10 个原生 Web Components
```

## 日常动线

| 时段 | 做什么 | 在哪 |
|---|---|---|
| 早上 5–10 分钟 | 今日到期的母题，先说后翻，点过关/忘了 | `site/index.html` |
| 白天 | 写笔记、讨论、推导 | Obsidian |
| 讨论完 | `python site/build.py` | 终端 |
| 要深看某个母题 | 从训练台点「打开母题页」，或直接开 `topics/*.html` | 母题页 |
| 面试前 | 计时器（弹窗）+ 一页纸作战卡 | `site/index.html` |

## 内容怎么进 html（三种来源）

### 1. 母题卡 —— 自动抽取，零标记（主力）

按 `templates/母题卡模板.md` 写好就行，build 自动抽：

| 卡面 | 来自字段 |
|---|---|
| 主卡 Q / A | `**母题**` / `**一句话结论**` |
| 恢复关键词 | `**恢复关键词**` |
| 子卡（折叠） | `**两层追问**`、`**同类变体**`、`**可迁移场景**`、`**完整回答骨架**`、`**本次断点**` |

**一个母题 = 一个训练单元 = 一张主卡**。子卡默认收起，不进复训调度。
字段缺失不报错，跳过即可——不因为格式不全卡住整条流水线。

### 2. 补充卡 —— `::card`（模板覆盖不到时）

```md
::card id=lru-01 tag=算法
Q: 问题
A: 答案，可以换多行
::end
```

写在任何被扫描的 md 里：`site/cards/`、`output/算法/`、`study/`、`wiki/interview/`、`wiki/thinking/`、`projects/`。
`id` 全库唯一，重复跳过。想加扫描目录改 `build.py` 的 `CARD_DIRS`。

### 3. 图 —— `::figure`（AI 生成，人审图）

```md
::figure lru-two-views.svg | 标题 | 说明文字
```

文件放 `site/figures/`。build 会把 SVG 内联进页面（多图时自动加 id 前缀防冲突）。
流程：**md 里描述需要什么图 → AI 生成 svg → 人看图对不对**。人不需要会写 SVG。

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
