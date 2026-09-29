#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从「刘宇广-网申-公共层.md」派生四份**可直接整段复制**的网申成稿。

## 为什么用脚本生成，而不是手抄四份

2026-09-28 主人明确要求：**不要「替换清单」，要改好的完整版本，直接复制粘贴。**
但四个方向各存一份完整简历 = 日后改一个数字要改四处，**必然漂移**（这是本库
「事实只有一个入口」的红线）。所以：

- 事实写在 `刘宇广-网申-公共层.md`（唯一入口，手改这里）；
- 本脚本按方向的**讲法**重新组织，生成四份**完整成稿**（打开即贴）；
- 生成时跑断言，保证「放开写法、守住事实」。

## 断言（与 make_variants.py 同一套纪律）

① 每条改写的数字，必须是**它所改自那一条**的子集（不许跨条搬运数字）
② 成稿里出现的每个数字，都必须在公共层里出现过（裁剪允许，编造不允许）
③ 每方向的核心锚点必须还在（防裁过头丢掉头号证据）
④ 每段的 bullet 数与规格一致

## 用法

    python make_net_versions.py     # 在 output/resume/ 下

改事实 → 改公共层 → 跑本脚本。不要手改成稿。
"""
from __future__ import annotations

import pathlib
import re

HERE = pathlib.Path(__file__).parent.resolve()
SRC = "刘宇广-网申-公共层.md"
NUM = re.compile(r"\d+(?:\.\d+)?")

raw = (HERE / SRC).read_text(encoding="utf-8")


# =====================================================================
# 拆公共层：按 "## " 切段，段内 "- " 开头的是 bullet，其余是段头
# =====================================================================

def parse_sections(text: str) -> dict[str, tuple[list[str], list[str]]]:
    """按 "## " 切段。段头只取**第一条 bullet 之前**的行——

    段尾那些 `---` 分隔线必须丢掉：它们属于排版不属于内容，混进段头会跑到
    bullet 前面去（实测：整段变成「段头 → --- → bullet」）。
    """
    out: dict[str, tuple[list[str], list[str]]] = {}
    cur: str | None = None
    head: list[str] = []
    body: list[str] = []
    for line in text.split("\n"):
        if line.startswith("## "):
            if cur:
                out[cur] = (head, body)
            cur = line[3:].strip()
            head, body = [], []
        elif cur is None:
            continue
        elif line.startswith("- "):
            body.append(line[2:])
        elif not body:
            head.append(line)
        # 第一条 bullet 之后的行（分隔线等）一律丢弃
    if cur:
        out[cur] = (head, body)
    return out


SEC = parse_sections(raw)


def sec(prefix: str) -> tuple[str, list[str], list[str]]:
    """返回 (段标题, 段头行, bullet 列表)。段标题要在成稿里变成 `###`。"""
    hit = [k for k in SEC if k.startswith(prefix)]
    assert len(hit) == 1, f"公共层里「{prefix}」命中 {len(hit)} 个段"
    head, body = SEC[hit[0]]
    return hit[0], head, body


BASE_INFO = SEC["基本信息"][0]
EDU = SEC["教育经历"][0]
E_NAME, E_HEAD, E = sec("实习1")
S_NAME, S_HEAD, S = sec("实习2")
R_NAME, R_HEAD, R = sec("项目 RuleArena")
_, _, SKILLS = sec("专业技能")
AWARD = SEC["获奖情况"][0]

assert [len(E), len(S), len(R)] == [6, 6, 6], f"公共层条数变了：{[len(E), len(S), len(R)]}"
assert len(SKILLS) == 6, f"技能全集应为 6 行，实测 {len(SKILLS)}"

BASE_NUMS = sorted(NUM.findall(raw))

# 不属于「简历数字指标」、因此不要求出现在公共层里的数字。
# 2027 = 届别 / 毕业年份（公共层里写作 2027.06，正则切不出来），它是时间标签不是主张。
ALLOWED_EXTRA = {"2027"}


def nums_of(t: str) -> list[str]:
    return sorted(NUM.findall(t))


def pick(base: list[str], spec: list[tuple]) -> list[str]:
    """spec = [(idx, 替换文本或 None)]；idx 是 1 基的公共层条号。"""
    used: list[int] = []
    out: list[str] = []
    for idx, repl in spec:
        assert 1 <= idx <= len(base), f"没有第 {idx} 条"
        assert idx not in used, f"第 {idx} 条被用了两次"
        used.append(idx)
        if repl is None:
            out.append(base[idx - 1])
        else:
            # ① 改写的数字必须是它所改自那一条的子集
            extra = sorted(set(nums_of(repl)) - set(nums_of(base[idx - 1])))
            assert not extra, f"第 {idx} 条改写引入了原条没有的数字 {extra}——那是编造，不是改写"
            out.append(repl)
    return out


# =====================================================================
# 四个方向的改写规格（语言体系照「投递方向与简历侧重.md」第 6.2 节）
# =====================================================================

E2_FDE = "权限边界可以自证：把查询、设备、规则、告警、导出与结算封装为 30 个 MCP 工具与 6 类 Capability Bundle，以 R0/R1/R2 操作风险分级与 Before/After Tool Hook 校验界定 Agent 可触达范围；80 条越权用例（跨租户 / 越权限 / 越范围）拦截率 100%，固定 72 条任务集（同模型同权限）完成率由 83.3% 提升至 95.8%"

E5_FDE = "客户收到的通知更少但更可信：「异常候选 ≠ 业务告警」三层分离，自适应基线从多日历史学习正常形态并输出异常候选，历史 dry-run 准入与告警指纹去重守住通知门槛，告警量降低 43%、异常平均研判时间 18min→6min"

E1_FDE = "把客户数据整理成能对账的账：独立构建 raw→interval→hourly→daily 四层能耗数据模型，定义 7 类质量状态与可信白名单，把参差读数整理为可信用能账、异常账与结算账；按 15 分钟周期处理 604 台设备、日均 5.8 万条读数，可信聚合完整率由 96.8% 提升至 99.7%"

E6_FDE = "交付以验收为准：建设 92 项单元测试与 30 项回归测试，覆盖统计口径、数据质量、工具参数、权限边界与失败恢复，核心链路回归通过率 98.4% —— 交付物的质量可以核验，不靠口头保证"

R1_FDE = "把业务规则转成可执行的规则：自然语言 → 候选 RuleSpec → 确定性校验 → 歧义清单 → 与业务方逐条确认 → 不可变 RuleVersion，仅允许优惠、退款、积分、会员领域固定原语，禁止动态表达式求值，未确认规则不得进入攻击运行"

E6_EVAL = "质量门禁：建设 92 项单元测试与 30 项回归测试，覆盖统计口径、数据质量、工具参数、权限边界与失败恢复，核心链路回归通过率 98.4%"

E2_EVAL = "固定基准才谈得上验收：把查询、设备、规则、告警、导出与结算封装为 30 个 MCP 工具与 6 类 Capability Bundle，实施 R0/R1/R2 操作风险分级与 Before/After Tool Hook 校验链；固定 72 条任务集（同模型同权限同快照）任务完成率由 83.3% 提升至 95.8%，80 条越权用例（跨租户 / 越权限 / 越范围）拦截率 100%"

E5_EVAL = "误报治理：「异常候选 ≠ 业务告警」三层分离，自适应基线输出异常候选，历史 dry-run 准入与告警指纹去重守住通知门槛，告警量降低 43%、平均研判时间 18min→6min —— 不把候选当结论"

E1_EVAL = "评测前提是可信数据：构建 raw→interval→hourly→daily 四层模型，定义 7 类质量状态与可信白名单，仅允许可信区间进入聚合层，可信聚合完整率由 96.8% 提升至 99.7%"

S3_EVAL = "对抗测试：构建 5 层查询安全边界（JWT + 租户权限 → 受治理 Tool 注册 → Tool Call Schema/Validator 校验 → 只读 SQL AST 审查 → 输出字段脱敏），300 条对抗请求中危险语句拦截率 100%、正常查询误拦率 2.7%"

E3_ENG = "性能优化：重构聚合查询路径，消除设备归属关联导致的重复 JOIN 与全表扫描，补充组合索引与预聚合，固定查询集核心统计接口 P95 由 20.4s 降至 2.8s（耗时降低 86.3%）"

E1_ENG = "数据建模与口径治理：独立构建 raw→interval→hourly→daily 四层能耗数据模型，定义 7 类质量状态与可信白名单，把参差读数整理为可信用能账、异常账与结算账，可信聚合完整率由 96.8% 提升至 99.7%"

E4_ENG = "稳定性：引入幂等窗口、任务状态持久化与启动时 7 天自动回补，解决服务重启与乱序补数造成的聚合缺口，定时聚合成功率由 96.9% 提升至 99.6%，人工补数次数降低 72%"

DIRECTIONS = {
    "刘宇广-网申-①AI应用.md": dict(
        label="① AI 应用 / Agent 开发",
        role="AI 应用开发工程师 / Agent 后端工程师（Python）",
        intro="全网申字段的**基准版**：事实与讲法都不做取舍，信息密度最均衡。也是四个方向里唯一保留全部六行技能行的一版。",
        self_eval=(
            "我做的是 Agent 应用的工程层：用 Agent 能力做业务应用，同时自研运行时关键模块（工具治理、上下文压缩、执行链路归因），"
            "让不确定的模型输出在生产里可验证、可回滚、可评测。三段经历构成一条主线——数据可信（数驭穹图）→ 执行可控（EnergyOps）"
            "→ 结果可证（RuleArena）。在金山独立设计实现 EnergyOps Agent 的数据链路与工具治理：30 个 MCP 工具收敛为 6 类 "
            "Capability Bundle，实施 R0/R1/R2 三级操作风险管控，在固定 72 条任务集（同模型同权限）上任务完成率由 83.3% 提升至 95.8%，"
            "80 条越权用例（跨租户 / 越权限 / 越范围）拦截率 100%。在初创公司核心开发企业问数平台 Data Agent 链路与 5 层查询安全边界，"
            "150 条评测集「SQL 可执行且结果口径正确」的查询占比由 78% 提升至 91%（判定含人工复核）。个人项目 RuleArena 做业务 Agent "
            "上线前的执行门禁（工具契约 + 运行时拦截 + 独立 Oracle）：双评测集实测中 dev 集策略上限已超过确定性 BFS，但重复运行暴露搜索"
            "不可复现（pass@3 = 57% vs pass^3 = 7%），据此如实拒绝放行。具备扎实的 Python 后端基本盘（FastAPI / PostgreSQL / Redis，"
            "幂等控制、状态机约束、异步任务编排）。核心原则是「能由代码确定性保证的，不交给模型」。2027 届应届生，可全职实习并提前到岗。"
        ),
        skills=[1, 2, 3, 4, 5, 6],
        E=[(1, None), (2, None), (3, None), (4, None), (5, None), (6, None)],
        S=[(1, None), (2, None), (3, None), (4, None), (5, None), (6, None)],
        R=[(1, None), (2, None), (3, None), (4, None), (5, None), (6, None)],
        must_have=["96.8% 提升至 99.7%", "pass^3 = 1/14", "Release Gate", "78% 提升至 91%"],
        jd=(
            "**AI 全栈 / 全栈工程师 JD 也归这一套**：职责是 LLM / Agent 应用开发 + 能写点前端页面的 → 用这份；"
            "技能行的「前端与实时交互」保留（这是被 ATS 命中的唯一入口）。\n\n"
            "**跳过线**：JD 要前端工程化深度（组件库 / 微前端 / 跨端 / 前端性能专项）→ 不投，那是前端岗披 AI 皮。"
        ),
    ),
    "刘宇广-网申-②FDE交付.md": dict(
        label="② FDE / AI 交付 / 解决方案",
        role="AI 交付工程师 / 解决方案工程师（FDE）",
        intro="交付语言：先讲客户最终拿到什么形态，再讲链路怎么搭的；每个 bullet 都往「可验收」上落。",
        self_eval=(
            "我做的是把 AI 能力交付进客户的真实业务流程：对接客户既有系统、把模糊需求转成双方确认的验收标准，交付能直接给业务用的结果，"
            "而不是一份需要解释的中间件。金山实习独立负责园区能耗平台的交付链路——对接第三方能耗平台 604 台水电表的累计读数，与行政、财务"
            "共建三道验收门，最终产出的月度结算单带计算说明与差异检查、可直接交财务核验；查询、设备等六类能力封装为 30 个 MCP 工具并按 "
            "R0/R1/R2 操作风险分级，权限边界用 80 条越权用例自证（拦截 100%）。在初创团队核心开发企业问数平台，面向没有专职数据团队的中小"
            "企业业务人员，交付「有来源、有口径、可验证、可编辑共享」的分析结果并支持回写协同表格。个人项目 RuleArena 把「业务方确认」做成"
            "机制：自然语言规则必须逐条确认才生效，候选风险要经独立沙箱真实重放、由独立 Oracle 裁决才算数。习惯从客户的验收标准倒推实现，"
            "而不是从代码能力正推功能。2027 届，可全职实习到毕业。"
        ),
        skills=[
            "AI 应用与受控操作：MCP 工具封装、Capability Bundle 路由、Hook 链治理、操作风险分级（R0/R1/R2）、HITL 确认、确定性 Oracle 裁决",
            "系统集成与交付：REST / SSE、第三方平台对接、权限与合规边界、验收标准共建、需求转译与客户沟通",
            "后端开发：Python / FastAPI / SQLAlchemy / Pydantic；异步任务编排；PostgreSQL、MySQL、Redis；幂等控制、状态机约束、失败语义分级",
            "前端与实时交互：JavaScript / TypeScript；SSE 实时监控界面与前后端状态一致性；Univer 在线表格集成",
            "数据工程：数据分层建模、指标口径治理、多源接入、湖仓查询",
            "工程交付：Git、Docker Compose、Nginx、CI/CD；Claude Code / Codex 仓库级实践；CET-6",
        ],
        E=[(6, E6_FDE), (5, E5_FDE), (1, E1_FDE), (2, E2_FDE), (3, None), (4, None)],
        S=[(6, None), (1, None), (2, None), (3, None), (4, None), (5, None)],
        # ② 保留 R6（前后端一致性）：客户现场常常连界面一起交付，这一条是②的加分项
        R=[(3, None), (1, R1_FDE), (2, None), (5, None), (4, None), (6, None)],
        must_have=["604 台设备", "80 条越权用例", "三道验收门", "与业务方逐条确认"],
        jd=(
            "JD 出现「客户现场 / 部署 / 对接 / 验收 / demo / PoC」→ 用 JD 原词替换对应位置的措辞。\n\n"
            "别把可靠性数字（20.4s→2.8s）删太干净——交付岗同样要看系统稳不稳。"
        ),
    ),
    "刘宇广-网申-③AI评测.md": dict(
        label="③ AI 评测 / 测试开发",
        role="AI 评测工程师 / 测试开发工程师（AI 方向）",
        intro="评测语言：判什么算过、谁说了算、怎么卡住发布、缺陷怎么定界。**这一方向的忌讳是堆业务价值数字**——增量指标留一到两个即可。",
        self_eval=(
            "我的主线是给不确定的模型输出建可复现的验收标准：评测集怎么设计、判定谁说了算、怎么卡住发布、缺陷怎么定界。金山实习为 Agent "
            "操作模块建固定基准：固定 72 条任务集（同一模型版本、同一权限配置、同一数据快照）上的任务完成率由 83.3% 提升至 95.8%，80 条越权"
            "用例（跨租户 / 越权限 / 越范围）拦截率 100%；配套 92 项单元测试与 30 项回归测试，核心链路回归通过率 98.4%。告警侧做误报治理："
            "用三层分离加 dry-run 准入守住通知门槛，不让「候选」冒充结论。在初创团队把问数质量做成可归因链路：六阶段拆分让业务理解、SQL 生成"
            "与执行错误能独立归因，单条 Bad Case 定位时间由 30 分钟降至 8 分钟，150 条评测集上「SQL 可执行且结果口径正确」的查询占比由 78% "
            "提升至 91%（判定含人工复核）。个人项目 RuleArena 是一套完整的评测与门禁系统：21+17 双评测集（hidden 物理隔离）、独立 Oracle 裁决、"
            "Release Gate 不达标就如实拒绝放行，并把「跑 3 次至少成一次」与「3 次次次都成」如实分开报。缺陷能定界到是工程 bug 还是效果问题。"
            "2027 届，可全职实习到毕业。"
        ),
        skills=[
            "评测与质量工程：评测集设计与防污染（hidden 物理隔离、Ground Truth 隔离）、pass@k 与 pass^k 重复性度量、确定性 Oracle 裁决 vs 模型自评、回归门禁与发布卡口、Bad Case 压缩与反例回流、误报 / 泄漏度量、故障定界（工程 vs 效果）、越权与提示注入对抗测试",
            "测试与工具链：pytest、CI/CD、Docker Compose；分层评测体系、归一化预算消融、Bad Case 回归集",
            "后端开发：Python / FastAPI / SQLAlchemy / Pydantic；REST / SSE、异步任务编排；PostgreSQL、MySQL、Redis；幂等控制、状态机约束",
            "数据工程：数据分层建模、指标口径治理、多源接入",
            "语言：CET-6，可阅读英文技术文档",
        ],
        E=[(6, E6_EVAL), (2, E2_EVAL), (5, E5_EVAL), (1, E1_EVAL), (4, None)],
        S=[(1, None), (2, None), (4, None), (3, S3_EVAL), (5, None), (6, None)],
        R=[(3, None), (1, None), (2, None), (5, None), (4, None)],
        must_have=["92 项单元", "对抗测试", "Release Gate", "150 条"],
        jd=(
            "JD 出现「模型评测体系 / 效果评测 / 回归 / 卡口 / 自动化测评」→ 在自我评价第 2 句前插入对方 JD 的原词。\n\n"
            "这一方向吃的是「能不能复现、能不能卡住」，不是业务涨幅——别把 43%、99.7% 全铺上去。"
        ),
    ),
    "刘宇广-网申-④工程稳定.md": dict(
        label="④ 工程稳定向 / 后端",
        role="后端开发工程师（Python）/ AI 应用工程师",
        intro="工程语言：稳不稳、口径谁定的、能不能审计。**这一档的忌讳是拿过度前沿的词当卖点**——Agent / 自研全部降级成一句。",
        self_eval=(
            "我的方向是把数据和后端链路做成稳定、可审计的生产系统。金山实习独立负责能耗数据链路：设计 raw→interval→hourly→daily 四层数据"
            "模型与 7 类质量状态、可信白名单，可信聚合完整率由 96.8% 提升至 99.7%；重构聚合查询路径，消除重复 JOIN 与全表扫描、补组合索引与"
            "预聚合，固定查询集核心统计接口 P95 由 20.4s 降至 2.8s；引入幂等窗口、任务状态持久化与启动自动回补，定时聚合成功率由 96.9% 提升"
            "至 99.6%，人工补数次数降低 72%；以 92 项单元测试与 30 项回归测试把关核心链路。在初创团队负责查询安全与数据接入：5 层安全边界"
            "（租户权限、受治理 Tool 校验、只读 SQL AST 审查、输出脱敏），300 条对抗请求中危险语句拦截率 100%、正常查询误拦率 2.7%，分析负载"
            "与客户生产库物理隔离。技术栈 Python / FastAPI / PostgreSQL / Redis，幂等控制、状态机约束、异步任务编排、失败语义分级都在项目里"
            "做过完整实现。2027 届，可全职实习到毕业，接受轮值。"
        ),
        skills=[
            "后端开发：Python / FastAPI / SQLAlchemy / Pydantic；REST / SSE、异步任务编排；PostgreSQL、MySQL、Redis；幂等控制、状态机约束、失败语义分级、长任务断线恢复",
            "数据工程：数据分层建模、湖仓查询路由、指标口径治理；DuckDB、Parquet",
            "质量与稳定性：pytest、CI/CD、Docker Compose、Nginx；回归测试与发布卡口、可观测性",
            "AI 应用：Agent 工具封装、操作风险分级、HITL 确认、上下文压缩与 Artifact 外置",
            "语言：CET-6，可阅读英文技术文档",
        ],
        E=[(3, E3_ENG), (1, E1_ENG), (4, E4_ENG), (6, None), (2, None), (5, None)],
        S=[(3, None), (2, None), (5, None), (4, None), (1, None), (6, None)],
        R=[(4, None), (3, None), (1, None), (5, None), (2, None)],
        must_have=["20.4s 降至 2.8s", "96.9% 提升至 99.6%", "2.7%"],
        jd=(
            "JD 出现「金融科技 / 国资背景 / 电力能源 / 数据治理」→ 把「口径治理 / 能对账 / 幂等」这三个词提到自我评价第一句。\n\n"
            "Agent / 自研这类词在这一档不加分，主体留给稳定与可审计。"
        ),
    ),
}

OPEN_Q = (
    "网申表单里的**开放题 / 简答题**（三个优势、为什么选这个岗位、最有挑战的项目）不在这里——"
    "见 `output/网申开放题作答-刘宇广.md`（按公司逐条追加，同一题目只留一份最优版本）。"
)


def block(name: str, head: list[str], body: list[str]) -> str:
    """成稿里的一段：### 公司/项目名 → 段头（项目行、工作描述等）→ bullet。"""
    return (
        f"### {name}\n\n"
        + "\n".join(head).strip()
        + "\n\n"
        + "\n".join(f"- {b}" for b in body)
        + "\n"
    )


