/* 长期仿真：模拟「完美执行力」跑 N 天，验证
     1. 不会死锁（所有母题都能被派到）
     2. 派单顺序符合依赖（前置一定先于后继）
     3. 复训负载不失控、抽检按 7 天一轮
   用假 Date 控制「今天」，其余全走 progress.html 的真实引擎。 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'progress.html'), 'utf8');
const code = html.match(/<script>\r?\n([\s\S]*?)<\/script>/)[1];

global.window = { addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => {} };
require(path.join(ROOT, '_data', 'clusters.js'));
require(path.join(ROOT, '_data', 'breaks.js'));
/* 与 test_dispatch 相同的原则卡桩（真数据由 build.py 生成在 _data/cards.js） */
global.window.MARVIS_CARD_CLUSTER = {
  id: 'card', name: '原则卡 · 读厚', zone: '准则',
  topics: [
    { id: 'adler-1', name: '课题分离', href: 'cards.html#card-adler-1' },
    { id: 'adler-2', name: '目的论：理由是造出来的', href: 'cards.html#card-adler-2' },
  ],
};

/* 假时钟：sandbox 里的 new Date() / Date.now() 都跟着 NOW 走 */
const START = new Date(2026, 8, 14, 9, 0, 0);   // 2026-09-14
let NOW = new Date(START.getTime());
class FakeDate extends Date {
  constructor(...a) { if (a.length === 0) super(NOW.getTime()); else super(...a); }
  static now() { return NOW.getTime(); }
}
function tick(n) { NOW = new Date(NOW.getTime() + n * 86400000); }

const store = {};
const sandbox = {
  window: global.window,
  localStorage: { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = v; } },
  document: {
    getElementById: () => ({ innerHTML: '', textContent: '', hidden: true, value: '' }),
    addEventListener: () => {}, querySelector: () => null,
  },
  alert: () => {}, confirm: () => true, console,
  Blob: function () {}, URL: { createObjectURL: () => '' },
  Date: FakeDate, Math, JSON, Object, Array, String, Number, Set,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

const g = (e) => vm.runInContext(e, sandbox);
const run = (s) => vm.runInContext(s, sandbox);

let fails = 0;
const ok = (l, c, x) => { console.log((c ? '  ✅ ' : '  ❌ ') + l + (x ? '  → ' + x : '')); if (!c) fails++; };

/* 完美执行：当天所有必做条目全部命中（life/drill 直接打钩） */
run(`
function completeAll() {
  var ds = today();
  S.days[ds].items.forEach(function (it, i) {
    if (!it.need || it.done) return;
    if (it.type === 'life') { it.done = true; return; }
    if (it.type === 'drill') {
      it.done = true;
      var p = S.drill.indexOf(it.key);
      if (p >= 0) S.drill.splice(p, 1);
      S.drill.push(it.key);
      return;
    }
    applyRate(ds, i, 'hit');
  });
}
`);

const DAYS = 45;
const firstSeen = {};      // 母题 key -> 第一次被派的日期
const newByDay = [];
const examDays = [];
const loadByDay = [];

run('S = load();');
for (let d = 0; d < DAYS; d++) {
  const ds = g('today()');
  run('render();');
  const items = g('JSON.parse(JSON.stringify(S.days[today()].items))');
  const need = items.filter(i => i.need);
  const fresh = items.filter(i => i.need && ['new', 'proj', 'rule', 'card'].includes(i.type));
  fresh.forEach(it => { if (!firstSeen[it.key]) firstSeen[it.key] = ds; });
  if (items.some(i => i.type === 'exam')) examDays.push(ds);
  newByDay.push({ ds, new: fresh.map(i => i.label.replace(/^(新母题|项目)：/, '')), rev: need.filter(i => i.type === 'rev').length, n: need.length });
  loadByDay.push(need.length);
  run('completeAll(); save();');
  tick(1);
}

const all = g('flat().map(function(x){return {key:x.key,id:x.id,name:x.name,cid:x.cid,after:x.after};})');
const never = all.filter(x => !firstSeen[x.key]);

