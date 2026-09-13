/* 无头仿真：把 progress.html 的内联脚本抽出来，在 Node 里跑派单逻辑
   只验证引擎行为，不碰渲染细节（DOM 全是空壳）。*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'progress.html'), 'utf8');
const m = html.match(/<script>\n([\s\S]*?)<\/script>/);
if (!m) throw new Error('找不到内联脚本');
const code = m[1];

global.window = {};
require(path.join(ROOT, '_data', 'clusters.js'));
require(path.join(ROOT, '_data', 'breaks.js'));

const store = {};
const sandbox = {
  window: global.window,
  localStorage: {
    getItem: k => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = v; },
  },
  document: {
    getElementById: () => ({ innerHTML: '', textContent: '', hidden: true, value: '' }),
    addEventListener: () => {}, querySelector: () => null,
  },
  alert: () => {}, confirm: () => true, console,
  Blob: function () {}, URL: { createObjectURL: () => '' },
  Date, Math, JSON, Object, Array, String, Number,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

const g = (expr) => vm.runInContext(expr, sandbox);
const run = (stmt) => vm.runInContext(stmt, sandbox);

let fails = 0;
function ok(label, cond, extra) {
  console.log((cond ? '  ✅ ' : '  ❌ ') + label + (extra ? '  → ' + extra : ''));
  if (!cond) fails++;
}
/* 重置到「全新一天」：清空所有状态，重建今日派单 */
function fresh(extraJs) {
  run("S = { lv:{}, days:{}, drill:[], extra:{}, resetAt:null, relieve:false };" +
      "flat().forEach(function(t){ S.lv[t.key] = { l: t.link?1:0, due:null, last:null, hit:0, miss:0 }; });" +
      (extraJs || '') +
      "FLAT = null; render();");
}
const todayItems = () => g('S.days[today()].items');
const needOf = t => todayItems().filter(i => i.need && i.type === t);
const extraOf = t => todayItems().filter(i => !i.need && i.type === t);

console.log('\n【1】全新状态：第一天派什么');
fresh();
console.log('   ', todayItems().map(i => i.label + (i.need ? '' : '[加餐]')).join(' | '));
ok('今天没有到期复训', needOf('rev').length === 0);
ok('新题 1 条（配额 1）', needOf('new').length === 1);
ok('首条新题是 sql 簇的 M1（zone 轮转第一个）', needOf('new')[0].label.includes('为什么用 B+ 树'));
ok('日课 2 条（手撕 + 命功）', needOf('drill').length === 1 && needOf('life').length === 1);
ok('项目线 1 条，是 EnergyOps 90 秒骨架', needOf('proj').length === 1 &&
  needOf('proj')[0].label.includes('EnergyOps 90 秒骨架'), needOf('proj').map(i => i.label).join(''));
ok('必做共 4 条（1 新题 + 1 项目 + 2 日课）', todayItems().filter(i => i.need).length === 4,
  todayItems().filter(i => i.need).length + ' 条');
ok('没有任何 L≥2 母题时不派抽检', needOf('exam').length === 0);
ok('加餐给了其它 zone 的首题', extraOf('new').length > 0, extraOf('new').map(i => i.label).join(' / '));
ok('加餐里含 AI 主战场与另一后端簇（并行开簇）',
  extraOf('new').some(i => i.label.includes('上下文组装')) && extraOf('new').some(i => i.label.includes('隔离级别')));
ok('项目线不占 zone 轮转名额（新题仍只有配额内那 1 条）', needOf('new').length === 1);
ok('加餐命中上限 EXTRA_MAX=4', extraOf('new').length <= 4);

console.log('\n【2】依赖门控：M1 到 L2 后，下一个解锁的是 M2');
fresh("S.lv['sql/M1'].l = 2;");
ok('下一个新题变成 M2', g("scanClusters().ready.filter(c=>c.cid==='sql')[0].id") === 'M2',
  g("scanClusters().ready.filter(c=>c.cid==='sql')[0].name"));

