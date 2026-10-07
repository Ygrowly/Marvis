# -*- coding: utf-8 -*-
"""审查修复（feat/life-os 第0、1期 review）：五档聚合补实现 + spec 口径修正 + 5 处 smell 清理。"""
import pathlib

ok = []

# ── 1. index.html：内化速览升级为五档聚合（补实质偏差的实现侧） ──────────────────
ip = pathlib.Path("site/index.html")
h = ip.read_text(encoding="utf-8")

old_render = """  (function () {
    var box = document.getElementById('insightbox');
    var I = window.MARVIS_INSIGHT, R = window.MARVIS_RECENT || [];
    var sum = document.getElementById('insightsum');
    if (!box || !I) return;
    var n = I.domains.reduce(function (a, d) { return a + d.files.length; }, 0);
    if (sum) sum.textContent = n + ' 正本 · ' + I.domains.length + ' 域';
    var bar = I.domains.map(function (d) {
      var tot = d.files.length;
      var ok = (d.stats['integrated'] || 0) + (d.stats['active'] || 0);
      return '<div style="margin-bottom:.625rem">' +
        '<div style="display:flex;justify-content:space-between;font-size:.8125rem">' +
        '<span>' + d.name + '</span><span style="color:var(--mv-muted)">' + tot +
        ' 正本 · 验收 ' + ok + '</span></div>' +
        '<div style="height:6px;background:var(--mv-line,#e5e1d8);border-radius:3px;overflow:hidden">' +
        '<div style="height:100%;width:' + (tot ? Math.round(ok / tot * 100) : 0) + '%;background:var(--mv-accent)"></div></div></div>';
    }).join('');"""

new_render = """  (function () {
    var box = document.getElementById('insightbox');
    var I = window.MARVIS_INSIGHT, R = window.MARVIS_RECENT || [];
    var sum = document.getElementById('insightsum');
    if (!box || !I) return;
    var n = I.domains.reduce(function (a, d) { return a + d.files.length; }, 0);
    if (sum) sum.textContent = n + ' 正本 · ' + I.domains.length + ' 域';

    /* ── 内化度五档（PLAN v2 §二 轴三）：0 空 / 1 暗(记录过) / 2 读厚(拆成情境→动作且人验过) / 3 训练(进派单有记录) / 4 亮(真实用上) ──
       build 端只供 frontmatter status（静态盘面）；「训练」「亮」两档的信号在 localStorage
       （mv.progress.v1 主线记录 / mv.brain.v1 uses 打卡），build 物理不可达，只能页面端聚合。 */
    var pageKey = {};                    /* 母题页 stem → 主线 key（clusters.js 的 pages 字段就是单卡页清单） */
    (window.MARVIS_CLUSTERS || []).forEach(function (c) {
      (c.topics || []).forEach(function (t) {
        (t.pages || []).forEach(function (p) {
          pageKey[String(p).replace(/\\.html$/, '').split('/').pop()] = c.id + '/' + t.id;
        });
      });
    });
    var PR = {};                         /* 原则卡 md 路径 → [卡id]（cards.js 的 src 字段） */
    ((window.MARVIS_CARDS || {}).principles || []).forEach(function (c) {
      (PR[c.src] = PR[c.src] || []).push(c.id);
    });
    var S = {}, B = { uses: {} };
    try { S = JSON.parse(localStorage.getItem('mv.progress.v1')) || {}; } catch (e) {}
    try { B = JSON.parse(localStorage.getItem('mv.brain.v1')) || B; } catch (e) {}
    var lv = S.lv || {};
    function trained(key) { var r = lv[key]; return !!(r && (r.last || r.due || r.l >= 1)); }
    function stageOf(f) {
      var s = (f.status === 'integrated' || f.status === 'active') ? 2 : 1;   /* status 基线：验过=读厚，否则=暗 */
      var ids = PR[f.path];                                                /* 原则卡：亮 > 训练 > 基线 */
      if (ids) {
        ids.forEach(function (id) {
          if ((B.uses[id] || []).length) s = 4;
          else if (s < 3 && trained('card/' + id)) s = 3;
        });
        return s;
      }
      var stem = f.path.split('/').pop().replace(/\\.md$/, '');
      if (pageKey[stem] && trained(pageKey[stem])) s = 3;                  /* 母题卡：所在主线训练过 → 训练档 */
      return s;
    }

    var LBL = ['空', '暗', '读厚', '训练', '亮'];
    var COL = ['#d8d2c4', '#b8a88f', '#7f9c7a', '#4d7c62', '#2f6b4f'];
    var bar = I.domains.map(function (d) {
      var counts = [0, 0, 0, 0, 0];
      d.files.forEach(function (f) { counts[stageOf(f)]++; });
      var tot = d.files.length || 1;
      var segs = counts.map(function (c, i) {
        return c ? '<div style="width:' + (c / tot * 100) + '%;background:' + COL[i] + '" title="' + LBL[i] + ' ' + c + '"></div>' : '';
      }).join('');
      return '<div style="margin-bottom:.625rem">' +
        '<div style="display:flex;justify-content:space-between;font-size:.8125rem">' +
        '<span>' + d.name + '</span><span style="color:var(--mv-muted)">' + d.files.length + ' 正本 · ' +
        ((counts[3] + counts[4]) ? '内化中 ' + (counts[3] + counts[4]) : '训练待启动') + '</span></div>' +
        '<div style="display:flex;height:6px;border-radius:3px;overflow:hidden">' + segs + '</div></div>';
    }).join('');
    var legend = '<div style="display:flex;gap:.75rem;font-size:.75rem;color:var(--mv-muted);margin-bottom:.75rem;flex-wrap:wrap">' +
      LBL.map(function (l, i) {
        return '<span><i style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' + COL[i] + ';margin-right:4px"></i>' + l + '</span>';
      }).join('') + '</div>';"""

