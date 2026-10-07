/* 内化聚合对账（PLAN v2 第2期）：映射完整性 + 五档翻档行为。
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
const motherFiles = I.domains.flatMap(d => d.files).filter(f => /topics\//.test(f.path) && /母题-/.test(f.path));
const missing = motherFiles.filter(f => !TP[f.path]);
ok(missing.length === 0, 'insight 母题正本全部可映射到页路径' + (missing.length ? '（缺 ' + missing.map(f => f.path).join('、') + '）' : ''));
const linePages = new Set();
ALLC.forEach(c => (c.topics || []).forEach(t => {
  (t.pages || []).forEach(p => linePages.add(String(p)));
  if (/^topics\/.+\.html$/.test(String(t.href || ''))) linePages.add(String(t.href));
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
