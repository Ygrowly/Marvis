/* 宫殿页（site/brain.html）接线校验 —— 真执行，不看字符串
   用法：node output/_verify_brain.js
   校验：① 依赖资源存在 ② 数据文件真能解析且结构对得上 ③ 所有 href 落地（站内 html / 站外 output / obsidian 笔记）
        ④ 双向可达 ⑤ 主脚本语法
*/
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const SITE = path.join(ROOT, 'site');
let fail = 0, pass = 0;

function ok(cond, msg) {
  if (cond) { pass++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ ' + msg); }
}
function exists(p) { return fs.existsSync(p); }

console.log('【依赖】宫殿页引用的资源');
const brainPath = path.join(SITE, 'brain.html');
ok(exists(brainPath), 'site/brain.html 存在');
const brain = fs.readFileSync(brainPath, 'utf8');
['_build/three/three.min.js', '_data/clusters.js', '_data/projects.js', '_data/rules.js', '_components/marvis.css']
  .forEach(function (rel) {
    ok(exists(path.join(SITE, rel)), '引用存在：' + rel);
  });

console.log('\n【数据】clusters.js / projects.js 真解析');
const ctx = { window: {} };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(SITE, '_data/clusters.js'), 'utf8'), ctx);
vm.runInContext(fs.readFileSync(path.join(SITE, '_data/projects.js'), 'utf8'), ctx);
vm.runInContext(fs.readFileSync(path.join(SITE, '_data/rules.js'), 'utf8'), ctx);
const clusters = ctx.window.MARVIS_CLUSTERS || [];
const projects = ctx.window.MARVIS_PROJECTS || [];
ok(clusters.length > 0, 'MARVIS_CLUSTERS 解析成功（' + clusters.length + ' 簇）');
ok(projects.length === 3, 'MARVIS_PROJECTS 解析成功（' + projects.length + ' 个项目）');

const tech = clusters.filter(function (c) { return c.zone === '一档' || c.zone === '二档'; });
ok(tech.length === 13, '技术地基簇 = 13（实际 ' + tech.length + '）');

console.log('\n【接线】技术主线的 href 全部落到真页面');
let badHref = [];
tech.forEach(function (c) {
  c.topics.forEach(function (t) {
    if (!exists(path.join(SITE, t.href))) badHref.push(c.id + '/' + t.id + ' → ' + t.href);
  });
});
ok(badHref.length === 0, '技术主线 href ' + tech.reduce(function (s, c) { return s + c.topics.length; }, 0) +
  ' 条全部存在' + (badHref.length ? '（缺失：' + badHref.slice(0, 3).join(' / ') + '）' : ''));

console.log('\n【接线】项目 ↔ pitch 簇 双向匹配（掌握度算得准的前提）');
const pitch = clusters.filter(function (c) { return c.id === 'pitch'; })[0];
ok(!!pitch, 'pitch 簇存在');
const projNames = projects.map(function (p) { return p.name; });
const pitchProjs = pitch ? Array.from(new Set(pitch.topics.map(function (t) { return t.proj; }))) : [];
const missA = projNames.filter(function (n) { return pitchProjs.indexOf(n) < 0; });
const missB = pitchProjs.filter(function (n) { return projNames.indexOf(n) < 0; });
ok(missA.length === 0, '每个项目都有对应 pitch 条目' + (missA.length ? '（缺：' + missA.join(',') + '）' : ''));
ok(missB.length === 0, '每条 pitch 的 proj 都能匹配到项目' + (missB.length ? '（多余：' + missB.join(',') + '）' : ''));
let badProj = [];
projects.forEach(function (p) {
  if (!exists(path.join(SITE, p.href))) badProj.push(p.name + ' → ' + p.href);
  (pitch ? pitch.topics : []).forEach(function (t) {
    if (t.proj !== p.name) return;
    const f = t.href.split('#')[0];
    if (!exists(path.join(SITE, f))) badProj.push(t.name + ' → ' + t.href);
  });
});
ok(badProj.length === 0, '项目页与口述锚点页存在' + (badProj.length ? '（缺：' + badProj.slice(0, 3).join(' / ') + '）' : ''));

