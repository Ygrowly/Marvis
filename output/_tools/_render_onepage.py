# -*- coding: utf-8 -*-
"""渲染一页通页面为 PNG（mid + deep 两档），供视觉审查用。

用法：
    python output/_render_onepage.py            # 渲染全部已存在的一页通
    python output/_render_onepage.py MySQL 并发与锁   # 只渲染指定模块
"""
import os, re, subprocess, sys, glob
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(OUT) == '_tools':          # 2026-10-04 起工具集中到 output/_tools/
    OUT = os.path.dirname(OUT)
ROOT = os.path.dirname(OUT)
ONEPAGE = os.path.join(ROOT, 'site', 'onepage')   # 一页族成品已上站（2026-10-04）
REVIEW = os.path.join(OUT, '_onepage_review')
os.makedirs(REVIEW, exist_ok=True)
CHROME = r'C:/Program Files/Google/Chrome/Application/chrome.exe'
MAX_H = 16000


def crop_tail(path, keep_tail=40):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.load()
    last = 0
    for y in range(h - 1, -1, -1):
        for x in range(0, w, 6):
            r, g, b = px[x, y]
            if not (r > 250 and g > 250 and b > 250):
                last = y
                break
        if last:
            break
    newh = min(h, last + 1 + keep_tail)
    if newh < h:
        im.crop((0, 0, w, newh)).save(path)
    return (w, newh)


def render_module(name):
    src = os.path.join(ONEPAGE, name + '-一页通.html')
    if not os.path.exists(src):
        print('skip (no page):', name)
        return
    url = 'file:///' + src.replace(os.sep, '/')
    png = os.path.join(REVIEW, name + '-mid.png')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=1', '--virtual-time-budget=4000',
                    '--window-size=1500,%d' % MAX_H, '--screenshot=' + png, url],
                   check=True, capture_output=True, timeout=120)
    print('%-14s mid  %s' % (name, crop_tail(png)))
    # deep 档：JS 默认 st.mode 会覆盖 body 属性，临时副本里改 JS 默认值
    s = open(src, encoding='utf-8').read()
    deep = s.replace('var st = { mode:"mid"', 'var st = { mode:"deep"', 1)
    tmp = os.path.join(REVIEW, '_tmp_' + name + '.html')
    open(tmp, 'w', encoding='utf-8', newline='\n').write(deep)
    try:
        png = os.path.join(REVIEW, name + '-deep.png')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--force-device-scale-factor=1', '--virtual-time-budget=4000',
                        '--window-size=1500,%d' % MAX_H, '--screenshot=' + png,
                        'file:///' + tmp.replace(os.sep, '/')],
                       check=True, capture_output=True, timeout=120)
        print('%-14s deep %s' % (name, crop_tail(png)))
    finally:
        os.remove(tmp)


if __name__ == '__main__':
    names = [a for a in sys.argv[1:] if not a.startswith('-')]
    if not names:
        names = [os.path.basename(p)[:-len('-一页通.html')]
                 for p in glob.glob(os.path.join(ONEPAGE, '*-一页通.html'))]
    for n in names:
        render_module(n)
