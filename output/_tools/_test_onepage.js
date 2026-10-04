// 一次性校验：用假 DOM 真执行一页通的 JS（不依赖浏览器）
const fs = require('fs');
const path = require('path');

const FILE = process.argv[2] || 'Agent运行时与工具-一页通.html';
console.log('== 被测页面: ' + FILE);
const html = fs.readFileSync(path.join(__dirname, FILE), 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.log('FAIL: 没找到 script'); process.exit(1); }
const code = m[1];

// 从源码里解析 ORDER 与 localStorage key，避免两页硬编码不一致
const om = code.match(/var ORDER = \[([^\]]+)\]/);
if (!om) { console.log('FAIL: 解析不到 ORDER'); process.exit(1); }
const ORDER = om[1].split(',').map(s => s.trim().replace(/["']/g, ''));
const km = code.match(/var KEY = "([^"]+)"/);
const LSKEY = km ? km[1] : 'mv.onepage.v1';
const card0 = (code.match(/card:"([A-Z]\d)"/) || [])[1] || ORDER[0];

// ---- 假 DOM ----
function El(tag) {
  const classes = new Set();
  const el = {
    tag, attrs: {}, classes, children: [], listeners: {},
    textContent: '', innerHTML: '', value: '',
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(el.attrs, k) ? el.attrs[k] : null; },
    setAttribute(k, v) { el.attrs[k] = String(v); },
    classList: {
      add: c => classes.add(c),
      remove: c => classes.delete(c),
      contains: c => classes.has(c),
      toggle: (c, f) => { const on = (f === undefined) ? !classes.has(c) : !!f; on ? classes.add(c) : classes.delete(c); return on; }
    },
    addEventListener(t, f) { (el.listeners[t] = el.listeners[t] || []).push(f); },
    appendChild(c) { el.children.push(c); return c; },
    fire(t) { (el.listeners[t] || []).forEach(f => f.call(el)); }
  };
  return el;
}
const reg = {};
function mk(id, tag) { const e = El(tag || 'div'); reg[id] = e; return e; }
['mainTable', 'cueToggle', 'cardSel', 'cueList', 'ptList', 'ansBox', 'critBox', 'critBtn', 'resetBtn', 'self20', 'selfOk'].forEach(id => mk(id));
const modeBtns = ['quick', 'mid', 'deep'].map(v => { const e = El('button'); e.attrs['data-mode-btn'] = v; return e; });
const body = El('body');
const store = {};
global.localStorage = {
  getItem: k => (Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); }
};
global.document = {
  body,
  getElementById: id => reg[id] || null,
  querySelectorAll: sel => (sel === '[data-mode-btn]' ? modeBtns : []),
  createElement: t => El(t)
};

// ---- 执行 ----
let ok = true;
function chk(name, cond, extra) {
  console.log((cond ? 'PASS  ' : 'FAIL  ') + name + (extra ? '  → ' + extra : ''));
  if (!cond) ok = false;
}
try { eval(code); } catch (e) { console.log('FAIL: JS 抛错 ' + e.message); process.exit(1); }

// 1 初始态
chk('body data-mode=mid', body.getAttribute('data-mode') === 'mid', body.getAttribute('data-mode'));
chk('mid 按钮高亮', modeBtns[1].classes.has('on') && !modeBtns[0].classes.has('on'));
chk('表格默认遮罩', reg.mainTable.classes.has('masked'));
chk('cueToggle 文案=对答案', reg.cueToggle.textContent === '对答案', reg.cueToggle.textContent);
chk('下拉张数 = ORDER 长度', reg.cardSel.children.length === ORDER.length,
  reg.cardSel.children.length + ' 项 / ORDER ' + ORDER.length);
chk('cue 渲染 5 条', (reg.cueList.innerHTML.match(/<li>/g) || []).length === 5);
chk('答案区默认收起（知识点+判据）', !reg.ansBox.classes.has('show'));
chk('按钮文案=答完了，看知识点与判据', reg.critBtn.textContent === '答完了，看知识点与判据', reg.critBtn.textContent);

