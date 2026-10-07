/* 渲染烟雾测试：捕获 render() 写进各容器的 HTML，检查标签闭合与关键区块是否都在。*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const { elStub } = require(path.join(ROOT, '_tests', '_dom_stub.js'));
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const code = html.match(/<script>\r?\n([\s\S]*?)<\/script>/)[1];

global.window = { addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => {} };
require(path.join(ROOT, '_data', 'clusters.js'));
require(path.join(ROOT, '_data', 'breaks.js'));

const dom = {};
function el(id) {
  if (!dom[id]) dom[id] = elStub(id);
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
ok('必做区按类型标签区分四条线（补派下拉里复训/主线新学/项目线/日课齐全）',
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
  "['mysql/1','mysql/2','mysql/3','redis/1','redis/3'].forEach(function(k){ S.lv[k].l = 2; });" +
  "S.lv['mysql/1'].miss = 2; S.lv['mysql/1'].due = shift(today(), -2);" +
  "BREAKS['topics/MySQL-母题-M1-为什么用B+树.html'] = " +
  "{ bp:'把回表和覆盖索引说混了', kw:['聚簇索引','回表'], fu:[{q:'什么时候不用回表？'}] };" +
  "delete S.days[today()]; render();", sandbox);
const need2 = el('needbox').innerHTML;
ok('出现抽检板块', need2.includes('开始抽检'), (need2.match(/开始抽检（\d+ 题/) || ['无'])[0]);
/* 池里有 5 条 L2：M1 同时到期要复训，被抽检排除 → 抽检只剩 4 条 */
/* 2026-09-25：必做区从五个板块改成一张平清单，类型前缀不再写进 label
   （渲染成 <span class="mv-tag t-exam">抽检</span>），计数改按标签 class */
ok('抽检条目出现在必做里（5 条池 − 1 条已在复训 = 4）', (need2.match(/mv-tag t-exam/g) || []).length === 4,
  (need2.match(/mv-tag t-exam/g) || []).length + ' 条');
const rows2 = need2.split('<div class="mv-cl-item');
const examRows = rows2.filter(r => r.includes('mv-tag t-exam'));
ok('抽检条目今日不可单独点击（必须走整轮）',
  examRows.length === 4 && examRows.every(r => !r.includes('onclick="rate(')), examRows.length + ' 条');
ok('抽检说明含「连答不回头」', need2.includes('连答不回头'));
ok('M1 同时在复训队列里（due 到期）', need2.includes('逾期 2 天'), '');
ok('复训卡面摊开上次断点', need2.includes('把回表和覆盖索引说混了'));
ok('同一条主线不会既进复训又进抽检',
  (need2.match(/索引与表设计/g) || []).length === 1, (need2.match(/索引与表设计/g) || []).length + ' 次');
ok('标签平衡（含抽检 + 项目线）', !balance(need2), balance(need2) || '');

console.log('\n【断点闭环：掉档时提示写回母题卡】');
vm.runInContext(
  "var i = S.days[today()].items.findIndex(function(x){ return x.type==='rev' && !x.done; });" +
  "rate(today(), i); doRate('miss');", sandbox);
const rb = el('ratebody').innerHTML;
ok('自评弹窗没有被关掉（停在提示上）', el('rate').hidden === false);
ok('提示把断点写回母题卡', rb.includes('本次断点'), rb.slice(0, 60).replace(/<[^>]+>/g, ''));
ok('掉档后等级降到 L1', g("S.lv['mysql/1'].l") === 1, 'L' + g("S.lv['mysql/1'].l"));
ok('提示里带出上次记的断点', rb.includes('把回表和覆盖索引说混了'));

