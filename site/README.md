# site · 知识宫殿（输出侧界面）

> md 负责**写与存**，html 负责**练与看全貌**。两者之间只有一条单向流。

## 目录

```text
site/
  index.html           唯一入口页：只放每日必需。计时器在弹窗里。第二个页面出现前不许建第三个
  build.py             扫描 md 里的 ::card，生成 _data/deck.json 与 deck.js
  cards/               卡片草稿区（::card 也可以直接写进任何 md）
  _data/               构建产物。deck.json 给未来用，deck.js 给 file:// 用
  _components/         marvis.css + marvis.js，7 个原生 Web Components
```

## 日常动线

| 时段 | 做什么 | 在哪 |
|---|---|---|
| 早上 5–10 分钟 | 今日到期卡片，先说后翻，点过关/忘了 | `site/index.html` |
| 白天 | 写笔记、学到能出题就加一行 `::card` | Obsidian |
| 改完卡片 | `python site/build.py` | 终端 |
| 面试前 | 90/60 秒计时器 + 一页纸作战卡打印 | `site/index.html` |

## 怎么加卡片

写在**任何被扫描的 md** 里（`site/cards/`、`output/算法/`、`study/`、`wiki/interview/`、`wiki/topics/`、`wiki/thinking/`、`projects/`）：

```md
::card id=lru-01 tag=算法
Q: LRU 为什么必须是哈希表 + 双向链表？
A: 哈希表 O(1) 定位，双向链表 O(1) 调序。
单链表拿不到前驱。
::end
```

- `id` 全库唯一，重复会被跳过
- `Q:` / `A:` 之后可以换多行，换行会保留
- `::end` 可省略（遇到下一个 `::card` 或文件结束自动收尾）
- 想加扫描目录，改 `build.py` 的 `SCAN_DIRS`

## 组件（7 个，已冻结）

| 标签 | 用途 | 关键属性 |
|---|---|---|
| `flip-card` | 翻转卡，先说后翻 | `q` `a` `tag` `gradable` |
| `timer-ring` | 限时输出计时 | `seconds` `label` `note` |
| `check-list` | 待办，`reset="daily"` 每天自动清零 | `key` `title` `reset` |
| `review-deck` | 1-3-7-14-30 间隔复训 | `title`（数据取 `window.MARVIS_DECK`） |
| `palace-map` | 宫殿房间，点击用 Obsidian URI 打开正本 | `vault` `layout="bar\|grid"` |
| `stat-bars` | 数据条 | `title` `data="标签:值,..."` `max` |
| `metric-strip` | 指标条 | 子 `<li data-label data-value>` |

进度存 `localStorage`，键名前缀 `mv.`。换机器不迁移——这是有意的，进度不是资产，脑子里的才是。

## 页面分层

| 位置 | 放什么 | 判据 |
|---|---|---|
| 入口页 `index.html` | 房间直达（紧凑条）、今日复训、今日保底 | 每天必用，5 秒内要能开始 |
| 弹窗 | 限时输出（4 个计时器） | 常用但非每日，不想跳页 |
| 二级页 | 暂不建 | 需要时再开，且先问「首页真的放不下吗」 |
| 本 README | 所有规则、用法、组件 API | 规则不进 html，避免双重维护 |

## 六条规则（违反任何一条，系统会死）

1. **单向流**：md → build.py → html。html 永不回写 md。
2. **卡片不手写进 html**：手写 json 必然烂尾。
3. **组件库冻结**：7 个定版，半年内不加。想加组件 = 用法错了，不是组件不够。
4. **只有一个入口页，且只放每日必需**：其余进弹窗或二级页。首页是「5 秒内开始练」的地方，不是功能展厅。
5. **规则只写在本文件**：不复制进 html，否则必然两边不一致。
6. **判据**：一个页面值不值得做，只看它逼你产生了多少次提取。

## 死法预警

| 信号 | 含义 |
|---|---|
| 页面数 > 每周打开次数 | 沦为第二个 `raw/` |
| 开始问「以哪个为准」 | 同步地狱 |
| 做页面的时间 > 练卡片的时间 | 搬运取代训练（最阴险的一种） |
| 需要搜索才能找到房间 | 宫殿变迷宫 |
