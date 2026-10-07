/* brain.html 静态回归测试：三个真实 bug 的教训固化（2026-10-04 批 6）+ 一页总览接线 + 数据对账。
   brain 内联脚本依赖 three.js，不做完整运行——这里验源码静态不变量与数据文件对账。*/
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
let fails = 0;
function ok(cond, label, detail) {
  console.log((cond ? '  ✅ ' : '  ❌ ') + label + (cond ? '' : '  → ' + (detail || '')));
  if (!cond) fails++;
}

const brain = fs.readFileSync(path.join(ROOT, 'brain.html'), 'utf8');

console.log('【源码不变量：历史上炸过的三处】');
ok(/#bookmask\[hidden\]\s*\{\s*display:\s*none/.test(brain),
  '书页遮罩 [hidden] 修复在（display:flex 曾压掉 hidden）');
ok(brain.includes('var key = n.canon || n.name'),
  'canon 反推在（clusters 显示名 ≠ 模块卡 module 字段）');
{
  const decl = brain.indexOf('var contents = m.contents || [];');
  const use = brain.indexOf("if (!preTxt && contents.length)");
  ok(decl >= 0 && use >= 0 && decl < use,
    'contents 声明在兜底使用之前（var 提升、赋值不提升）',
    'decl=' + decl + ' use=' + use);
}

console.log('【一页总览接线（2026-10-04）】');
ok(brain.includes("actBtn('onepage/' + encodeURIComponent(n.canon || n.name) + '-一页通.html', '一页总览', true)"),
  '书页弹层有「一页总览」主按钮，走 canon');

global.window = {};
require(path.join(ROOT, '_data', 'modules.js'));
require(path.join(ROOT, '_data', 'cards.js'));
const modules = global.window.MARVIS_MODULES || [];
const cards = global.window.MARVIS_CARDS || {};

console.log('【一页族对账：模块名 → site/onepage 文件】');
ok(modules.length === 13, 'modules.js 13 个模块', String(modules.length));
for (const m of modules) {
  const op = path.join(ROOT, 'onepage', m.module + '-一页通.html');
  const mp = path.join(ROOT, 'modules', m.module + '.html');
  ok(fs.existsSync(op), 'onepage/' + m.module + '-一页通.html 存在');
  ok(fs.existsSync(mp), 'modules/' + m.module + '.html 概览页存在');
  if (fs.existsSync(op)) {
    ok(fs.readFileSync(op, 'utf8').includes('← 第二大脑书架'),
      m.module + ' 一页通带导航条（回书架/模块概览）');
  }
}

console.log('【地基包对账：13/13，module 字段与 modules.js 一致】');
ok((cards.grounds || []).length === 13, 'cards.js grounds = 13', String((cards.grounds || []).length));
// 原则卡总数不写死——与原则卡正本里的 card 小节对账（增卡只改正本，这里自动跟）
const nCardsInMd = fs.readdirSync(path.join(ROOT, '..', 'wiki', 'cards'))
  .filter(f => f.startsWith('原则-') && f.endsWith('.md'))
  .reduce((a, f) => a + (fs.readFileSync(path.join(ROOT, '..', 'wiki', 'cards', f), 'utf8').match(/^## card\s/gm) || []).length, 0);
ok((cards.principles || []).length === nCardsInMd, 'cards.js principles 与原则卡正本对账',
  'js=' + (cards.principles || []).length + ' md=' + nCardsInMd);
const modNames = new Set(modules.map(m => m.module));
for (const g of cards.grounds || []) {
  ok(modNames.has(g.module), '地基包 ' + g.id + ' 的 module「' + g.module + '」能对上模块');
  const f = path.join(ROOT, '..', 'wiki', 'cards', '地基-' + g.module + '.md');
  ok(fs.existsSync(f), 'wiki/cards/地基-' + g.module + '.md 存在');
}

console.log('【内化馆关联节（2026-10-04 审查教训：grab_list 只认列表项，行内关联曾被静默丢掉）】');
{
  const cardsHtml = fs.readFileSync(path.join(ROOT, 'cards.html'), 'utf8');
  const rulesN = (cardsHtml.match(/href="rules\.html"/g) || []).length;
  ok(rulesN >= 10, 'R 系关联链到 rules.html（≥10）', String(rulesN));
  ok(!cardsHtml.includes('[['), 'cards.html 无 raw [[ 残留');
  const cardsJs = fs.readFileSync(path.join(ROOT, '_data', 'cards.js'), 'utf8');
  const m = cardsJs.match(/window\.MARVIS_CARDS = (\{[\s\S]*?\});\s*\n/);
  let nLinks = 0;
  if (m) {
    const d = JSON.parse(m[1]);
    nLinks = (d.principles || []).reduce((a, c) => a + (c.links || []).length, 0);
  }
  ok(nLinks >= 20, '原则卡关联条目 ≥20（行内顿号写法可解析）', String(nLinks));
}

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));
process.exit(fails ? 1 : 0);