console.log('\n【限时与答案 fold】');
vm.runInContext(
  "S = load();" +
  "['mysql/1','mysql/2','mysql/3','redis/1','redis/3'].forEach(function(k){ S.lv[k].l = 2; });" +
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
  "  {type:'new', key:'mysql/1', need:true, done:true,  label:'新主线：索引与表设计', sub:'x', score:'hit'}," +
  "  {type:'rev', key:'mysql/2', need:true, done:false, label:'复训：联合索引', sub:'y'}," +
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

console.log('\n【完整答案：不是只有一句话结论和骨架】');
/* 2026-09-26：主线页原来每题只给「骨架 + 一句话结论」，没有能照着讲的答案。
   现在每张母题卡两段：口述稿（一段话）+ 分层要点，都折叠在主线页上。 */
const MOD = path.join(ROOT, 'modules');
const mysql = fs.readdirSync(MOD).filter(f => f.startsWith('MySQL-'));
let panels = 0, cards = 0;
mysql.forEach(f => {
  const h = fs.readFileSync(path.join(MOD, f), 'utf8');
  panels += (h.match(/完整回答 · 口述稿/g) || []).length;
  cards += (h.match(/class="mv-mt-name"/g) || []).length / 2;   // 骨架区 + 母题区各一次
});
ok('MySQL 七条主线页都渲染出完整答案块', panels === 80,
  panels + ' 块（17 母题 ×（骨架区 + 母题区）+ 46 张翻转卡下半段）');
ok('母题数与答案块数对得上', cards === 17, cards + ' 张母题');
ok('字数标注是构建时实测，不写死 60 秒',
  /实测 \d+ 字 · 按 4 字\/秒折算约 \d+ 秒/.test(
    fs.readFileSync(path.join(MOD, 'MySQL-01-索引与表设计.html'), 'utf8')));
ok('分层要点也上了页面（追问深挖用）',
  fs.readFileSync(path.join(MOD, 'MySQL-01-索引与表设计.html'), 'utf8').includes('分层要点'));

/* 母题层已全库补齐（2026-09-28：87/87），断言反过来：每个模块都要有完整回答块 */
const ALLMODS = ['MySQL', 'LLM与上下文', 'Agent运行时与工具', 'Redis', 'RAG与检索', '网络基础',
  '评测观测与治理', '消息队列', '并发与锁', 'Linux与部署', 'PostgreSQL', '操作系统', '数据存储选型'];
/* 母题完整回答挂在主线页（骨架区 + 母题区），概览页只在有总纲题时才带 */
const noAns = ALLMODS.filter(m => !fs.readdirSync(MOD)
  .filter(f => f.startsWith(m + '-'))
  .some(f => fs.readFileSync(path.join(MOD, f), 'utf8').includes('完整回答 · 口述稿')));
ok('13 个模块的主线页都挂上了母题完整回答', noAns.length === 0, noAns.join('/') || '全部有');

console.log('\n【本主线的题：背面是题级答案，不是骨架】');
/* 2026-09-26：题单 352 道题挂 96 张母题（97% 的题与同母题其它题共用一段话），
   原来背面是 q_answer() 凑的「结论 + 展开：骨架」——答非所问。现在背面主体是
   md 第 8 节的题级答案，下半段再挂所属母题的完整回答 + 单卡入口。 */
const MYSQL_DIR = path.join(ROOT, 'modules');
const lineFiles = fs.readdirSync(MYSQL_DIR).filter(f => /^MySQL-\d/.test(f));
let nMore = 0, nCard = 0, allBack = '';
lineFiles.forEach(f => {
  const h = fs.readFileSync(path.join(MYSQL_DIR, f), 'utf8');
  nCard += (h.match(/<flip-card /g) || []).length;
  nMore += (h.match(/mv-fc-more/g) || []).length;
  allBack += h;
});
ok('MySQL 七条主线页共 46 张翻转卡', nCard === 46, nCard + ' 张');
ok('每张卡都挂了母题完整回答 + 单卡入口（下半段）', nMore === 46, nMore + ' 段');
ok('背面不再是「展开：骨架」那套',
  !allBack.includes('展开：约束') && !allBack.includes('>展开：'),
  (allBack.match(/展开：[^"<]{0,40}/) || ['无'])[0]);
ok('题级答案真的回答了这道题（Memory / Archive / zlib 出现在 Q3 的答案里）',
  allBack.includes('ARCHIVE') && allBack.includes('MEMORY') && allBack.includes('zlib'));
ok('提问「三范式」的题拿到了范式答案（不再复用 InnoDB 那段）',
  allBack.includes('2NF 非主键列完全依赖主键'));
ok('下半段带单卡入口', allBack.includes('打开单卡 M1 →'));
/* 一档十模块 253 题已全写（2026-09-26 夜）；二档三模块还没写，
   那里必须用「用母题结论顶上」标明，不能假装是答案。 */
const z2 = fs.readdirSync(path.join(MOD)).filter(f => /^(PostgreSQL|操作系统|数据存储选型)-\d/.test(f));
ok('二档模块还没写题级答案时，背面标明「用母题结论顶上」',
  z2.length > 0 && z2.some(f =>
    fs.readFileSync(path.join(MOD, f), 'utf8').includes('还没写题级答案')), z2.length + ' 页');
ok('一档模块（Redis 等）已经没有这个标注了',
  !fs.readdirSync(path.join(MOD)).filter(f => /^Redis-\d/.test(f)).some(f =>
    fs.readFileSync(path.join(MOD, f), 'utf8').includes('还没写题级答案')));

console.log('\n【总纲题：归属主线不是行号的题不能消失】');
/* 2026-09-27 审查发现：md 题单里「归属主线」写的是「全 / 前提 / ——」的题，
   _by_line 按行号分组时归不到任何主线页 —— 6 道总纲题（如何评测一个 Agent、
   设计一个生产级 RAG、MQ 三大作用…）一直没露面。现在它们落到模块概览页。 */
const Z1 = ['MySQL', 'LLM与上下文', 'Agent运行时与工具', 'Redis', 'RAG与检索',
  '网络基础', '评测观测与治理', '消息队列', '并发与锁', 'Linux与部署'];
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const idRe = new RegExp('card-id="(' + Z1.map(reEsc).join('|') + ')-q\\d+"', 'g');
const qids = new Set();
fs.readdirSync(MOD).forEach(f => {
  const h = fs.readFileSync(path.join(MOD, f), 'utf8');
  (h.match(idRe) || []).forEach(x => qids.add(x.slice(9, -1)));
});
ok('一档十模块 253 道题全部都能翻到', qids.size === 253, qids.size + ' 道');
ok('原先消失的总纲题已露出（Redis 分布式锁 / 如何评测一个 Agent / 设计生产级 RAG）',
  qids.has('Redis-q19') && qids.has('评测观测与治理-q1') && qids.has('RAG与检索-q1'), '');
ok('总纲题带「不属于某一条主线」的说明',
  fs.readFileSync(path.join(MOD, '评测观测与治理.html'), 'utf8')
    .includes('本模块的题 · 总纲'));

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