console.log('\n【接线】宫殿页自己挂的链接（f 字段：站外 html / 站内目录 / obsidian 笔记）');
// 注意：不能写成 /f: '(...)/ —— 'href: ' 里也含 "f: '"，会误匹配出一堆假路径
const fRefs = Array.from(new Set((brain.match(/[{,]\s*f: '([^']+)'/g) || [])
  .map(function (s) { return s.replace(/^[{,]\s*f: '/, '').replace(/'$/, ''); })));
ok(fRefs.length > 0, '宫殿页自挂链接 ' + fRefs.length + ' 条');
const outRefs = fRefs.filter(function (r) { return r.indexOf('../output/') === 0; });
const dirRefs = fRefs.filter(function (r) { return r.slice(-1) === '/'; });
const mdRefs = fRefs.filter(function (r) { return r.indexOf('../') !== 0 && r.slice(-1) !== '/'; });
ok(outRefs.length >= 3, '站外成品 ' + outRefs.length + ' 条（秋招破局 / 台账 / 简历等）');
let badOut = outRefs.filter(function (r) { return !exists(path.join(SITE, r)); });
ok(badOut.length === 0, '站外成品全部存在' + (badOut.length ? '（缺：' + badOut.join(' / ') + '）' : ''));
let badDir = dirRefs.filter(function (r) { return !exists(path.join(SITE, r)); });
ok(badDir.length === 0, '站内目录存在（' + dirRefs.join(',') + '）');
ok(mdRefs.length >= 5, 'obsidian 笔记 ' + mdRefs.length + ' 条（去重后）');
let badOb = mdRefs.filter(function (r) { return !exists(path.join(ROOT, r + '.md')); });
ok(badOb.length === 0, '引用的笔记全部存在' + (badOb.length ? '（缺：' + badOb.join(' / ') + '）' : ''));

console.log('\n【接线】操作系统厅 → 准则页锚点（与 rules.js 同源）');
const rules = ctx.window.MARVIS_RULES || [];
// 馆内 href 是拼出来的：href: 'rules.html#r-' + r.id —— 校验模板在 + 数据源同源
const tpl = /href: 'rules\.html#r-' \+ r\.id/.test(brain);
ok(rules.length > 0 && tpl,
  '操作系统厅直接读 rules.js（' + rules.length + ' 条准则，锚点模板 ' + (tpl ? '在' : '缺') + '）');
ok(brain.indexOf('MARVIS_RULES') >= 0, '宫殿页引用 MARVIS_RULES（与准则页同源，不重复维护）');
ok(fs.existsSync(path.join(SITE, 'rules.html')), 'rules.html 存在');

console.log('\n【可达】双向');
const idx = fs.readFileSync(path.join(SITE, 'index.html'), 'utf8');
ok(idx.indexOf('brain.html') >= 0, '首页 → 宫殿');
ok(brain.indexOf('index.html') >= 0, '宫殿 → 首页');
ok(brain.indexOf('progress.html') >= 0, '宫殿 → 进度页');

console.log('\n【语法】主脚本');
const scripts = brain.match(/<script>([\s\S]*?)<\/script>/g) || [];
ok(scripts.length > 0, '找到内联脚本 ' + scripts.length + ' 块');
scripts.forEach(function (s, i) {
  const body = s.replace(/^<script>/, '').replace(/<\/script>$/, '');
  try {
    new vm.Script(body, { filename: 'brain.html#' + (i + 1) });
    pass++; console.log('  ✓ 第 ' + (i + 1) + ' 块语法通过');
  } catch (e) {
    fail++; console.log('  ✗ 第 ' + (i + 1) + ' 块语法错误：' + String(e.message).slice(0, 300));
  }
});

console.log('\n—— 通过 ' + pass + ' 项，失败 ' + fail + ' 项 ——');
process.exit(fail ? 1 : 0);
