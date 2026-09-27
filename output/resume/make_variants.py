#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""按投递方向派生简历成品（方向改写器）。

## 红线（2026-09-20 修订）：事实不变，表达自由

- **事实层不可变**：数字、口径、可验证主张。唯一来源 = 母版 `刘宇广-AI应用开发-2027届.html`
  （它同时是 ① AI 应用/Agent 的成品）+ `刘宇广-简历量化指标口径.md`。
- **表达层按方向自由**：措辞与动词、强调哪一面、bullet 的详略与取舍、
  技能行的标签与顺序——不同岗位看的东西不同，同一件事本来就该有不同的讲法。
- **编辑入口仍然只有 1 个**：事实只在母版里改；本脚本只负责把同一批事实
  按各方向的讲法重新组织。

## 为什么推翻旧红线

旧版要求「四份 bullet 文本完全相同、只许换顺序」。那条规则把「不许分叉事实」
错误地实现成了「不许改写法」——而真实的风险从来不是措辞不同，是**数字和主张对不上**。
所以断言换成下面这组，既放开写法、又守住事实：

  ① 变体里出现的每个数字都必须在母版里出现过（不许凭空造数）
  ② 每条改写后的 bullet，其数字必须是**它所改自的那一条**的子集
     （不许跨条搬运数字——这是最容易发生的隐性编造）
  ③ 母版是变体的数字超集：**裁剪允许，编造不允许**
  ④ 每个方向必须保留自己那几条核心事实（防裁剪过头丢掉头号证据）
  ⑤ 技能行齐全、每段列表至少 3 条、母版结构没被改坏
  ⑥ 版面由 `check_layout.py` 的双尺证明（1 页 + 没有静默裁切）

## 改写依据（判断不写在注释里，写在正本里）

每个方向「面试官先问什么 / 该用什么词 / 忌什么」以及「同一件事在各方向怎么读」，
完整对照表在正本 `投递方向与简历侧重.md` **第 6 节**：

- **6.2 四个方向的语言体系** —— 第一问 / 该用的语言 / 忌讳
- **6.3 同一事实的写法对照** —— 逐格摘自四份已落地的成品（所以它同时是校验基线）

**改本文件的规格之前先看那两张表**，改完把新的实际写法回写 6.3（表与成品必须同步，
否则下次照着过期的表改）。

## 用法（在 output/resume/ 下）

    python make_variants.py                # 从母版重新派生三个方向
    python check_layout.py --all --export  # 然后必须重导 + 双尺校验四份

