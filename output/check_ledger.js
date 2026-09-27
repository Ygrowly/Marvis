/* 台账冒烟测试：把 output/秋招投递台账.html 里的脚本抠出来，在假 DOM 里真跑一遍。
 *
 * 用法（在库根目录）：
 *     node output/check_ledger.js
 *
 * 为什么要它：`node --check` 只验语法。这一行曾经真实漏过——
 *     ['D','Grab'],\n/* 注释 *\/\n['A','字节跳动',...],
 * 少了逗号后 JS 把它解析成 **成员访问** `['D'][...]['A'][...]`：语法合法、
 * --check 全绿，但 DATA 里多出一个 undefined 元素、少一条真实标的，
 * 打开页面就是白屏。只有真执行才看得见。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const HTML = path.join(__dirname, '秋招投递台账.html');
const src = fs.readFileSync(HTML, 'utf8');
const m = src.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('✗ 没找到 <script> 段'); process.exit(1); }

const els = {};
function mk(id) {
  return {
    id, textContent: '', style: {}, _html: '',
    set innerHTML(v) { this._html = v; },
    get innerHTML() { return this._html; },
    classList: { add() {}, remove() {}, contains() { return false; } },
    addEventListener() {}, querySelectorAll() { return []; },
    getAttribute() { return null; }, nextElementSibling: null,
  };
}
const sandbox = {
  document: {
    getElementById(id) { return els[id] || (els[id] = mk(id)); },
    querySelectorAll() { return []; },
    createElement() { return mk('a'); },
    body: mk('body'),
  },
  window: {}, localStorage: { getItem() { return null; }, setItem() {} },
  Blob: function () {}, URL: { createObjectURL() { return ''; } },
  FileReader: function () {}, confirm: () => false, setTimeout: () => {},
  console, DATA: undefined,
};
sandbox.globalThis = sandbox;

let DATA;
try {
  vm.createContext(sandbox);
  DATA = vm.runInContext(m[1] + '\n;DATA', sandbox);
} catch (e) {
  console.error('✗ 脚本执行失败：' + e.message);
  process.exit(1);
}

const fails = [];
const ok = (cond, label, detail) => {
  console.log((cond ? '  ✓ ' : '  ✗ ') + label + (detail ? '  ' + detail : ''));
  if (!cond) fails.push(label);
};

// ① 数组完整性——就是抓出「成员访问陷阱」的那条
const holes = DATA.map((r, i) => (Array.isArray(r) && r[0] ? null : i)).filter((i) => i !== null);
ok(DATA.length >= 100, 'DATA 长度', String(DATA.length));
ok(holes.length === 0, '每个元素都是合法行（无 undefined / 无成员访问塌陷）', holes.length ? '空洞下标 ' + holes.join(',') : '');

// ② 字段完整性
const badLen = DATA.filter((r) => !Array.isArray(r) || r.length < 6).length;
ok(badLen === 0, '每行至少有 6 个字段', badLen ? badLen + ' 行异常' : '');
const badLayer = [...new Set(DATA.map((r) => r[0]))].filter((k) => !['S', 'A', 'B', 'C', 'D'].includes(k));
ok(badLayer.length === 0, '层标识只在 S/A/B/C/D 内', badLayer.join(','));
const badTag = [...new Set(DATA.map((r) => r[3]))].filter((k) => !['ok', 'mid', 'no', 'skip'].includes(k));
ok(badTag.length === 0, '门槛标识都在已定义的四档内', badTag.join(','));

// ③ id 与下标对齐（浏览器里的投递进度是用 't'+下标存的，一旦错位就是静默丢数据）
const misaligned = DATA.filter((r, i) => r.id !== 't' + i).length;
ok(misaligned === 0, 'id = t+下标，与保存的进度对齐', misaligned ? misaligned + ' 行错位' : '');

// ④ 渲染 / 统计分支真的跑通
const h = els.tb.innerHTML || '';
ok(h.length > 0, 'render() 产出了行 HTML', h.length + ' 字节');
ok((h.match(/<tr data-id=/g) || []).length === DATA.length, '渲染行数 = DATA 长度');
ok(!/undefined/.test(h), '渲染结果里没有 undefined 泄漏');
ok(String(els.nTarget.textContent) === String(DATA.length), '统计卡分母 = DATA 长度（不是写死的 75）');
ok(Math.abs(parseFloat(els.bar.style.width)) <= 100, '进度条宽度在 0–100 之间', els.bar.style.width);

// ⑤ 新维度：AI 评测 / 测试
const evalRows = DATA.filter((r) => r[6] === 'eval');
ok(evalRows.length >= 10, 'AI 评测序列行数', String(evalRows.length));
ok((h.match(/class="tag ev"/g) || []).length === evalRows.length, '评测徽标数量 = eval 行数');
ok(evalRows.every((r) => r[7] && r[7].length > 8), '每条评测行都有备注（说明为什么对口）');
const skipRows = DATA.filter((r) => r[3] === 'skip');
ok(skipRows.length >= 2, 'Infra 跳过档已用上', skipRows.map((r) => r[1]).join(' / '));

// ⑥ 投递入口链接：每行都要有一个能点的 URL，且渲染出来必须真的带 <a>
const LINKS = vm.runInContext('LINKS', sandbox);
ok(Array.isArray(LINKS), 'LINKS 数组存在');
ok(LINKS.length === DATA.length, 'LINKS 条数 = DATA 行数（下标一一对应）',
   LINKS.length + ' vs ' + DATA.length);
const badUrl = LINKS.map((u, i) => (/^https?:\/\/\S+$/.test(u || '') ? null : i)).filter((i) => i !== null);
ok(badUrl.length === 0, '每条入口都是完整 http(s) 链接', badUrl.length ? '异常下标 ' + badUrl.join(',') : '');
const anchors = (h.match(/<a class="ent[\s"]/g) || []).length;
ok(anchors === DATA.length, '渲染出的入口链接数 = 行数', String(anchors));
ok(!/href="undefined"/.test(h), '没有 undefined 链接泄漏');
const searches = LINKS.filter((u) => u.indexOf('baidu.com/s?wd=') > -1).length;
ok(searches <= 10, '搜索兜底条数在可接受范围', String(searches));

console.log('');
if (fails.length) { console.error('✗ 台账冒烟测试未通过：' + fails.join('；')); process.exit(1); }
console.log('✓ 台账冒烟测试全绿 —— ' + DATA.length + ' 个标的（AI 评测 ' + evalRows.length +
            ' · 投递入口 ' + LINKS.length + ' 条，其中搜索兜底 ' + searches + '）');
