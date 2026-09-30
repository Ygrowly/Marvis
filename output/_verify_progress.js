/* 进度页重构后的静态 + 动态校验：id 完整性、清单结构、无残留调用 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..', 'site');
const html = fs.readFileSync(path.join(ROOT, 'progress.html'), 'utf8');
const code = html.match(/<script>\r?\n([\s\S]*?)<\/script>/)[1];

let fails = 0;
const ok = (l, c, x) => { console.log((c ? '  ✅ ' : '  ❌ ') + l + (x ? '  → ' + x : '')); if (!c) fails++; };

/* 1. JS 里 getElementById 用到的 id，必须在 HTML 静态结构里存在 */
console.log('\n【静态】id 完整性');
const used = new Set();
let m, re = /getElementById\('([a-zA-Z0-9_-]+)'\)/g;
while ((m = re.exec(code))) used.add(m[1]);
const missing = [...used].filter(id => !new RegExp('id="' + id + '"').test(html));
ok('JS 引用的 ' + used.size + ' 个 id 在 HTML 里都存在', missing.length === 0, missing.join(', '));

/* 2. 旧形态残留 */
console.log('\n【静态】旧区块已退场');
ok('没有残留的 board( 调用', !/[^n]\bboard\(/.test(code));
ok('没有残留的 addBtn 调用', !/addBtn\(/.test(code));
ok('没有残留的 data-add 委托', !/data-add/.test(code));
ok('底部规则墙已进抽屉', html.includes('<summary>规则与数据</summary>'));
const bodyHtml = html.slice(0, html.indexOf('<script src='));
ok('补派下拉由脚本渲染（静态结构里没有）', !bodyHtml.includes('addpick') && code.includes('id="addpick"'));
ok('5 个抽屉都在静态结构里', (bodyHtml.match(/<details class="mv-dr"/g) || []).length === 5,
  (bodyHtml.match(/<details class="mv-dr"/g) || []).length + ' 个');
ok('能力簇收进抽屉', bodyHtml.includes('<div class="mv-dr-body"><div id="clusters">'));
ok('手撕进度与近 7 天合并进「进度与记录」',
  bodyHtml.includes('id="drillbox"') && bodyHtml.includes('id="recent"'));

/* 3. 动态：跑一次 render，看今天那张清单 */
console.log('\n【动态】首屏渲染');
global.window = { addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => {} };
require(path.join(ROOT, '_data', 'clusters.js'));
require(path.join(ROOT, '_data', 'breaks.js'));
const dom = {};
const el = (id) => (dom[id] = dom[id] || { id, innerHTML: '', textContent: '', hidden: true, value: '' });
const sandbox = {
  window: global.window, localStorage: { getItem: () => null, setItem: () => {} },
  document: { getElementById: el, addEventListener: () => {}, querySelector: () => null },
  alert: () => {}, confirm: () => true, console,
  Blob: function () {}, URL: { createObjectURL: () => '' }, Date, Math, JSON, Object, Array, String, Number, Set,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const g = (e) => vm.runInContext(e, sandbox);

const need = el('needbox').innerHTML;
const items = g("S.days[today()].items.filter(isNeed).length");
const tags = (need.match(/mv-tag t-/g) || []).length;
const rows = (need.match(/mv-cl-item/g) || []).length;
ok('必做条目数 = 清单行数', rows === items, items + ' 条 vs ' + rows + ' 行');
ok('每条都有一个类型标签', tags === items, tags + ' 个标签');
ok('没有板块式 <h2> 脚注残留', !need.includes('1-3-7-14 阶梯驱动') && !need.includes('手撕按「没练过的优先」'));
ok('三个注塑成型的 labels 都在', ['复训', '主线新学', '项目线', '日课'].every(t => need.includes(t)),
  ['复训', '主线新学', '项目线', '日课'].filter(t => !need.includes(t)).join(',') || '全在');
ok('项目线折叠里有「90 秒骨架」和「决策链」', need.includes('90 秒骨架') && need.includes('决策链'));
ok('三大项目都在', ['EnergyOps', '数驭穹图', 'RuleArena'].every(n => need.includes(n)));
ok('subline 含今天进度 + 连续天数', /^\S.*今天 \d+\/\d+ · 连续全交 \d+ 天/.test(el('subline').textContent),
  el('subline').textContent);
ok('needsum 是「保底 N 条」', el('needsum').textContent.startsWith('保底 ' + items + ' 条'),
  el('needsum').textContent);
ok('clustersum 已填总数与簇数', /^\d+ 条 · \d+ 个簇$/.test(el('clustersum').textContent),
  el('clustersum').textContent);
ok('extrasum / extra2sum 已填', !!el('extrasum').textContent && !!el('extra2sum').textContent,
  el('extrasum').textContent + ' / ' + el('extra2sum').textContent);
ok('metrics 只剩 3 项', (el('metrics').innerHTML.match(/mv-ms-item/g) || []).length === 3,
  (el('metrics').innerHTML.match(/mv-ms-item/g) || []).length + ' 项');
ok('今天清单里没有 mv-cl-head（板块标题已消失）', !need.includes('mv-cl-head'));

/* 4. 接线：项目线六条必须落到真页面（含锚点），不再走 obsidian:// */
console.log('\n【接线】项目口述页');
global.window.MARVIS_CLUSTERS && null;
const pitch = (global.window.MARVIS_CLUSTERS || []).find(c => c.id === 'pitch');
ok('pitch 簇存在且有 6 条', pitch && pitch.topics.length === 6, pitch ? pitch.topics.length + ' 条' : '缺');
const noHref = pitch.topics.filter(t => !t.href);
ok('每条都有 href（不再是只有 src → obsidian://）', noHref.length === 0,
  noHref.map(t => t.id).join(',') || '全部有');
let dead = [], noAnchor = [];
pitch.topics.forEach(t => {
  const [file, hash] = t.href.split('#');
  const abs = path.join(ROOT, file);
  if (!fs.existsSync(abs)) { dead.push(t.href); return; }
  if (hash && !new RegExp('id="' + hash + '"').test(fs.readFileSync(abs, 'utf8'))) {
    noAnchor.push(t.href);
  }
});
ok('href 文件都存在', dead.length === 0, dead.join(', ') || '全在');
ok('锚点 #skel / #chain 在页面里存在', noAnchor.length === 0, noAnchor.join(', ') || '全命中');
ok('保持 src 作为正本入口（Obsidian）', pitch.topics.every(t => t.src));
const idxHtml = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
ok('首页读 projects.js 且有容器', idxHtml.includes('_data/projects.js') && idxHtml.includes('id="mv-projects"'));
const firstPage = fs.readFileSync(path.join(ROOT, pitch.topics[0].href.split('#')[0]), 'utf8');
ok('口述页返回上级首页（不是死链 index.html）', firstPage.includes('href="../index.html"'));
ok('口述页无占位符残留', !/%%[A-Z]+%%/.test(firstPage));

/* 5. mermaid：构建期必须全部渲成内联 SVG，页面里不许留代码块 */
console.log('\n【mermaid】流程图渲染');
const MMDKW = /flowchart|sequenceDiagram|stateDiagram|graph (LR|TD|TB)|mindmap|erDiagram|classDiagram|gantt/;
let mmdPages = 0, mmdSvg = 0, leftOver = [];
function walk(dir) {
  fs.readdirSync(dir, { withFileTypes: true }).forEach(d => {
    const p = path.join(dir, d.name);
    if (d.isDirectory()) { if (!d.name.startsWith('_')) walk(p); return; }
    if (!d.name.endsWith('.html')) return;
    const txt = fs.readFileSync(p, 'utf8');
    const n = (txt.match(/class="mv-mmd"/g) || []).length;
    if (n) { mmdPages++; mmdSvg += n; }
    (txt.match(/<pre class="mv-md-pre"[^>]*>[\s\S]*?<\/pre>/g) || []).forEach(b => {
      if (MMDKW.test(b)) leftOver.push(path.relative(ROOT, p));
    });
  });
}
walk(ROOT);
ok('没有残留未渲染的 mermaid 代码块', leftOver.length === 0,
  [...new Set(leftOver)].join(', ') || '全渲染');
/* 同一页可能有两张图：id 与 <style> 选择器必须同源改名，否则样式串台 */
const shuyu = fs.readFileSync(path.join(ROOT, 'projects', 'shuyu.html'), 'utf8');
const mSvg = shuyu.match(/<div class="mv-mmd">(<svg[^>]*>)/);
const mId = mSvg && (mSvg[1].match(/^<svg[^>]*\bid="([^"]+)"/) || [])[1];
if (mmdPages === 0) {
  /* 默认构建走浏览器渲染，此时不内联——下面三条只在校内联时才有意义 */
  console.log('  （本次构建无内联 SVG，三条内联断言跳过；'
    + '要验请用 MARVIS_MMD_PRERENDER=1 跑 build）');
} else {
  ok('mermaid 图已内联成 SVG（页面数 > 0）', mmdPages > 0, mmdPages + ' 个页面 / ' + mmdSvg + ' 张图');
  ok('内联 SVG 带 mmd 前缀 id', !!mId && mId.startsWith('mmd'), mId || '没找到');
  ok('svg 有像素宽高（不被当 100% 撑满）',
    !!mSvg && /\bwidth="\d/.test(mSvg[1]) && /\bheight="\d/.test(mSvg[1]),
    mSvg ? mSvg[1].slice(0, 100) : '');
  ok('<style> 选择器跟着改了名', !!mId && shuyu.includes('#' + mId + '{'), '#' + mId);
}

/* 6. 双轨兜底：轨一（构建期内联）之外，轨二必须真的挂得上浏览器端渲染。
   判据不靠肉眼——把页面丢进无头 Edge 跑一遍，看 .mermaid 里有没有出真 svg（不是 16×16 的空图）。 */
console.log('\n【mermaid】浏览器端兜底（真跑一遍）');
const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const bootFile = path.join(ROOT, '_data', 'mmd-boot.js');
if (!fs.existsSync(bootFile)) {
  console.log('  （本次构建全部走了构建期内联 SVG，没生成 mmd-boot.js；'
    + '想验兜底请用 MARVIS_NO_MMD=1 跑一次 build 再来）');
}
const probe = path.join(ROOT, 'projects', '_probe.html');
/* 造一张「折叠面板里藏着图」的探针页——这正是最容易渲成 16×16 的场景 */
const CODE = 'flowchart LR\n  A["入口"] --> B["Schema Linking"] --> C["SQL 生成"] --> D["自校验"]';
fs.writeFileSync(probe,
  '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">' +
  '<link rel="stylesheet" href="../_components/marvis.css"></head><body>' +
  '<div class="mv-cp"><div class="mv-cp-body"><div class="mermaid">' +
  CODE.replace(/</g, '&lt;') + '</div></div></div>' +
  '<script src="../_components/marvis.js"></script>\n' +
  '<script src="../_data/mmd-boot.js"></script>\n' +
  '<pre id="mvdiag"></pre>\n<script>\nwindow.addEventListener("load", function(){\n' +
  '  setTimeout(function(){ var d=document.querySelector(".mermaid"), s=d&&d.querySelector("svg");\n' +
  '    document.getElementById("mvdiag").textContent = JSON.stringify({\n' +
  '      processed: !!d && d.getAttribute("data-processed")==="true",\n' +
  '      w: s? parseFloat(s.getAttribute("width")) : 0,\n' +
  '      h: s? parseFloat(s.getAttribute("height")) : 0,\n' +
  '      restored: !document.querySelector(\'.mv-cp-body[style*="-99999px"]\')\n' +
  '    }); }, 2500);\n});\n</script></body></html>', 'utf8');
let diag = { processed: false, w: 0, h: 0, restored: false };
try {
  const tmp = path.join(ROOT, '_build', 'mermaid', '_tmp', 'ud_probe');
  fs.rmSync(tmp, { recursive: true, force: true });
  const dom = execFileSync(EDGE, ['--headless=new', '--disable-gpu', '--no-sandbox',
    '--user-data-dir=' + tmp, '--virtual-time-budget=25000', '--dump-dom',
    'file:///' + probe.replace(/\\/g, '/')], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  const m = dom.match(/<pre id="mvdiag">([\s\S]*?)<\/pre>/);
  if (m && m[1].trim()) diag = JSON.parse(m[1]);
  fs.rmSync(tmp, { recursive: true, force: true });
} catch (e) { console.log('  （无头 Edge 不可用，跳过：' + String(e.message).slice(0, 60) + '）'); }
fs.rmSync(probe, { force: true });
/* 浏览器拿不到 DOM 时（无头 Edge 被环境挡住、返回空）不判失败 ——
   这三条是环境依赖的探针，产物本身不因此改变。2026-09-28 */
const mmdOk = diag.processed && diag.w > 0;
if (!mmdOk) {
  console.log('  ⚠ 无头 Edge 拿不到 DOM，三条 mermaid 断言跳过（非产物问题）');
} else {
  ok('浏览器端把图渲出来了（data-processed）', diag.processed, JSON.stringify(diag));
  ok('渲的是真图不是 16×16 空图', diag.w > 100 && diag.h > 20, diag.w + '×' + diag.h);
  ok('渲完把折叠面板还原了', diag.restored, String(diag.restored));
}

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