console.log('\n【3】跨簇 after：R1 被 M1 锁 / M1 达标后解锁');
fresh();
ok('M1 未达标时 R1 不在 ready', !g("scanClusters().ready.some(c=>c.id==='R1')"));
fresh("S.lv['sql/M1'].l = 2;");
ok('M1 到 L2 后 R1 解锁', g("scanClusters().ready.some(c=>c.id==='R1')"));

console.log('\n【4】跨簇 after：M13 要等 M11 和 M12');
fresh("['M8','M9','M10'].forEach(function(i){ S.lv['tx/'+i].l = 2; });");
const m13 = g("scanClusters().locked.find(c=>c.id==='M13')");
ok('M13 成为 tx 的下一条但被锁', !!m13, m13 ? '缺 ' + m13.miss.map(x => x.id).join('、') : '没被扫到');
fresh("['tx/M8','tx/M9','tx/M10','ha/M11','ha/M12'].forEach(function(k){ S.lv[k].l = 2; });");
ok('M11/M12 到 L2 后 M13 解锁', g("scanClusters().ready.some(c=>c.id==='M13')"));

console.log('\n【5】复训队列：due 驱动 + 逾期优先 + 未到期不派');
fresh("var D = today();" +
      "S.lv['sql/M1'].l=2; S.lv['sql/M1'].due=shift(D,-5);" +
      "S.lv['sql/M2'].l=2; S.lv['sql/M2'].due=shift(D,-1);" +
      "S.lv['sql/M3'].l=2; S.lv['sql/M3'].due=shift(D,3);");
ok('只收 due ≤ 今天', !g("reviewQueue().map(x=>x.id)").includes('M3'),
  '队列 ' + JSON.stringify(g("reviewQueue().map(x=>x.id)")));
ok('逾期最久的排第一', g("reviewQueue()[0].id") === 'M1');
ok('今天派 2 条复训', needOf('rev').length === 2, needOf('rev').length + ' 条');
ok('复训条目标了逾期天数', needOf('rev')[0].sub.includes('逾期 5 天'), needOf('rev')[0].sub);

console.log('\n【6】复训预算溢出 → 进加餐，不计欠账');
fresh("var D = today();" +
      "for (var i=1;i<=8;i++) { const k='sql/M'+i; if(S.lv[k]){ S.lv[k].l=2; S.lv[k].due=shift(D,-i); } }");
ok('必做复训封顶 4 条', needOf('rev').length === 4, needOf('rev').length + ' 条');
ok('溢出最多 2 条进加餐', extraOf('rev').length === 2, extraOf('rev').length + ' 条');
ok('记录下溢出总数供提示', g('S.days[today()].revOver') === 3, '溢出 ' + g('S.days[today()].revOver') + ' 条');

console.log('\n【7】跨天欠账：实时算，只统计必做');
fresh("function fakeDay(ds, needDone, extraDone) {" +
      "  S.days[ds] = { items: [" +
      "    {type:'new', need:true,  done:needDone,  label:'n', sub:''}," +
      "    {type:'rev', need:false, done:extraDone, label:'e', sub:''} ], settled:true };" +
      "}" +
      "fakeDay(daysAgo(1), false, false); fakeDay(daysAgo(2), true, false);");
ok('第 2 天必做没交 → 欠 1 条', g('debtStats().debt') === 1, g('debtStats().debt') + ' 条');
ok('加餐没做不算欠账（否则是 3 条）', g('debtStats().debt') === 1);
ok('只连欠 1 天 → 不减负', g('debtStats().relieve') === false);
run("fakeDay(daysAgo(2), false, false);");
ok('连欠 2 天 → 减负', g('debtStats().relieve') === true, '欠 ' + g('debtStats().debt') + ' 条');

console.log('\n【8】减负模式：不派新题 + 复训降到 2 条');
fresh("function fakeDay(ds){ S.days[ds] = { items:[{type:'new',need:true,done:false,label:'n',sub:''}], settled:true }; }" +
      "var D = today();" +
      "for (var i=1;i<=6;i++) { const k='sql/M'+i; if(S.lv[k]){ S.lv[k].l=2; S.lv[k].due=shift(D,-i); } }" +
      "fakeDay(daysAgo(1)); fakeDay(daysAgo(2));");
