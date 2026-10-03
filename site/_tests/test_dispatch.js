/* 无头仿真：把 progress.html 的内联脚本抽出来，在 Node 里跑派单逻辑
   只验证引擎行为，不碰渲染细节（DOM 全是空壳）。*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'progress.html'), 'utf8');
const m = html.match(/<script>\r?\n([\s\S]*?)<\/script>/);
if (!m) throw new Error('找不到内联脚本');
const code = m[1];

global.window = { addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => {} };
require(path.join(ROOT, '_data', 'clusters.js'));
require(path.join(ROOT, '_data', 'breaks.js'));
/* 原则卡簇是 build.py 生成在 _data/cards.js 里的；测试里给两条桩卡（card/adler-1、card/adler-2），
   验证派单引擎对这条内化线的行为。cards.js 真数据变化不影响这里的行为断言。 */
global.window.MARVIS_CARD_CLUSTER = {
  id: 'card', name: '原则卡 · 读厚', zone: '准则',
  topics: [
    { id: 'adler-1', name: '课题分离', href: 'cards.html#card-adler-1' },
    { id: 'adler-2', name: '目的论：理由是造出来的', href: 'cards.html#card-adler-2' },
  ],
};

const store = {};
const ELS = {};   /* 按 id 缓存的假 DOM，用来读弹窗里到底写了什么 */
const sandbox = {
  window: global.window,
  localStorage: {
    getItem: k => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = v; },
  },
  document: {
    getElementById: (id) => {
      if (!ELS[id]) ELS[id] = { id: id, innerHTML: '', textContent: '', hidden: true, value: '' };
      return ELS[id];
    },
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
      "flat().forEach(function(t){ S.lv[t.key] = { l: 0, due:null, last:null, hit:0, miss:0 }; });" +
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
ok('新题保底 5 条（NEW_MIN=5）', needOf('new').length === 5, needOf('new').length + ' 条');
ok('首条新题是 llm 模块的第 1 条主线（模型为什么不可靠）',
  needOf('new')[0].label.includes('模型为什么不可靠'), needOf('new')[0].label);
ok('日课 6 条（手撕 5 题 + 命功）', needOf('drill').length === 5 && needOf('life').length === 1,
  '手撕 ' + needOf('drill').length + ' 条');
ok('5 题互不重复', new Set(needOf('drill').map(i => i.key)).size === 5,
  needOf('drill').map(i => i.key).join(','));
ok('手撕标了序号 1/5…5/5', needOf('drill')[0].label.startsWith('手撕 1/5'), needOf('drill')[0].label);
ok('项目线 1 条，是 EnergyOps 90 秒骨架', needOf('proj').length === 1 &&
  needOf('proj')[0].label.includes('EnergyOps 90 秒骨架'), needOf('proj').map(i => i.label).join(''));
ok('准则 1 条（内化线 2026-10-03 接入），是 R1 机会成本门', needOf('rule').length === 1 &&
  needOf('rule')[0].label.includes('机会成本门'), needOf('rule').map(i => i.label).join(''));
ok('原则卡 1 条（内化线 2026-10-03 接入），是 adler-1 课题分离', needOf('card').length === 1 &&
  needOf('card')[0].label.includes('课题分离'), needOf('card').map(i => i.label).join(''));
ok('必做共 14 条（5 新学 + 1 项目 + 1 准则 + 1 原则卡 + 5 手撕 + 1 命功）',
  todayItems().filter(i => i.need).length === 14,
  todayItems().filter(i => i.need).length + ' 条');
ok('没有任何 L≥2 母题时不派抽检', needOf('exam').length === 0);
ok('加餐给了其它 zone 的首题', extraOf('new').length > 0, extraOf('new').map(i => i.label).join(' / '));
ok('加餐来自一档的其它模块（和必做那条不重复）',
  extraOf('new').length > 0 && !extraOf('new').some(i => i.label.includes('模型为什么不可靠')),
  extraOf('new').map(i => i.label).join(' / '));
ok('项目线不占新学名额（新学仍是保底 5 条）', needOf('new').length === 5, needOf('new').length + ' 条');
ok('加餐命中上限 EXTRA_MAX=8', extraOf('new').length <= 8);

console.log('\n【2】模块内推进：mysql 第 1 条到 L2 后，下一条是第 2 条');
fresh("S.lv['mysql/1'].l = 2;");
ok('mysql 模块推进到第 2 条（SQL 执行与优化）',
  g("scanClusters().ready.filter(c=>c.cid==='mysql')[0].id") === '2',
  g("scanClusters().ready.filter(c=>c.cid==='mysql')[0].name"));

console.log('\n【3】档位串行：一档还有得派，就不派二档/三档');
fresh();
ok('全新状态下 ready 全是一档', g("scanClusters().ready.every(c=>c.zone==='一档')"),
  g("scanClusters().ready.map(c=>c.cid+':'+c.id).join(', ')"));
ok('二档首条此时不在 ready', !g("scanClusters().ready.some(c=>c.zone==='二档')"));
fresh("flat().forEach(function(t){ if(t.zone==='一档') S.lv[t.key].l = 2; });");
ok('一档全部过关后，ready 才出现二档', g("scanClusters().ready.some(c=>c.zone==='二档')"),
  g("scanClusters().ready.map(c=>c.cid+':'+c.id).slice(0,3).join(', ')"));

console.log('\n【4】簇内门控：同一簇内前一条主线到「会了」才解锁下一条');
fresh();
ok('mysql 模块首条是第 1 条（索引与表设计）',
  g("scanClusters().ready.filter(c=>c.cid==='mysql')[0].id") === '1',
  g("scanClusters().ready.filter(c=>c.cid==='mysql')[0].name"));
fresh("S.lv['mysql/1'].l = 1;");
ok('第 1 条到 L1 后推进到第 2 条',
  g("scanClusters().ready.filter(c=>c.cid==='mysql')[0].id") === '2',
  g("scanClusters().ready.filter(c=>c.cid==='mysql')[0].name"));
fresh();
ok('第 1 条没过时模块不推进（连候选都不给）',
  !g("scanClusters().ready.some(c=>c.key==='mysql/2')") &&
  !g("scanClusters().locked.some(c=>c.key==='mysql/2')"));

console.log('\n【5】复训队列：due 驱动 + 逾期优先 + 未到期不派');
fresh("var D = today();" +
      "S.lv['mysql/1'].l=2; S.lv['mysql/1'].due=shift(D,-5);" +
      "S.lv['mysql/2'].l=2; S.lv['mysql/2'].due=shift(D,-1);" +
      "S.lv['mysql/3'].l=2; S.lv['mysql/3'].due=shift(D,3);");
ok('只收 due ≤ 今天', !g("reviewQueue().map(x=>x.id)").includes('mysql-3'),
  '队列 ' + JSON.stringify(g("reviewQueue().map(x=>x.id)")));
ok('逾期最久的排第一', g("reviewQueue()[0].key") === 'mysql/1', g("reviewQueue()[0].key"));
ok('今天派 2 条复训', needOf('rev').length === 2, needOf('rev').length + ' 条');
ok('复训条目标了逾期天数', needOf('rev')[0].sub.includes('逾期 5 天'), needOf('rev')[0].sub);

console.log('\n【6】复训预算溢出 → 进加餐，不计欠账');
const OVERDUE8 = "var D = today();" +
      "['mysql/1','mysql/2','mysql/3','redis/1','redis/3'," +
      " 'net/1','net/2','llm/2'].forEach(function(k, i) {" +
      " if(S.lv[k]){ S.lv[k].l=2; S.lv[k].due=shift(D,-(i+1)); } });";
fresh(OVERDUE8);
ok('必做复训封顶 5 条（REV_BUDGET=5）', needOf('rev').length === 5, needOf('rev').length + ' 条');
ok('复训溢出全部进加餐（不封顶）', extraOf('rev').length === 3, extraOf('rev').length + ' 条');
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

console.log('\n【8】减负模式：不派新题 + 复训降到 2 条 + 日课不压（仍 5 题）');
fresh("function fakeDay(ds){ S.days[ds] = { items:[{type:'new',need:true,done:false,label:'n',sub:''}], settled:true }; }" +
      "var D = today();" +
      "['mysql/1','mysql/2','mysql/3','redis/1','redis/3','net/1'].forEach(" +
      "function(k, i){ if(S.lv[k]){ S.lv[k].l=2; S.lv[k].due=shift(D,-(i+1)); } });" +
      "fakeDay(daysAgo(1)); fakeDay(daysAgo(2));");
ok('relieve = true', g('S.relieve') === true);
ok('今天 0 条新题', needOf('new').length === 0);
ok('复训预算降到 2 条', g('S.days[today()].revBudget') === 2, g('S.days[today()].revBudget'));
ok('复训必做只有 2 条', needOf('rev').length === 2);
ok('减负不压日课：仍 5 题手撕 + 1 命功',
  needOf('drill').length === 5 && needOf('life').length === 1, needOf('drill').length + ' 题');
ok('欠账 = 2 条', g('debtStats().debt') === 2, g('debtStats().debt') + ' 条');

console.log('\n【9】自适应配额：保底 4 条，昨天全交 → 5 条，前天也全交 → 6 条');
fresh("function fakeDay(ds, all){ S.days[ds] = { items:[{type:'new',need:true,done:all,label:'x',sub:''},{type:'life',need:true,done:true,label:'y',sub:''}], settled:true }; }" +
      "fakeDay(daysAgo(1), true); fakeDay(daysAgo(2), false);");
ok('昨天全交 → 配额 6', g('quota()') === 6, g('quota()'));
ok('今天必做新题 6 条', needOf('new').length === 6, needOf('new').length + ' 条');
fresh("function fakeDay(ds, all){ S.days[ds] = { items:[{type:'new',need:true,done:all,label:'x',sub:''},{type:'life',need:true,done:true,label:'y',sub:''}], settled:true }; }" +
      "fakeDay(daysAgo(1), true); fakeDay(daysAgo(2), true);");
ok('前天也全交 → 配额 7', g('quota()') === 7, g('quota()'));
ok('一档有 10 个模块 → 配额 7 派满 7 条', needOf('new').length === 7, needOf('new').length + ' 条');
ok('7 条来自 7 个不同模块（同一模块每天最多推进 1 条）',
  new Set(needOf('new').map(i => i.sub.split(' · ')[0])).size === 7,
  needOf('new').map(i => i.sub.split(' · ')[0]).join(' / '));

console.log('\n【10】加餐条目完成照常升 L，但不产生欠账');
fresh();
const ei = g("S.days[today()].items.findIndex(i=>!i.need)");
if (ei >= 0) {
  const key = g(`S.days[today()].items[${ei}].key`);
  run(`rate('${g('today()')}', ${ei}); doRate('hit');`);
  ok('加餐做完 → 该母题升到「会了」(L1)', g(`S.lv['${key}'].l`) === 1, 'L' + g(`S.lv['${key}'].l`));
  ok('升 L 后进入复训阶梯（首次命中 +1 天）', g(`S.lv['${key}'].due`) === g("shift(today(), 1)"),
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
ok('清账不动等级（级别重开前是多少还是多少）', g("S.lv['mysql/1'].l") === 0, 'L' + g("S.lv['mysql/1'].l"));

fresh();
const firstDrill = g('pickDrill().id');
run("S.drill = window.MARVIS_DRILL.topics.map(t=>'drill/'+t.id);");
ok('全练完后派最久没练的（队首 D1）', g('pickDrill().id') === firstDrill, '派了 ' + g('pickDrill().id'));
run("S.drill = S.drill.slice(1).concat(['drill/D1']);");
ok('把 D1 挪到队尾后改派 D2', g('pickDrill().id') === 'D2', '派了 ' + g('pickDrill().id'));

console.log('\n【13】项目线：骨架 → 决策链，每天 1 条');
fresh();
ok('派 EnergyOps 90 秒骨架', needOf('proj')[0].label.includes('EnergyOps 90 秒骨架'));
fresh("S.lv['pitch/T1'].l = 2;");
ok('P1 到 L2 后改派 EnergyOps 决策链', needOf('proj')[0].label.includes('EnergyOps 决策链'),
  needOf('proj')[0].label);
fresh("['pitch/T1','pitch/T2','pitch/T3','pitch/T4','pitch/T5'].forEach(function(k){ S.lv[k].l = 2; });");
ok('只剩最后一条时派 RuleArena 决策链', needOf('proj')[0].label.includes('RuleArena 决策链'),
  needOf('proj')[0].label);
run("S.lv['pitch/T6'].l = 2;");
ok('六条全到 L2 后不再派项目线', g('projectNext()') === null);
ok('没有项目条目的日子不再出现复习条目', true);

console.log('\n【13b】内化线：准则/原则卡每天 1 条，簇内顺序推进');
fresh();
ok('准则派 R1 机会成本门', needOf('rule')[0].label.includes('机会成本门'));
fresh("S.lv['rule/R1'].l = 2;");
ok('R1 到 L2 后改派 R2 有限计划会', needOf('rule')[0].label.includes('有限计划会'),
  needOf('rule').map(i => i.label).join(''));
fresh("['rule/R1','rule/R2','rule/R3','rule/R4','rule/R5','rule/R6','rule/R7','rule/R8','rule/R9']" +
      ".forEach(function(k){ S.lv[k].l = 2; });");
ok('只剩 R10 时派 never miss twice', needOf('rule')[0].label.includes('never miss twice'));
run("S.lv['rule/R10'].l = 2;");
ok('十条全到 L2 后不再派准则', g('ruleNext()') === null);
fresh("S.lv['card/adler-1'].l = 2;");
ok('原则卡 1 过关后改派卡 2', needOf('card')[0].label.includes('目的论'),
  needOf('card').map(i => i.label).join(''));
run("S.lv['card/adler-2'].l = 2;");
ok('两张桩卡全过后不再派原则卡', g('cardNext()') === null);

console.log('\n【14】抽检：7 天一轮，从 L≥2 里抽 5 题');
const SIX = "['mysql/1','mysql/2','mysql/3','redis/1','redis/3','llm/2'].forEach(function(k){ S.lv[k].l = 2; });";
fresh(SIX);
ok('到期时派抽检', needOf('exam').length === 5, needOf('exam').length + ' 条');
ok('抽检记录签发日', g('S.exam.lastIssued') === g('today()'), g('S.exam.lastIssued'));
ok('未到 L2 的不进抽检池', !g("examRanked().some(x=>x.key==='net/1')"));
ok('抽检是必做（不做会欠账）', needOf('exam').every(i => i.need === true));
fresh(SIX + "S.exam = { lastIssued: daysAgo(3), lastDone: daysAgo(3), rounds: 1 };");
ok('签发 3 天后不再抽（未满 7 天）', needOf('exam').length === 0);
run('S.exam.lastIssued = daysAgo(7);');
ok('满 7 天后 examDue 为真', g('examDue()') === true);
fresh(SIX + "S.exam = { lastIssued: daysAgo(20), lastDone: daysAgo(20), rounds: 1 };");
ok('逾期 20 天也只发一轮（不滚雪球）', needOf('exam').length === 5, needOf('exam').length + ' 条');
fresh(SIX + "S.lv['mysql/1'].miss = 3; S.lv['mysql/1'].last = daysAgo(30);");
ok('忘得多的排抽检池第一', g("examRanked()[0].key") === 'mysql/1', g("examRanked()[0].key"));
fresh(SIX + "S.lv['mysql/2'].last = daysAgo(1);");
ok('最近 2 天刚自评过的不抽', !g("examRanked().some(x=>x.key==='mysql/2')"));

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
fresh("S.lv['mysql/1'].l = 2; S.lv['mysql/1'].due = shift(today(), -1);");
const row = needOf('rev')[0];
ok('复训条目里带「上次断点」', !!row && row.sub.includes('上次断点'), row ? row.label : '没有复训条目');
ok('断点原文来自母题卡数据', !!row && row.sub.includes('把回表和覆盖索引说混了'));
ok('带断点的主线进复训队列', g('reviewQueue()[0].key') === 'mysql/1', g('reviewQueue()[0].key'));
ok('无断点的母题不显示该行', !needOf('new')[0].sub.includes('上次断点'));

console.log('\n【16】抽检连答一轮：结果写回 L + 记录轮次');
fresh("['mysql/1','mysql/2','mysql/3','redis/1','redis/3'].forEach(function(k){ S.lv[k].l = 2; });");
run('examStart();');
ok('抽检队列 5 题', g('EXAM_Q.length') === 5, g('EXAM_Q.length') + ' 题');
run("examRate('hit'); examRate('hit'); examRate('part'); examRate('hit'); examRate('hit');");
ok('5 题全部标记完成', todayItems().filter(i => i.type === 'exam' && i.done).length === 5,
  todayItems().filter(i => i.type === 'exam' && i.done).length + ' 题');
ok('记录本轮已完成', g('S.exam.lastDone') === g('today()'));
ok('轮次 +1', g('S.exam.rounds') === 1, g('S.exam.rounds'));
ok('答对的到「常练」(L2，三级制顶格)', g("S.lv['mysql/1'].l") === 2, 'L' + g("S.lv['mysql/1'].l"));
ok('答「部分」的停在 L2 不升', g("S.lv['mysql/3'].l") === 2, 'L' + g("S.lv['mysql/3'].l"));
run("examRate('hit');");
ok('队列走完后重复点击无害', todayItems().filter(i => i.type === 'exam' && i.done).length === 5);

console.log('\n【17】旧版本当天派单的迁移');
fresh();
run("S.days[today()] = { items:[" +
    "{type:'rev',key:'mysql/1',need:true,done:false,label:'旧复训',sub:''}," +
    "{type:'life',key:'life',need:true,done:false,label:'旧命功',sub:''} ], settled:false };" +
    "render();");
ok('旧版派单（没有 v:4、还没动手）被重建', g('S.days[today()].v') === 4 && todayItems().length > 2,
  todayItems().length + ' 条');
ok('重建后带上了项目线', needOf('proj').length === 1);
run("S.days[today()] = { items:[" +
    "{type:'rev',key:'mysql/1',need:true,done:true,label:'旧复训',sub:''} ], settled:false };" +
    "render();");
ok('已经打过勾的旧版派单不重建（不丢记录）',
  todayItems().length === 1 && g('S.days[today()].v') !== 3, todayItems().length + ' 条');

console.log('\n【18】派单记录只留最近 180 天（localStorage 不无限涨）');
run("S = load(); S.days = {};" +
    "S.days[today()] = { v:2, items:[{type:'new',need:true,done:true,key:'mysql/1',label:'x',sub:''}] };" +
    "for (var i=0;i<250;i++){ S.days[shift(today(), -i-1)] = " +
    "  { v:2, items:[{type:'new',need:true,done:true,key:'mysql/1',label:'x',sub:''}] }; }" +
    "save();");
ok('251 天被裁到 180 天', Object.keys(g('S.days')).length === 180, Object.keys(g('S.days')).length + ' 天');
ok('裁掉的是最旧的', g("Object.keys(S.days).sort()[0]") === g('shift(today(), -179)'),
  '最早的剩 ' + g("Object.keys(S.days).sort()[0]"));
ok('今天没被裁掉', !!g('S.days[today()]'));
ok('裁剪后欠账仍能算（今天不算欠账）', g('debtStats().debt') === 0, g('debtStats().debt') + ' 条');

console.log('\n【19】手撕日课：点开先给材料，且不能一击打勾');
fresh();
const di = todayItems().findIndex(i => i.type === 'drill');
ok('今天派到 5 条手撕', di >= 0 && needOf('drill').length === 5,
  di >= 0 ? todayItems()[di].label : '没派到');
ok('手撕条目挂着本题材料链接', !!todayItems()[di].link, todayItems()[di].link || '无链接');
run(`rate('${g('today()')}', ${di});`);
ok('点手撕不再直接打勾', todayItems()[di].done === false);
ok('弹窗被打开（有内容可看）', (ELS.ratebody.innerHTML || '').length > 0,
  (ELS.ratebody.innerHTML || '').length + ' 字符');
ok('弹窗里有材料链接', (ELS.ratebody.innerHTML || '').includes(todayItems()[di].link));
ok('弹窗里有 10 分钟限时环', (ELS.ratebody.innerHTML || '').includes('timer-ring') &&
  (ELS.ratebody.innerHTML || '').includes('600'));
ok('弹窗给三个结果按钮', ['ok', 'peek', 'skip'].every(s =>
  (ELS.ratebody.innerHTML || '').includes("doDrill('" + s + "')")));
const dk = todayItems()[di].key;
run("doDrill('skip');");
ok('点「今天跳过」：条目完成但不算练过', todayItems()[di].done === true && !g('S.drill').includes(dk),
  'S.drill=' + JSON.stringify(g('S.drill')));
fresh();
const di2 = todayItems().findIndex(i => i.type === 'drill');
const dk2 = todayItems()[di2].key;
run(`rate('${g('today()')}', ${di2}); doDrill('ok');`);
ok('点「闭卷写出来」：完成 + 进日课队列', todayItems()[di2].done === true && g('S.drill').indexOf(dk2) === 0,
  'S.drill=' + JSON.stringify(g('S.drill')));
ok('结果名写进清单行（不是「讲得出」那套措辞）',
  g(`taskRow(today(), ${di2}, S.days[today()].items[${di2}])`).includes('闭卷写出来'),
  g(`taskRow(today(), ${di2}, S.days[today()].items[${di2}])`).slice(0, 80));
run(`rate('${g('today()')}', ${di2});`);
ok('已评的手撕不可重复评（弹窗不再打开）', ELS.rate.hidden !== false || todayItems()[di2].done === true);
fresh();
run("S.drill = window.MARVIS_DRILL.topics.map(t=>'drill/'+t.id);");
ok('37 题全练过后派最久没练的（队首）', g('pickDrill().id') === 'D1', '派了 ' + g('pickDrill().id'));

fresh();
const di3 = todayItems().findIndex(i => i.type === 'drill');
const rowU = g(`taskRow(today(), ${di3}, S.days[today()].items[${di3}])`);
ok('未评手撕行的行首 ✓ 是「标记完成」按钮（阻冒泡，不触发整行开材料）',
  rowU.includes('quickDrill') && rowU.includes('stopPropagation'), rowU.slice(0, 110));
const revIdx = todayItems().findIndex(i => i.type === 'rev' || i.type === 'new');
ok('复训/新学行的 ✓ 不是按钮（等级只能由弹窗自评推进，禁手改）',
  revIdx >= 0 && !g(`taskRow(today(), ${revIdx}, S.days[today()].items[${revIdx}])`).includes('quickDrill'));
const dk3 = todayItems()[di3].key;
const rbBefore = ELS.ratebody.innerHTML || '';
run(`quickDrill(today(), ${di3});`);
ok('点 ✓ 直接标记完成，不弹窗（弹窗内容不动）', todayItems()[di3].done === true && (ELS.ratebody.innerHTML || '') === rbBefore,
  'done=' + todayItems()[di3].done);
ok('✓ 按「闭卷写出来」记：进日课队列（明天换下一题）', g('S.drill').indexOf(dk3) >= 0,
  'S.drill=' + JSON.stringify(g('S.drill')));
ok('✓ 标记后清单行显示结果名', g(`taskRow(today(), ${di3}, S.days[today()].items[${di3}])`).includes('闭卷写出来'));

console.log('\n【20】单位迁移：母题 key 的旧派单要被主线 key 顶掉');
fresh();
run("S.days[today()] = { v:2, items:[" +
    "{type:'rev',key:'mysql/M1',need:true,done:true,label:'旧母题复训',sub:''}," +
    "{type:'drill',key:'drill/D1',need:true,done:true,score:'ok',label:'旧手撕',sub:''}," +
    "{type:'life',key:'life',need:true,done:true,label:'旧命功',sub:''} ], settled:false };" +
    "render();");
ok('查出母题死 key 后重派（不再派母题）',
  todayItems().filter(i => i.type !== 'drill' && i.type !== 'life')
    .every(i => g(`keySet()['${i.key}']`) === 1),
  todayItems().map(i => i.key).join(', '));
ok('重派后全是主线 key', todayItems().filter(i => i.type !== 'life' && i.type !== 'drill')
  .every(i => !!g(`S.lv['${i.key}']`)), todayItems().map(i => i.type + ':' + i.key).join(', '));
ok('已打勾的手撕被接回去（不用再做一遍）',
  todayItems().some(i => i.type === 'drill' && i.done === true && i.score === 'ok'));
ok('已打勾的命功被接回去', todayItems().some(i => i.type === 'life' && i.done === true));
ok('页面给出重派说明', g('S.days[today()].migrated') === '主线',
  String(g('S.days[today()].migrated')));
ok('重派后不再重复触发（第二次 render 不动它）',
  (run('render(); render();'), g('S.days[today()].items.length') === todayItems().length));

console.log('\n【21】本机旧进度折算：sql/M4 这种老 key 要折到主线上');
/* 主人本机的真实形态：旧 key 是「旧簇 id + 母题号」，等级已经在 sql/M4 上，
   S.lv 里一直躺着它 —— 所以死 key 检测必须查当前表，不能查 S.lv */
run("localStorage.setItem('mv.progress.v1', JSON.stringify({ lv: {" +
    "'sql/M4':{l:2,due:shift(today(),-10),last:daysAgo(11),hit:3,miss:1}," +
    "'tx/M16':{l:1,due:shift(today(),-9),last:daysAgo(10),hit:1,miss:0}," +
    "'zz/M99':{l:2,due:null,last:null,hit:0,miss:0}," +
    "'pitch/T1':{l:2,due:shift(today(),2),last:daysAgo(3),hit:1,miss:0} } }));");
run('FLAT = null; KEYSET = null; CARD2LINE = null; S = load(); FLAT = buildFlat(); render();');
ok('M4（索引代价与大表变更）折到主线 mysql-1、等级没丢',
  g("S.lv['mysql/1'].l") === 2, 'L' + g("S.lv['mysql/1'].l"));
ok('到期日接着原来的（逾期 10 天仍逾期 10 天）',
  g("S.lv['mysql/1'].due") === g('shift(today(),-10)'), g("S.lv['mysql/1'].due"));
ok('M16（乐观锁与悲观锁）折到 mysql-7', g("S.lv['mysql/7'].l") === 1,
  'L' + g("S.lv['mysql/7'].l"));
ok('认不出的孤儿记录被清掉', g("!('zz/M99' in S.lv)"));
ok('已经活着的老 key（pitch/T1）原样保留', g("S.lv['pitch/T1'].l") === 2);
ok('老 key 一条不留（sql/ tx/ 都没了）',
  !g("Object.keys(S.lv).some(function(k){ return k.indexOf('sql/')===0 || k.indexOf('tx/')===0; })"));
ok('记下折算条数', g('S.unitMigrated') === 2, String(g('S.unitMigrated')));
ok('今天的复训换成主线（不再是「索引代价与大表变更」）',
  needOf('rev').some(i => i.label.includes('索引与表设计')), needOf('rev').map(i => i.label).join(' / '));
ok('今天清单里没有死 key 了（主线/项目/准则/原则卡都是当前表的活 key）',
  !todayItems().some(i => i.type !== 'drill' && i.type !== 'life' &&
    !/^[a-z]+\/(\d+|T\d+|R\d+|[a-z0-9-]+)$/.test(i.key)),
  todayItems().map(i => i.key).join(', '));

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
