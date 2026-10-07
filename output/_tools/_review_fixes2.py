# -*- coding: utf-8 -*-
"""审查修复 v2：训练档映射 bug（页 stem 带模块前缀导致 md stem miss）——build 直出
MARVIS_TOPIC_PAGE（md 正本路径 → 母题页路径），页面端改用，另加对账测试 test_insight.js。"""
import pathlib

ok = []

# ── 1. build.py：breaks.js 写出后追加 pagekey.js ──
bp = pathlib.Path("site/build.py")
s = bp.read_text(encoding="utf-8")
anchor = '(OUT_DATA / "breaks.js").write_text('
assert anchor in s
# 找到 breaks 写出语句的结尾（同一语句块结束的行）——在其后插入 pagekey 写出
idx = s.index(anchor)
end = s.index("\n\n", idx)
insert = '''

    # 母题 md 正本路径 → 母题页路径（PLAN v2 第1期审查修复：内化速览「训练档」映射用；
    # 页 stem 带模块名前缀而 md stem 不带，页面端自行拼接会 miss，故由 build 直出）
    (OUT_DATA / "pagekey.js").write_text(
        "window.MARVIS_TOPIC_PAGE = " + json.dumps({t["src"]: t["page"] for t in topics},
                                                   ensure_ascii=False, sort_keys=True) + ";\\n",
        encoding="utf-8")'''
s = s[:end] + insert + s[end:]
bp.write_text(s, encoding="utf-8", newline="\n")
ok.append("build.py：pagekey.js 直出（md→页路径）")

# ── 2. index.html：渲染映射改用 pagekey.js ──
ip = pathlib.Path("site/index.html")
h = ip.read_text(encoding="utf-8")

old_map = """    var pageKey = {};                    /* 母题页 stem → 主线 key（clusters.js 的 pages 字段就是单卡页清单） */
    (window.MARVIS_CLUSTERS || []).forEach(function (c) {
      (c.topics || []).forEach(function (t) {
        (t.pages || []).forEach(function (p) {
          pageKey[String(p).replace(/\\.html$/, '').split('/').pop()] = c.id + '/' + t.id;
        });
      });
    });"""
new_map = """    var pageToLine = {};                 /* 母题页路径 → 主线 key（clusters.js pages 完整路径，与 breaks 键同形态） */
    (window.MARVIS_CLUSTERS || []).forEach(function (c) {
      (c.topics || []).forEach(function (t) {
        (t.pages || []).forEach(function (p) { pageToLine[String(p)] = c.id + '/' + t.id; });
      });
    });
    var TP = window.MARVIS_TOPIC_PAGE || {};  /* 母题 md 正本路径 → 页路径（build 直出 pagekey.js；页 stem 带模块前缀，勿自行拼接） */"""
assert old_map in h, "old pageKey map not found"
h = h.replace(old_map, new_map, 1)

old_lookup = """      var stem = f.path.split('/').pop().replace(/\\.md$/, '');
      if (pageKey[stem] && trained(pageKey[stem])) s = 3;                  /* 母题卡：所在主线训练过 → 训练档 */
      return s;"""
new_lookup = """      var lp = TP[f.path] && pageToLine[TP[f.path]];
      if (lp && trained(lp)) s = 3;                                        /* 母题卡：所在主线训练过 → 训练档 */
      return s;"""
assert old_lookup in h, "old lookup not found"
h = h.replace(old_lookup, new_lookup, 1)

h = h.replace('<script src="_data/insight.js"></script>',
              '<script src="_data/insight.js"></script>\n<script src="_data/pagekey.js"></script>', 1)
ip.write_text(h, encoding="utf-8", newline="\n")
ok.append("index.html：训练档映射改用 MARVIS_TOPIC_PAGE")

