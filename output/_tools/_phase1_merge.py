# -*- coding: utf-8 -*-
"""第1期B：progress 引擎并入 index.html（今日页合并），progress → 重定向 stub，测试改路径。"""
import pathlib

prog = pathlib.Path("site/progress.html").read_text(encoding="utf-8")

# ── 头部：标题 / 返回链 / h1 ──
prog = prog.replace("<title>Marvis · 进度</title>", "<title>Marvis · 今日</title>")
old_head = '<a class="mv-back" href="index.html">← 今日</a>\n  <h1 class="mv-h1">进度</h1>'
new_head = '''<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap">
    <h1 class="mv-h1" style="margin:0">今日 · 进度与作业</h1>
    <div style="display:flex;gap:8px;align-items:center">
      <a class="mv-btn mv-btn-primary" href="brain.html" style="text-decoration:none">第二大脑</a>
      <button class="mv-btn" onclick="mvOpen('drill')">限时输出</button>
      <a class="mv-btn" href="obsidian://open?vault=Marvis&amp;file=site%2FREADME" style="text-decoration:none">用法与规则</a>
    </div>
  </div>'''
assert old_head in prog, "head not found"
prog = prog.replace(old_head, new_head)

# subline 前插台账提醒条
old_sub = '<p class="mv-sub" id="subline">'
remind = '''<div class="mv-bd" id="ledger-remind" hidden style="margin-bottom:20px;border-left:3px solid var(--mv-warn)">
    <b id="lr-title"></b>　<span id="lr-text" style="color:var(--mv-muted)"></span>
    <a href="#ledger" style="color:var(--mv-accent);text-decoration:none">打开问题台账 →</a>
  </div>

  <p class="mv-sub" id="subline">'''
assert old_sub in prog, "subline not found"
prog = prog.replace(old_sub, remind, 1)

# ── 规则抽屉重复段去重（保留后一处更详细版）──
dup = "        <b>模块内按序号</b>：一个模块 = 一条链，从它的第 01 条主线开始，01 → 02 → 03 依次推进（后面的主线会用到前面的知识）；前一条到「会了」才解锁下一条，所以每个模块每天最多推进 1 条。<br>\n"
assert dup in prog, "dup para not found"
prog = prog.replace(dup, "", 1)

# ── 规则与数据抽屉后插：模块墙 + 项目口述 + 宫殿 + 底部 note ──
anchor = '</details>\n\n<div class="mv-modal-mask" id="rate"'
assert anchor in prog, "rate anchor not found"
insert_html = '''</details>

  <h2 class="mv-h2" style="margin-top:26px">模块学习 <small>点进去看主线与母题 · 共 <span id="mv-modn">0</span> 个模块</small></h2>
  <div class="mv-modcards" id="mv-modules"></div>
  <p class="mv-note" id="mv-reviews" style="margin-top:6px"></p>

  <h2 class="mv-h2" style="margin-top:26px">项目口述 <small>90 秒骨架 → 决策链 · 先讲再对</small></h2>
  <div class="mv-modcards" id="mv-projects"></div>

  <palace-map vault="Marvis" layout="bar">
    <ul>
      <li data-icon="规" data-name="规则" data-file="CLAUDE" data-desc="全库宪法：四状态、目录职责、连接规则"></li>
      <li data-icon="账" data-name="台账" data-file="questions" data-desc="加工的唯一驱动源，唯一指标每周闭环 ≥1"></li>
      <li data-icon="课" data-name="课程" data-file="study/00-学习总导航与知识生长协议" data-desc="课程底库（01–10 已归档 archive/study-courses/）"></li>
      <li data-icon="干" data-name="主干" data-file="wiki/topics/AI应用开发能力地图" data-desc="岗位基线、掌握度台账、能力课程"></li>
      <li data-icon="能" data-name="EnergyOps" data-file="projects/EnergyOps/EnergyOps-项目说明" data-desc="金山实习：用量聚合、结算、受控 Agent"></li>
      <li data-icon="驭" data-name="数驭穹图" data-file="projects/数驭穹图/数驭穹图项目说明" data-desc="NL2SQL：语义层、路由、权限、证据绑定"></li>
      <li data-icon="则" data-name="RuleArena" data-file="projects/RuleArena/RuleArena-项目说明" data-desc="动态计划下如何可靠执行与验收"></li>
      <li data-icon="面" data-name="表达" data-file="wiki/interview/个人项目含金量表达铁律" data-desc="三段接法、四张反降格话术卡、60 秒骨架"></li>
      <li data-icon="法" data-name="方法" data-file="wiki/thinking/母题驱动证据闭环学习法" data-desc="学习执行内核，锁定 8 周；1-3-7-14 复训"></li>
      <li data-icon="窖" data-name="地窖" data-file="" data-cellar data-desc="raw/ 积压。允许不记得，允许检索，不进宫殿"></li>
    </ul>
  </palace-map>

  <p class="mv-note" style="margin-top:28px">
    做页面的时间若超过练卡片的时间，说明又在做「准备好了」的替身。规则与组件用法见
    <a href="obsidian://open?vault=Marvis&amp;file=site%2FREADME" style="color:var(--mv-accent)">site/README.md</a>。
  </p>

<div class="mv-modal-mask" id="rate"'''
prog = prog.replace(anchor, insert_html, 1)

# ── 数据 script 扩展 ──
prog = prog.replace('<script src="_data/ledger.js"></script>',
  '<script src="_data/ledger.js"></script>\n<script src="_data/modules.js"></script>\n'
  '<script src="_data/reviews.js"></script>\n<script src="_data/projects.js"></script>', 1)

