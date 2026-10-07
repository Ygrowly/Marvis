# -*- coding: utf-8 -*-
"""第2期：index 改用共享聚合库；brain 右栏换画像三栏；test_insight 升级。3D 书架隐喻不动（取舍记 PLAN 停车场）。"""
import pathlib, re

ok = []

# ── 1. index.html：内联聚合块 → MarvisInsight 库调用 ──
ip = pathlib.Path("site/index.html")
h = ip.read_text(encoding="utf-8")

start = h.index("    /* ── 内化度五档（PLAN v2 §二 轴三）")
end_marker = "    var legend = '<div style=\"display:flex;gap:.75rem;font-size:.75rem;color:var(--mv-muted);margin-bottom:.75rem;flex-wrap:wrap\">'"
end = h.index(end_marker)
# legend 行到其结束（'</div>'' 后还有 .join('') + '</div>';）
end = h.index("</div>' + '</div>';  ? NOPLACE", end) if False else h.index(".join('') + '</div>';", end) + len(".join('') + '</div>';")
old_block = h[start:end]
assert "stageOf" in old_block and "legend" in old_block, "block content unexpected"

new_block = """    /* ── 内化度五档：唯一实现已上移 _components/insight.js（第2期），今日页与画像页共用 ── */
    var IDX = window.MarvisInsight.buildIndex({
      clusters: window.MARVIS_CLUSTERS, drill: window.MARVIS_DRILL,
      ruleCluster: window.MARVIS_RULE_CLUSTER, cards: window.MARVIS_CARDS,
      topicPage: window.MARVIS_TOPIC_PAGE
    });
    var LV = {}, USES = {};
    try { var _ps = JSON.parse(localStorage.getItem('mv.progress.v1')) || {}; LV = _ps.lv || {}; } catch (e) {}
    try { var _bs = JSON.parse(localStorage.getItem('mv.brain.v1')); USES = (_bs && _bs.uses) || {}; } catch (e) {}
    var AGG = window.MarvisInsight.aggregate(window.MARVIS_INSIGHT, IDX, LV, USES);
    var LBL = AGG.stageNames, COL = AGG.stageCss;
    var bar = AGG.domains.map(function (d) {
      var tot = d.total || 1;
      var segs = d.counts.map(function (c, i) {
        return c ? '<div style="width:' + (c / tot * 100) + '%;background:' + COL[i] + '" title="' + LBL[i] + ' ' + c + '"></div>' : '';
      }).join('');
      return '<div style="margin-bottom:.625rem">' +
        '<div style="display:flex;justify-content:space-between;font-size:.8125rem">' +
        '<span>' + d.name + '</span><span style="color:var(--mv-muted)">' + d.total + ' 正本 · ' +
        (d.internalized ? '内化中 ' + d.internalized : '训练待启动') + '</span></div>' +
        '<div style="display:flex;height:6px;border-radius:3px;overflow:hidden">' + segs + '</div></div>';
    }).join('');
    var legend = '<div style="display:flex;gap:.75rem;font-size:.75rem;color:var(--mv-muted);margin-bottom:.75rem;flex-wrap:wrap">' +
      LBL.map(function (l, i) {
        return '<span><i style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' + COL[i] + ';margin-right:4px"></i>' + l + '</span>';
      }).join('') + '</div>';"""
h = h[:start] + new_block + h[end:]

h = h.replace('<script src="_data/pagekey.js"></script>',
  '<script src="_data/pagekey.js"></script>\n<script src="_components/insight.js"></script>', 1)
ip.write_text(h, encoding="utf-8", newline="\n")
ok.append("index.html：聚合改用共享库")

# ── 2. brain.html：数据标签 + 右栏三卡换画像 + 标题导语 ──
bp = pathlib.Path("site/brain.html")
b = bp.read_text(encoding="utf-8")

b = b.replace('<script src="_data/modules.js"></script>',
  '<script src="_data/modules.js"></script>\n<script src="_data/pagekey.js"></script>\n'
  '<script src="_data/insight.js"></script>\n<script src="_data/domains.js"></script>\n'
  '<script src="_components/insight.js"></script>', 1)