# ── 3. test_insight.js：对账测试（映射完整性 = 训练档可达性） ──
test = """/* 内化速览对账（PLAN v2 第1期审查修复）：训练档映射链路的完整性。
   链路 = 母题 md 正本（insight.js 的 path）→ MARVIS_TOPIC_PAGE → 母题页路径 → clusters 主线 pages。
   哪一环断了，那张母题卡在今日页速览里就永远到不了「训练」档。 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const ROOT = path.join(__dirname, '..', '..');
const ctx = { window: {}, console };
vm.createContext(ctx);
['insight.js', 'pagekey.js', 'clusters.js', 'cards.js'].forEach(f => {
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'site', '_data', f), 'utf8'), ctx);
});
const I = ctx.window.MARVIS_INSIGHT;
const TP = ctx.window.MARVIS_TOPIC_PAGE;
const CL = ctx.window.MARVIS_CLUSTERS;
const C = ctx.window.MARVIS_CARDS;
let fails = 0;
const ok = (cond, msg) => { console.log((cond ? '  ✅ ' : '  ❌ ') + msg); if (!cond) fails++; };

ok(TP && Object.keys(TP).length > 80, 'MARVIS_TOPIC_PAGE 覆盖母题正本 ' + (TP ? Object.keys(TP).length : 0) + ' 个');
const motherFiles = I.domains.flatMap(d => d.files).filter(f => /topics\\//.test(f.path) && /母题-/.test(f.path));
const missing = motherFiles.filter(f => !TP[f.path]);
ok(missing.length === 0, 'insight 母题正本全部可映射到页路径' + (missing.length ? '（缺 ' + missing.map(f => f.path).join('、') + '）' : ''));
const linePages = new Set();
CL.forEach(c => (c.topics || []).forEach(t => (t.pages || []).forEach(p => linePages.add(String(p)))));
const orphan = Object.values(TP).filter(p => !linePages.has(p));
ok(orphan.length === 0, 'TOPIC_PAGE 页路径全部挂在某条主线下（训练档可达）' + (orphan.length ? '（孤儿 ' + orphan.slice(0, 3).join('、') + '）' : ''));
const principleSrcs = new Set(C.principles.map(c => c.src));
const cardFiles = I.domains.flatMap(d => d.files).filter(f => f.path.indexOf('wiki/cards/原则-') === 0);
const noCard = cardFiles.filter(f => !principleSrcs.has(f.path));
ok(cardFiles.length > 0 && noCard.length === 0, '原则卡正本全部可映射到派单卡 id' + (noCard.length ? '（缺 ' + noCard.map(f => f.path).join('、') + '）' : ''));

if (fails) { console.log('❌ ' + fails + ' 项对账失败'); process.exit(1); }
console.log('✅ 内化速览映射对账全通过');
"""
pathlib.Path("site/_tests/test_insight.js").write_text(test, encoding="utf-8", newline="\n")
ok.append("site/_tests/test_insight.js：对账测试新建")

# ── 4. CI 列表 + CLAUDE/MAP 口径（5 node → 6 node） ──
cp = pathlib.Path(".github/workflows/check-build.yml")
s = cp.read_text(encoding="utf-8")
s = s.replace("for t in test_dispatch test_progression test_render test_sync test_brain; do",
              "for t in test_dispatch test_progression test_render test_sync test_brain test_insight; do")
cp.write_text(s, encoding="utf-8", newline="\n")
ok.append("check-build.yml：套件列表 +test_insight")

for f, old, new in [
    ("CLAUDE.md", "`_tests/`（回归测试：5 个 node + 1 个 python，手跑", "`_tests/`（回归测试：6 个 node + 1 个 python，手跑"),
    ("MAP.md", "`site/_tests/test_dispatch.js`、`test_render.js`、`test_progression.js`、`test_sync.js`、`test_brain.js`（node；",
     "`site/_tests/test_dispatch.js`、`test_render.js`、`test_progression.js`、`test_sync.js`、`test_brain.js`、`test_insight.js`（node；末者为内化速览映射对账）"),
]:
    p = pathlib.Path(f)
    s = p.read_text(encoding="utf-8")
    assert old in s, f + " 口径行 not found"
    p.write_text(s.replace(old, new, 1), encoding="utf-8", newline="\n")
    ok.append(f + "：测试口径 6 node")

print("\n".join("✔ " + x for x in ok))