assert old_render in h, "old insight render block not found"
h = h.replace(old_render, new_render, 1)
h = h.replace("    box.innerHTML = bar + list;\n  })();", "    box.innerHTML = legend + bar + list;\n  })();", 1)

# mv.review 清理：可见说明（规则抽屉）+ 退役时点注释
old_rule = "数据默认写在这台机器的浏览器里（键名 mv.progress.v1），"
add_rule = "<b>旧账作废</b>：旧首页复训牌组的独立账本 mv.review 已于 2026-10-07 作废（与派单引擎互不相通），打开本页自动清除；唯一账本是 mv.progress.v1。<br>\n        数据默认写在这台机器的浏览器里（键名 mv.progress.v1），"
assert old_rule in h
h = h.replace(old_rule, add_rule, 1)
old_mig = "/* 双复训合并（PLAN v2 第0期）：旧首页牌组的独立账本 mv.review 与派单引擎互不相通，作废清除。 */"
new_mig = "/* 双复训合并（PLAN v2 第0期）：旧首页牌组的独立账本 mv.review 与派单引擎互不相通，作废清除。\n   幂等迁移码，计划保留至 2026-11-07（给旧设备缓存一个清理窗口），之后可整行移除。 */"
assert old_mig in h
h = h.replace(old_mig, new_mig, 1)

# today() 刻意重复注释（测试 VM 抽内联脚本单跑需自包含）
old_today = "function today() { return dstr(new Date()); }"
assert old_today in h
h = h.replace(old_today,
  "/* 与 marvis.js 的 today() 刻意重复：三套测试 VM 抽本页内联脚本单跑，必须自包含，勿合并 */\nfunction today() { return dstr(new Date()); }", 1)
ip.write_text(h, encoding="utf-8", newline="\n")
ok.append("index.html：五档聚合 + mv.review 可见说明与退役时点 + today 注释")

# ── 2. marvis.js 头注组件数修正（6 → 8） ──
mp = pathlib.Path("site/_components/marvis.js")
s = mp.read_text(encoding="utf-8")
assert "六个组件" in s
s = s.replace("六个组件", "八个组件", 1)
mp.write_text(s, encoding="utf-8", newline="\n")
ok.append("marvis.js：头注组件数 6→8")

# ── 3. build.py write_insight：去掉函数内重复 import，标注刻意一趟双产出 ──
bp = pathlib.Path("site/build.py")
s = bp.read_text(encoding="utf-8")
old = """def write_insight():
    import datetime as _dt
    today = _dt.date.today()"""
new = """def write_insight():
    # 域聚合与新到架同趟扫描是刻意设计：同一遍 frontmatter 读取双产出，不做职责拆分。
    today = datetime.date.today()"""
assert old in s
s = s.replace(old, new, 1)
bp.write_text(s, encoding="utf-8", newline="\n")
ok.append("build.py：write_insight 复用模块级 datetime + 双产出注释")