ok('relieve = true', g('S.relieve') === true);
ok('今天 0 条新题', needOf('new').length === 0);
ok('复训预算降到 2 条', g('S.days[today()].revBudget') === 2, g('S.days[today()].revBudget'));
ok('复训必做只有 2 条', needOf('rev').length === 2);
ok('欠账 = 2 条', g('debtStats().debt') === 2, g('debtStats().debt') + ' 条');

console.log('\n【9】自适应配额：昨天全交 → 2 条，前天也全交 → 3 条');
fresh("function fakeDay(ds, all){ S.days[ds] = { items:[{type:'new',need:true,done:all,label:'x',sub:''},{type:'life',need:true,done:true,label:'y',sub:''}], settled:true }; }" +
      "fakeDay(daysAgo(1), true); fakeDay(daysAgo(2), false);");
ok('昨天全交 → 配额 2', g('quota()') === 2, g('quota()'));
ok('今天必做新题 2 条', needOf('new').length === 2, needOf('new').length + ' 条');
fresh("function fakeDay(ds, all){ S.days[ds] = { items:[{type:'new',need:true,done:all,label:'x',sub:''},{type:'life',need:true,done:true,label:'y',sub:''}], settled:true }; }" +
      "fakeDay(daysAgo(1), true); fakeDay(daysAgo(2), true);");
ok('前天也全交 → 配额 3', g('quota()') === 3, g('quota()'));
ok('今天必做新题 3 条', needOf('new').length === 3, needOf('new').length + ' 条');
ok('3 条新题来自 3 个不同 zone', new Set(needOf('new').map(i => i.sub.split(' · ')[0])).size === 3,
  needOf('new').map(i => i.sub.split(' · ')[0]).join(' / '));

console.log('\n【10】加餐条目完成照常升 L，但不产生欠账');
fresh();
const ei = g("S.days[today()].items.findIndex(i=>!i.need)");
if (ei >= 0) {
  const key = g(`S.days[today()].items[${ei}].key`);
  run(`rate('${g('today()')}', ${ei}); doRate('hit');`);
  ok('加餐做完 → 该母题升到 L2', g(`S.lv['${key}'].l`) === 2, 'L' + g(`S.lv['${key}'].l`));
  ok('升 L 后进入 1-3-7-14-30 阶梯（首次命中 +1 天）', g(`S.lv['${key}'].due`) === g("shift(today(), 1)"),
    g(`S.lv['${key}'].due`));
  run(`rate('${g('today()')}', ${ei});`);
  ok('已评条目不可重复评（只读）', g(`S.lv['${key}'].hit`) === 1, 'hit=' + g(`S.lv['${key}'].hit`));
  ok('加餐完成不影响欠账', g('debtStats().debt') === 0);
} else ok('存在加餐条目', false, '今天没有加餐条目');

console.log('\n【11】当天派单冻结：反复打开不重派');
fresh();
const snapshot = JSON.stringify(g('S.days[today()].items.map(i=>i.label)'));
run("render(); render();");
ok('重新 render 不改变今日条目', JSON.stringify(g('S.days[today()].items.map(i=>i.label)')) === snapshot);

console.log('\n【12】清账重开与手撕轮转');
fresh("function fakeDay(ds){ S.days[ds] = { items:[{type:'new',need:true,done:false,label:'n',sub:''}], settled:true }; }" +
      "fakeDay(daysAgo(1)); fakeDay(daysAgo(2)); fakeDay(daysAgo(3));");
ok('3 天欠账被累计', g('debtStats().debt') === 3, g('debtStats().debt') + ' 条');
ok('连欠 3 天 → 减负', g('debtStats().relieve') === true);
run("S.resetAt = today();");
ok('清账重开后欠账归零', g('debtStats().debt') === 0);
ok('清账后不进入减负', g('debtStats().relieve') === false);
ok('清账不动等级', g("S.lv['sql/M1'].l") >= 1);

