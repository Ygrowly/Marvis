/* 内化速览对账（PLAN v2 第1期审查修复）：训练档映射链路的完整性。
   链路 = 母题 md 正本（insight.js 的 path）→ MARVIS_TOPIC_PAGE → 母题页路径 → clusters 主线 pages。
   哪一环断了，那张母题卡在今日页速览里就永远到不了「训练」档。 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const ROOT = path.join(__dirname, '..', '..');
const ctx = { window: {}, console };
vm.createContext(ctx);
['insight.js', 'pagekey.js', 'clusters.js', 'cards.js'].forEach(f => {
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'site', '_data', f), 'utf8'), ctx);
});
const I = ctx.window.MARVIS_INSIGHT;
const TP = ctx.window.MARVIS_TOPIC_PAGE;
const CL = ctx.window.MARVIS_CLUSTERS;
const C = ctx.window.MARVIS_CARDS;
let fails = 0;
const ok = (cond, msg) => { console.log((cond ? '  ✅ ' : '  ❌ ') + msg); if (!cond) fails++; };

ok(TP && Object.keys(TP).length > 80, 'MARVIS_TOPIC_PAGE 覆盖母题正本 ' + (TP ? Object.keys(TP).length : 0) + ' 个');
const motherFiles = I.domains.flatMap(d => d.files).filter(f => /topics\//.test(f.path) && /母题-/.test(f.path));
const missing = motherFiles.filter(f => !TP[f.path]);
ok(missing.length === 0, 'insight 母题正本全部可映射到页路径' + (missing.length ? '（缺 ' + missing.map(f => f.path).join('、') + '）' : ''));
const linePages = new Set();
const CLALL = [].concat(CL, ctx.window.MARVIS_DRILL ? [ctx.window.MARVIS_DRILL] : [], ctx.window.MARVIS_RULE_CLUSTER ? [ctx.window.MARVIS_RULE_CLUSTER] : []);
CLALL.forEach(c => (c.topics || []).forEach(t => {
  (t.pages || []).forEach(p => linePages.add(String(p)));
  if (/^topics\/.+\.html$/.test(String(t.href || ''))) linePages.add(String(t.href));  // drill 型
}));
const orphan = Object.values(TP).filter(p => !linePages.has(p));
ok(orphan.length === 0, 'TOPIC_PAGE 页路径全部挂在某条主线下（训练档可达）' + (orphan.length ? '（孤儿 ' + orphan.slice(0, 3).join('、') + '）' : ''));
const principleSrcs = new Set(C.principles.map(c => c.src));
const cardFiles = I.domains.flatMap(d => d.files).filter(f => f.path.indexOf('wiki/cards/原则-') === 0);
const noCard = cardFiles.filter(f => !principleSrcs.has(f.path));
ok(cardFiles.length > 0 && noCard.length === 0, '原则卡正本全部可映射到派单卡 id' + (noCard.length ? '（缺 ' + noCard.map(f => f.path).join('、') + '）' : ''));

if (fails) { console.log('❌ ' + fails + ' 项对账失败'); process.exit(1); }
console.log('✅ 内化速览映射对账全通过');
