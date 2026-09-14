/* 渲染烟雾测试：捕获 render() 写进各容器的 HTML，检查标签闭合与关键区块是否都在。*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'progress.html'), 'utf8');
const code = html.match(/<script>\r?\n([\s\S]*?)<\/script>/)[1];

global.window = {};
require(path.join(ROOT, '_data', 'clusters.js'));
require(path.join(ROOT, '_data', 'breaks.js'));

const dom = {};
function el(id) {
  if (!dom[id]) dom[id] = { id, innerHTML: '', textContent: '', hidden: true, value: '' };
  return dom[id];
}
const sandbox = {
  window: global.window,
  localStorage: { getItem: () => null, setItem: () => {} },
  document: { getElementById: el, addEventListener: () => {}, querySelector: () => null },
  alert: () => {}, confirm: () => true, console,
  Blob: function () {}, URL: { createObjectURL: () => '' },
  Date, Math, JSON, Object, Array, String, Number, Set,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

let fails = 0;
const ok = (l, c, x) => { console.log((c ? '  ✅ ' : '  ❌ ') + l + (x ? '  → ' + x : '')); if (!c) fails++; };
const g = (expr) => vm.runInContext(expr, sandbox);

/* 标签平衡检查（只认我们生成的简单标签，忽略自闭合与 void） */
const VOID = new Set(['br', 'hr', 'img', 'input', 'meta', 'link']);
function balance(htmlStr) {
  const stack = [];
  const re = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(\/?)>/g;
  let m;
  while ((m = re.exec(htmlStr))) {
    const [, close, tag, self] = m;
    if (self === '/' || (VOID.has(tag.toLowerCase()) && !close)) continue;
    if (close) {
      if (stack.pop() !== tag) return '闭合错位：</' + tag + '>';
    } else stack.push(tag);
  }
  return stack.length ? '未闭合：' + stack.join(',') : null;
}

const ids = ['metrics', 'needbox', 'extrabox', 'clusters', 'drillbox', 'recent', 'heat', 'streakv', 'extralist', 'subline', 'needsum', 'recentsum'];
console.log('\n【渲染烟雾测试】');
for (const id of ids) {
  const h = el(id).innerHTML || el(id).textContent;
  ok('#' + id + ' 有内容', !!h, h ? h.length + ' 字符' : '空');
  if (el(id).innerHTML) {
    const b = balance(el(id).innerHTML);
    ok('#' + id + ' 标签平衡', !b, b || '');
  }
}

console.log('\n【关键区块】');
const need = el('needbox').innerHTML;
ok('必做区含「复训 / 主线新学 / 项目线 / 日课」四个板块',
  need.includes('复训') && need.includes('主线新学') && need.includes('项目线') && need.includes('日课'));
ok('项目线板块列出三个项目', ['EnergyOps', '数驭穹图', 'RuleArena'].every(n => need.includes(n)));
ok('项目线板块有骨架/决策链条目', need.includes('90 秒骨架') && need.includes('决策链'));
ok('无 L2 母题时不出现抽检板块', !need.includes('开始抽检'));
ok('加餐区渲染', el('extrabox').innerHTML.includes('mv-cl') || el('extrabox').innerHTML.includes('mv-bd'));
/* 期望值从数据推导，不写死——2026-09-13 加 PostgreSQL 簇时 10/55 这两个硬编码值
   立刻过期（55+19=74），测试反而成了噪声源。 */
const wantClusters = (global.window.MARVIS_CLUSTERS || []).length;
const wantChips = (global.window.MARVIS_CLUSTERS || [])
  .reduce((n, c) => n + ((c.topics || []).length), 0);
