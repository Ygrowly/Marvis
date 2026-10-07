# -*- coding: utf-8 -*-
"""第2期审查修复：入口残留三处+生成器锚点化 + 文档三处矛盾 + 共享 barHtml 消重复 + domains join 键约定。"""
import pathlib

ok = []

# ── A1. brain.html：books 厅点书面板两态按钮 + 删去内化馆 ──
bp = pathlib.Path("site/brain.html")
b = bp.read_text(encoding="utf-8")
old = """      if (n.href && n.href.indexOf('cards.html') !== 0) acts.appendChild(actBtn(n.href, '阅读闭环', false));
      acts.appendChild(actBtn('cards.html', '去内化馆', true));"""
new = """      if (n.href && n.href.indexOf('cards.html#') === 0) acts.appendChild(actBtn(n.href, '打开卡详情', true));
      else if (n.href) acts.appendChild(actBtn(n.href, '阅读闭环', false));"""
assert old in b, "A1 anchor"
b = b.replace(old, new, 1)

# A2. books 厅无正本的书不再回退 cards.html
old = "      href: b.href ? ob(b.href) : 'cards.html', lines: lines"
assert old in b
b = b.replace(old, "      href: b.href ? ob(b.href) : null, lines: lines", 1)

# A4. 点书面板"去进度页"→"回今日"；fallback2D 无 href 灰显
old = '<div style="margin-top:10px"><a class="mv-btn mv-btn-primary" href="progress.html" style="text-decoration:none">去进度页</a>\'</div>\';'
b = b.replace('href="progress.html" style="text-decoration:none">去进度页</a>',
              'href="index.html" style="text-decoration:none">回今日</a>', 1)
old = "        a.href = n.href || 'progress.html';"
assert old in b, "A4 fallback anchor"
b = b.replace(old, "        if (n.href) { a.href = n.href; } else { a.style.color = 'var(--mv-muted)'; a.style.cursor = 'default'; }", 1)

# A-extra. 头部 h1（上次替换未命中确认）——已确认成功，此处幂等
b = b.replace('<h1 class="mv-h1" style="margin:0">我的书架</h1>',
              '<h1 class="mv-h1" style="margin:0">人生画像 · 书架</h1>', 1)
bp.write_text(b, encoding="utf-8", newline="\n")
ok.append("brain.html：卡详情两态按钮 / href 回退 / 回今日 / fallback 灰显")

# ── A5. build.py：R 系 wikilink 锚点化（别名 100% 带 R\d+，无 id 则纯文本不留裸链） ──
bp2 = pathlib.Path("site/build.py")
s = bp2.read_text(encoding="utf-8")
old = """            if target in _RULE_BOOKS:
                return '<a href="rules.html">%s</a>' % esc(alias)
            return esc(alias)"""
new = """            if target in _RULE_BOOKS:
                m = re.search(r"\\bR\\d+\\b", alias)
                if m:   # 别名带 R 系 id → 直达 rules.html#r- 锚点（无锚裸链是治理事故）
                    return '<a href="rules.html#r-%s">%s</a>' % (m.group(0), esc(alias))
                return esc(alias)
            return esc(alias)"""
assert old in s, "A5 anchor"
s = s.replace(old, new, 1)
bp2.write_text(s, encoding="utf-8", newline="\n")
ok.append("build.py：R 系关联锚点化（生成器层根治）")

# ── C1. insight.js：barHtml + buildIndexFromWindow（消两页重复渲染） ──
ip = pathlib.Path("site/_components/insight.js")
s = ip.read_text(encoding="utf-8")
old = """  var api = { buildIndex: buildIndex, stageOf: stageOf, aggregate: aggregate,
              trained: trained, stageNames: STAGE_NAMES, stageCss: STAGE_CSS };"""
