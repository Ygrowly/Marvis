# -*- coding: utf-8 -*-
"""CI 诊断：rebuild 产物 vs HEAD 里的产物（check-build 断言失败时调用）。

只报告不改文件，退出码恒为 0（诊断不该再把CI 弄红一次）。

三种成因要能一眼分开（2026-10-07 修bug 时补的判别力）：
  ① 纯换行——  work只有 CRLF/LF 差异，规范成 LF 后与 blob 逐字节相同；
  ② 顺序不同——  两边「条目集合」完全一样，只是排列次序不同（键序 / 数组序）；
     这就是psort 修之前那个 bug 的签名：同一份源码，Windows 与 Linux 排出来的
     顺序不一样（pathlib 的 Path 比较在 Windows 上大小写不敏感）。
     再看一眼两边的顺序，报出「谁在谁前面」，一眼就能确认是不是大小写那对。
  ③ 真内容差异 —— 集合都不同，那就是md 正本改了但产物没重新生成，照提示跑
     python site/build.py 再提交。
"""
import json
import re
import subprocess
import sys


def run(*a):
    return subprocess.run(list(a), capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


# 1) 全部改动的产物文件（不写死清单——以前写死三个，漏一个就看不见那个）
changed = [ln[3:] for ln in run("git", "status", "--porcelain", "site/").splitlines()
           if ln[:3].strip() in ("M", "A", "D", "R", "??")]
if not changed:
    print("site/ 下没有改动 —— 那断言可能是别的原因（如 CRLF / 文件缺失），"
          "先看上一条 git status --porcelain site/ 的输出。")
    sys.exit(0)

# 2) 数据类文件按「条目」切，顺序问题才看得出来
ENTRY_KEYS = ("module", "id", "key", "href", "title", "path", "date", "no")


def entries(txt):
    """把 JS 载荷粗切成条目：抓每条开头的标识字段值。

    不追求解析正确（那是 JS 的事），只要能给出稳定的「条目签名序列」，
    足以判断「集合相同、顺序不同」。
    注意 key 允许带引号——产物里写的是 {"module": "..."}。
    """
    pat = r'\{\s*\"?(?:%s)\"?\s*:\s*(\"(?:[^\"\\]|\\.)*\"|[^,{}]+)' \
        % "|".join(ENTRY_KEYS)
    return [m.group(1).strip() for m in re.finditer(pat, txt)]


def keys(txt):
    """顶层对象的键（breaks.js 形如 "topics/....html": {...}，键在 { 外面）。

    breaks.js 是「文件名 -> 断点信息」的字典，键就是条目标识，
    但键写在 { 之前，所以走不到 entries()——拿它当第二条判别路径。
    """
    pat = r'\"((?:[^\"\\]|\\.)+)\"\s*:\s*\{'
    return [m.group(1) for m in re.finditer(pat, txt)]


nl = "\n"
for f in changed:
    blob = subprocess.run(["git", "show", "HEAD:" + f],
                          capture_output=True).stdout.replace(b"\r\n", b"\n")
    try:
        work = open(f, "rb").read().replace(b"\r\n", b"\n")
    except OSError:
        print("%s | 本地不存在（CI 上被删/未生成？）" % f)
        continue

    print("=" * 72)
    print("%s | blob %d B | work %d B" % (f, len(blob), len(work)))

    if work == blob:
        print("  -> 内容一致（差异仅 CRLF/LF）")
        continue

    eb = entries(blob.decode("utf-8", "replace")) or keys(blob.decode("utf-8", "replace"))
    ew = entries(work.decode("utf-8", "replace")) or keys(work.decode("utf-8", "replace"))
    if eb and eb and sorted(eb) == sorted(ew):
        print("  -> 成因② 集合相同、顺序不同 = 遍历顺序不确定")
        for i, (x, y) in enumerate(zip(eb, ew)):
            if x != y:
                print("     第 %d / %d 个条目：blob=%s  work=%s" % (i + 1, len(eb), x, y))
                print("     各自前后各一项：blob[%s, %s]  work[%s, %s]"
                      % (eb[i - 1] if i else "-", eb[i + 1] if i + 1 < len(eb) else "-",
                         ew[i - 1] if i else "-", ew[i + 1] if i + 1 < len(ew) else "-"))
                break
        print("     → 查 build.py 的遍历点：排序必须走 psort()（key=as_posix），"
              "直接排 Path 对象会随平台变（Windows 大小写不敏感 / POSIX 码点序）。")
        continue

    if eb or ew:
        sb, sw = set(eb), set(ew)
        print("  -> 成因③ 真内容差异：仅 blob 有 %d 条、仅 work 有 %d 条"
              % (len(sb - sw), len(sw - sb)))
        for x in list(sb - sw)[:3]:
            print("     - blob only:", x[:120])
        for x in list(sw - sb)[:3]:
            print("     + work only:", x[:120])

    for i, (a, b) in enumerate(zip(blob, work)):
        if a != b:
            print("  first byte diff at %d" % i)
            print("    BLOB:", blob[max(0, i - 40):i + 40].decode("utf-8", "replace"))
            print("    WORK:", work[max(0, i - 40):i + 40].decode("utf-8", "replace"))
            break
    else:
        print("  前缀一致，长度差", abs(len(blob) - len(work)))

print("=" * 72)
print("修法：本地跑 python site/build.py 后重新提交。")
sys.exit(0)