console.log(`\n【长跑 ${DAYS} 天 · 每天全部命中】`);
console.log('\n前 14 天派了什么：');
newByDay.slice(0, 14).forEach(r => {
  console.log('  ' + r.ds + '  ' + String(r.n).padStart(2) + ' 条必做（复训 ' + r.rev + '）  ' +
    (r.new.length ? r.new.join(' ｜ ') : '—'));
});
console.log('\n后 14 天：');
newByDay.slice(-14).forEach(r => {
  console.log('  ' + r.ds + '  ' + String(r.n).padStart(2) + ' 条必做（复训 ' + r.rev + '）  ' +
    (r.new.length ? r.new.join(' ｜ ') : '—'));
});

console.log('\n【断言】');
ok('没有母题被永久卡住（死锁）', never.length === 0,
  never.length ? never.map(x => x.id).join(', ') : '');
ok('45 天内所有母题都被派过', Object.keys(firstSeen).length === all.length,
  Object.keys(firstSeen).length + '/' + all.length);

/* 依赖序：每个母题被派的日期必须 ≥ 它的 after 前置被派的日期 */
const bad = [];
all.forEach(x => {
  (x.after || []).forEach(dep => {
    const dk = g(`ID2KEY['${dep}']`);
    if (!dk || !firstSeen[dk] || !firstSeen[x.key]) return;
    if (firstSeen[dk] >= firstSeen[x.key]) bad.push(x.id + ' 早于前置 ' + dep);
  });
});
ok('after 前置一定先于后继被派', bad.length === 0, bad.join('; '));

/* 簇内序：同簇数组序前面的先被派 */
const bad2 = [];
const byCluster = {};
all.forEach(x => { (byCluster[x.cid] = byCluster[x.cid] || []).push(x); });
Object.keys(byCluster).forEach(cid => {
  const arr = byCluster[cid];
  for (let i = 1; i < arr.length; i++) {
    if (firstSeen[arr[i].key] && firstSeen[arr[i - 1].key] &&
        firstSeen[arr[i].key] < firstSeen[arr[i - 1].key]) {
      bad2.push(cid + ': ' + arr[i].id + ' 早于 ' + arr[i - 1].id);
    }
  }
});
ok('同簇内数组序即学习序', bad2.length === 0, bad2.join('; '));

/* 抽检轮次随 L2 池子变暖而变化（三级制下池子冷、轮次自然少），
   所以不再断言「固定 6-8 轮」，改断言真正的规则：轮次存在、且间隔 ≥ EXAM_GAP-1 天。 */
var _gaps = [];
for (var _i = 1; _i < examDays.length; _i++) {
  _gaps.push(Math.round((new Date(examDays[_i]) - new Date(examDays[_i - 1])) / 86400000));
}
ok('抽检确实在跑且不密于 7 天一轮',
  examDays.length >= 2 && _gaps.every(function (x) { return x >= 6; }),
  examDays.length + ' 轮：' + examDays.join(', '));

const maxLoad = Math.max(...loadByDay), avgLoad = loadByDay.reduce((a, b) => a + b, 0) / loadByDay.length;
ok('不封顶后每日必做条数仍在合理区间（≤30）', maxLoad <= 30, '峰值 ' + maxLoad + ' 条，均值 ' + avgLoad.toFixed(1));
ok('45 天后没有欠账（全是必做全交）', g('debtStats().debt') === 0, g('debtStats().debt') + ' 条');
ok('45 天后不再派新题（都学完了）',
  newByDay.slice(-5).every(r => r.new.length === 0),
  newByDay.slice(-5).map(r => r.new.length).join(','));

console.log('\n各能力簇学完顺序（按簇内第一个被派的日子）：');
Object.keys(byCluster)
  .map(cid => ({ cid, first: firstSeen[byCluster[cid][0].key] || '9999' }))
  .sort((a, b) => a.first < b.first ? -1 : 1)
  .forEach(o => console.log('  ' + o.first + '  ' + o.cid));

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
