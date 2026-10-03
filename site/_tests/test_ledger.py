# -*- coding: utf-8 -*-
"""问题台账解析器回归测试（2026-10-02）

跑法：python site/_tests/test_ledger.py
build.py 的 parse_questions_text 是纯函数，这里喂固定文本，不依赖仓库实际内容；
questions.md 版式（字段名、节名、状态标记）变动后这里必须仍全绿，改版式先改这里。
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import parse_questions_text  # noqa: E402

FIXTURE = """# 问题台账

## 周巡检（每周一次 · 15 分钟）

- [ ] 逐条更新「触碰」

## 当前战役（active · 上限 7）

### Q-2026-021 · 投递流水线跑起来 [active]

- 为什么现在：五大行 10/7–10/9 截止，
  这行折行续文应当并回同一字段
- 下一步：今天一个 30 min 投递块
- 落点：`output/秋招投递台账.html`
- 触碰：2026-09-24 ｜ 创建：2026-10-02

### Q-2026-022 · 没写状态标记的问题

- 下一步：字段不能串进上一条
- 触碰：2026-09-07 ｜ 创建：2026-09-07

## 移交与转出（这里的问题不该被解析）

- 2026-03-01 · Q-2026-099 · 假闭环行不许计数

## 已闭环

- 2026-03-04 · Q-2026-030 · 本周闭环
- 2026-02-20 · Q-2026-029 · 上周的不算
- 2026-01-09 · Q-2026-007 · 老账

## 冷却区（parked · 重启条件必填）

### Q-2026-009 · Java 最小可用栈 [parked]

- 为什么冷却：无对口投递
- 重启条件：再投 Java 栈岗位进面后 1 周
"""


def main():
    today = datetime.date(2026, 3, 6)          # 该周周五；周一 = 2026-03-02
    led = parse_questions_text(FIXTURE, today=today)

    # 周界：周一算本周起点
    assert led["weekStart"] == "2026-03-02", led["weekStart"]

    # active 解析 + 字段折行并回
    a = led["active"]
    assert [q["id"] for q in a] == ["Q-2026-021", "Q-2026-022"], a
    q21, q22 = a
    assert q21["title"] == "投递流水线跑起来"
    assert "五大行" in q21["why"] and "折行续文" in q21["why"], q21["why"]
    assert q21["next"] == "今天一个 30 min 投递块"
    assert q21["target"] == "`output/秋招投递台账.html`"
    assert q21["touched"] == "2026-09-24" and q21["created"] == "2026-10-02"

    # 状态标记缺省 → 跟随所在节；字段绝不串进上一条
    assert q22["status"] == "active"
    assert q22["why"] == "", q22
    assert q22["next"] == "字段不能串进上一条"
    assert q22["touched"] == "2026-09-07" and q22["created"] == "2026-09-07"

    # 移交区的「date · Q-xxx」行不算闭环；closed 只收已闭环节
    assert [c["id"] for c in led["closed"]] == ["Q-2026-030", "Q-2026-029", "Q-2026-007"], led["closed"]

    # 周计数只数本周一及以后
    week = sum(1 for c in led["closed"] if c["date"] >= led["weekStart"])
    assert week == 1, week

    # parked 解析
    p = led["parked"]
    assert len(p) == 1 and p[0]["id"] == "Q-2026-009", p
    assert p[0]["restart"] == "再投 Java 栈岗位进面后 1 周", p[0]["restart"]

    # 周一当天作为 today：当天闭环算本周（闭环行必须挂在「已闭环」节下）
    led2 = parse_questions_text(
        "## 已闭环\n\n- 2026-03-02 · Q-2026-001 · x\n",
        today=datetime.date(2026, 3, 2))
    assert led2["weekStart"] == "2026-03-02"
    assert sum(1 for c in led2["closed"] if c["date"] >= led2["weekStart"]) == 1

    print("test_ledger: 全部断言通过 ✅（active 字段/折行/状态缺省 · closed 周界 · parked 重启条件）")


if __name__ == "__main__":
    main()
