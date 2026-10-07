# -*- coding: utf-8 -*-
"""CI 诊断：对比 HEAD blob 与 rebuild 产物的第一差异字节（断言失败时调用）。"""
import subprocess
import sys

files = ["site/_data/breaks.js", "site/_data/cards.js", "site/_data/modules.js"]
for f in files:
    blob = subprocess.run(["git", "show", "HEAD:" + f], capture_output=True).stdout
    work = open(f, "rb").read()
    norm = work.replace(b"\r\n", b"\n")
    print(f, "| blob", len(blob), "| work", len(work), "| norm", len(norm))
    if norm == blob:
        print("  -> 内容一致（纯换行差异）")
        continue
    for i, (a, b) in enumerate(zip(blob, norm)):
        if a != b:
            print("  first content diff at byte", i)
            print("  BLOB:", repr(blob[max(0, i - 50):i + 50]))
            print("  WORK:", repr(norm[max(0, i - 50):i + 50]))
            break
    else:
        print("  前缀一致，长度差", abs(len(blob) - len(norm)))
sys.exit(0)