b = b.replace("<title>我的书架 · 第二大脑</title>", "<title>第二大脑 · 人生画像</title>", 1)
b = b.replace('<h1 class="mv-h1" style="margin:0">我的书架</h1>',
              '<h1 class="mv-h1" style="margin:0">人生画像 · 书架</h1>', 1)

# 右栏 DOM id 改语义名
b = b.replace('<div class="side-card" id="side-due"></div>', '<div class="side-card" id="side-who"></div>', 1)
b = b.replace('<div class="side-card" id="side-situ"></div>', '<div class="side-card" id="side-map"></div>', 1)
b = b.replace('<div class="side-card" id="side-progress"></div>', '<div class="side-card" id="side-track"></div>', 1)

# buildSide 整段替换为 buildPortrait
m = re.search(r"  // ── 今日内化侧栏 ───────────────────────────────────────────\n  \(function buildSide\(\) \{.*?\n  \}\);\n", b, re.S)
assert m, "buildSide block not found"
portrait = """  // ── 画像三栏（PLAN v2 第2期）：我是谁 / 我的版图 / 我的轨迹 ──
  // 今日职责（到期清单、今日情境）已唯一归今日页；本页只回答「我在哪、往哪走」。
  (function buildPortrait() {
    var IDX = window.MarvisInsight.buildIndex({
      clusters: window.MARVIS_CLUSTERS, drill: window.MARVIS_DRILL,
      ruleCluster: window.MARVIS_RULE_CLUSTER, cards: window.MARVIS_CARDS,
      topicPage: window.MARVIS_TOPIC_PAGE
    });
    var AGG = window.MarvisInsight.aggregate(window.MARVIS_INSIGHT, IDX, (S.lv || {}), (B.uses || {}));

    // ① 我是谁：当前战役 + 位置 + 总体进度（overall 在上方已按本事+作品算出）
    var dom = (window.MARVIS_DOMAINS || []);
    var camp = document.getElementById('side-who');
    camp.innerHTML =
      '<h4>我是谁 <em>位置与战役</em></h4>' +
      '<div class="side-big">2027 秋招<small> · 当前唯一挂载战役</small></div>' +
      '<p class="side-note">能力底盘 = Agent 应用开发（AI 主战场四簇 + 后端基本盘）。' +
      '整体掌握度 <b>' + overall + '%</b>（本事 + 作品口径），内化线（准则 + 读厚卡）单列看版图。</p>' +
      '<div class="side-btns"><a class="mv-btn" href="obsidian://open?vault=Marvis&amp;file=wiki%2Ftopics%2FAI%E5%BA%94%E7%94%A8%E5%BC%80%E5%8F%91%E8%83%BD%E5%8A%9B%E5%9C%B0%E5%9B%BE" style="text-decoration:none">能力地图</a></div>';

    // ② 我的版图：域 × 五档矩阵（与今日页「内化速览」同一实现、同一份数据）
    var LBL = AGG.stageNames, COL = AGG.stageCss;
    var order = dom.map(function (d) { return d.name; });
    var byName = {};
    AGG.domains.forEach(function (d) { byName[d.name] = d; });
    var rows = order.map(function (name) {
      var d = byName[name];
      if (!d || !d.total) {
        return '<div style="margin-top:0.625rem"><div style="display:flex;justify-content:space-between;font-size:0.8125rem">' +
          '<span style="color:var(--mv-muted)">' + name + '</span><span style="color:var(--mv-muted)">还没长</span></div>' +
          '<div class="mini-track"><i style="width:0"></i></div></div>';
      }
      var tot = d.total || 1;
      var segs = d.counts.map(function (c, i) {
        return c ? '<i style="display:inline-block;width:' + (c / tot * 100) + '%;height:100%;background:' + COL[i] + '"></i>' : '';
      }).join('');
      return '<div style="margin-top:0.625rem"><div style="display:flex;justify-content:space-between;font-size:0.8125rem">' +
        '<span>' + name + '</span><span style="color:var(--mv-muted)">' + d.total + ' 正本 · 内化中 ' + d.internalized + '</span></div>' +
        '<div class="mini-track" style="display:flex">' + segs + '</div></div>';
    }).join('');
    var leg = '<div style="display:flex;gap:.5rem;font-size:.75rem;color:var(--mv-muted);margin-top:.5rem;flex-wrap:wrap">' +
      LBL.map(function (l, i) { return '<span><i style="display:inline-block;width:7px;height:7px;border-radius:2px;background:' + COL[i] + ';margin-right:3px"></i>' + l + '</span>'; }).join('') + '</div>';
    document.getElementById('side-map').innerHTML =
      '<h4>我的版图 <em>域 × 内化五档</em></h4>' + rows + leg +
      '<div class="side-btns"><a class="mv-btn" href="index.html#insight" style="text-decoration:none">今日页同款速览</a></div>';

    // ③ 我的轨迹：真实反馈三项——⚡用上次数、已读透正本、本周台账闭环
    var usesN = 0;
    Object.keys(B.uses || {}).forEach(function (k) { usesN += (B.uses[k] || []).length; });
    var neu = nodes.filter(function (n) { return (n.hall === 'os' || n.hall === 'books') && !n.untrained; }).length;
    var wk = 0, wd;
    try {
      var LS = JSON.parse(localStorage.getItem('mv.ledger.v1')) || {};
      var d0 = new Date(); d0.setDate(d0.getDate() - ((d0.getDay() + 6) % 7));
      var ws = d0.getFullYear() + '-' + ('0' + (d0.getMonth() + 1)).slice(-2) + '-' + ('0' + d0.getDate()).slice(-2);
      Object.keys(LS.done || {}).forEach(function (k) { if (LS.done[k] >= ws) wk++; });
      wd = LS.check;
    } catch (e) {}
    function tri(label, v, unit) {
      return '<div style="flex:1;min-width:4.5rem"><div class="ms-label" style="font-size:.75rem;color:var(--mv-muted)">' + label + '</div>' +
        '<div class="side-big" style="font-size:1.25rem">' + v + '<small style="font-size:.75rem"> ' + unit + '</small></div></div>';
    }
    document.getElementById('side-track').innerHTML =
      '<h4>我的轨迹 <em>真实反馈，不是感觉</em></h4>' +
      '<div style="display:flex;gap:.5rem;flex-wrap:wrap">' +
      tri('⚡ 真实用上', usesN, '次') + tri('已读透', neu, '正本') + tri('本周闭环', wk, '题') + '</div>' +
      '<p class="side-note">' + (wd ? '上次台账巡检 ' + wd + '。' : '台账还没巡检过。') +
      '轨迹只记真实发生的事：用上一次、读透一份、闭环一题。</p>';
  })();
"""
b = b[:m.start()] + portrait + b[m.end():]