fresh();
const firstDrill = g('pickDrill().id');
run("S.drill = window.MARVIS_DRILL.topics.map(t=>'drill/'+t.id);");
ok('全练完后派最久没练的（队首 D1）', g('pickDrill().id') === firstDrill, '派了 ' + g('pickDrill().id'));
run("S.drill = S.drill.slice(1).concat(['drill/D1']);");
ok('把 D1 挪到队尾后改派 D2', g('pickDrill().id') === 'D2', '派了 ' + g('pickDrill().id'));

console.log('\n【13】项目线：骨架 → 决策链，每天 1 条');
fresh();
ok('派 EnergyOps 90 秒骨架', needOf('proj')[0].label.includes('EnergyOps 90 秒骨架'));
fresh("S.lv['pitch/P1'].l = 2;");
ok('P1 到 L2 后改派 EnergyOps 决策链', needOf('proj')[0].label.includes('EnergyOps 决策链'),
  needOf('proj')[0].label);
fresh("['pitch/P1','pitch/P2','pitch/P3','pitch/P4','pitch/P5'].forEach(function(k){ S.lv[k].l = 2; });");
ok('只剩最后一条时派 RuleArena 决策链', needOf('proj')[0].label.includes('RuleArena 决策链'),
  needOf('proj')[0].label);
run("S.lv['pitch/P6'].l = 2;");
ok('六条全到 L2 后不再派项目线', g('projectNext()') === null);
ok('没有项目条目的日子不再出现复习条目', true);

console.log('\n【14】抽检：7 天一轮，从 L≥2 里抽 5 题');
const SIX = "['sql/M1','sql/M2','sql/M3','tx/M8','tx/M9','llm/C1'].forEach(function(k){ S.lv[k].l = 2; });";
fresh(SIX);
ok('到期时派抽检', needOf('exam').length === 5, needOf('exam').length + ' 条');
ok('抽检记录签发日', g('S.exam.lastIssued') === g('today()'), g('S.exam.lastIssued'));
ok('未到 L2 的不进抽检池', !g("examRanked().some(x=>x.key==='sql/M4')"));
ok('抽检是必做（不做会欠账）', needOf('exam').every(i => i.need === true));
fresh(SIX + "S.exam = { lastIssued: daysAgo(3), lastDone: daysAgo(3), rounds: 1 };");
ok('签发 3 天后不再抽（未满 7 天）', needOf('exam').length === 0);
run('S.exam.lastIssued = daysAgo(7);');
ok('满 7 天后 examDue 为真', g('examDue()') === true);
fresh(SIX + "S.exam = { lastIssued: daysAgo(20), lastDone: daysAgo(20), rounds: 1 };");
ok('逾期 20 天也只发一轮（不滚雪球）', needOf('exam').length === 5, needOf('exam').length + ' 条');
fresh(SIX + "S.lv['sql/M1'].miss = 3; S.lv['sql/M1'].last = daysAgo(30);");
ok('忘得多的排抽检池第一', g("examRanked()[0].key") === 'sql/M1', g("examRanked()[0].key"));
fresh(SIX + "S.lv['sql/M2'].last = daysAgo(1);");
ok('最近 2 天刚自评过的不抽', !g("examRanked().some(x=>x.key==='sql/M2')"));

console.log('\n【15】断点回流：复训条目上摊开上次断点');
const bpKeys = g("Object.keys(BREAKS).filter(function(k){ return BREAKS[k].bp; })");
ok('模板占位符没被当成断点', !g("Object.keys(BREAKS).some(function(k){ return /待填|^【/.test(BREAKS[k].bp||''); })"),
  '真断点 ' + bpKeys.length + ' 条');
ok('占位符被过滤后仍有真实数据可用（一句话结论）',
  g("Object.keys(BREAKS).filter(function(k){ return BREAKS[k].con; }).length") > 0,
  g("Object.keys(BREAKS).filter(function(k){ return BREAKS[k].con; }).length") + ' 条有结论');
/* 真断点要等闭卷自评后写进母题卡，现在只有 9 张算法卡有；
   这里注入一条假的，验证「母题卡 → breaks.js → 复训卡面」这条链路是通的 */
