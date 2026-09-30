/* 云同步层单测（2026-10-01）
   真跑一遍 sync.js：本地存储用 Map 模拟，GitHub 用内存假 API（带 sha 校验）。
   跑法：node site/_tests/test_sync.js
*/
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const code = fs.readFileSync(path.join(ROOT, '_components', 'sync.js'), 'utf8');

let pass = 0, fail = 0;
function ok(cond, name, extra) {
  if (cond) { pass++; console.log('  ✅ ' + name + (extra ? '  → ' + extra : '')); }
  else { fail++; console.log('  ❌ ' + name + (extra ? '  → ' + extra : '')); }
}
function head(s) { console.log('\n【' + s + '】'); }

/* ---------- 环境桩 ---------- */
function makeLS() {
  const m = new Map();
  const ls = {
    get length() { return m.size; },
    key: (i) => Array.from(m.keys())[i],
    getItem: (k) => (m.has(String(k)) ? m.get(String(k)) : null),
    setItem: (k, v) => m.set(String(k), String(v)),
    removeItem: (k) => m.delete(String(k)),
    _m: m,
  };
  return ls;
}

/* 内存版 GitHub Contents API：远端只有一个文件，PUT 必须带对 sha */
function makeAPI() {
  const api = {
    doc: null,                 // {content: base64} 的内容原文
    sha: null,
    puts: 0,
    gets: 0,
    nextSha: 'sha0',
    base64: (s) => Buffer.from(s, 'utf8').toString('base64'),
    text: (b) => Buffer.from(String(b).replace(/\s/g, ''), 'base64').toString('utf8'),
  };
  api.fetch = function (u, opt) {
    if (!opt || opt.method !== 'PUT') {
      api.gets++;
      if (!api.doc) return Promise.resolve({ ok: false, status: 404, json: () => Promise.resolve({ message: 'Not Found' }) });
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ sha: api.sha, content: api.base64(api.doc) }) });
    }
    api.puts++;
    return Promise.resolve({ json: () => Promise.resolve({}) }).then(function (r) {
      const body = JSON.parse(opt.body);
      if (api.sha && body.sha !== api.sha) {
        return { ok: false, status: 409, json: () => Promise.resolve({ message: "sha does not match" }) };
      }
      api.doc = Buffer.from(String(body.content).replace(/\s/g, ''), 'base64').toString('utf8');
      api.sha = 'sha' + (++api.putCounter || (api.putCounter = 1));
      return { ok: true, status: 200, json: () => Promise.resolve({ content: { sha: api.sha } }) };
    });
  };
  return api;
}

function boot(ls, sharedApi) {
  const api = sharedApi || makeAPI();
  const win = { addEventListener: () => {}, removeEventListener: () => {}, dispatchEvent: () => {} };
  const sandbox = {
    console,
    window: win,
    localStorage: ls,
    document: {
      readyState: 'complete',
      body: { appendChild: () => {} },
      head: { appendChild: () => {} },
      createElement: () => ({ style: {}, setAttribute: () => {}, querySelector: () => null, querySelectorAll: () => [], appendChild: () => {} }),
      addEventListener: () => {},
      visibilityState: 'visible',
    },
    navigator: { platform: 'Node' },
    fetch: (u, o) => api.fetch(u, o),
    TextEncoder, TextDecoder,
    btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
    atob: (s) => Buffer.from(s, 'base64').toString('binary'),
    setTimeout, clearTimeout, setInterval: () => 0, clearInterval,
    Date, Math, JSON, Object, Array, String, Number, Promise, CustomEvent: function (t, o) { this.type = t; this.detail = o && o.detail; },
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox);
  return { api, S: sandbox.window.MarvisSync, win, sandbox };
}

const CFG = { owner: 'Ygrowly', repo: 'Marvis', branch: 'main', path: 'data/marvis-sync.json', token: 'tok' };