**不要直接改变体文件**——下次派生会覆盖它。这就是「编辑入口恒为 1」的执行方式。
"""
from __future__ import annotations

import pathlib
import re

HERE = pathlib.Path(__file__).parent.resolve()
MASTER = "刘宇广-AI应用开发-2027届.html"
NUM = re.compile(r"\d+(?:\.\d+)?")

src = (HERE / MASTER).read_text(encoding="utf-8")

# =====================================================================
# 事实源：把母版拆成可寻址的块
# =====================================================================

ULS = [m.group(0) for m in re.finditer(r"[ \t]*<ul>.*?</ul>", src, re.S)]
LIS = [re.findall(r"<li\b.*?</li>", u, re.S) for u in ULS]
SKILLS = [m.group(0).strip() for m in re.finditer(r'<div class="skill"[^>]*>.*?</div>', src)]
MASTER_NUMS = sorted(NUM.findall(src))

assert len(ULS) == 3, f"母版应有 3 个列表（EnergyOps / 数驭穹图 / RuleArena），实测 {len(ULS)}"
assert [len(x) for x in LIS] == [5, 5, 7], f"母版各列表条数变了：{[len(x) for x in LIS]}"
# ①2026-09-28 起母版加了第 3 面：前端技能行（第 4 行）+ RuleArena「前后端一致性」条（第 7 条）。
#    这两块不进②③④的方向派生（那三份按各自语言体系取舍），**只武装①**：AI 全栈 / 全栈
#    JD 投的就是母版。改这里之前先想清楚：母版加内容 = 挤版面，每加一行都要双尺验证。
assert len(SKILLS) == 4, f"技能行应为 4 行（含新增前端行），实测 {len(SKILLS)}"

UL_NAMES = ["EnergyOps", "数驭穹图", "RuleArena"]


def nums_of(text: str) -> list[str]:
    return sorted(NUM.findall(text))


# =====================================================================
# 各方向的改写规格
# =====================================================================
# op 语法：('k', i) 保留第 i 条原文 | ('r', i, txt) 改写第 i 条 | ('x', i) 删除第 i 条
# 列表顺序 = 该方向显示顺序；第 i 条 = 母版里的第 i 条（1 基）
# 未出现在 uls 里的列表 = 原顺序原样

# ---------------------------------------------------------------------
# ② FDE / AI 交付 —— 交付与验收语言
#   视角转换：客户现场怎么验收 → 需求怎么转译 → 问题怎么闭环 → 判定基准谁说了算
# ---------------------------------------------------------------------
E5_FDE = ('结算设<b>三道质量门</b>并与业务方共同确认：事实源门→预演门（分摊守恒校验）→'
          '责任门（<b>行政确认 + 财务核验</b>），任一失败阻断正式账单生成，分摊守恒率 100%；'
          '交付前 92 项单元 + 30 项回归测试把关，核心链路通过率 98.4%')

E4_FDE = ('<b>「异常候选 ≠ 业务告警」三层分离</b>：从多日历史学习正常形态输出异常候选，'
          '历史 dry-run 准入与告警指纹去重守住通知门槛——<b>客户收到的通知更少但更可信</b>，'
          '告警量降低 43%、平均研判时间 18min→6min')

E1_FDE = ('<b>把客户数据整理成能对账的账</b>：独立构建 '
          '<b>raw→interval→hourly→daily 四层能耗数据模型</b>与 7 类质量状态、可信白名单'
          '（含停用表残留起始数据、新表无起始读数），把参差读数整理为可信用能账、异常账与结算账，'
          '可信聚合完整率 96.8%→99.7%')

E2_FDE = ('把查询、设备、规则、告警、导出与结算封装为 <b>30 个 MCP 工具</b>与 6 类 Capability Bundle，'
          '以 <b>R0/R1/R2 操作风险分级</b>与 Before/After Tool 校验链界定 Agent 可触达范围；'
          '<b>80 条越权用例</b>（跨租户 / 越权限 / 越范围）<b>拦截率 100%</b>——'
          '客户最在意的权限边界可以自证；固定 72 条任务集（同模型同权限）完成率 83.3%→95.8%')

R1_FDE = ('把业务规则转成可执行的规则：自然语言 → 候选 <b>RuleSpec</b> → 确定性校验 → 歧义清单 → '
          '<b>与业务方逐条确认</b> → 不可变 RuleVersion，仅允许优惠、退款、积分、会员领域固定原语，'
          '禁止动态表达式求值，未确认规则不得进入攻击运行')

R2_FDE = ('<b>「候选风险 ≠ 确认漏洞」</b>：Agent 提议只算候选，经 Reference Simulator 快速探索 → '
          '干净 Commerce Sandbox 真实 HTTP 重放 → 由 Agent 之外的<b>独立 Oracle</b> 依据资金守恒、'
          '状态生命周期与幂等不变量裁决；<b>判定基准双方共同认可，Agent 不能触达 Ground Truth</b>')

R4_FDE = ('<b>交付过程中打出并修正四个真实缺陷</b>：工具层把沙箱「业务拒绝」'
          '（HTTP 200 + status: REJECTED）读成成功、504 未走恢复路径、同幂等键重放被当成新写入、'
          '门禁理由码泄给 Agent——全是真实运行打出来的，修完补回归测试（6 个测试文件）后重跑出上述数字')

R6_FDE = ('确认违规经删除式 <b>Delta Debugging</b> 压缩为 1-minimal 反例并绑定完整证据链'
          '（请求序列 + 回执 + 事件 + 状态 Diff + 违反的不变量），修复版本自动重放历史反例与正常 Case，'
          '反例沉淀为可加入回归套件的用例；显式 FSM 编排支持 Checkpoint 恢复与 '
          '<b>ACTION_UNKNOWN</b> 超时语义')

R5_FDE = ('建立 <b>21 + 17 双评测集</b>（hidden 物理隔离、Runtime 不可读）与四基线归一化预算消融'
          '（<b>golden-v4 / deepseek-v4.1-flash</b>）：hidden 集重复 3 次暴露 '
          '<b>pass@3 = 8/14 而 pass^3 = 1/14</b>，据此 Release Gate 如实拒绝放行（hidden 57% &lt; 75%）；'
          '机制层误报 0 / 泄漏 0 / 稳定重放 42/42')

SK_L2_FDE = ('<b>系统集成与交付：</b>REST / SSE、第三方平台对接、权限与合规边界、验收标准共建；'
             'Python、FastAPI、SQLAlchemy、Pydantic；异步任务编排；PostgreSQL、MySQL、Redis、DuckDB、'
             'Parquet；数据分层建模、指标口径治理；幂等控制、状态机约束、失败语义分级')

# ---------------------------------------------------------------------
# ③ AI 评测 / 测试 —— 可复现、可归因、能卡住发布
#   视角转换：判什么算过 → 谁说了算（确定性优先） → 怎么卡发布 → 缺陷怎么定界 → 反例怎么回流
# ---------------------------------------------------------------------
E5_EVAL = ('结算设<b>三道质量门</b>：事实源门→预演门（分摊守恒校验）→责任门（行政确认 + 财务核验），'
           '任一失败阻断正式账单生成，分摊守恒率 100%；<b>92 项单元 + 30 项回归测试</b>把关核心链路，'
           '通过率 98.4%')

E2_EVAL = ('把查询、设备、规则、告警、导出与结算封装为 <b>30 个 MCP 工具</b>与 6 类 Capability Bundle，'
           '实施 <b>R0/R1/R2 操作风险分级</b>与 Before/After Tool 校验链，固定 72 条任务集'
           '（同模型同权限）完成率 83.3%→95.8%；<b>80 条越权用例</b>（跨租户 / 越权限 / 越范围）'
           '<b>拦截率 100%</b>')

E4_EVAL = ('<b>误报治理「异常候选 ≠ 业务告警」三层分离</b>：自适应基线输出异常候选，'
           '历史 dry-run 准入与告警指纹去重守住通知门槛，告警量降低 43%、平均研判时间 18min→6min')

E1_EVAL = ('<b>「三账一体」核心设计</b>：独立构建 raw→interval→hourly→daily '
           '<b>四层能耗数据模型</b>，定义 7 类质量状态与可信白名单，'
           '把参差读数整理为可信用能账、异常账与结算账，可信聚合完整率 96.8%→99.7%')

D5_EVAL = ('<b>断言式口径校验：健康度评分与一票否决</b>——核心指标缺少业务定义即暂停该域自动问数；'
           'Schema/DDL 变更自动生成差异任务并降级资产可信度，过期语义不能冒充当前口径')

D3_EVAL = ('分析负载与客户生产库物理隔离：文件、协同表格与同步数据以 Parquet 副本交由 DuckDB 本地计算，'
           '强实时查询走只读受限连接（EXPLAIN 成本预估、慢查询熔断降级）；大结果外置为 <b>Artifact</b>，'
           '单次分析上下文 Token 18.4K→3.6K（↓80.4%）')

R4_EVAL = ('<b>缺陷定界（工程 bug vs 效果缺陷）</b>：执行中打出并修正四个真实缺陷——'
           '工具层把沙箱「业务拒绝」（HTTP 200 + status: REJECTED）读成成功、504 未走恢复路径、'
           '同幂等键重放被当成新写入、门禁理由码泄给 Agent；修完补回归测试（6 个测试文件）后重跑出上述数字')

SK_EVAL = ('<b>评测与质量工程：</b>评测集设计与防污染（hidden 物理隔离、Ground Truth 隔离）、'
           'pass^k 重复性度量、确定性 Oracle 裁决与模型自评的取舍、回归门禁与发布卡口、'
           'Bad Case 压缩与反例回流、误报 / 泄漏度量、故障定界（工程 vs 效果）、越权与提示注入对抗测试')

# ---------------------------------------------------------------------
# ④ 工程稳定向 —— 稳定、可审计、口径治理（C 层金融科技 / 央企 / 工业）
#   只动两条标签与排序，其余保留：C 层第一关在网申表单，不在简历措辞
# ---------------------------------------------------------------------
E3_ENG = ('<b>稳定性与性能：</b>重构聚合查询路径，消除设备归属关联导致的重复 JOIN 与全表扫描，'
          '补充组合索引与预聚合，固定查询集核心统计接口 P95 20.4s→2.8s；'
          '引入幂等窗口与任务状态持久化，定时聚合成功率 96.9%→99.6%')

E1_ENG = ('<b>数据建模与口径治理：</b>独立构建 raw→interval→hourly→daily '
          '<b>四层能耗数据模型</b>，定义 7 类质量状态与可信白名单（含停用表残留起始数据、新表无起始读数），'
          '把参差读数整理为可信用能账、异常账与结算账，可信聚合完整率 96.8%→99.7%')


DIRECTIONS = {
    "4": dict(
        filename="刘宇广-AI应用开发-工程交付向-2027届.html",
        title="刘宇广 - AI 应用开发 / 后端工程师",
        role="AI 应用 / 后端工程师",
        lede="工程交付向：把 AI 能力做成可审计、可回滚的生产系统——分层建模与口径治理、"
             "失败语义分级与幂等控制、性能与稳定性优化；不确定的输出由确定性检查兜住。",
        uls={0: [("r", 3, E3_ENG), ("r", 1, E1_ENG), ("k", 5), ("k", 2), ("k", 4)],
             1: [("k", 3), ("k", 2), ("k", 5), ("k", 4), ("k", 1)],
             2: [("k", 4), ("k", 3), ("k", 1), ("k", 6), ("k", 2), ("k", 5)]},
        skills=[2, 3, 1],
        must_have=["P95 20.4s→2.8s", "96.9%→99.6%", "口径一票否决", "四个真实缺陷",
                   "幂等", "96.8%→99.7%", "ActionReceipt"],
    ),
    "3": dict(
        filename="刘宇广-AI评测与测试开发-2027届.html",
        title="刘宇广 - AI 评测 / 测试开发",
        role="AI 评测 / 测试开发",
        lede="给不确定的模型输出建可复现的验收标准：把「哪版更好」变成能重跑、能归因、"
             "能卡住发布的确定性证据——评测集与防污染、独立 Oracle 裁决、回归门禁与反例回流。",
        uls={0: [("r", 5, E5_EVAL), ("r", 2, E2_EVAL), ("r", 4, E4_EVAL), ("r", 1, E1_EVAL)],  # 裁掉性能条
             1: [("k", 1), ("k", 2), ("r", 5, D5_EVAL), ("r", 3, D3_EVAL), ("k", 4)],
             2: [("k", 5), ("k", 2), ("k", 3), ("r", 4, R4_EVAL), ("k", 6), ("k", 1)]},
        skills=[("new", SK_EVAL), 1, 3, 2],
        must_have=["双评测集", "独立 Oracle", "Release Gate", "pass^3 = 1/14",
                   "92 项单元", "150 条评测集", "六阶段可归因链路"],
    ),
    "2": dict(
        filename="刘宇广-AI交付工程师-2027届.html",
        title="刘宇广 - AI 交付工程师（FDE）",
        role="AI 交付工程师（FDE）",
        lede="把 AI 落进客户的真实流程：对接客户既有系统、与业务方共建可验收标准、"
             "交付稳定的结果而不是可解释的中间件——解决方案从需求转译开始，到稳定运行结束。",
        uls={0: [("r", 5, E5_FDE), ("r", 4, E4_FDE), ("r", 1, E1_FDE), ("r", 2, E2_FDE), ("k", 3)],
             2: [("k", 3), ("r", 1, R1_FDE), ("r", 4, R4_FDE), ("r", 2, R2_FDE),
                 ("r", 6, R6_FDE), ("r", 5, R5_FDE)]},
        skills=[3, (2, SK_L2_FDE), 1],
        must_have=["三道质量门", "行政确认 + 财务核验", "80 条越权用例", "¥1920",
                   "Delta Debugging", "96.8%→99.7%", "交付过程中打出并修正四个真实缺陷"],
    ),
}


# =====================================================================
# 派生
# =====================================================================

def build_ul(sec: int, ops: list[tuple]) -> tuple[str, list[str]]:
    """按 ops 生成一段 <ul>，并返回 (html, 被删掉的母版条索引)。"""
    used: list[int] = []
    items: list[str] = []
    for op in ops:
        kind, idx = op[0], op[1]
        assert 1 <= idx <= len(LIS[sec]), f"{UL_NAMES[sec]} 没有第 {idx} 条"
        assert idx not in used, f"{UL_NAMES[sec]} 第 {idx} 条被用了两次"
        used.append(idx)
        if kind == "x":
            continue
        if kind == "k":
            items.append(LIS[sec][idx - 1])
        else:
            text = op[2]
            # ② 改写的数字必须是它所改自那一条的子集（不许跨条搬运数字）
            extra = sorted(set(nums_of(text)) - set(nums_of(LIS[sec][idx - 1])))
            assert not extra, (f"{UL_NAMES[sec]} 第 {idx} 条改写引入了原条没有的数字 {extra}"
                               f"——那是编造，不是改写")
            items.append(f"<li>{text}</li>")
    dropped = [i for i in range(1, len(LIS[sec]) + 1) if i not in used]
    if dropped:
        pass  # 允许裁剪，但 must_have 与 min_len 会兜住「裁过头」
    assert len(items) >= 3, f"{UL_NAMES[sec]} 只剩 {len(items)} 条——裁过头了"
    return "      <ul>\n        " + "\n        ".join(items) + "\n      </ul>", dropped


def build_skills(spec: list) -> str:
    out: list[str] = []
    labels: list[str] = []
    for item in spec:
        if isinstance(item, tuple):
            if item[0] == "new":
                text = item[1]
                # 新增行的数字必须来自母版整体（它没有单一祖先）
                extra = sorted(set(nums_of(text)) - set(MASTER_NUMS))
                assert not extra, f"新增技能行引入了母版没有的数字 {extra}"
                out.append(f'<div class="skill">{text}</div>')
                labels.append("new")
            else:
                idx, text = item
                extra = sorted(set(nums_of(text)) - set(nums_of(SKILLS[idx - 1])))
                assert not extra, f"技能行 {idx} 改写引入了原行没有的数字 {extra}"
                out.append(f'<div class="skill">{text}</div>')
                labels.append(f"L{idx}→改写")
        else:
            out.append(SKILLS[item - 1])
            labels.append(f"L{item}")
    return "    " + "\n    ".join(out), labels


def build(key: str, spec: dict) -> None:
    s = src
    name = spec["filename"]
    dropped_log: list[str] = []

    for pat, rep, what in (
        (r"<title>.*?</title>", f"<title>{spec['title']}</title>", "title"),
        (r'(<div class="role"[^>]*>).*?(</div>)', rf"\1{spec['role']}\2", "岗位名行"),
        (r'(<div class="lede"[^>]*>).*?(</div>)', rf"\1{spec['lede']}\2", "定位句"),
    ):
        s, n = re.subn(pat, rep, s, count=1, flags=re.S)
        assert n == 1, f"没找到{what}"

    # 列表：从后往前替换，避免前面的替换打乱后面的匹配位置
    for sec in sorted(spec["uls"], reverse=True):
        m = list(re.finditer(r"[ \t]*<ul>.*?</ul>", s, re.S))[sec]
        new_ul, dropped = build_ul(sec, spec["uls"][sec])
        if dropped:
            dropped_log.append(f"{UL_NAMES[sec]} 裁掉母版第 {dropped} 条")
        s = s[: m.start()] + new_ul + s[m.end():]

    # 技能行
    hits = list(re.finditer(r'[ \t]*<div class="skill"[^>]*>.*?</div>', s))
    assert len(hits) == 4, f"母版技能行应为 4 行，实测 {len(hits)} 行"
    new_sk, labels = build_skills(spec["skills"])
    s = s[: hits[0].start()] + new_sk + s[hits[-1].end():]

    # ---- ① 变体数字 ⊆ 母版数字（裁剪允许，编造不允许）----
    extra = sorted(set(nums_of(s)) - set(MASTER_NUMS))
    assert not extra, f"{name}: 出现母版里没有的数字 {extra}"

    # ---- ④ 核心事实锚点必须还在 ----
    missing = [k for k in spec["must_have"] if k not in s]
    assert not missing, f"{name}: 丢了本方向的核心事实 {missing}——裁过头了"

    # ---- ⑤ 结构完整性 ----
    expected_li = sum(len(LIS[sec]) for sec in range(3) if sec not in spec["uls"]) + sum(
        sum(1 for o in ops if o[0] != "x") for ops in spec["uls"].values())
    assert s.count("<li") == expected_li, f"{name}: li 数应为 {expected_li}，实测 {s.count('<li')}"
    assert s.count('<div class="skill"') == len(spec["skills"]), f"{name}: 技能行数量与规格不符"
    assert s.count("<html") == 1 and s.count("</html>") == 1, f"{name}: 结构被改坏"

    (HERE / name).write_text(s, encoding="utf-8", newline="\n")
    print(f"  ✓ {name}")
    print(f"      技能行 {' → '.join(labels)}")
    for d in dropped_log:
        print(f"      ⚠ {d}")


def main() -> None:
    print("从母版派生（按方向改写；事实锚点与数字集合都会断言）：")
    for key in ("4", "3", "2"):
        build(key, DIRECTIONS[key])
    print("\n下一步：python check_layout.py --all --export")


if __name__ == "__main__":
    main()