# 图例与导语微调（画像语义）
b = b.replace("第二大脑，做成一面书架。<b>五个区就是五个方向，一本书就是一个模块、一个项目、一条准则或一本读过的书</b>，名字印在书脊上。",
  "第二大脑，做成一面书架照 X 光。<b>五个区就是五个方向，一本书就是一个模块、一个项目、一条准则或一本读过的书</b>，名字印在书脊上；右侧三栏回答「我是谁、我的版图、我的轨迹」。")
bp.write_text(b, encoding="utf-8", newline="\n")
ok.append("brain.html：画像三栏 + 数据标签 + 标题导语")

# ── 3. test_insight.js：升级为「共享库对账 + 五档模拟」 ──
test = """/* 内化聚合对账（PLAN v2 第2期）：映射完整性 + 五档翻档行为。
   链路 = 母题 md 正本（insight.js）→ MARVIS_TOPIC_PAGE → 母题页路径 → 簇主线（pages 或 drill 型 href）。
   哪一环断了，那张卡在今日页与画像页就永远到不了「训练」档。 */
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..', '..');
global.window = {};
const MarvisInsight = require(path.join(ROOT, 'site', '_components', 'insight.js'));
['insight.js', 'pagekey.js', 'clusters.js', 'cards.js', 'domains.js'].forEach(f => {
  require(path.join(ROOT, 'site', '_data', f));
});
const I = window.MARVIS_INSIGHT, TP = window.MARVIS_TOPIC_PAGE,
      C = window.MARVIS_CARDS, DOM = window.MARVIS_DOMAINS;
const ALLC = [].concat(window.MARVIS_CLUSTERS, window.MARVIS_DRILL ? [window.MARVIS_DRILL] : [],
                       window.MARVIS_RULE_CLUSTER ? [window.MARVIS_RULE_CLUSTER] : []);
let fails = 0;
const ok = (cond, msg) => { console.log((cond ? '  ✅ ' : '  ❌ ') + msg); if (!cond) fails++; };

ok(TP && Object.keys(TP).length > 80, 'MARVIS_TOPIC_PAGE 覆盖母题正本 ' + Object.keys(TP).length + ' 个');
const motherFiles = I.domains.flatMap(d => d.files).filter(f => /topics\\//.test(f.path) && /母题-/.test(f.path));
const missing = motherFiles.filter(f => !TP[f.path]);
ok(missing.length === 0, 'insight 母题正本全部可映射到页路径' + (missing.length ? '（缺 ' + missing.map(f => f.path).join('、') + '）' : ''));
const linePages = new Set();
ALLC.forEach(c => (c.topics || []).forEach(t => {
  (t.pages || []).forEach(p => linePages.add(String(p)));
  if (/^topics\\/.+\\.html$/.test(String(t.href || ''))) linePages.add(String(t.href));
}));
const orphan = Object.values(TP).filter(p => !linePages.has(p));
ok(orphan.length === 0, 'TOPIC_PAGE 页路径全部挂在某条主线下（训练档可达）' + (orphan.length ? '（孤儿 ' + orphan.slice(0, 3).join('、') + '）' : ''));
const principleSrcs = new Set(C.principles.map(c => c.src));
const cardFiles = I.domains.flatMap(d => d.files).filter(f => f.path.indexOf('wiki/cards/原则-') === 0);
const noCard = cardFiles.filter(f => !principleSrcs.has(f.path));
ok(cardFiles.length > 0 && noCard.length === 0, '原则卡正本全部可映射到派单卡 id');

/* 五档行为：空账本无训练/亮；给定主线 lv 与卡 uses 后对应正本翻档 */
const IDX = MarvisInsight.buildIndex({ clusters: window.MARVIS_CLUSTERS, drill: window.MARVIS_DRILL,
  ruleCluster: window.MARVIS_RULE_CLUSTER, cards: window.MARVIS_CARDS, topicPage: TP });
const base = MarvisInsight.aggregate(I, IDX, {}, {});
ok(base.domains.every(d => d.counts[3] === 0 && d.counts[4] === 0), '空账本无「训练/亮」档');
const firstLine = ALLC.find(c => (c.topics || []).some(t => (t.pages || []).length));
const lineKey = firstLine.id + '/' + firstLine.topics.find(t => (t.pages || []).length).id;
const linePage = firstLine.topics.find(t => (t.pages || []).length).pages[0];
const lv = {}; lv[lineKey] = { l: 1, last: '2026-10-07', due: null, hit: 1, miss: 0 };
const after = MarvisInsight.aggregate(I, IDX, lv, { 'jy-1': ['2026-10-07 说了就算'] });
const promoted = after.domains.flatMap(d => d.files).filter(f => f.stage >= 3);
ok(promoted.some(f => TP[f.path] === linePage), '主线有训练记录 → 该主线的母题正本翻「训练」档');
const jyFile = after.domains.flatMap(d => d.files).find(f => f.path === 'wiki/cards/原则-精确努力.md');
ok(jyFile && jyFile.stage === 4, '原则卡有 uses 打卡 → 翻「亮」档（实际 ' + (jyFile && jyFile.stage) + '）');
ok(after.domains.every(d => d.counts.reduce((a, b) => a + b, 0) === d.total), '每域五档计数守恒');
ok(Array.isArray(DOM) && DOM.length >= 4 && DOM.every(d => d.name && d.color), '域登记表就绪（' + DOM.map(d => d.name).join('/') + '）');

if (fails) { console.log('❌ ' + fails + ' 项对账失败'); process.exit(1); }
console.log('✅ 内化聚合对账全通过（含五档行为模拟）');
"""
pathlib.Path("site/_tests/test_insight.js").write_text(test, encoding="utf-8", newline="\n")
ok.append("test_insight.js：升级五档行为模拟")

print("\n".join("✔ " + x for x in ok))