# ── mv.review 作废（静默清理一次）──
tail_anchor = "S = load();\nrender();\nrenderLedger();"
assert tail_anchor in prog, "tail anchor not found"
prog = prog.replace(tail_anchor,
  "/* 双复训合并（PLAN v2 第0期）：旧首页牌组的独立账本 mv.review 与派单引擎互不相通，作废清除。 */\n"
  "try { if (localStorage.getItem('mv.review')) { localStorage.removeItem('mv.review'); "
  "console.info('[marvis] 旧复训账本 mv.review 已作废清除（唯一账本 mv.progress.v1）'); } } catch (e) {}\n\n"
  + tail_anchor, 1)

# ── 页面脚本：今日入口区块渲染 ──
page_js = '''
/* ── 以下为今日入口区块（原 index 页并入）：模块墙 / 项目口述 / 台账提醒条 / 限时输出 ── */
  function mvOpen(id) { var el = document.getElementById(id); if (el) el.hidden = false; }
  function mvClose(id) { var el = document.getElementById(id); if (el) el.hidden = true; }
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') mvClose('drill'); });

  (function () {
    var el = document.getElementById('mv-reviews');
    var list = window.MARVIS_REVIEWS || [];
    if (!el) return;
    if (!list.length) { el.remove(); return; }
    el.innerHTML = '面试诊断：' + list.map(function (r) {
      return '<a href="' + r.href + '" style="color:var(--mv-accent);text-decoration:none">' +
        r.title.replace(/复盘报告$/, '') + '</a>　' + r.items + ' 题 · ' + r.missing + ' 个缺失模块';
    }).join('　·　');
  })();

  (function () {
    var el = document.getElementById('mv-modules');
    var list = window.MARVIS_MODULES || [];
    if (!el) return;
    if (!list.length) { el.remove(); return; }
    var n = document.getElementById('mv-modn');
    if (n) n.textContent = list.length;
    el.innerHTML = list.map(function (m) {
      return '<a class="mv-modcard" href="' + m.href + '">' +
        '<div class="mv-modcard-name">' + m.module + '</div>' +
        '<div class="mv-modcard-meta">' + m.lines + ' 主线 · <b>' + m.topics + '</b> 母题' +
        (m.ready ? ' · 已提炼 ' + m.ready : '') + '</div></a>';
    }).join('');
  })();

  (function () {
    var el = document.getElementById('mv-projects');
    var list = window.MARVIS_PROJECTS || [];
    if (!el) return;
    if (!list.length) { el.remove(); return; }
    el.innerHTML = list.map(function (p) {
      return '<a class="mv-modcard" href="' + p.href + '">' +
        '<div class="mv-modcard-name">' + p.name + '</div>' +
        '<div class="mv-modcard-meta">' + p.lead + '</div></a>';
    }).join('');
  })();

  (function () {
    var el = document.getElementById('ledger-remind');
    if (!el) return;
    var LS = {};
    try { LS = JSON.parse(localStorage.getItem('mv.ledger.v1')) || {}; } catch (e) {}
    var wd = new Date().getDay();
    var gap = LS.check ? Math.round((Date.now() - new Date(LS.check)) / 86400000) : null;
    var Lg = window.MARVIS_LEDGER || null;
    var wc = 0, ws;
    if (Lg) {
      var d = new Date();
      d.setDate(d.getDate() - ((d.getDay() + 6) % 7));
      ws = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
      (Lg.closed || []).forEach(function (c) { if (c.date >= ws) wc++; });
    }
    var wt = (Lg && Lg.weekTarget) || 1;
    function show(t, x) {
      document.getElementById('lr-title').textContent = t;
      document.getElementById('lr-text').textContent = x;
      el.hidden = false;
    }
    if (gap === null || gap > 7) show('台账该巡检了', (gap === null ? '从没记过巡检' : '上次巡检 ' + LS.check + '，已隔 ' + gap + ' 天') + ' · 15 分钟逐条过一遍。');
    else if (wd === 1) show('周一巡检', '15 分钟过一遍台账：更新触碰、该关的关、该 park 的 park。');
    else if (Lg && wc < wt && wd >= 3) show('本周还没闭环问题（' + wc + '/' + wt + '）', '挑台账里最小的一条，今天关掉。');
  })();
'''
sync_tail = ("window.addEventListener('mv:sync', function () { S = load(); render(); });\n"
             "document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeRate(); });\n</script>")
assert sync_tail in prog, "sync tail not found"
prog = prog.replace(sync_tail,
  "window.addEventListener('mv:sync', function () { S = load(); render(); });\n"
  "document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeRate(); });\n"
  + page_js + "</script>", 1)

pathlib.Path("site/index.html").write_text(prog, encoding="utf-8", newline="\n")
print("index.html 合并完成:", len(prog), "chars")

# ── progress.html → 重定向 stub ──
stub = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=index.html">
<title>Marvis · 已合并</title>
</head>
<body class="mv-page">
<div class="mv-wrap">
  <p class="mv-note" style="margin-top:3rem">进度与作业已于 2026-10-07 并入 <a href="index.html" style="color:var(--mv-accent)">今日页</a>（PLAN v2 第1期·两页一库）。本页只作旧链接重定向。</p>
</div>
</body>
</html>
'''
pathlib.Path("site/progress.html").write_text(stub, encoding="utf-8", newline="\n")
print("progress.html → 重定向 stub")

# ── 测试路径改指向 index.html ──
for t in ["test_dispatch.js", "test_render.js", "test_progression.js"]:
    p = pathlib.Path("site/_tests") / t
    s = p.read_text(encoding="utf-8")
    s2 = s.replace("'progress.html'", "'index.html'").replace('"progress.html"', '"index.html"')
    if s2 != s:
        p.write_text(s2, encoding="utf-8", newline="\n")
        print(t, "路径 → index.html")
