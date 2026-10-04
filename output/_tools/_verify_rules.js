/* 行事准则（rules）数据校验 —— 真执行
   用法：node output/_verify_rules.js
   校验：① rules.js 与 clusters.js 的 MARVIS_RULE_CLUSTER id 双向对齐
        ② 每条派单 href 指向 rules.html 的真实锚点（锚点 id = 'r-' + id）
        ③ src 指向的正本 md 真实存在
        ④ 未激活状态：MARVIS_CLUSTERS 里不应该有 rule 簇（防手滑提前接入）
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const SITE = path.join(ROOT, 'site');
let fail = 0, pass = 0;
function ok(c, m) { if (c) { pass++; console.log('  ✓ ' + m); } else { fail++; console.log('  ✗ ' + m); } }

const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(SITE, '_data', 'clusters.js'), 'utf8'), ctx);
vm.runInContext(fs.readFileSync(path.join(SITE, '_data', 'rules.js'), 'utf8'), ctx);

const rules = ctx.window.MARVIS_RULES || [];
const cluster = ctx.window.MARVIS_RULE_CLUSTER;
const clusters = ctx.window.MARVIS_CLUSTERS || [];
const page = fs.readFileSync(path.join(SITE, 'rules.html'), 'utf8');

console.log('【数据】');
ok(rules.length >= 8, 'rules.js 题面 ' + rules.length + ' 条');
ok(!!cluster, 'clusters.js 里有 MARVIS_RULE_CLUSTER');
ok(cluster && cluster.topics.length === rules.length,
  '两处条数一致（' + (cluster ? cluster.topics.length : 0) + ' vs ' + rules.length + '）');

console.log('\n【对齐】题面 ↔ 派单条目 id 双向');
const aIds = (cluster ? cluster.topics : []).map(function (t) { return t.id; });
const bIds = rules.map(function (r) { return r.id; });
const missA = bIds.filter(function (i) { return aIds.indexOf(i) < 0; });
const missB = aIds.filter(function (i) { return bIds.indexOf(i) < 0; });
ok(missA.length === 0 && missB.length === 0,
  'id 完全对应' + (missA.length || missB.length ? '（缺 ' + missA + ' / ' + missB + '）' : ''));

console.log('\n【接线】派单 href 指向 rules.html 真实锚点');
const missingAnchor = [];
(cluster ? cluster.topics : []).forEach(function (t) {
  const parts = t.href.split('#');
  if (parts[0] !== 'rules.html') { missingAnchor.push(t.id + ' 目标不是 rules.html'); return; }
  // 页面里锚点是运行时生成的（id = 'r-' + id），所以校验渲染模板里有 'r-' + r.id
  if (page.indexOf("d.id = 'r-' + r.id") < 0 && page.indexOf('r-' + parts[1]) < 0) {
    missingAnchor.push(t.id + ' 锚点模板缺失');
  }
});
ok(missingAnchor.length === 0, '全部锚点可生成' + (missingAnchor.length ? '（' + missingAnchor.join('; ') + '）' : ''));

console.log('\n【接线】正本 md 存在');
const badSrc = [];
(cluster ? cluster.topics : []).forEach(function (t) {
  if (!t.src) { badSrc.push(t.id + ' 缺 src'); return; }
  if (!fs.existsSync(path.join(ROOT, t.src))) badSrc.push(t.id + ' → ' + t.src);
});
ok(badSrc.length === 0, '原标题全部存在（' + ((cluster ? cluster.topics : [])[0] || {}).src + ' 等）' +
  (badSrc.length ? '（' + badSrc.join('; ') + '）' : ''));

console.log('\n【未激活】不该提前混进派单池');
const leaked = clusters.filter(function (c) { return c.id === 'rule' || c.zone === '准则'; });
ok(leaked.length === 0, 'MARVIS_CLUSTERS 里没有 rule 簇（现有档位轮转不受影响）');
ok(clusters.length === 14, '簇数仍为 14（13 模块 + pitch），实际 ' + clusters.length);

console.log('\n【页面】rules.html 结构');
ok(page.indexOf('_data/rules.js') >= 0, '引用 rules.js');
ok(page.indexOf('MARVIS_RULES') >= 0, '读取 MARVIS_RULES');
ok(page.indexOf('_components/marvis.css') >= 0, '复用时站内样式');
const scripts = page.match(/<script>([\s\S]*?)<\/script>/g) || [];
scripts.forEach(function (s, i) {
  const body = s.replace(/^<script>/, '').replace(/<\/script>$/, '');
  try { new vm.Script(body, { filename: 'rules.html#' + (i + 1) }); pass++; console.log('  ✓ 内联脚本 ' + (i + 1) + ' 语法通过'); }
  catch (e) { fail++; console.log('  ✗ 内联脚本 ' + (i + 1) + ' 语法错误：' + e.message.slice(0, 160)); }
});

console.log('\n—— 通过 ' + pass + ' 项，失败 ' + fail + ' 项 ——');
process.exit(fail ? 1 : 0);