ok('能力簇 ' + wantClusters + ' 个折叠块',
  (el('clusters').innerHTML.match(/mv-pg-c"/g) || []).length === wantClusters,
  (el('clusters').innerHTML.match(/mv-pg-c"/g) || []).length + ' 个');
ok('能力簇含全部 ' + wantChips + ' 条母题 chip',
  (el('clusters').innerHTML.match(/mv-pg-chip/g) || []).length === wantChips,
  (el('clusters').innerHTML.match(/mv-pg-chip/g) || []).length + ' 条');
ok('近 7 天区（无历史时给空态）', el('recent').innerHTML.length > 0);
ok('热力图 35 格', (el('heat').innerHTML.match(/mv-hc/g) || []).length === 35,
  (el('heat').innerHTML.match(/mv-hc/g) || []).length + ' 格');
ok('副标题已填', el('subline').textContent.includes('今天'), el('subline').textContent);

/* 模拟学了一阵：验证抽检板块 + 断点回流渲染 */
console.log('\n【抽检板块 + 断点回流】');
vm.runInContext(
  "['sql/M1','sql/M2','sql/M3','tx/M8','tx/M9'].forEach(function(k){ S.lv[k].l = 2; });" +
  "S.lv['sql/M1'].miss = 2; S.lv['sql/M1'].due = shift(today(), -2);" +
  "BREAKS['topics/MySQL-母题-M1-为什么用B+树.html'] = " +
  "{ bp:'把回表和覆盖索引说混了', kw:['聚簇索引','回表'], fu:[{q:'什么时候不用回表？'}] };" +
  "delete S.days[today()]; render();", sandbox);
const need2 = el('needbox').innerHTML;
ok('出现抽检板块', need2.includes('开始抽检'), (need2.match(/开始抽检（\d+ 题/) || ['无'])[0]);
/* 池里有 5 条 L2：M1 同时到期要复训，被抽检排除 → 抽检只剩 4 条 */
ok('抽检条目出现在必做里（5 条池 − 1 条已在复训 = 4）', (need2.match(/抽检：/g) || []).length === 4,
  (need2.match(/抽检：/g) || []).length + ' 条');
const rows2 = need2.split('<div class="mv-cl-item');
const examRows = rows2.filter(r => r.includes('抽检：'));
ok('抽检条目今日不可单独点击（必须走整轮）',
  examRows.length === 4 && examRows.every(r => !r.includes('onclick="rate(')), examRows.length + ' 条');
ok('抽检说明含「连答不回头」', need2.includes('连答不回头'));
ok('M1 同时在复训队列里（due 到期）', need2.includes('逾期 2 天'), '');
ok('复训卡面摊开上次断点', need2.includes('把回表和覆盖索引说混了'));
ok('同一条母题不会既进复训又进抽检',
  (need2.match(/为什么用 B\+ 树/g) || []).length === 1, (need2.match(/为什么用 B\+ 树/g) || []).length + ' 次');
ok('标签平衡（含抽检 + 项目线）', !balance(need2), balance(need2) || '');

console.log('\n【断点闭环：掉档时提示写回母题卡】');
vm.runInContext(
  "var i = S.days[today()].items.findIndex(function(x){ return x.type==='rev' && !x.done; });" +
  "rate(today(), i); doRate('miss');", sandbox);
const rb = el('ratebody').innerHTML;
ok('自评弹窗没有被关掉（停在提示上）', el('rate').hidden === false);
ok('提示把断点写回母题卡', rb.includes('本次断点'), rb.slice(0, 60).replace(/<[^>]+>/g, ''));
ok('掉档后等级降到 L1', g("S.lv['sql/M1'].l") === 1, 'L' + g("S.lv['sql/M1'].l"));
ok('提示里带出上次记的断点', rb.includes('把回表和覆盖索引说混了'));

console.log('\n【限时与答案 fold】');
vm.runInContext(
  "S = load();" +
  "['sql/M1','sql/M2','sql/M3','tx/M8','tx/M9'].forEach(function(k){ S.lv[k].l = 2; });" +
  "BREAKS['topics/MySQL-母题-M1-为什么用B+树.html'] = { bp:'把回表和覆盖索引说混了', " +
  "  con:'聚簇索引存整行、二级索引存主键', kw:['聚簇索引','回表'], fu:[{q:'什么时候不用回表？'}] };" +
  "delete S.days[today()]; render();", sandbox);

const projIdx = g("S.days[today()].items.findIndex(function(x){return x.type==='proj';})");
ok('当天有项目线条目', projIdx >= 0);
vm.runInContext("rate(today(), " + projIdx + ");", sandbox);
ok('项目线用 90 秒限时（不是抽检的 60）', el('ratebody').innerHTML.includes('seconds="90"'),
  (el('ratebody').innerHTML.match(/seconds="\d+"/) || ['无'])[0]);
vm.runInContext("closeRate();", sandbox);

const examIdx = g("S.days[today()].items.findIndex(function(x){return x.type==='exam';})");
ok('当天有抽检条目', examIdx >= 0, examIdx + '');
vm.runInContext("rate(today(), " + examIdx + ");", sandbox);
ok('抽检用 60 秒限时', el('ratebody').innerHTML.includes('seconds="60"'),
  (el('ratebody').innerHTML.match(/seconds="\d+"/) || ['无'])[0]);
ok('答案 fold 里有「一句话结论」', el('ratebody').innerHTML.includes('一句话结论'));
ok('答案 fold 默认折叠', /<details(?![^>]*\sopen)/.test(el('ratebody').innerHTML));
ok('卡面摊开上次断点', el('ratebody').innerHTML.includes('把回表和覆盖索引说混了'));
vm.runInContext("closeRate();", sandbox);

/* 新题必须闭卷：结论就是答案，不能摆在弹窗里 */
const newIdx = g("S.days[today()].items.findIndex(function(x){return x.type==='new';})");
if (newIdx >= 0) {
  vm.runInContext("rate(today(), " + newIdx + ");", sandbox);
  const nh = el('ratebody').innerHTML;
  ok('新题弹窗不给一句话结论', !nh.includes('一句话结论'));
  ok('新题弹窗不给恢复关键词 fold', !nh.includes('说完再点开'));
  ok('新题弹窗保留打开材料入口', nh.includes('打开材料'));
} else ok('当天有新题可测', false, '没有新题条目');
vm.runInContext("closeRate();", sandbox);

/* 模拟有历史：验证近 7 天板块 */
console.log('\n【近 7 天：有历史时】');
vm.runInContext(
  "S.days[daysAgo(1)] = { items: [" +
  "  {type:'new', key:'sql/M1', need:true, done:true,  label:'新母题：为什么用 B+ 树', sub:'x', score:'hit'}," +
  "  {type:'rev', key:'sql/M2', need:true, done:false, label:'复训：联合索引', sub:'y'}," +
  "  {type:'new', key:'llm/C1', need:false, done:false, label:'加餐条目', sub:'z'} ], settled:true };" +
  "render();", sandbox);
const recent = el('recent').innerHTML;
ok('近 7 天展开出一组', (recent.match(/mv-pg-c"/g) || []).length === 1, (recent.match(/mv-pg-c"/g) || []).length + ' 组');
ok('显示「昨日」', recent.includes('昨日'));
ok('显示必做完成数 1/2', recent.includes('1/2 必做'), recent.match(/\d+\/\d+ 必做/));
ok('昨日 3 条全列出', (recent.match(/mv-cl-item/g) || []).length === 3, (recent.match(/mv-cl-item/g) || []).length + ' 条');
ok('已评条目只读（无 onclick）', !/mv-cl-item on"[^>]*onclick/.test(recent));
ok('未评条目可点开补评', /onclick="rate\('20\d\d-\d\d-\d\d',\d\)"/.test(recent), '');
ok('近 7 天标签统计待补评', el('recentsum').textContent.includes('待补评 1'), el('recentsum').textContent);
ok('欠账被实时算出', el('subline').textContent.includes('累计欠账 1 条'), el('subline').textContent);
ok('昨日加餐条目不计欠账（欠 1 而不是 2）', vm.runInContext('debtStats().debt', sandbox) === 1,
  vm.runInContext('debtStats().debt', sandbox) + ' 条');

console.log('\n【近 7 天：标签平衡】');
const b2 = balance(recent);
ok('近 7 天区块标签平衡', !b2, b2 || '');

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