new = """  /* 从 window 全局自动取参建索引（今日页/画像页同参，测试传 global.window） */
  function buildIndexFromWindow(w) {
    w = w || (typeof window !== 'undefined' ? window : {});
    return buildIndex({ clusters: w.MARVIS_CLUSTERS, drill: w.MARVIS_DRILL,
      ruleCluster: w.MARVIS_RULE_CLUSTER, cards: w.MARVIS_CARDS,
      topicPage: w.MARVIS_TOPIC_PAGE });
  }

  /* 五档分段条 + 图例的唯一 HTML 实现。AGG = aggregate() 产出；
     opts.empty = 无数据域名数组（画像页按宪法显示「还没长」行）。 */
  function barHtml(AGG, opts) {
    opts = opts || {};
    var LBL = AGG.stageNames, COL = AGG.stageCss;
    var rows = AGG.domains.map(function (d) {
      var tot = d.total || 1;
      var segs = d.counts.map(function (c, i) {
        return c ? '<div style="width:' + (c / tot * 100) + '%;background:' + COL[i] +
          '" title="' + LBL[i] + ' ' + c + '"></div>' : '';
      }).join('');
      return '<div style="margin-bottom:.625rem">' +
        '<div style="display:flex;justify-content:space-between;font-size:.8125rem">' +
        '<span>' + d.name + '</span><span style="color:var(--mv-muted)">' + d.total + ' 正本 · ' +
        (d.internalized ? '内化中 ' + d.internalized : '训练待启动') + '</span></div>' +
        '<div style="display:flex;height:' + (opts.height || 6) + 'px;border-radius:3px;overflow:hidden">' + segs + '</div></div>';
    }).join('');
    var emptyRows = (opts.empty || []).map(function (name) {
      return '<div style="margin-bottom:.625rem"><div style="display:flex;justify-content:space-between;font-size:.8125rem">' +
        '<span style="color:var(--mv-muted)">' + name + '</span><span style="color:var(--mv-muted)">还没长</span></div>' +
        '<div style="display:flex;height:' + (opts.height || 6) + 'px;border-radius:3px;overflow:hidden;background:rgba(0,0,0,.05)"></div></div>';
    }).join('');
    var legend = '<div style="display:flex;gap:.75rem;font-size:.75rem;color:var(--mv-muted);margin-bottom:.75rem;flex-wrap:wrap">' +
      LBL.map(function (l, i) {
        return '<span><i style="display:inline-block;width:8px;height:8px;border-radius:2px;background:' + COL[i] + ';margin-right:4px"></i>' + l + '</span>';
      }).join('') + '</div>';
    return legend + rows + emptyRows;
  }

  var api = { buildIndex: buildIndex, buildIndexFromWindow: buildIndexFromWindow,
              barHtml: barHtml, stageOf: stageOf, aggregate: aggregate,
              trained: trained, stageNames: STAGE_NAMES, stageCss: STAGE_CSS };"""
assert old in s, "C1 anchor"
s = s.replace(old, new, 1)
ip.write_text(s, encoding="utf-8", newline="\n")
ok.append("insight.js：barHtml + buildIndexFromWindow")

# ── C2. index.html：渲染段改用 barHtml ──
ip = pathlib.Path("site/index.html")
s = ip.read_text(encoding="utf-8")
start = s.index("    /* ── 内化度五档：唯一实现已上移 _components/insight.js")
endm = "    var legend = '<div style=\"display:flex;gap:.75rem;font-size:.75rem;color:var(--mv-muted);margin-bottom:.75rem;flex-wrap:wrap\">'"
end = s.index(endm)
end = s.index(".join('') + '</div>';", end) + len(".join('') + '</div>';")
new_block = """    /* ── 内化度五档：实现与渲染都在 _components/insight.js（与画像页同一份） ── */
    var IDX = window.MarvisInsight.buildIndexFromWindow(window);
    var LV = {}, USES = {};
    try { var _ps = JSON.parse(localStorage.getItem('mv.progress.v1')) || {}; LV = _ps.lv || {}; } catch (e) {}
    try { var _bs = JSON.parse(localStorage.getItem('mv.brain.v1')); USES = (_bs && _bs.uses) || {}; } catch (e) {}
    var AGG = window.MarvisInsight.aggregate(window.MARVIS_INSIGHT, IDX, LV, USES);
    var bar = window.MarvisInsight.barHtml(AGG);"""
s = s[:start] + new_block + s[end:]
assert "box.innerHTML = legend + bar + list;" in s
s = s.replace("box.innerHTML = legend + bar + list;", "box.innerHTML = bar + list;", 1)
ip.write_text(s, encoding="utf-8", newline="\n")
ok.append("index.html：改用 barHtml")

# ── C3. brain.html：版图渲染改用 barHtml（空域走 opts.empty） + buildIndexFromWindow ──
bp = pathlib.Path("site/brain.html")
b = bp.read_text(encoding="utf-8")
old = """    var IDX = window.MarvisInsight.buildIndex({
      clusters: window.MARVIS_CLUSTERS, drill: window.MARVIS_DRILL,
      ruleCluster: window.MARVIS_RULE_CLUSTER, cards: window.MARVIS_CARDS,
      topicPage: window.MARVIS_TOPIC_PAGE
    });
    var AGG = window.MarvisInsight.aggregate(window.MARVIS_INSIGHT, IDX, (S.lv || {}), (B.uses || {}));"""
new = """    var IDX = window.MarvisInsight.buildIndexFromWindow(window);
    var AGG = window.MarvisInsight.aggregate(window.MARVIS_INSIGHT, IDX, (S.lv || {}), (B.uses || {}));"""
assert old in b, "C3 idx anchor"
b = b.replace(old, new, 1)