# ── 4. site/README.md：decks 口径残留 + 组件数 ──
rp = pathlib.Path("site/README.md")
s = rp.read_text(encoding="utf-8")
old = "_data/              构建产物 decks.json / modules.js / reviews.js / breaks.js / projects.js（数据）+ .js（file:// 用）；例外：clusters.js 与 rules.js 是手写数据源"
new = "_data/              构建产物 cards.js / insight.js / recent.js / modules.js / reviews.js / breaks.js / projects.js / ledger.js / mmd-boot.js（decks 已随双复训合并停生成）；例外：clusters.js 与 rules.js 是手写数据源"
assert old in s
s = s.replace(old, new, 1)
rp.write_text(s, encoding="utf-8", newline="\n")
ok.append("site/README.md：_data 口径更新")

# ── 5. PLAN.md：五档口径修正 + 数字校正 ──
pp = pathlib.Path("site/PLAN.md")
s = pp.read_text(encoding="utf-8")
old = "| **1 地基** | 卡 frontmatter 加 `domain:`；build 聚合内化度五档→`_data/insight.js`；index+progress 合并为今日页（保留派单引擎，清三套迁移补丁中的死键）；新到架信息流 | `python site/build.py` 产出 insight.js；全部 15 卡+87 母题卡有 domain；今日页单页完成\"看清单→练→记账\"全闭环；CI 绿 |"
new = "| **1 地基** | 卡 frontmatter 加 `domain:`；build 聚合域×状态（静态盘面）→`_data/insight.js`；内化度五档由**页面端聚合**（mv.progress.v1 / mv.brain.v1 信号 build 物理不可达）接入今日页速览；index+progress 合并为今日页（保留派单引擎，清三套迁移补丁中的死键）；新到架信息流 | `python site/build.py` 产出 insight.js；全部 15 卡+96 母题卡有 domain；今日页单页完成\"看清单→练→记账\"全闭环；速览显示五档分布；CI 绿 |"
assert old in s
s = s.replace(old, new, 1)
old2 = "| **2 画像** | brain 重构三栏画像页；宫殿皮肤（读矩阵数据）；cards/rules 退役为下钻视图；`_data/domains.js` 上线 | 画像页三栏齐；矩阵数据与 localStorage 信号对账测试；cards.html/rules.html 不再被任何页面作为独立入口链接 |"
new2 = "| **2 画像** | brain 重构三栏画像页（五档矩阵从今日页速览函数上移共用）；宫殿皮肤（读矩阵数据）；cards/rules 退役为下钻视图；`_data/domains.js` 上线 | 画像页三栏齐；矩阵数据与 localStorage 信号对账测试；cards.html/rules.html 不再被任何页面作为独立入口链接 |"
assert old2 in s
s = s.replace(old2, new2, 1)
pp.write_text(s, encoding="utf-8", newline="\n")
ok.append("PLAN.md：五档口径修正（build 静态 + 页面端聚合）+ 96 校正")

# ── 6. 测试桩共享：_dom_stub.js + 三测试改引用 ──
stub = """'use strict';
/* 共享假 DOM 元素桩（审查 smell 修复：三份测试的同一字面量收拢到此）。
   remove/style 是今日页渲染 IIFE 需要的最小面；按需在测试里再扩。 */
function elStub(id) {
  return { id: id, innerHTML: '', textContent: '', hidden: true, value: '',
           remove: function () {}, style: {} };
}
module.exports = { elStub: elStub };
"""
pathlib.Path("site/_tests/_dom_stub.js").write_text(stub, encoding="utf-8", newline="\n")

fixes = [
    ("site/_tests/test_dispatch.js",
     "if (!ELS[id]) ELS[id] = { id: id, innerHTML: '', textContent: '', hidden: true, value: '', remove: () => {}, style: {} };",
     "if (!ELS[id]) ELS[id] = elStub(id);"),
    ("site/_tests/test_render.js",
     "if (!dom[id]) dom[id] = { id, innerHTML: '', textContent: '', hidden: true, value: '', remove: () => {}, style: {} };",
     "if (!dom[id]) dom[id] = elStub(id);"),
    ("site/_tests/test_progression.js",
     "getElementById: () => ({ innerHTML: '', textContent: '', hidden: true, value: '', remove: () => {}, style: {} }),",
     "getElementById: (id) => elStub(id),"),
]
for f, old, new in fixes:
    p = pathlib.Path(f)
    s = p.read_text(encoding="utf-8")
    assert old in s, f + " stub line not found"
    # 在首个 require 行后挂共享桩引用
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("const ") and "require(" in ln:
            last_require = i
    lines.insert(last_require + 1, "const { elStub } = require(path.join(ROOT, '_tests', '_dom_stub.js'));")
    s = "\n".join(lines)
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8", newline="\n")
    ok.append(f + "：桩改共享 elStub")

print("\n".join("✔ " + x for x in ok))
