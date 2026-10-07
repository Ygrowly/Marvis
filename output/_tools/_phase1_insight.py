# -*- coding: utf-8 -*-
"""第1期D：build.py 增 write_insight()——insight.js（域×状态分布）+ recent.js（新到架），并接入今日页。"""
import pathlib, re

p = pathlib.Path("site/build.py")
s = p.read_text(encoding="utf-8")

# 1) parse_brain_cards_file 的 out 加 domain
old = '''    out = {
        "kind": kind,
        "source": (meta.get("source") or path.stem).strip(),'''
new = '''    out = {
        "kind": kind,
        "domain": (meta.get("domain") or "学识").strip(),
        "source": (meta.get("source") or path.stem).strip(),'''
assert old in s
s = s.replace(old, new, 1)

# 2) write_insight 函数（插在 write_ledger 定义前）
insight_fn = '''
# ── 内化画像静态层（PLAN v2 第1期）：wiki 正本 → _data/insight.js + recent.js ──────────
# insight.js：域 × 状态分布（画像页/今日页「内化速览」用；内化度五档的运行时信号
# 在 localStorage，由页面端聚合，build 只供静态盘面）。
# recent.js：新到架——近 14 天 created/updated 的正本与阅读流水，保证"落盘即上站"。
INSIGHT_ROOTS = ["wiki/cards", "wiki/topics", "wiki/thinking", "wiki/interview", "reading"]
RECENT_DAYS = 14
RECENT_CAP = 24


def _front_title(body):
    m = re.search(r"^#\\s+(.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def write_insight():
    import datetime as _dt
    today = _dt.date.today()
    domains, recent = {}, []
    for root in INSIGHT_ROOTS:
        for path in sorted((ROOT / root).rglob("*.md")):
            if path.name.startswith("README"):
                continue
            meta, body = split_front(path.read_text(encoding="utf-8"))
            status = (meta.get("status") or "").strip() or "未标注"
            domain = (meta.get("domain") or "").strip()
            kind = (meta.get("type") or "").strip()
            title = _front_title(body) or path.stem
            rel = path.relative_to(ROOT).as_posix()
            if domain:
                d = domains.setdefault(domain, {"name": domain, "files": []})
                d["files"].append({"title": title, "path": rel, "kind": kind, "status": status})
            if kind in ("topic", "study-module", "brain-cards") or rel.startswith("reading/"):
                for key in ("updated", "created"):
                    raw = (meta.get(key) or "").strip()
                    if raw:
                        try:
                            age = (today - _dt.date.fromisoformat(raw[:10])).days
                        except ValueError:
                            break
                        if age <= RECENT_DAYS:
                            recent.append({"date": raw[:10], "title": title,
                                           "path": rel, "status": status})
                        break
    out_domains = []
    for name in sorted(domains):
        d = domains[name]
        d["files"].sort(key=lambda f: f["title"])
        d["stats"] = {}
        for f in d["files"]:
            d["stats"][f["status"]] = d["stats"].get(f["status"], 0) + 1
        out_domains.append(d)
    recent.sort(key=lambda r: r["date"], reverse=True)
    recent = recent[:RECENT_CAP]
    (OUT_DATA / "insight.js").write_text(
        "window.MARVIS_INSIGHT = " + json.dumps({"generated": today.isoformat(),
                                                 "domains": out_domains},
                                                ensure_ascii=False) + ";\\n",
        encoding="utf-8")
    (OUT_DATA / "recent.js").write_text(
        "window.MARVIS_RECENT = " + json.dumps(recent, ensure_ascii=False) + ";\\n",
        encoding="utf-8")
    n_files = sum(len(d["files"]) for d in out_domains)
    print("内化速览：%d 域 %d 正本 → insight.js；新到架 %d 条（近 %d 天）→ recent.js"
          % (len(out_domains), n_files, len(recent), RECENT_DAYS))


'''
anchor = "# ── 问题台账（questions.md → _data/ledger.js，进度页「问题台账」抽屉用）────────────"
assert anchor in s
s = s.replace(anchor, insight_fn + anchor, 1)

# 3) main 里调用（write_ledger() 后）
old_main = "    write_ledger()\n\n    inject_mermaid_runtime()"
assert old_main in s
s = s.replace(old_main, "    write_ledger()\n    write_insight()\n\n    inject_mermaid_runtime()", 1)

p.write_text(s, encoding="utf-8", newline="\n")
print("build.py: write_insight 接入完成")

# 4) 今日页插抽屉 + 渲染脚本
ip = pathlib.Path("site/index.html")
h = ip.read_text(encoding="utf-8")

drawer = '''<details class="mv-dr" id="insight">
    <summary>内化速览与新到架 <em id="insightsum"></em></summary>
    <div class="mv-dr-body"><div id="insightbox"></div></div>
  </details>

  <details class="mv-dr">
    <summary>规则与数据</summary>'''
assert '<details class="mv-dr">\n    <summary>规则与数据</summary>' in h
h = h.replace('<details class="mv-dr">\n    <summary>规则与数据</summary>', drawer, 1)

h = h.replace('<script src="_data/projects.js"></script>',
  '<script src="_data/projects.js"></script>\n<script src="_data/insight.js"></script>\n<script src="_data/recent.js"></script>', 1)

render_js = '''
  (function () {
    var box = document.getElementById('insightbox');
    var I = window.MARVIS_INSIGHT, R = window.MARVIS_RECENT || [];
    var sum = document.getElementById('insightsum');
    if (!box || !I) return;
    var n = I.domains.reduce(function (a, d) { return a + d.files.length; }, 0);
    if (sum) sum.textContent = n + ' 正本 · ' + I.domains.length + ' 域';
    var bar = I.domains.map(function (d) {
      var tot = d.files.length;
      var ok = (d.stats['integrated'] || 0) + (d.stats['active'] || 0);
      return '<div style="margin-bottom:.625rem">' +
        '<div style="display:flex;justify-content:space-between;font-size:.8125rem">' +
        '<span>' + d.name + '</span><span style="color:var(--mv-muted)">' + tot +
        ' 正本 · 验收 ' + ok + '</span></div>' +
        '<div style="height:6px;background:var(--mv-line,#e5e1d8);border-radius:3px;overflow:hidden">' +
        '<div style="height:100%;width:' + (tot ? Math.round(ok / tot * 100) : 0) + '%;background:var(--mv-accent)"></div></div></div>';
    }).join('');
    var list = R.length ? '<div class="mv-ms-label" style="margin:1rem 0 .5rem">新到架 <span style="font-weight:400">· 近 14 天落盘，点进 Obsidian 即读</span></div>' +
      R.map(function (r) {
        return '<div style="display:flex;gap:.75rem;font-size:.875rem;padding:.25rem 0">' +
          '<span style="color:var(--mv-muted);white-space:nowrap">' + r.date + '</span>' +
          '<a href="obsidian://open?vault=Marvis&file=' + encodeURIComponent(r.path.replace(/\\.md$/, '')) +
          '" style="color:var(--mv-accent);text-decoration:none">' + r.title + '</a>' +
          (r.status && r.status !== 'integrated' ? '<span style="color:var(--mv-muted)">（' + r.status + '）</span>' : '') +
          '</div>';
      }).join('') : '';
    box.innerHTML = bar + list;
  })();
'''
tail = "    box.innerHTML = bar + list;\n  })();"
h = h.replace("    if (gap === null || gap > 7) show(", render_js + "\n    if (gap === null || gap > 7) show(", 1)
ip.write_text(h, encoding="utf-8", newline="\n")
print("index.html: 内化速览抽屉接入")