old = """    // ② 我的版图：域 × 五档矩阵（与今日页「内化速览」同一实现、同一份数据）
    var LBL = AGG.stageNames, COL = AGG.stageCss;
    var order = dom.map(function (d) { return d.name; });
    var byName = {};
    AGG.domains.forEach(function (d) { byName[d.name] = d; });
    var rows = order.map(function (name) {
      var d = byName[name];
      if (!d || !d.total) {
        return '<div style="margin-top:0.625rem"><div style="display:flex;justify-content:space-between;font-size:0.8125rem">' +
          '<span style="color:var(--mv-muted)">' + name + '</span><span style="color:var(--mv-muted)">还没长</span></div>' +
          '<div class="mini-track"><i style="width:0"></i></div></div>';
      }
      var tot = d.total || 1;
      var segs = d.counts.map(function (c, i) {
        return c ? '<i style="display:inline-block;width:' + (c / tot * 100) + '%;height:100%;background:' + COL[i] + '"></i>' : '';
      }).join('');
      return '<div style="margin-top:0.625rem"><div style="display:flex;justify-content:space-between;font-size:0.8125rem">' +
        '<span>' + name + '</span><span style="color:var(--mv-muted)">' + d.total + ' 正本 · 内化中 ' + d.internalized + '</span></div>' +
        '<div class="mini-track" style="display:flex">' + segs + '</div></div>';
    }).join('');
    var leg = '<div style="display:flex;gap:.5rem;font-size:.75rem;color:var(--mv-muted);margin-top:.5rem;flex-wrap:wrap">' +
      LBL.map(function (l, i) { return '<span><i style="display:inline-block;width:7px;height:7px;border-radius:2px;background:' + COL[i] + ';margin-right:3px"></i>' + l + '</span>'; }).join('') + '</div>';
    document.getElementById('side-map').innerHTML =
      '<h4>我的版图 <em>域 × 内化五档</em></h4>' + rows + leg +
      '<div class="side-btns"><a class="mv-btn" href="index.html#insight" style="text-decoration:none">今日页同款速览</a></div>';"""
new = """    // ② 我的版图：域 × 五档矩阵（与今日页同一实现同一渲染，barHtml 出自共享库）
    var order = dom.map(function (d) { return d.name; });
    var have = {};
    AGG.domains.forEach(function (d) { have[d.name] = true; });
    var empty = order.filter(function (n) { return !have[n]; });
    document.getElementById('side-map').innerHTML =
      '<h4>我的版图 <em>域 × 内化五档</em></h4>' +
      window.MarvisInsight.barHtml(AGG, { height: 7, empty: empty }) +
      '<div class="side-btns"><a class="mv-btn" href="index.html#insight" style="text-decoration:none">今日页同款速览</a></div>';"""
assert old in b, "C3 map anchor"
b = b.replace(old, new, 1)
bp.write_text(b, encoding="utf-8", newline="\n")
ok.append("brain.html：版图改用 barHtml（空域 opts.empty）")

# ── C4. domains.js：删摆设 id，写明 join 键约定 ──
dp = pathlib.Path("site/_data/domains.js")
s = dp.read_text(encoding="utf-8")
s = s.replace("""/* 人生域登记表（PLAN v2 §二轴一）——域是个人宪法：一行一域，定了少动。
   规矩：有首张卡才建（正本 frontmatter domain: 首次出现该域时）；渲染层按本表顺序展示，
   insight（_data/insight.js）里没有数据的启用域如实显示「还没长」。
   候选域只登记注释，首卡落地时启用并移入上方列表。 */
window.MARVIS_DOMAINS = [
  { id: 'shiye', name: '事业', color: '#4C82B8', desc: '秋招、项目、工作输出与职业决策' },
  { id: 'xueshi', name: '学识', color: '#7F9C7A', desc: '技术学习、阅读与思想框架' },
  { id: 'guanxi', name: '关系', color: '#D85A30', desc: '人、沟通、出牌与家庭' },
  { id: 'shenxin', name: '身心', color: '#993C1D', desc: '睡眠饮食运动、心态与情绪' }
];""",
"""/* 人生域登记表（PLAN v2 §二轴一）——域是个人宪法：一行一域，定了少动。
   规矩：有首张卡才建（正本 frontmatter domain: 首次出现该域时）；渲染层按本表顺序展示，
   insight（_data/insight.js）里没有数据的启用域如实显示「还没长」。
   【join 键约定】正本 frontmatter 的 domain: 值、build 聚合键、本表 name 是同一个字符串——
   改中文名 = 改宪法：必须同步全部正本 frontmatter，且 test_insight 的「域名 ∈ 登记表」断言会红。
   不设 id 字段：没有第二个消费方之前，第二个键就是摆设（第2期审查 smell）。 */
window.MARVIS_DOMAINS = [
  { name: '事业', color: '#4C82B8', desc: '秋招、项目、工作输出与职业决策' },
  { name: '学识', color: '#7F9C7A', desc: '技术学习、阅读与思想框架' },
  { name: '关系', color: '#D85A30', desc: '人、沟通、出牌与家庭' },
  { name: '身心', color: '#993C1D', desc: '睡眠饮食运动、心态与情绪' }
];""", 1)
dp.write_text(s, encoding="utf-8", newline="\n")
ok.append("domains.js：删摆设 id + join 键约定")

print("\n".join("✔ " + x for x in ok))