def build(fname: str, spec: dict) -> None:
    E_out = pick(E, spec["E"])
    S_out = pick(S, spec["S"])
    R_out = pick(R, spec["R"])
    skills = spec["skills"]
    if skills and isinstance(skills[0], int):
        skills = [SKILLS[i - 1] for i in skills]

    body = "\n".join([
        f"# 刘宇广 — 网申版 · {spec['label']}（成稿）",
        "",
        f"> **本文件由 `make_net_versions.py` 从 `刘宇广-网申-公共层.md` 自动生成，不要手改**（改了会被下次生成覆盖）。",
        f"> 改数字 / 口径 → 改公共层 → 重跑脚本。",
        "",
        f"> **怎么用**：牛客网申助手里建一套简历，按字段整段复制即可。{spec['intro']}",
        "",
        "---",
        "",
        "## 基本信息",
        "",
        "\n".join(BASE_INFO).strip(),
        "",
        "---",
        "",
        "## 教育经历",
        "",
        "\n".join(EDU).strip(),
        "",
        "---",
        "",
        "## 求职意向",
        "",
        "| 字段   | 内容               |",
        "| ---- | ---------------- |",
        f"| 期望职位 | {spec['role']} |",
        "| 期望城市 | （按投递岗位填写）         |",
        "| 期望薪资 | 面议               |",
        "",
        "> 期望职位只填一个方向（填多个会被系统匹配降权）。",
        "",
        "---",
        "",
        "## 实习经历",
        "",
        block(E_NAME, E_HEAD, E_out),
        block(S_NAME, S_HEAD, S_out),
        "---",
        "",
        "## 项目经历",
        "",
        block(R_NAME, R_HEAD, R_out),
        "---",
        "",
        "## 专业技能",
        "",
        "\n".join(f"- {s}" for s in skills),
        "",
        "---",
        "",
        "## 自我评价",
        "",
        spec["self_eval"].strip(),
        "",
        "---",
        "",
        "## 获奖情况",
        "",
        "\n".join(AWARD).strip(),
        "",
        "---",
        "",
        "## 按这家 JD 再调一层（可选）",
        "",
        spec["jd"],
        "",
        "**三层微调法**：① 选方向（已经选了这份）→ ② 按 JD 第一条职责把对应 bullet 提到该段第一句 → ③ 措辞向 JD 原词靠。",
        "**红线**：不许新增数字与主张；JD 提到但没做过的（Dify / LangChain / 前端工程化）一律不写。",
        "",
        "---",
        "",
        "## 开放题",
        "",
        OPEN_Q,
        "",
    ])

    # ---- ② 成稿数字 ⊆ 公共层数字（裁剪允许，编造不允许）----
    extra = sorted(set(nums_of(body)) - set(BASE_NUMS) - ALLOWED_EXTRA)
    assert not extra, f"{fname}: 出现公共层里没有的数字 {extra}"

    # ---- ③ 核心锚点 ----
    missing = [k for k in spec["must_have"] if k not in body]
    assert not missing, f"{fname}: 丢了本方向的核心事实 {missing}——裁过头了"

    (HERE / fname).write_text(body, encoding="utf-8", newline="\n")
    print(f"  ✓ {fname}  （E{len(E_out)}/S{len(S_out)}/R{len(R_out)} 条 · 技能 {len(skills)} 行）")


def main() -> None:
    print("从网申公共层派生四份成稿（生成时跑数字与锚点断言）：")
    for fname, spec in DIRECTIONS.items():
        build(fname, spec)
    print("\n四份都是完整成稿 —— 打开整段复制即可，不用再自己拼。")


if __name__ == "__main__":
    main()