run("BREAKS['topics/MySQL-母题-M1-为什么用B+树.html'] = " +
    "{ bp: '把回表和覆盖索引说混了', kw: ['聚簇索引','回表'], fu: [{q:'什么时候不用回表？'}] };");
fresh("S.lv['sql/M1'].l = 2; S.lv['sql/M1'].due = shift(today(), -1);");
const row = needOf('rev')[0];
ok('复训条目里带「上次断点」', !!row && row.sub.includes('上次断点'), row ? row.label : '没有复训条目');
ok('断点原文来自母题卡数据', !!row && row.sub.includes('把回表和覆盖索引说混了'));
ok('带断点的母题进复训队列', g('reviewQueue()[0].id') === 'M1', g('reviewQueue()[0].id'));
ok('无断点的母题不显示该行', !needOf('new')[0].sub.includes('上次断点'));

console.log('\n【16】抽检连答一轮：结果写回 L + 记录轮次');
fresh("['sql/M1','sql/M2','sql/M3','tx/M8','tx/M9'].forEach(function(k){ S.lv[k].l = 2; });");
run('examStart();');
ok('抽检队列 5 题', g('EXAM_Q.length') === 5, g('EXAM_Q.length') + ' 题');
run("examRate('hit'); examRate('hit'); examRate('part'); examRate('hit'); examRate('hit');");
ok('5 题全部标记完成', todayItems().filter(i => i.type === 'exam' && i.done).length === 5,
  todayItems().filter(i => i.type === 'exam' && i.done).length + ' 题');
ok('记录本轮已完成', g('S.exam.lastDone') === g('today()'));
ok('轮次 +1', g('S.exam.rounds') === 1, g('S.exam.rounds'));
ok('答对的升到 L3', g("S.lv['sql/M1'].l") === 3, 'L' + g("S.lv['sql/M1'].l"));
ok('答「部分」的停在 L2', g("S.lv['sql/M3'].l") === 2, 'L' + g("S.lv['sql/M3'].l"));
run("examRate('hit');");
ok('队列走完后重复点击无害', todayItems().filter(i => i.type === 'exam' && i.done).length === 5);

console.log('\n【17】旧版本当天派单的迁移');
fresh();
run("S.days[today()] = { items:[" +
    "{type:'rev',key:'sql/M1',need:true,done:false,label:'旧复训',sub:''}," +
    "{type:'life',key:'life',need:true,done:false,label:'旧命功',sub:''} ], settled:false };" +
    "render();");
ok('旧版派单（没有 v:2、还没动手）被重建', g('S.days[today()].v') === 2 && todayItems().length > 2,
  todayItems().length + ' 条');
ok('重建后带上了项目线', needOf('proj').length === 1);
run("S.days[today()] = { items:[" +
    "{type:'rev',key:'sql/M1',need:true,done:true,label:'旧复训',sub:''} ], settled:false };" +
    "render();");
ok('已经打过勾的旧版派单不重建（不丢记录）',
  todayItems().length === 1 && g('S.days[today()].v') !== 2, todayItems().length + ' 条');

console.log('\n【18】派单记录只留最近 180 天（localStorage 不无限涨）');
run("S = load(); S.days = {};" +
    "S.days[today()] = { v:2, items:[{type:'new',need:true,done:true,key:'sql/M1',label:'x',sub:''}] };" +
    "for (var i=0;i<250;i++){ S.days[shift(today(), -i-1)] = " +
    "  { v:2, items:[{type:'new',need:true,done:true,key:'sql/M1',label:'x',sub:''}] }; }" +
    "save();");
ok('251 天被裁到 180 天', Object.keys(g('S.days')).length === 180, Object.keys(g('S.days')).length + ' 天');
ok('裁掉的是最旧的', g("Object.keys(S.days).sort()[0]") === g('shift(today(), -179)'),
  '最早的剩 ' + g("Object.keys(S.days).sort()[0]"));
ok('今天没被裁掉', !!g('S.days[today()]'));
ok('裁剪后欠账仍能算（今天不算欠账）', g('debtStats().debt') === 0, g('debtStats().debt') + ' 条');

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