// 2 切到深挖
modeBtns[2].fire('click');
chk('点 deep → data-mode=deep', body.getAttribute('data-mode') === 'deep', body.getAttribute('data-mode'));
chk('deep 后 mid 取消高亮', !modeBtns[1].classes.has('on') && modeBtns[2].classes.has('on'));

// 3 对答案 / 遮回去
reg.cueToggle.fire('click');
chk('点一次 → 去掉遮罩', !reg.mainTable.classes.has('masked'));
chk('文案变「遮住答案」', reg.cueToggle.textContent === '遮住答案', reg.cueToggle.textContent);
reg.cueToggle.fire('click');
chk('再点 → 恢复遮罩', reg.mainTable.classes.has('masked'));

// 4 一个按钮同时展开知识点 + 判据
reg.critBtn.fire('click');
chk('点一次 → 答案区展开', reg.ansBox.classes.has('show'));
chk('展开后按钮=遮住答案', reg.critBtn.textContent === '遮住答案', reg.critBtn.textContent);
chk('展开时判据已写入', reg.critBox.textContent.indexOf('通过判据') === 0);
chk('展开时知识点已渲染', (reg.ptList.innerHTML.match(/<li>/g) || []).length >= 10);
reg.critBtn.fire('click');
chk('再点 → 答案区收起', !reg.ansBox.classes.has('show'));
chk('收起后按钮复原', reg.critBtn.textContent === '答完了，看知识点与判据');

// 5 换一张（A5 → A6）—— 换卡应自动收起答案区
reg.critBtn.fire('click');
chk('展开后换卡前是展开', reg.ansBox.classes.has('show'));
const before = reg.cardSel.value;
const expectNext = ORDER[(ORDER.indexOf(card0) + 1) % ORDER.length];
reg.resetBtn.fire('click');
chk('换一张到下一母题', reg.cardSel.value === expectNext, before + ' → ' + reg.cardSel.value + '（期望 ' + expectNext + '）');
chk('换卡后答案区自动收起', !reg.ansBox.classes.has('show'));
chk('换卡后 cue 仍 5 条', (reg.cueList.innerHTML.match(/<li>/g) || []).length === 5);

// 6 下拉选择（取最后一张母题，验证渲染跟着切）
const lastCard = ORDER[ORDER.length - 1];
reg.cardSel.value = lastCard;
reg.cardSel.fire('change');
chk('下拉选 ' + lastCard + ' → 渲染对应', reg.critBox.textContent.indexOf('通过判据') === 0 && reg.cueList.innerHTML.length > 0);

// 7 20 秒版存本机
reg.self20.value = '测试 20 秒版';
reg.self20.fire('input');
chk('20 秒版写入 localStorage', new RegExp('测试 20 秒版').test(store[LSKEY] || ''), reg.selfOk.textContent);
chk('刷新后能读回（st.self）', JSON.parse(store[LSKEY]).self === '测试 20 秒版');

// 8 知识点清单：每张母题都要渲染，且条数足够
let minPts = 99, totalPts = 0, ptsOk = true;
ORDER.forEach(k => {
  reg.cardSel.value = k;
  reg.cardSel.fire('change');
  const n = (reg.ptList.innerHTML.match(/<li>/g) || []).length;
  const q = (reg.cueList.innerHTML.match(/<li>/g) || []).length;
  totalPts += n;
  if (n < minPts) minPts = n;
  if (n < 10 || q !== 5) { console.log('FAIL  ' + k + ' 知识点 ' + n + ' 条 / cue ' + q + ' 条'); ptsOk = false; }
});
chk('每张母题 cue 5 条 + 知识点 ≥10 条', ptsOk, '知识点合计 ' + totalPts + ' 条，最少一张 ' + minPts + ' 条');

// 9 持久化键名
chk('localStorage key = ' + LSKEY, Object.prototype.hasOwnProperty.call(store, LSKEY), LSKEY);
chk('两页 key 不串台', LSKEY.indexOf('mv.onepage') === 0);

console.log('\n' + (ok ? 'ALL PASS' : 'HAS FAIL'));
process.exit(ok ? 0 : 1);
