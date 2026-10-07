/* 内化聚合库（PLAN v2 第2期）：五档矩阵的唯一实现，今日页与第二大脑画像页共用。
   纯函数、零 DOM 依赖——Node 测试可直接 require，浏览器挂 window.MarvisInsight。
   五档口径见 site/PLAN.md §二轴三：0 空 / 1 暗(记录过) / 2 读厚(拆成情境→动作且人验过) / 3 训练(进派单有记录) / 4 亮(真实用上)。 */
(function () {
  'use strict';

  var STAGE_NAMES = ['空', '暗', '读厚', '训练', '亮'];
  var STAGE_CSS = ['#d8d2c4', '#b8a88f', '#7f9c7a', '#4d7c62', '#2f6b4f'];

  /* 建索引：簇（含 drill 手撕簇与 rule 准则簇）→ 主线 key；原则卡 md 正本 → 派单卡 id。
     data = { clusters, drill, ruleCluster, cards, topicPage }，全部来自 build 产物，调用方注入。 */
  function buildIndex(data) {
    data = data || {};
    var pageToLine = {};
    [].concat(data.clusters || [], data.drill ? [data.drill] : [], data.ruleCluster ? [data.ruleCluster] : [])
      .forEach(function (c) {
        (c.topics || []).forEach(function (t) {
          (t.pages || []).forEach(function (p) { pageToLine[String(p)] = c.id + '/' + t.id; });
          /* drill 型条目没有 pages 字段，href 直指母题页 */
          if (/^topics\/.+\.html$/.test(String(t.href || ''))) pageToLine[String(t.href)] = c.id + '/' + t.id;
        });
      });
    var principles = {};
    ((data.cards && data.cards.principles) || []).forEach(function (c) {
      (principles[c.src] = principles[c.src] || []).push(c.id);
    });
    return { pageToLine: pageToLine, principles: principles, topicPage: data.topicPage || {} };
  }

  function trained(lv, key) {
    var r = lv[key];
    return !!(r && (r.last || r.due || r.l >= 1));
  }

  /* 单个正本的内化档位。lv = mv.progress.v1 的 {lv:{…}}，uses = mv.brain.v1 的 uses。 */
  function stageOf(index, lv, uses, file) {
    var s = (file.status === 'integrated' || file.status === 'active') ? 2 : 1;
    var ids = index.principles[file.path];
    if (ids) {
      ids.forEach(function (id) {
        if ((uses[id] || []).length) s = 4;
        else if (s < 3 && trained(lv, 'card/' + id)) s = 3;
      });
      return s;
    }
    var page = index.topicPage[file.path];
    var line = page && index.pageToLine[page];
    if (line && trained(lv, line)) s = 3;
    return s;
  }

  /* 聚合：insight（build 静态盘面）+ 索引 + 本机信号 → 域×五档矩阵 */
  function aggregate(insight, index, lv, uses) {
    lv = lv || {}; uses = uses || {};
    var domains = ((insight && insight.domains) || []).map(function (d) {
      var counts = [0, 0, 0, 0, 0];
      var files = (d.files || []).map(function (f) {
        var st = stageOf(index, lv, uses, f);
        counts[st]++;
        return { title: f.title, path: f.path, kind: f.kind, status: f.status, stage: st };
      });
      return { name: d.name, counts: counts, files: files,
               total: files.length, internalized: counts[3] + counts[4] };
    });
    return { domains: domains, stageNames: STAGE_NAMES, stageCss: STAGE_CSS };
  }

  var api = { buildIndex: buildIndex, stageOf: stageOf, aggregate: aggregate,
              trained: trained, stageNames: STAGE_NAMES, stageCss: STAGE_CSS };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else if (typeof window !== 'undefined') window.MarvisInsight = api;
})();
