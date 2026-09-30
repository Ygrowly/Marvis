/* Marvis 云同步 v0.1（2026-10-01）
   把整个 mv.* 命名空间打包成一个 JSON，存到 GitHub 仓库根目录下的 data/marvis-sync.json。
   认证用细粒度令牌（只对该仓库 Contents 读写），令牌只存在本机浏览器，绝不进仓库。

   设计要点：
   1. localStorage 降为离线层——断网照样能点，页面不等网络。
   2. 拦 localStorage.setItem 收集脏标记，所以全站 165 个页面零改动。
   3. 每键带时间戳影子表，冲突时新的赢；主进度 mv.progress.v1 额外做逐条合并。
   4. 写不上去也不丢：本地时间戳已经记下了，下次任意设备拉的时候本地赢。
*/
(function () {
  'use strict';

  var CFG_KEY = 'mv.sync.cfg';
  var TS_KEY = 'mv.sync.ts';
  var DEV_KEY = 'mv.sync.dev';
  var NS = 'mv.';
  var INTERNAL = {};
  INTERNAL[CFG_KEY] = 1; INTERNAL[TS_KEY] = 1; INTERNAL[DEV_KEY] = 1;
  var DEBOUNCE_MS = 45000;
  var API = 'https://api.github.com';
  var DEF_PATH = 'data/marvis-sync.json';

  /* ---------- 基础读写（走原始 setItem，不触发钩子） ---------- */
  /* 拿的是装钩子之前的原始引用，不依赖 Storage.prototype 存在（测试环境里没有） */
  var _set = null, _get = null;
  try { _set = localStorage.setItem.bind(localStorage); } catch (e) { _set = function (k, v) { localStorage.setItem(k, v); }; }
  try { _get = localStorage.getItem.bind(localStorage); } catch (e) { _get = function (k) { return localStorage.getItem(k); }; }
  function rawGet(k) { try { return _get.call(localStorage, k); } catch (e) { return null; } }
  function rawSet(k, v) { try { _set.call(localStorage, k, v); } catch (e) {} }

  function cfg() {
    var o = null;
    try { o = JSON.parse(rawGet(CFG_KEY) || '{}'); } catch (e) { o = {}; }
    if (!o.branch) o.branch = 'main';
    if (!o.path) o.path = DEF_PATH;
    return o;
  }
  function setCfg(patch) {
    var c = cfg();
    for (var k in patch) if (Object.prototype.hasOwnProperty.call(patch, k)) c[k] = patch[k];
    rawSet(CFG_KEY, JSON.stringify(c));
    return c;
  }
  function ready() {
    var c = cfg();
    return !!(c.token && c.owner && c.repo);
  }

  /* ---------- 时间戳影子表 ---------- */
  function tsAll() { try { return JSON.parse(rawGet(TS_KEY) || '{}') || {}; } catch (e) { return {}; } }
  function tsSet(k, t) {
    var a = tsAll(); a[k] = t; rawSet(TS_KEY, JSON.stringify(a));
  }

  function devId() {
    var d = rawGet(DEV_KEY);
    if (!d) {
      d = (navigator.platform || 'dev').replace(/\s+/g, '') + '-' +
          Math.random().toString(36).slice(2, 6);
      rawSet(DEV_KEY, d);
    }
    return d;
  }

  /* ---------- 命名空间快照 ---------- */
  function snapshot() {
    var o = {}, i, k;
    for (i = 0; i < localStorage.length; i++) {
      k = localStorage.key(i);
      if (!k || k.indexOf(NS) !== 0 || INTERNAL[k]) continue;
      o[k] = localStorage.getItem(k);
    }
    return o;
  }

  /* ---------- base64（UTF-8 安全） ---------- */
  function enc(s) {
    var bytes = new TextEncoder().encode(s), bin = '', CH = 0x8000, i;
    for (i = 0; i < bytes.length; i += CH) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
    }
    return btoa(bin);
  }
  function dec(b64) {
    var bin = atob(String(b64).replace(/\s/g, '')), bytes = new Uint8Array(bin.length), i;
    for (i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }

  /* ---------- 合并 ---------- */
  /* 主进度特殊处理：lv 逐条比 last 谁新，days 并集，其余字段取有值的一边 */
  function mergeProgress(aStr, bStr) {
    var a = null, b = null;
    try { a = JSON.parse(aStr); } catch (e) {}
    try { b = JSON.parse(bStr); } catch (e) {}
    if (!a) return bStr; if (!b) return aStr;

    var out = { lv: {}, days: {}, drill: [], extra: {}, exam: {}, resetAt: null };

    var lvk = {};
    Object.keys(a.lv || {}).forEach(function (k) { lvk[k] = 1; });
    Object.keys(b.lv || {}).forEach(function (k) { lvk[k] = 1; });
    Object.keys(lvk).forEach(function (k) {
      var x = (a.lv || {})[k], y = (b.lv || {})[k];
      if (!x) { out.lv[k] = y; return; }
      if (!y) { out.lv[k] = x; return; }
      var xl = x.last || '', yl = y.last || '';
      var w = (yl > xl) ? y : (xl > yl ? x : ((x.l || 0) >= (y.l || 0) ? x : y));
      /* hit/miss 取最大值而不是累加：累加不幂等，每次合并翻一倍，
         还会让「内容没变就不提交」的判断永远为假，白白多出 commit */
      out.lv[k] = {
        l: Math.max(x.l || 0, y.l || 0),
        due: w.due || null,
        last: w.last || null,
        hit: Math.max(x.hit || 0, y.hit || 0),
        miss: Math.max(x.miss || 0, y.miss || 0)
      };
    });

    var dk = {};
    Object.keys(a.days || {}).forEach(function (k) { dk[k] = 1; });
    Object.keys(b.days || {}).forEach(function (k) { dk[k] = 1; });
    Object.keys(dk).forEach(function (k) {
      var x = (a.days || {})[k], y = (b.days || {})[k];
      if (!x) { out.days[k] = y; return; }
      if (!y) { out.days[k] = x; return; }
      out.days[k] = ((x.items || []).length >= (y.items || []).length) ? x : y;
    });

    var seen = {};
    [].concat(a.drill || [], b.drill || []).forEach(function (d) {
      var k = (d && (d.date || d.d || '') + '|' + (d.id || '')) || '';
      if (seen[k]) return; seen[k] = 1; out.drill.push(d);
    });
    out.extra = Object.assign({}, b.extra || {}, a.extra || {});
    out.exam = (a.exam && Object.keys(a.exam).length) ? a.exam : (b.exam || {});
    out.resetAt = (a.resetAt && a.resetAt > (b.resetAt || '')) ? a.resetAt : (b.resetAt || a.resetAt || null);
    return JSON.stringify(out);
  }

  function merge(local, remote) {
    var out = { data: {}, ts: {} }, seen = {};
    Object.keys(local.data || {}).forEach(function (k) { seen[k] = 1; });
    Object.keys(remote.data || {}).forEach(function (k) { seen[k] = 1; });
    Object.keys(seen).forEach(function (k) {
      var lt = (local.ts || {})[k] || 0, rt = (remote.ts || {})[k] || 0;
      var ld = local.data[k], rd = remote.data[k];
      if (k === 'mv.progress.v1' && ld && rd) {
        out.data[k] = mergeProgress(ld, rd);
        out.ts[k] = Math.max(lt, rt);
        return;
      }
      if (rt > lt) { out.data[k] = rd; out.ts[k] = rt; }
      else { out.data[k] = ld; out.ts[k] = lt; }
    });
    return out;
  }

  /* 内容没变就不提交，省掉 pull→重绘→save 造成的空转 commit */
  function sameDoc(a, b) {
    try {
      return JSON.stringify({ ts: a.ts, data: a.data }) ===
             JSON.stringify({ ts: b.ts, data: b.data });
    } catch (e) { return false; }
  }

  /* ---------- 回写本地（挂起钩子，避免自己触发自己） ---------- */
  var suspended = false;
  function restore(doc) {
    var changed = [], k, v;
    suspended = true;
    try {
      Object.keys(doc.data || {}).forEach(function (k2) {
        var v2 = doc.data[k2];
        if (v2 == null) return;
        if (rawGet(k2) === v2) return;      // 没变就不写，省一次重绘
        rawSet(k2, v2);
        changed.push(k2);
      });
      var ts = doc.ts || {};
      var cur = tsAll();
      Object.keys(ts).forEach(function (k3) { cur[k3] = ts[k3]; });
      rawSet(TS_KEY, JSON.stringify(cur));
    } finally { suspended = false; }
    return changed;
  }

  /* ---------- GitHub Contents API ---------- */
  function hdrs(c) {
    return {
      'Authorization': 'Bearer ' + c.token,
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json'
    };
  }
  function url(c) {
    return API + '/repos/' + encodeURIComponent(c.owner) + '/' + encodeURIComponent(c.repo) +
           '/contents/' + c.path.split('/').map(encodeURIComponent).join('/');
  }
  function getFile(c) {
    return fetch(url(c) + '?ref=' + encodeURIComponent(c.branch), {
      headers: hdrs(c), cache: 'no-store'
    }).then(function (r) {
      if (r.status === 404) return null;
      if (!r.ok) return r.json().then(function (j) { throw new Error((j && j.message) || ('HTTP ' + r.status)); });
      return r.json();
    });
  }
  function putFile(c, body) {
    return fetch(url(c), { method: 'PUT', headers: hdrs(c), body: JSON.stringify(body) })
      .then(function (r) {
        return r.json().then(function (j) {
          if (!r.ok) throw new Error((j && j.message) || ('HTTP ' + r.status));
          return j;
        });
      });
  }

  /* ---------- 拉取 / 推送 ---------- */
  var status = 'off';      // off | idle | dirty | busy | error
  var lastMsg = '';
  var timer = null;
  var inflight = null;
  var listeners = [];

  function emit(reason) {
    listeners.forEach(function (f) { try { f(reason); } catch (e) {} });
    try { window.dispatchEvent(new CustomEvent('mv:sync', { detail: { reason: reason } })); } catch (e) {}
    paint();
  }
  function setStatus(s, msg) { status = s; lastMsg = msg || ''; paint(); }
  function localDoc() { return { ts: tsAll(), data: snapshot() }; }

  function pull() {
    if (!ready()) { setStatus('off', '还没填令牌'); return Promise.resolve(false); }
    if (inflight) return inflight;
    setStatus('busy', '拉取中');
    var c = cfg();
    inflight = getFile(c).then(function (cur) {
      var doc;
      try { doc = cur ? JSON.parse(dec(cur.content)) : null; } catch (e) { doc = null; }
      if (!doc) doc = { v: 1, ts: {}, data: {} };
      /* 远端还没有内容 → 把本机这份当作首版推上去，省得手动点一次「立即上传」 */
      if (!cur || !Object.keys(doc.data || {}).length) {
        return push(true).then(function () { return true; });
      }
      var merged = merge(localDoc(), doc);
      var changed = restore(merged);
      setStatus('idle', '已同步');
      inflight = null;
      if (changed.length) emit('pull');
      return changed.length > 0;
    }).catch(function (e) {
      inflight = null;
      setStatus('error', '拉取失败：' + e.message);
      return false;
    });
    return inflight;
  }

  function push(force) {
    if (!ready()) { setStatus('off', '还没填令牌'); return Promise.resolve(false); }
    var c = cfg(), attempt = 0;

    function once() {
      attempt++;
      return getFile(c).then(function (cur) {
        var doc;
        try { doc = cur ? JSON.parse(dec(cur.content)) : null; } catch (e) { doc = null; }
        if (!doc) doc = { v: 1, ts: {}, data: {} };
        var merged = merge(localDoc(), doc);
        if (cur && sameDoc(merged, doc)) { setStatus('idle', '已同步'); return true; }
        var body = {
          message: 'progress sync ' + stamp() + ' · ' + devId(),
          content: enc(JSON.stringify({
            v: 1, ts: merged.ts, data: merged.data,
            meta: { device: devId(), updatedAt: new Date().toISOString() }
          })),
          branch: c.branch
        };
        if (cur) body.sha = cur.sha;
        return putFile(c, body).then(function () {
          var back = restore(merged);
          setStatus('idle', '已同步 ' + timeNow());
          if (back.length) emit('push');
          return true;
        });
      }).catch(function (e) {
        // 别人刚写过，sha 过期 → 重取一次再试
        if (attempt < 3 && /sha|conflict|does not match/i.test(e.message || '')) return once();
        throw e;
      });
    }

    if (inflight) return inflight;
    setStatus('busy', '上传中');
    inflight = once().catch(function (e) {
      setStatus('error', '上传失败：' + e.message);
      return false;
    }).then(function (r) { inflight = null; return r; });
    return inflight;
  }

  function markDirty() {
    if (!ready()) return;
    setStatus('dirty', '有改动待上传');
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () { timer = null; push(); }, DEBOUNCE_MS);
  }
  function flush() {
    if (timer) { clearTimeout(timer); timer = null; }
    if (status === 'dirty') return push();
    return Promise.resolve(false);
  }

  function stamp() {
    var d = new Date(), p = function (n) { return String(n).padStart(2, '0'); };
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }
  function timeNow() {
    var d = new Date(), p = function (n) { return String(n).padStart(2, '0'); };
    return p(d.getHours()) + ':' + p(d.getMinutes());
  }

  /* ---------- 钩子：拦写入 ---------- */
  function installHook() {
    if (localStorage.__mvHooked) return;
    try {
      Object.defineProperty(localStorage, '__mvHooked', { value: true, enumerable: false });
    } catch (e) {}
    var orig = localStorage.setItem.bind(localStorage);
    localStorage.setItem = function (k, v) {
      orig(k, v);
      if (suspended) return;
      if (typeof k !== 'string' || k.indexOf(NS) !== 0 || INTERNAL[k]) return;
      tsSet(k, Date.now());
      markDirty();
    };
  }

  /* ---------- 界面：右下角状态徽章 + 设置面板 ---------- */
  var badge = null, panel = null;
  var TONE = {
    off:    ['#888780', '未配置'],
    idle:   ['#0F6E56', '已同步'],
    dirty:  ['#BA7517', '待上传'],
    busy:   ['#185FA5', '同步中'],
    error:  ['#A32D2D', '出错']
  };
  function paint() {
    if (!badge) return;
    var t = TONE[status] || TONE.off;
    badge.style.borderColor = t[0];
    badge.textContent = '云同步 · ' + t[1] + (lastMsg && status !== 'idle' ? ' · ' + lastMsg : '');
    badge.title = lastMsg || t[1];
  }
  function buildBadge() {
    if (badge) return;
    badge = document.createElement('div');
    badge.setAttribute('data-mv-sync', 'badge');
    badge.style.cssText = 'position:fixed;right:14px;bottom:14px;z-index:9999;cursor:pointer;' +
      'font:12px/1 system-ui,-apple-system,"Segoe UI",sans-serif;padding:6px 10px;border-radius:999px;' +
      'border:1px solid #888780;background:#fff;color:#2C2C2A;opacity:.82;box-shadow:0 1px 4px rgba(0,0,0,.12)';
    badge.onclick = openPanel;
    document.body.appendChild(badge);
    paint();
  }
  function openPanel() {
    if (panel) { panel.style.display = 'block'; return; }
    var c = cfg();
    panel = document.createElement('div');
    panel.setAttribute('data-mv-sync', 'panel');
    panel.style.cssText = 'position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.35);' +
      'display:flex;align-items:center;justify-content:center;padding:16px';
    panel.innerHTML =
      '<div style="background:#fff;border-radius:12px;max-width:30rem;width:100%;padding:18px;' +
      'font:13px/1.7 system-ui,-apple-system,"Segoe UI",sans-serif;color:#2C2C2A">' +
        '<div style="font-size:14px;font-weight:500;margin-bottom:4px">云同步设置</div>' +
        '<div style="color:#5F5E5A;font-size:12px;margin-bottom:12px">' +
          '进度写回仓库的 <code>data/marvis-sync.json</code>。令牌只存在这台机器的浏览器里，不会进仓库。' +
          '建议只对这一个仓库开 Contents 读写。' +
        '</div>' +
        row('GitHub 用户名', 'owner', c.owner || '') +
        row('仓库名', 'repo', c.repo || '') +
        row('分支', 'branch', c.branch || 'main') +
        row('文件路径', 'path', c.path || DEF_PATH) +
        row('访问令牌', 'token', c.token || '', true) +
        '<div id="mv-sync-msg" style="min-height:1.6em;font-size:12px;color:#0F6E56"></div>' +
        '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">' +
          btn('保存配置', 'save') + btn('立即拉取', 'pull') + btn('立即上传', 'push') +
          btn('清除配置', 'clear') + btn('关闭', 'close') +
        '</div>' +
      '</div>';
    panel.onclick = function (e) { if (e.target === panel) panel.style.display = 'none'; };
    document.body.appendChild(panel);
    panel.querySelectorAll('button[data-a]').forEach(function (b) {
      b.onclick = function () { act(b.getAttribute('data-a')); };
    });
  }
  function row(label, name, val, pwd) {
    return '<label style="display:block;margin-bottom:8px;font-size:12px;color:#5F5E5A">' + label +
      '<input data-f="' + name + '" type="' + (pwd ? 'password' : 'text') + '" value="' + String(val).replace(/"/g, '&quot;') + '" ' +
      'style="display:block;width:100%;margin-top:2px;padding:6px 8px;border:1px solid #D3D1C7;border-radius:6px;' +
      'font:13px/1.4 ui-monospace,Consolas,monospace;color:#2C2C2A"></label>';
  }
  function btn(text, a) {
    return '<button data-a="' + a + '" style="padding:6px 12px;border:1px solid #D3D1C7;border-radius:6px;' +
      'background:#fff;color:#2C2C2A;font-size:13px;cursor:pointer">' + text + '</button>';
  }
  function msg(s, bad) {
    var el = panel && panel.querySelector('#mv-sync-msg');
    if (el) { el.textContent = s || ''; el.style.color = bad ? '#A32D2D' : '#0F6E56'; }
  }
  function act(a) {
    var vals = {};
    panel.querySelectorAll('input[data-f]').forEach(function (i) { vals[i.getAttribute('data-f')] = i.value.trim(); });
    if (a === 'close') { panel.style.display = 'none'; return; }
    if (a === 'save') {
      setCfg(vals); msg('已保存，正在拉取…'); pull().then(function () { msg('配置已保存'); });
      return;
    }
    if (a === 'clear') {
      setCfg({ owner: '', repo: '', branch: 'main', path: DEF_PATH, token: '' });
      setStatus('off', '已清除'); msg('配置已清除'); return;
    }
    if (a === 'pull') {
      setCfg(vals); msg('拉取中…');
      pull().then(function (ch) { msg(ch ? '拉到新数据，页面已刷新' : '已是最新'); });
      return;
    }
    if (a === 'push') {
      setCfg(vals); msg('上传中…');
      push(true).then(function (ok) { msg(ok ? '已上传' : '上传失败，看徽章提示', !ok); });
      return;
    }
  }

  /* ---------- 启动 ---------- */
  function boot() {
    installHook();
    buildBadge();
    if (!ready()) { setStatus('off', '还没填令牌'); return; }
    // 先渲染本地（秒开），再后台拉；拉到新的就通知页面重绘
    pull();
    window.addEventListener('pagehide', function () { flush(); });
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') flush();
    });
    // 兜底：每 10 分钟兜一次，防止 debounce 被关页打断
    setInterval(function () { if (status === 'dirty') push(); }, 600000);
  }

  window.MarvisSync = {
    cfg: cfg, setCfg: setCfg, ready: ready,
    pull: pull, push: push, flush: flush,
    status: function () { return status; },
    openPanel: openPanel,
    on: function (f) { listeners.push(f); }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
})();
