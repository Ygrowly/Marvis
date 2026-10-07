# -*- coding: utf-8 -*-
"""构建产物可复现性回归：遍历顺序不许依赖平台。

2026-10-07 加。背景：那晚 check-build 一直红，本地怎么重跑都复现不了——
根因是 `sorted(rglob(...))` 直接排Path 对象，而 pathlib 的Path 比较走
`_str_normcase`：Windows 上大小写不敏感（linux < llm），POSIX 上按码点序
（'L' < 'l'）→ 两端给出不同的模块顺序 → modules.js / breaks.js / cards.js
的条目序不同 → rebuild 产物与提交进仓库的不一致。

修法是 psort()（key = as_posix）。本测试守住两件事：
  ① psort 的顺序在两端一致（拿平台相关的两个名字当标尺，见check_sorted_key）；
  ② build.py 里凡是「遍历 glob/rglob 结果」的地方都走 psort，不许直接排 Path。
     光修不守 = 下次加遍历点又踩回去，而这类bug 本地100% 复现不了。
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BUILD = ROOT / "site" / "build.py"
src = BUILD.read_text(encoding="utf-8")

fails = []

# ---- ① psort 自身：排序键必须是字符串，不能是 Path 对象 --------------------
# 标尺：大小写不同的同族前缀。Windows 的Path 比较（大小写不敏感）给
# Linux 在前，POSIX 的码点序给 LLM 在前——两端相反，这才是那条bug 的标尺。
def psort(paths):
    return sorted(paths, key=lambda p: p.as_posix())


ruler = [pathlib.PurePosixPath("wiki/topics/LLM与上下文-模块卡.md"),
         pathlib.PurePosixPath("wiki/topics/Linux与部署-模块卡.md")]
got = [p.name for p in psort(ruler)]
got_names = got
if got != ["LLM与上下文-模块卡.md", "Linux与部署-模块卡.md"]:
    fails.append("psort 的排序键不是纯码点序：%s" % got)
else:
    print("  ✅ psort 键序 = 原始码点序（LLM 在 Linux 前，两端一致）")

# 反向对照：用旧写法（直接排 Path 对象）在本机上跑一遍，把「这写法随平台变」
# 这件事本身打印出来——下一个人再看到 psort 的注释时，能立刻对上号。
_win = [p.name for p in sorted([pathlib.Path("Linux与部署-模块卡.md"),
                                 pathlib.Path("LLM与上下文-模块卡.md")])]
print("     （对照）旧写法 sorted(Path) 在本机给的是 %s"
      % " / ".join(x[:4] for x in _win))
if _win != got_names:
    print("     → 确实相反：Linux 排在 LLM 前，这就是 CI 与本地产物不一致的来源")
else:
    fails.append("旧写法在本机竟与 psort 同序，说明标尺没选中大小写那一对")

# ---- ② build.py 里所有遍历点都必须走 psort --------------------------------
# 只管「glob/rglob 结果」这一种形状——排序对象是 Path，平台相关。
# 排字符串（如 sorted(domains)）跨平台本来就确定，不归这里管。
lines = src.split("\n")
bad = []
for i, ln in enumerate(lines, 1):
    st = ln.strip()
    if st.startswith("#"):
        continue
    if re.search(r"\b(r?glob)\s*\(", st) and re.match(r"for\s+\w+\s+in\s+", st):
        if "psort(" not in st:
            bad.append("L%d: %s" % (i, st[:78]))
    # for..in sorted(...) 且sorted 里排的是 glob 结果、又没有显式 key
    if re.match(r"for\s+\w+\s+in\s+sorted\(", st) and "key=" not in st \
            and re.search(r"(r?glob|psort)\s*\(", st):
        bad.append("L%d: %s" % (i, st[:78]))

if bad:
    fails.append("这些遍历点没有走 psort()：\n       " + "\n       ".join(bad))
else:
    n = sum(1 for ln in lines if "psort(" in ln and not ln.strip().startswith("#"))
    print("  ✅ build.py 全部 %d 处 psort 点都在（glob/rglob 无裸遍历、无裸 sorted(Path)）" % n)

if fails:
    print("\n❌ build 可复现性回归失败：")
    for f in fails:
        print("  -", f)
    sys.exit(1)

print("test_determinism: 全部断言通过 ✅（排序键跨平台确定 + 无裸 sorted(Path)）")