(async function run() {
  head('加载与配置');
  let e = boot(makeLS());
  ok(!!e.S, 'MarvisSync 暴露出来了');
  ok(e.S.status() === 'off', '没填令牌时状态是 off', e.S.status());
  e.S.setCfg(CFG);
  ok(e.S.ready() === true, '填完令牌后 ready');

  head('钩子：写本地键就记脏');
  e = boot(makeLS());
  e.S.setCfg(CFG);
  e.api.fetch = () => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ sha: 's', content: Buffer.from('{"v":1,"ts":{},"data":{}}').toString('base64') }) });
  localStorage_write(e, 'mv.done.MySQL-01-q3', '1');
  ok(e.S.status() === 'dirty', '写完 mv.* 键 → 状态 dirty', e.S.status());
  ok(JSON.parse(e.sandbox.localStorage.getItem('mv.sync.ts') || '{}')['mv.done.MySQL-01-q3'] > 0, '时间戳已记下');
  e.sandbox.localStorage.setItem('other.thing', 'x');
  ok(!JSON.parse(e.sandbox.localStorage.getItem('mv.sync.ts') || '{}')['other.thing'], '非 mv. 前缀不进同步');

  head('首次推送：远端空 → 本机这份当首版');
  e = boot(makeLS());
  e.S.setCfg(CFG);
  localStorage_write(e, 'mv.progress.v1', JSON.stringify({ lv: { 'mysql/1': { l: 2, last: '2026-10-01' } }, days: {} }));
  localStorage_write(e, 'mv.done.MySQL-01-q1', '1');
  await e.S.push(true);
  ok(e.api.puts === 1, '推了一次', 'puts=' + e.api.puts);
  const doc1 = JSON.parse(e.api.doc);
  ok(doc1.data['mv.done.MySQL-01-q1'] === '1', '小键进去了');
  ok(JSON.parse(doc1.data['mv.progress.v1']).lv['mysql/1'].l === 2, '主进度进去了');
  ok(!!doc1.meta && !!doc1.meta.device, 'meta 记了设备');

  head('换一台机器：拉下来就是同一份');
  const e2 = boot(makeLS(), e.api);   // 共用同一个远端
  e2.S.setCfg(CFG);
  const changed = await e2.S.pull();
  ok(changed === true, 'pull 报告有更新');
  ok(e2.sandbox.localStorage.getItem('mv.done.MySQL-01-q1') === '1', '小键同步过来');
  ok(JSON.parse(e2.sandbox.localStorage.getItem('mv.progress.v1')).lv['mysql/1'].l === 2, '主进度同步过来');

  head('两端各改一部分 → 合并而不是互相覆盖');
  localStorage_write(e, 'mv.done.a', '1');                    // 机器 A 改 a
  localStorage_write(e2, 'mv.done.b', '1');                   // 机器 B 改 b
  await e.S.push(true);
  await e2.S.push(true);                                      // B 推送时远端已有 A 的 a
  const merged = JSON.parse(e2.api.doc);
  ok(merged.data['mv.done.a'] === '1', 'A 的改动留着');
  ok(merged.data['mv.done.b'] === '1', 'B 的改动也留着');
  await e.S.pull();
  ok(e.sandbox.localStorage.getItem('mv.done.b') === '1', 'A 拉回了 B 的改动');

  head('主进度逐条合并：谁练得新听谁的');
  const eA = boot(makeLS()), eB = boot(makeLS(), eA.api);
  eA.S.setCfg(CFG); eB.S.setCfg(CFG);
  const pA = { lv: { 'mysql/1': { l: 2, last: '2026-10-01', hit: 3, miss: 0 }, 'redis/1': { l: 1, last: '2026-09-20', hit: 1, miss: 0 } }, days: {}, drill: [], extra: {}, exam: {}, resetAt: null };
  const pB = { lv: { 'mysql/1': { l: 1, last: '2026-09-25', hit: 1, miss: 1 }, 'redis/1': { l: 2, last: '2026-09-29', hit: 2, miss: 0 } }, days: {}, drill: [], extra: {}, exam: {}, resetAt: null };
  localStorage_write(eA, 'mv.progress.v1', JSON.stringify(pA));
  localStorage_write(eB, 'mv.progress.v1', JSON.stringify(pB));
  await eA.S.push(true);
  await eB.S.push(true);
  const fin = JSON.parse(JSON.parse(eA.api.doc).data['mv.progress.v1']);
  ok(fin.lv['mysql/1'].last === '2026-10-01', 'mysql/1 取 A（更晚练的）', fin.lv['mysql/1'].last);
  ok(fin.lv['redis/1'].last === '2026-09-29', 'redis/1 取 B（更晚练的）', fin.lv['redis/1'].last);
  ok(fin.lv['mysql/1'].hit === 3, '命中次数取最大值且不翻倍', String(fin.lv['mysql/1'].hit));

  head('空转不产生 commit');
  const putsBefore = eA.api.puts;
  await eA.S.pull();
  await eA.S.push(true);
  await eA.S.push(true);
  ok(eA.api.puts === putsBefore, '内容没变就不提交', '新增 puts=' + (eA.api.puts - putsBefore));

  head('sha 冲突自动重试');
  const eC = boot(makeLS());
  eC.S.setCfg(CFG);
  const realFetch = eC.api.fetch;
  let first = true;
  eC.api.fetch = function (u, o) {
    if (o && o.method === 'PUT' && first) { first = false; return Promise.resolve({ ok: false, status: 409, json: () => Promise.resolve({ message: 'sha does not match' }) }); }
    return realFetch(u, o);
  };
  localStorage_write(eC, 'mv.done.c', '1');
  await eC.S.push(true);
  ok(eC.S.status() === 'idle', '冲突后重试成功', eC.S.status());
  ok(JSON.parse(eC.api.doc).data['mv.done.c'] === '1', '重试后内容确实上去了');

  head('断网不丢：本地时间戳记着，下次拉的时候本地赢');
  const eD = boot(makeLS());
  eD.S.setCfg(CFG);
  localStorage_write(eD, 'mv.progress.v1', JSON.stringify({ lv: { 'net/1': { l: 1, last: '2026-10-01' } }, days: {} }));
  eD.api.fetch = () => Promise.reject(new Error('offline'));
  await eD.S.push(true);
  ok(eD.S.status() === 'error', '上传失败 → 报 error', eD.S.status());
  const good = boot(makeLS());
  good.S.setCfg(CFG);
  const remoteDoc = { v: 1, ts: { 'mv.progress.v1': 1 }, data: { 'mv.progress.v1': JSON.stringify({ lv: {}, days: {} }) } };
  good.api.doc = JSON.stringify(remoteDoc);
  good.api.sha = 'old';
  good.api.fetch = () => Promise.resolve({
    ok: true, status: 200,
    json: () => Promise.resolve({ sha: 'old', content: Buffer.from(JSON.stringify(remoteDoc)).toString('base64') })
  });
  localStorage_write(good, 'mv.progress.v1', JSON.stringify({ lv: { 'net/1': { l: 1, last: '2026-10-01' } }, days: {} }));
  await good.S.pull();
  ok(JSON.parse(good.sandbox.localStorage.getItem('mv.progress.v1')).lv['net/1'], '远端的空进度没吃掉本地数据');

  head('中文与编码往返');
  const e5 = boot(makeLS());
  e5.S.setCfg(CFG);
  localStorage_write(e5, 'mv.note', '中文 ✦ 断点：长事务会撑爆连接数');
  await e5.S.push(true);
  ok(JSON.parse(e5.api.doc).data['mv.note'] === '中文 ✦ 断点：长事务会撑爆连接数', 'UTF-8 往返无损');

  console.log('\n' + (fail ? '❌ 失败 ' + fail + ' 项 / 共 ' + (pass + fail) : '✅ 全部通过 · ' + pass + ' 项'));
  process.exit(fail ? 1 : 0);
})().catch(function (err) { console.error(err); process.exit(1); });

function localStorage_write(env, k, v) { env.sandbox.localStorage.setItem(k, v); }
