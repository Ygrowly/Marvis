(function () {
  'use strict';
  var KEY = 'mv.progress.v1', BKEY = 'mv.brain.v1', MASTER = 1;
  var S = null, B = { uses: {} };
  try { S = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { S = null; }
  if (!S || typeof S !== 'object') S = {};
  if (!S.lv) S.lv = {};
  try { B = JSON.parse(localStorage.getItem(BKEY) || '{}') || {}; } catch (e) { B = {}; }
  if (!B.uses) B.uses = {};
  function lvOf(k) { return (S.lv[k] && S.lv[k].l) || 0; }
  function ob(p) { return 'obsidian://open?vault=Marvis&file=' + encodeURIComponent(p); }
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function todayStr() { var d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }

  // ── 五个区（暖木书房调：蓝 denim / 赭 amber / 紫 iris / 苔绿 / 陶土，参考 Japandi 暖调）──
  var HALLS = [
    { k: 'tech',  name: '本事 · 技术地基', color: 0x4C82B8, dark: 0x2C5A8C, css: '#4C82B8' },
    { k: 'work',  name: '作品 · 三个项目', color: 0xC08A3E, dark: 0x8A5E1E, css: '#C08A3E' },
    { k: 'os',    name: '操作系统 · 行事准则', color: 0x8B7FD4, dark: 0x5C50A8, css: '#8B7FD4' },
    { k: 'field', name: '战场 · 秋招', color: 0x6FA054, dark: 0x47702F, css: '#6FA054' },
    { k: 'books', name: '书架 · 读过的', color: 0xCE7B57, dark: 0x9A4E2E, css: '#CE7B57' }
  ];

  var nodes = [];

  // ① 本事：模块 = 一本书，主线印在下钻面板
  (window.MARVIS_CLUSTERS || []).forEach(function (c) {
    if (c.zone !== '一档' && c.zone !== '二档') return;
    var tot = c.topics.length, got = 0;
    c.topics.forEach(function (t) { if (lvOf(c.id + '/' + t.id) >= MASTER) got++; });
    // 归一：clusters 的显示名（Redis 与缓存）≠ 模块卡 module 字段（Redis）——
    // 用第一条主线的 href 反推正本模块名，概览页链接与 modules.js / 地基包查找都用它
    var firstHref = (c.topics[0] && c.topics[0].href) || '';
    var canon = (firstHref.match(/^modules\/(.+)-\d+-/) || [])[1] || c.name;
    var m0 = null;
    (window.MARVIS_MODULES || []).forEach(function (x) { if (x.module === canon) m0 = x; });
    nodes.push({
      hall: 'tech', id: c.id, name: c.name, canon: canon,
      ratio: tot ? got / tot : 0, got: got, tot: tot,
      desc: c.zone + ' · ' + got + '/' + tot + ' 条主线已到「会了」',
      href: m0 ? m0.href : '',
      lines: c.topics.map(function (t) {
        return { n: t.id + ' · ' + t.name, href: t.href, lv: lvOf(c.id + '/' + t.id) };
      })
    });
  });

  // ② 作品：项目 = 一本书，口述条目印在下钻面板
  var pitch = (window.MARVIS_CLUSTERS || []).filter(function (c) { return c.id === 'pitch'; })[0];
  (window.MARVIS_PROJECTS || []).forEach(function (p) {
    var lines = [], got = 0, tot = 0;
    if (pitch) pitch.topics.forEach(function (t) {
      if (t.proj !== p.name) return;
      tot++;
      var l = lvOf('pitch/' + t.id);
      if (l >= MASTER) got++;
      lines.push({ n: t.name, href: t.href, lv: l });
    });
    nodes.push({
      hall: 'work', id: p.id, name: p.name, ratio: tot ? got / tot : 0,
      got: got, tot: tot, desc: p.lead, href: p.href, lines: lines
    });
  });

  // ③ 行事准则：一条准则 = 一本书（2026-10-03 起可训练，等级挂 rule/R*）
  (window.MARVIS_RULES || []).forEach(function (r) {
    var l = lvOf('rule/' + r.id);
    nodes.push({
      hall: 'os', id: r.id, name: r.name,
      ratio: l >= 2 ? 1 : (l >= 1 ? 0.5 : 0), tot: 1, got: l >= 1 ? 1 : 0,
      desc: r.action, href: 'rules.html#r-' + r.id, lines: [], rule: r
    });
  });

  // ④ 战场：秋招成品 = 一本书（不进派单，恒灰）
  [
    { n: '秋招破局方案', d: 'offer = 投递量 × 过筛率 × 转化率；两条可观测止损线', f: '../output/秋招破局方案.html', h: true },
    { n: '投递台账 108 家', d: '五层分组 S16 / A28 / B35 / C21 / D8 + 硬窗口日历', f: '../output/秋招投递台账.html', h: true },
    { n: '简历族（母版+3 方向）', d: '事实不变、表达自由；只改母版再派生', f: '../output/resume/刘宇广-AI应用开发-2027届.html', h: true },
    { n: '面试复盘报告', d: '乐元素 · 线上 AI 业务推演的实测评分与缺失模块', f: 'reviews/', h: true },
    { n: '网申开放题作答', d: '逐条最优版本，纯文本可直接粘进表单', f: '../output/网申开放题作答-刘宇广.md', h: false }
  ].forEach(function (r, i) {
    nodes.push({
      hall: 'field', id: 'a' + i, name: r.n, ratio: 0, untrained: true,
      desc: r.d, href: r.h ? r.f : ob(r.f), lines: []
    });
  });

  // ⑤ 书架·读过的：挂了读厚卡的书可训练（等级挂 card/{id}），其余是读完只留下概念的灰册
  var byBook = {};
  ((window.MARVIS_CARDS && window.MARVIS_CARDS.principles) || []).forEach(function (c) {
    if (!byBook[c.source]) byBook[c.source] = { cards: [], author: c.author, href: c.source_href };
    byBook[c.source].cards.push(c);
  });
  Object.keys(byBook).forEach(function (src) {
    var b = byBook[src], tot = b.cards.length, got = 0, rSum = 0;
    var lines = b.cards.map(function (c) {
      var l = lvOf('card/' + c.id);
      rSum += (l >= 2 ? 1 : (l >= 1 ? 0.5 : 0));
      if (l >= 1) got++;
      return { n: c.name, href: 'cards.html#card-' + c.id, lv: l, card: true, cid: c.id, one: c.one };
    });
    nodes.push({
      hall: 'books', id: src, name: src,
      ratio: tot ? rSum / tot : 0, tot: tot, got: got,
      desc: (b.author ? b.author + ' · ' : '') + '读厚 ' + tot + ' 张 · 遇到情境知道怎么做',
      href: b.href ? ob(b.href) : 'cards.html', lines: lines
    });
  });
  [
    { n: '心态制胜', d: '行动规则整份的触发来源：自我1离线、自我2当班——还没读厚', f: 'reading/discussions/2026-09-06-心态制胜-discussion' },
    { n: '儒释道·道篇·身体与命功', d: '命功框架的来源：身体是电池——还没读厚', f: 'reading/notes/2026-09-09-儒释道-道篇-身体与命功' },
    { n: '二十岁困惑与目标制定', d: '二十岁三问；讨论全程留档——还没读厚', f: 'reading/discussions/2026-09-24-二十岁困惑与目标制定-discussion' },
    { n: '能力圈与位置价值', d: '不懂不做、位置决定价值——还没读厚', f: 'reading/notes/2026-09-25-能力圈与位置价值' }
  ].forEach(function (r, i) {
    nodes.push({ hall: 'books', id: 'l' + i, name: r.n, ratio: 0, untrained: true, desc: r.d, href: ob(r.f), lines: [] });
  });

  /* 掌握度三档（借数字花园的成熟度范式：人眼分不清十档深浅，三段一眼就懂）
     0 = 还没读进去（灰、薄册） · 1 = 正在读（厅色、中等厚） · 2 = 已读透（深色、最厚） */
  function lv3(n) {
    if (n.untrained) return 0;
    if (n.tot) return n.ratio >= 1 ? 2 : (n.ratio > 0 ? 1 : 0);
    return 0;
  }
  var LV_WORD = ['还没读进去', '正在读', '已读透'];

  document.getElementById('legend').innerHTML =
    HALLS.map(function (h) {
      return '<span><span class="k" style="background:' + h.css + '"></span>' + h.name + '</span>';
    }).join('') +
    '<span><span class="k" style="background:#B4B2A9"></span>灰薄册 = 还没读进去</span>' +
    '<span>越厚越实 = 练得越透</span>' +
    '<span>半透明虚影 = 还没长出来的部分</span>';

  // 整体掌握度沿用旧口径（本事+作品），内化线（准则+读厚卡）单列一个数
  var techNodes = nodes.filter(function (n) { return n.hall === 'tech' || n.hall === 'work'; });
  var G = 0, T = 0;
  techNodes.forEach(function (n) { G += n.got || 0; T += n.tot || 0; });
  var overall = T ? Math.round(G / T * 100) : 0;
  var neuNodes = nodes.filter(function (n) {
    return (n.hall === 'os' || n.hall === 'books') && !n.untrained;
  });
  var NG = 0, NT = 0;
  neuNodes.forEach(function (n) { NG += n.got || 0; NT += n.tot || 0; });
  var internal = NT ? Math.round(NG / NT * 100) : 0;

  var bars = document.getElementById('bars');
  HALLS.forEach(function (h) {
    var list = nodes.filter(function (n) { return n.hall === h.k; });
    var trained = list.filter(function (n) { return !n.untrained; });
    var pct = 0;
    if (trained.length) {
      var g = 0, t = 0;
      trained.forEach(function (n) { g += n.got; t += n.tot; });
      pct = t ? Math.round(g / t * 100) : 0;
    }
    var un = list.filter(function (n) { return n.untrained; }).length;
    var d = document.createElement('div');
    d.className = 'bar';
    d.innerHTML = '<small>' + h.name + (un ? ' · ' + un + ' 项未读厚' : '') + '</small>' +
      '<strong>' + (trained.length ? pct + '%' : '—') + '</strong>' +
      '<div class="track"><i style="width:' + (trained.length ? pct : 0) + '%;background:' + h.css + '"></i></div>';
    bars.appendChild(d);
  });

  var PROFILE = { name: '刘宇广 · 2027 届', who: '南华大学本科 · 求职 AI 应用开发 / Agent 后端' };

  function panelCore() {
    var p = document.getElementById('panel');
    var cnt = [0, 0, 0];
    nodes.forEach(function (n) { cnt[lv3(n)]++; });
    p.innerHTML = '<h3>' + PROFILE.name + '</h3>' +
      '<div class="meta">' + PROFILE.who + '</div>' +
      '<div class="meta">已接入派单的部分掌握度 <b>' + overall + '%</b>（' + G + '/' + T + '） · ' +
      '内化线（准则 + 读厚卡）<b>' + internal + '%</b>（' + NG + '/' + NT + '）</div>' +
      '<div class="meta">这座书架共 ' + nodes.length + ' 本：已读透 <b>' + cnt[2] +
      '</b> · 正在读 <b>' + cnt[1] + '</b> · 还没读进去 <b>' + cnt[0] + '</b></div>' +
      '<div style="margin-top:10px"><a class="mv-btn mv-btn-primary" href="progress.html" style="text-decoration:none">去进度页</a>' +
      ' <a class="mv-btn" href="cards.html" style="text-decoration:none">去内化馆</a></div>';
    nodes.forEach(function (x) { if (x.label) x.label.classList.remove('hot'); });
  }

  function fallback2D(reason) {
    var st = document.getElementById('stage');
    st.style.height = 'auto';
    st.innerHTML = '<p class="mv-note" style="margin:10px 0 0">已降级为 2D 列表（' +
      reason + '）。内容与下钻完全一样，只是不立体。</p>';
    var fb = document.createElement('div');
    fb.className = 'fallback';
    HALLS.forEach(function (h) {
      var box = document.createElement('div');
      box.className = 'fb-hall';
      box.innerHTML = '<h4>' + h.name + '</h4>';
      nodes.filter(function (n) { return n.hall === h.k; }).forEach(function (n) {
        var a = document.createElement('a');
        var lv = lv3(n);
        a.textContent = (lv === 2 ? '● ' : lv === 1 ? '◐ ' : '○ ') + n.name +
          (n.tot ? '（' + n.got + '/' + n.tot + '）' : '');
        a.href = n.href || 'progress.html';
        box.appendChild(a);
      });
      fb.appendChild(box);
    });
    st.appendChild(fb);
    panelCore();
  }
  if (typeof THREE === 'undefined') { fallback2D('three.js 未加载'); return; }

  // ── 3D：一面书架墙 ────────────────────────────────────────
  var stage = document.getElementById('stage');
  var canvas = document.getElementById('cv');
  var labelBox = document.getElementById('labels');
  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  } catch (e) {
    fallback2D('这台机器/浏览器没有可用的 WebGL');
    return;
  }
  renderer.setClearColor(0x000000, 0);          // 透明背景，透出 CSS 的暖色晕染
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(40, 1, 0.1, 400);

  // 布光：半球光铺环境底色 + 一盏暖主光负责投影（光位偏正前上，影子短而干净）+ 冷补光拉层次
  scene.add(new THREE.HemisphereLight(0xfff6e8, 0x9a8468, 0.92));
  var lk = new THREE.DirectionalLight(0xfff1dc, 1.0);
  lk.position.set(4, 22, 20);
  lk.castShadow = true;
  lk.shadow.mapSize.set(2048, 2048);
  lk.shadow.camera.left = -26; lk.shadow.camera.right = 26;
  lk.shadow.camera.top = 20; lk.shadow.camera.bottom = -6;
  lk.shadow.camera.near = 1; lk.shadow.camera.far = 80;
  lk.shadow.bias = -0.0006;
  scene.add(lk);
  var lf = new THREE.DirectionalLight(0xdfe8ff, 0.28);
  lf.position.set(-10, 5, 9);
  scene.add(lf);

  var meshes = [];
  var BOOK_H = 3.3, BOOK_D = 1.7, GAP_B = 0.07, PAD = 0.55;
  function bookW(lv) { return [0.44, 0.66, 0.92][lv]; }

  // —— 纹理套件（全部 canvas 现画，零外部依赖；sRGB 标记保证输出色彩正确）——
  function srgb(t) { t.encoding = THREE.sRGBEncoding; return t; }

  // 木纹：底色 + 克制的深浅细条纹（层板与背板共用一套画法，换底色即可）
  function woodTex(base, w, h) {
    var c = document.createElement('canvas'); c.width = w; c.height = h;
    var g = c.getContext('2d');
    g.fillStyle = base; g.fillRect(0, 0, w, h);
    for (var i = 0; i < 60; i++) {
      g.fillStyle = 'rgba(52,36,22,' + (0.03 + Math.random() * 0.05).toFixed(3) + ')';
      g.fillRect(0, Math.random() * h, w, Math.random() * 1.3 + 0.3);
    }
    for (var j = 0; j < 18; j++) {
      g.fillStyle = 'rgba(255,240,214,' + (0.03 + Math.random() * 0.05).toFixed(3) + ')';
      g.fillRect(0, Math.random() * h, w, Math.random() * 1.2 + 0.3);
    }
    var t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return srgb(t);
  }
  var plankMat = new THREE.MeshStandardMaterial({ map: woodTex('#96744f', 256, 64), roughness: 0.78 });
  var boardMat = new THREE.MeshStandardMaterial({ map: woodTex('#5c4834', 512, 256), roughness: 0.9 });

  // 书页侧纹：奶白纸面 + 细密页线——书架上「这是一本书」的另一半证据
  var pagesMat = (function () {
    var c = document.createElement('canvas'); c.width = 64; c.height = 256;
    var g = c.getContext('2d');
    g.fillStyle = '#f1e8d4'; g.fillRect(0, 0, 64, 256);
    for (var y = 4; y < 252; y += 3) {
      g.fillStyle = 'rgba(172,148,108,' + (y % 9 === 0 ? 0.26 : 0.15) + ')';
      g.fillRect(2, y, 60, 1);
    }
    g.fillStyle = 'rgba(118,94,62,.28)'; g.fillRect(0, 0, 2, 256); g.fillRect(62, 0, 2, 256);
    return new THREE.MeshStandardMaterial({ map: srgb(new THREE.CanvasTexture(c)), roughness: 0.88 });
  })();

  // 书脊：竖排书名（楷体烫金）+ 装帧带 + 曲面明暗（左受光右背光），字号随字数自适应（最长 12 字）
  function spineTex(text, col, wpx, lv) {
    var c = document.createElement('canvas');
    c.width = wpx; c.height = 340;
    var g = c.getContext('2d');
    g.fillStyle = '#' + col.getHexString(); g.fillRect(0, 0, wpx, 340);
    var gr = g.createLinearGradient(0, 0, wpx, 0);
    gr.addColorStop(0, 'rgba(255,255,255,.30)');
    gr.addColorStop(0.2, 'rgba(255,255,255,.05)');
    gr.addColorStop(0.72, 'rgba(0,0,0,0)');
    gr.addColorStop(1, 'rgba(0,0,0,.22)');
    g.fillStyle = gr; g.fillRect(0, 0, wpx, 340);
    g.fillStyle = 'rgba(0,0,0,.16)';
    g.fillRect(0, 10, wpx, 7); g.fillRect(0, 323, wpx, 7);
    g.fillStyle = 'rgba(255,249,238,.5)';
    g.fillRect(wpx * 0.5 - 5, 26, 10, 2); g.fillRect(wpx * 0.5 - 5, 312, 10, 2);
    var name = String(text).replace(/\s+/g, '');
    var chars = name.slice(0, 12).split('');
    var fit = Math.max(18, Math.min(38, Math.floor(250 / chars.length)));
    var step = fit * 1.22;
    var y0 = 170 - (chars.length - 1) * step / 2;
    // 书名用楷体（书法感）+ 烫金渐变 + 深色描边——任何书脊色上都醒目
    g.font = '600 ' + fit + 'px "KaiTi","STKaiti","楷体","Noto Serif SC","Microsoft YaHei",serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.lineWidth = Math.max(2, fit * 0.10);
    g.strokeStyle = 'rgba(42,26,10,.55)';
    g.lineJoin = 'round';
    var gold = g.createLinearGradient(0, y0 - chars.length * step / 2, 0, y0 + chars.length * step / 2);
    gold.addColorStop(0, '#fff3cf');
    gold.addColorStop(0.5, '#f7dfa4');
    gold.addColorStop(1, '#e8c078');
    g.fillStyle = lv === 0 ? 'rgba(255,240,206,.82)' : gold;
    chars.forEach(function (ch, i) {
      g.strokeText(ch, wpx / 2, y0 + i * step);
      g.fillText(ch, wpx / 2, y0 + i * step);
    });
    return srgb(new THREE.CanvasTexture(c));
  }

  // 书色：厅色为底，未练的掺灰（仍看得出属于哪个区），已读透的压深；同排书加微差避免「复制粘贴」感
  function bookColor(h, lv, i) {
    var c = new THREE.Color(h.color);
    if (lv === 0) c.lerp(new THREE.Color(0xcec7b8), 0.55);
    else if (lv === 2) c.lerp(new THREE.Color(h.dark), 0.45);
    var hsl = { h: 0.6, s: 0.5, l: 0.5 };
    c.getHSL(hsl);
    c.setHSL((hsl.h + ((i * 0.37) % 1 - 0.5) * 0.018 + 1) % 1,
             Math.max(0.06, Math.min(0.85, hsl.s + ((i * 0.61) % 1 - 0.5) * 0.10)),
             Math.max(0.16, Math.min(0.72, hsl.l + ((i * 0.23) % 1 - 0.5) * 0.07)));
    c.convertSRGBToLinear();
    return c;
  }

  // 每区预留的虚影书位：一眼看到「还没长出来的部分」
  var GHOSTS = { tech: 2, work: 0, os: 0, field: 0, books: 1 };

  // 分组：每厅一组竖排书
  var groups = HALLS.map(function (h) {
    var list = nodes.filter(function (n) { return n.hall === h.k; });
    var w = 0;
    list.forEach(function (n, i) { w += bookW(lv3(n)) + (i ? GAP_B : 0); });
    var ng = GHOSTS[h.k] || 0;
    if (ng) w += list.length ? GAP_B : 0;
    w += ng * (0.5 + GAP_B);
    var avg = 0;
    list.forEach(function (n) { avg += lv3(n); });
    avg = list.length ? avg / list.length : 0;
    return { h: h, list: list, ghosts: ng, w: w + PAD * 2, avg: avg };
  });

  // 两行布局：第一行 本事+作品，第二行 操作系统+战场+书架（按实际书宽算，不写死）
  var ROWS = [['tech', 'work'], ['os', 'field', 'books']];
  var ROW_GAP = 0.8;
  function rowWidth(ids) {
    var w = 0;
    ids.forEach(function (id, i) {
      var g = groups.filter(function (x) { return x.h.k === id; })[0];
      if (g) w += g.w + (i ? ROW_GAP : 0);
    });
    return w;
  }
  var WALL_W = Math.max(rowWidth(ROWS[0]), rowWidth(ROWS[1]));
  var X0 = -WALL_W / 2;

  var SHELF_Y = [4.5, 0];          // 两行层板的顶面高度
  var TOP_Y = SHELF_Y[0] + BOOK_H + 1.3;   // 顶部铭牌中心

  // 背板
  var board = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_W + 0.5, TOP_Y - SHELF_Y[1] + BOOK_H + 1.0, 0.25),
    boardMat
  );
  board.position.set(0, (TOP_Y - 1.0 + SHELF_Y[1]) / 2 + 0.2, -BOOK_D / 2 - 0.3);
  board.receiveShadow = true;
  scene.add(board);

  groups.forEach(function (grp) {
    var h = grp.h;
    var ri = 0, idx = 0;
    ROWS.forEach(function (ids, r) {
      ids.forEach(function (id, j) {
        if (id === h.k) { ri = r; idx = j; }
      });
    });
    var rowIds = ROWS[ri];
    var gx = -rowWidth(rowIds) / 2;   // 每行各自居中，行内组数和宽度不同也能对住
    for (var j = 0; j < rowIds.length; j++) {
      var g2 = groups.filter(function (x) { return x.h.k === rowIds[j]; })[0];
      if (rowIds[j] === h.k) break;
      gx += g2.w + ROW_GAP;
    }
    var baseY = SHELF_Y[ri];

    // 层板：木纹 + 接收投影
    var plank = new THREE.Mesh(
      new THREE.BoxGeometry(grp.w, 0.22, BOOK_D + 0.35),
      plankMat
    );
    plank.position.set(gx + grp.w / 2, baseY - 0.11, 0);
    plank.castShadow = true; plank.receiveShadow = true;
    scene.add(plank);

    // 一本书 = 一个条目
    var cx = gx + PAD;
    grp.list.forEach(function (n, bi) {
      var lv = lv3(n);
      var w = bookW(lv);
      var bh = BOOK_H * (0.93 + ((bi * 0.23) % 1) * 0.13);   // 书高微差，一排书才有真实感
      var col = bookColor(h, lv, bi);
      var spine = new THREE.MeshStandardMaterial({
        map: spineTex(n.name, col, lv === 0 ? 62 : (lv === 1 ? 88 : 118), lv),
        roughness: 0.58, metalness: 0.02
      });
      // 非书脊的五个面全是纸纹侧面——书脊是布面装帧，书芯是奶白纸块
      var book = new THREE.Mesh(
        new THREE.BoxGeometry(w, bh, BOOK_D),
        [pagesMat, pagesMat, pagesMat, pagesMat, spine, pagesMat]
      );
      book.position.set(cx + w / 2, baseY + bh / 2, 0);
      book.userData.homeZ = 0;
      book.castShadow = true; book.receiveShadow = true;
      scene.add(book);
      n.mesh = book;
      meshes.push(book);

      var lb = document.createElement('div');
      lb.className = 'lbl';
      lb.textContent = n.name;
      lb.style.display = 'none';     // 名字在书脊上，标签只在悬停时出
      lb.addEventListener('click', function (e) { e.stopPropagation(); openBook(n); });
      labelBox.appendChild(lb);
      n.label = lb;

      cx += w + GAP_B;
    });

    // 虚影书位：虚线描边的空位——一眼读出「这里预留着一本还没长出来的书」
    for (var gi = 0; gi < grp.ghosts; gi++) {
      var gw = 0.5;
      var gl = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(gw, BOOK_H * 0.97, BOOK_D)),
        new THREE.LineDashedMaterial({ color: 0x8a7460, dashSize: 0.3, gapSize: 0.18, transparent: true, opacity: 0.6 })
      );
      gl.computeLineDistances();
      gl.position.set(cx + gw / 2, baseY + BOOK_H * 0.485, 0);
      scene.add(gl);
      cx += gw + GAP_B;
    }

    // 区名标签
    var hl = document.createElement('div');
    hl.className = 'lbl hall-lbl';
    hl.innerHTML = '<b>' + h.name + '</b><i>' + grp.list.length + ' 本</i>';
    labelBox.appendChild(hl);
    h.label = hl;
    h.anchor = new THREE.Vector3(gx + grp.w / 2, baseY + BOOK_H + 0.55, 0.6);
  });

  // 顶部铭牌 = 我（深木纹 + 双描边 + 暖金字）
  var nameCanvas = document.createElement('canvas');
  nameCanvas.width = 1024; nameCanvas.height = 128;
  (function () {
    var g = nameCanvas.getContext('2d');
    g.fillStyle = '#6b5138'; g.fillRect(0, 0, 1024, 128);
    for (var i = 0; i < 40; i++) {
      g.fillStyle = 'rgba(30,20,12,' + (0.05 + Math.random() * 0.09).toFixed(3) + ')';
      g.fillRect(0, Math.random() * 128, 1024, Math.random() * 1.8 + 0.5);
    }
    g.strokeStyle = 'rgba(243,223,178,.55)'; g.lineWidth = 3;
    g.strokeRect(8, 8, 1008, 112);
    g.strokeStyle = 'rgba(243,223,178,.22)'; g.lineWidth = 1;
    g.strokeRect(17, 17, 990, 94);
    g.fillStyle = '#f3dfb2';
    g.font = '600 30px "KaiTi","STKaiti","楷体","Noto Serif SC","Microsoft YaHei",serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(PROFILE.name + ' · AI 应用开发 / Agent 后端 · 整体 ' + overall + '% · 内化 ' + internal + '%', 512, 66);
  })();
  var plaqueSide = new THREE.MeshStandardMaterial({ color: 0x6b5138, roughness: 0.8 });
  var plaque = new THREE.Mesh(
    new THREE.BoxGeometry(Math.min(WALL_W, 13.5), 1.3, 0.32),
    [
      plaqueSide, plaqueSide, plaqueSide, plaqueSide,
      new THREE.MeshStandardMaterial({ map: srgb(new THREE.CanvasTexture(nameCanvas)), roughness: 0.7 }),
      plaqueSide
    ]
  );
  plaque.position.set(0, TOP_Y, 0);
  plaque.castShadow = true; plaque.receiveShadow = true;
  scene.add(plaque);
  meshes.push(plaque);

  var coreLbl = document.createElement('div');
  coreLbl.className = 'lbl hall-lbl';
  coreLbl.innerHTML = '<b>我</b><i>整体 ' + overall + '% · 内化 ' + internal + '%</i>';
  coreLbl.style.display = 'none';
  coreLbl.addEventListener('click', function (e) { e.stopPropagation(); panelCore(); });
  labelBox.appendChild(coreLbl);
  var coreAnchor = new THREE.Vector3(0, TOP_Y, 0.8);

  // ── 翻开一本书：左页概要/前序，右页目录（2026-10-03 晚，按主人「点书翻开」的意象）──
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function mdInline(s) {   // 只认 **加粗** 一种标记——概要/前序来自模块卡与地基包，别让星号露出来
    return esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  }
  function dot(lv) { return lv >= 2 ? '●' : (lv >= 1 ? '◐' : '○'); }
  function bkEl(id) { return document.getElementById(id); }
  function tocRow(href, lv, name, sub) {
    var a = document.createElement('a');
    a.className = 'bk-row';
    if (href) { a.href = href; a.target = '_blank'; }
    a.innerHTML = '<span class="bk-dot">' + dot(lv || 0) + '</span>' +
      '<span class="bk-row-name">' + esc(name) + '</span>' +
      (sub ? '<span class="bk-row-sub">' + esc(sub) + '</span>' : '');
    return a;
  }
  function actBtn(href, label, primary) {
    var a = document.createElement('a');
    a.className = 'mv-btn' + (primary ? ' mv-btn-primary' : '');
    a.href = href; a.target = '_blank';
    a.textContent = label;
    return a;
  }
  function groundOf(moduleName) {
    var g = null;
    ((window.MARVIS_CARDS && window.MARVIS_CARDS.grounds) || []).forEach(function (x) {
      if (x.module === moduleName) g = x;
    });
    return g;
  }
  function openBook(n) {
    var h = HALLS.filter(function (x) { return x.k === n.hall; })[0];
    var lv = lv3(n);
    bkEl('bk-strip').style.background = h.css;
    var tag = bkEl('bk-tag');
    tag.textContent = h.name;
    tag.style.background = h.css;
    bkEl('bk-title').textContent = n.name;
    var meta = ['状态：' + LV_WORD[lv]];
    if (n.tot) meta.push('掌握度 ' + Math.round(n.ratio * 100) + '%（' + n.got + '/' + n.tot + '）');
    bkEl('bk-meta').textContent = meta.join(' · ');

    var abs = bkEl('bk-abs'), pre = bkEl('bk-pre');
    var preSec = bkEl('bk-pre-sec');
    var toc = bkEl('bk-toc'); toc.innerHTML = '';
    var acts = bkEl('bk-actions'); acts.innerHTML = '';

    if (n.hall === 'tech') {
      var key = n.canon || n.name;   // 正本模块名（Redis 与缓存 → Redis）
      var m = (window.MARVIS_MODULES || []).filter(function (x) { return x.module === key; })[0] || {};
      var g = groundOf(key);
      var contents = m.contents || [];   // 先声明——下面的前序兜底要用（var 提升但赋值不提升）
      abs.innerHTML = mdInline((g && g.positioning) || m.summary || n.desc);
      var preTxt = (g && g.model) || m.reason || '';
      if (!preTxt && contents.length) {
        // 模块卡没写一句话结论 / 为什么现在时，用主线问题串当前序（引用式组装，不复制正文）
        preTxt = '本书依次回答 ' + contents.length + ' 问：' +
          contents.map(function (c) { return '「' + (c.lead || c.name) + '」'; }).join('；') + '。';
      }
      pre.innerHTML = mdInline(preTxt);
      preSec.style.display = preTxt ? '' : 'none';
      n.lines.forEach(function (ln, i) {
        var c = contents[i] || {};
        var sub = [];
        if (c.lead) sub.push(c.lead);
        if (c.topics) sub.push(c.topics + ' 母题');
        toc.appendChild(tocRow(ln.href, ln.lv, (c.no ? c.no + ' · ' : '') + ln.n, sub.join(' · ')));
      });
      acts.appendChild(actBtn(n.href, '打开模块概览', true));
      if (g) acts.appendChild(actBtn('cards.html#' + g.id, '地基包', false));
    } else if (n.hall === 'work') {
      abs.innerHTML = mdInline(n.desc);
      preSec.style.display = 'none';
      n.lines.forEach(function (ln) {
        toc.appendChild(tocRow(ln.href, ln.lv, ln.n,
          ln.lv >= 2 ? '讲透了' : (ln.lv >= 1 ? '讲得出' : '还没练')));
      });
      acts.appendChild(actBtn(n.href, '打开口述页', true));
    } else if (n.hall === 'os' && n.rule) {
      abs.innerHTML = mdInline(n.rule.action);
      pre.innerHTML = mdInline(n.rule.scene);
      preSec.style.display = '';
      toc.appendChild(tocRow('rules.html#r-' + n.rule.id, lv, '去训练这条准则', '情境 → 动作'));
      toc.appendChild(tocRow(ob(n.rule.src), null, '打开正本', n.rule.src));
      acts.appendChild(actBtn('rules.html#r-' + n.rule.id, '去训练', true));
    } else if (n.hall === 'books' && n.lines && n.lines.length) {
      abs.innerHTML = mdInline(n.desc);
      var uses = 0;
      n.lines.forEach(function (ln) { uses += ((B.uses[ln.cid] || []).length); });
      pre.textContent = '读厚 ' + n.lines.length + ' 张 · 「会了」' + n.got +
        ' 张 · 真实用上 ⚡' + uses + ' 次';
      preSec.style.display = '';
      n.lines.forEach(function (ln) {
        toc.appendChild(tocRow(ln.href, ln.lv, ln.n, ln.one || '读厚卡'));
      });
      if (n.href && n.href.indexOf('cards.html') !== 0) acts.appendChild(actBtn(n.href, '阅读闭环', false));
      acts.appendChild(actBtn('cards.html', '去内化馆', true));
    } else {
      abs.innerHTML = mdInline(n.desc || '这本书还没写概要——在内化馆给它写读厚卡，书页就会长出内容。');
      preSec.style.display = 'none';
      if (n.href) {
        toc.appendChild(tocRow(n.href, null, '打开原文 / 页面', ''));
        acts.appendChild(actBtn(n.href, '打开', true));
      }
    }

    var mask = bkEl('bookmask');
    mask.hidden = false;
    requestAnimationFrame(function () { mask.classList.add('open'); });
    try { history.replaceState(null, '', '#book-' + encodeURIComponent(n.name)); } catch (e) {}
    nodes.forEach(function (x) { if (x.label) x.label.classList.toggle('hot', x === n); });
  }
  function closeBook() {
    var mask = bkEl('bookmask');
    mask.classList.remove('open');
    mask.hidden = true;
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) {}
    nodes.forEach(function (x) { if (x.label) x.label.classList.remove('hot'); });
  }
  window.closeBook = closeBook;
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeBook(); });

  // ── 相机：正面平视，只允许小幅左右转 ──────────────────────
  var theta = 0, phi = 1.40, dist = 21.5;
  var drag = false, px = 0, py = 0;
  stage.addEventListener('mousedown', function (e) {
    drag = true; px = e.clientX; py = e.clientY; stage.classList.add('dragging');
  });
  window.addEventListener('mouseup', function () { drag = false; stage.classList.remove('dragging'); });
  window.addEventListener('mousemove', function (e) {
    if (!drag) return;
    theta -= (e.clientX - px) * 0.004;
    theta = Math.max(-0.46, Math.min(0.46, theta));   // ±26°：能看侧面，不会转到迷路
    phi -= (e.clientY - py) * 0.003;
    phi = Math.max(1.18, Math.min(1.52, phi));
    px = e.clientX; py = e.clientY;
  });
  stage.addEventListener('wheel', function (e) {
    e.preventDefault();
    dist = Math.max(7, Math.min(34, dist + e.deltaY * 0.014));
  }, { passive: false });

  var raycaster = new THREE.Raycaster(), mouse = new THREE.Vector2();
  function pick(e) {
    var r = canvas.getBoundingClientRect();
    mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
    mouse.y = -((e.clientY - r.top) / r.height) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    return raycaster.intersectObjects(meshes, false)[0];
  }
  stage.addEventListener('click', function (e) {
    var hit = pick(e);
    if (!hit) return;
    if (hit.object === plaque) { panelCore(); return; }
    var n = nodes.filter(function (x) { return x.mesh === hit.object; })[0];
    if (n) openBook(n);
  });

  var hovered = null;
  stage.addEventListener('mousemove', function (e) {
    if (drag) return;
    var hit = pick(e);
    var n = hit ? nodes.filter(function (x) { return x.mesh === hit.object; })[0] : null;
    if (n !== hovered) {
      if (hovered && hovered.mesh) hovered.mesh.position.z = hovered.mesh.userData.homeZ || 0;
      if (n && n.mesh) n.mesh.position.z = 0.55;      // 抽出来一点，像从架上取下
      hovered = n;
    }
    nodes.forEach(function (x) { if (x.label) x.label.classList.toggle('hot', x === n); });
    stage.style.cursor = (hit || n) ? 'pointer' : '';
  });

  function resize() {
    var w = stage.clientWidth, h = stage.clientHeight;
    renderer.setSize(w, h, false);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize);
  resize();

  var v = new THREE.Vector3();
  function place(lb, vec) {
    v.copy(vec).project(camera);
    var w = stage.clientWidth, h = stage.clientHeight;
    lb.style.left = ((v.x * 0.5 + 0.5) * w) + 'px';
    lb.style.top = ((-v.y * 0.5 + 0.5) * h) + 'px';
    if (v.z <= 1) lb.style.visibility = 'visible';
  }

  panelCore();

  (function loop() {
    requestAnimationFrame(loop);
    camera.position.set(
      dist * Math.sin(phi) * Math.sin(theta),
      dist * Math.cos(phi),
      dist * Math.sin(phi) * Math.cos(theta)
    );
    camera.lookAt(0, 4.5, 0);   // 对准整面墙的中部（含顶部铭牌），否则铭牌会被裁掉
    renderer.render(scene, camera);

    HALLS.forEach(function (h) { if (h.label) place(h.label, h.anchor); });
    place(coreLbl, coreAnchor);
    if (hovered && hovered.label) place(hovered.label, hovered.mesh.position.clone().add(new THREE.Vector3(0, BOOK_H / 2 + 0.45, 0.6)));
  })();

  // ── 今日内化侧栏 ───────────────────────────────────────────
  (function buildSide() {
    // ① 今日到期（与技术主线同一套 due 数据）
    var t = todayStr(), due = 0;
    (window.MARVIS_CLUSTERS || []).forEach(function (c) {
      if (c.zone !== '一档' && c.zone !== '二档') return;
      c.topics.forEach(function (tp) {
        var s = S.lv[c.id + '/' + tp.id];
        if (s && s.due && s.due <= t && s.l >= 1) due++;
      });
    });
    [window.MARVIS_RULE_CLUSTER, window.MARVIS_CARD_CLUSTER].forEach(function (c) {
      if (!c) return;
      c.topics.forEach(function (tp) {
        var s = S.lv[c.id + '/' + tp.id];
        if (s && s.due && s.due <= t && s.l >= 1) due++;
      });
    });
    document.getElementById('side-due').innerHTML =
      '<h4>今日到期 <em>复训阶梯 1 / 3 / 7 / 14 天</em></h4>' +
      '<div class="side-big">' + due + '<small> 条等着被提取</small></div>' +
      '<p class="side-note">' + (due ? '逾期久的排前面。提取（闭卷讲）比重看有效得多。' : '今天没有到期复训——去推进新主线或用加餐多长一块。') + '</p>' +
      '<div class="side-btns"><a class="mv-btn mv-btn-primary" href="progress.html" style="text-decoration:none">去进度页清账</a></div>';

    // ② 今日情境：准则 + 原则卡里按日期轮换一张（每天换，不用挑）
    var pool = [];
    (window.MARVIS_RULES || []).forEach(function (r) {
      pool.push({ kind: 'rule', id: r.id, name: r.name, src: '行事准则', scene: r.scene, action: r.action, href: 'rules.html#r-' + r.id });
    });
    ((window.MARVIS_CARDS && window.MARVIS_CARDS.principles) || []).forEach(function (c) {
      pool.push({ kind: 'card', id: c.id, name: c.name, src: c.source, scene: c.scene, action: c.action, href: 'cards.html#card-' + c.id });
    });
    var d = new Date();
    var di = d.getFullYear() * 372 + (d.getMonth() + 1) * 31 + d.getDate();
    var pick = pool.length ? pool[di % pool.length] : null;
    var usesN = pick ? (B.uses[pick.id] || []).length : 0;
    document.getElementById('side-situ').innerHTML =
      '<h4>今日情境 <em>' + (pick ? (pick.kind === 'rule' ? '行事准则' : '读厚原则卡') : '') + '</em></h4>' +
      (pick
        ? '<div style="font-size:15px;font-weight:500">' + pick.name + ' <span style="font-size:11px;color:#888780">' + pick.src + '</span></div>' +
          '<div class="situ"><b>情境</b>　' + pick.scene +
          '<details><summary>想好了，对一下标准动作</summary><div style="margin-top:6px">' + pick.action + '</div></details></div>' +
          '<div class="side-btns">' +
          '<a class="mv-btn mv-btn-primary" href="' + pick.href + '" style="text-decoration:none">去训练</a>' +
          '<button class="mv-btn" type="button" onclick="marvisUse(\'' + pick.id + '\')">⚡ 记一笔：今天用上了</button>' +
          '</div>' +
          '<p class="side-note">这张卡真实用过 <b id="situ-use">' + usesN + '</b> 次。内化 = 概念变成动作，动作被真实场景反复提取。</p>'
        : '<p class="side-note">还没有可轮换的情境卡——先读一本书，写一份读厚正本。</p>');

    // ③ 内化进度
    var rGot = 0, rTot = (window.MARVIS_RULES || []).length;
    (window.MARVIS_RULES || []).forEach(function (r) { if (lvOf('rule/' + r.id) >= MASTER) rGot++; });
    var cAll = (window.MARVIS_CARDS && window.MARVIS_CARDS.principles) || [];
    var cGot = 0, cTot = cAll.length;
    cAll.forEach(function (c) { if (lvOf('card/' + c.id) >= MASTER) cGot++; });
    function mini(label, got, tot, color) {
      var pct = tot ? Math.round(got / tot * 100) : 0;
      return '<div style="margin-top:8px"><div style="display:flex;justify-content:space-between;font-size:12px">' +
        '<span>' + label + '</span><span style="color:#888780">' + got + '/' + tot + '</span></div>' +
        '<div class="mini-track"><i style="width:' + pct + '%;background:' + color + '"></i></div></div>';
    }
    document.getElementById('side-progress').innerHTML =
      '<h4>内化进度 <em>「会了」以上的条目</em></h4>' +
      mini('行事准则', rGot, rTot, '#7F77DD') +
      mini('读厚原则卡', cGot, cTot, '#D85A30') +
      '<div class="side-btns" style="margin-top:10px">' +
      '<a class="mv-btn" href="cards.html" style="text-decoration:none">内化馆</a>' +
      '<a class="mv-btn" href="rules.html" style="text-decoration:none">行事准则</a></div>';
  })();

  // ⚡ 打卡：真实用上一次（存 mv.brain.v1，随 mv.* 云同步；内化馆同键可见）
  window.marvisUse = function (id) {
    var note = prompt('在哪用上的？（一句话，可留空）', '');
    if (note === null) return;
    B.uses[id] = B.uses[id] || [];
    B.uses[id].push({ d: todayStr(), note: (note || '').trim() });
    try { localStorage.setItem(BKEY, JSON.stringify(B)); } catch (e) {}
    var el = document.getElementById('situ-use');
    if (el) el.textContent = (B.uses[id] || []).length;
  };

  // 深链：brain.html#book-<书名> 直接翻开那本书（分享 / 回归测试都用得上）
  (function () {
    var m = location.hash.match(/^#book-(.+)$/);
    if (!m) return;
    var nm = decodeURIComponent(m[1]);
    var n = nodes.filter(function (x) { return x.name === nm; })[0];
    if (n) openBook(n);
  })();

  window.MARVIS_BRAIN = { nodes: nodes, overall: overall, internal: internal, openBook: openBook };
})();
