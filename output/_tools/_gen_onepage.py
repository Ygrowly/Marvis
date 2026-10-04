# -*- coding: utf-8 -*-
"""一页复习舱（一页通）脚手架生成器 —— output/_gen_onepage.py

从 wiki/topics/<模块>/ 的模块卡 + 母题卡正本，生成该模块的「一页通」脚手架：
可自动推导的部分（检索表 / 闭卷器数据 / 验收门 / 边界 / 误判候选）直接填好，
必须人工撰写的部分（01 主干图 SVG + 主干叙事 + 04 第二张图 + 05 数字板）留 TODO 桩，
并同步产出一份《素材包》md，把撰写这几块所需的正本素材集中到一起。

用法：
    python output/_gen_onepage.py                 # 列出全部模块与生成状态
    python output/_gen_onepage.py RAG与检索        # 生成脚手架 + 素材包
    python output/_gen_onepage.py Redis --force    # 覆盖重生成（仅限仍是脚手架的页）

产出：
    output/<模块>-一页通.html        脚手架页（带 ONEPAGER-SCAFFOLD 标记）
    output/<模块>-一页通-素材.md     撰写素材包（正本抽取，只读参考）

定稿流程（约一次会话）：
    1. 跑生成器 → 打开素材包，读「主线拆解」表
    2. 写 01 主干图 SVG（3–5 层管道/循环，蓝主线 + 橙手段 + 紫评测 + 绿回灌，参考 RAG 页）
    3. 写主干叙事（一段读完，150–250 字，粗体只给关键词）
    4. 写 04 第二张图（本模块最硬的一笔账）与 05 数字板（每个数带推导）
    5. 补 02 检索表「项目证据」列的一句话证据、06 误判的 ✓ 判据
    6. 删掉页顶 SCAFFOLD 标记行（可选），页即转为手工维护：
       之后的修订直接改 HTML，重跑生成器不会覆盖已定稿的页。
"""
import io, os, re, sys, json, glob

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE)) if os.path.basename(_HERE) == '_tools' else os.path.dirname(_HERE)
TOPICS = os.path.join(ROOT, 'wiki', 'topics')
OUT = os.path.join(ROOT, 'output')
SITE_ONEPAGE = os.path.join(ROOT, 'site', 'onepage')   # 成品页上站（2026-10-04）
MARKER = 'ONEPAGER-SCAFFOLD v1'


# ---------------------------------------------------------------- 正本解析

def read(p):
    return io.open(p, encoding='utf-8').read()


def clean(t, keep_bold=False):
    t = re.sub(r'\[\[|\]\]', '', t)
    if keep_bold:
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    else:
        t = t.replace('**', '')
    t = re.sub(r'`([^`]*)`', r'\1', t)
    t = ' '.join(t.split())
    return t.strip(' ·|')


def find_module_dir(name):
    d = os.path.join(TOPICS, name)
    if not os.path.isdir(d):
        sys.exit(u'wiki/topics/ 下没有模块目录：%s' % name)
    return d


def read_module_card(d):
    cands = [f for f in os.listdir(d)
             if f.endswith('.md') and not f.startswith(u'母题-') and u'模块' in f]
    if not cands:
        cands = [f for f in os.listdir(d) if f.endswith('.md') and not f.startswith(u'母题-')]
    if not cands:
        sys.exit(u'目录下没有模块卡 md：%s' % d)
    return read(os.path.join(d, sorted(cands)[0]))


def split_sections(card):
    """按 '## N.' 切节，返回 {1: text, ...}"""
    secs = {}
    marks = list(re.finditer(r'\n## (\d+)\.[^\n]*', card))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(card)
        secs[int(m.group(1))] = card[m.end():end]
    return secs


def parse_mother_list(sec):
    rows = []
    for m in re.finditer(r'\n\|\s*([A-Z]{1,2}\d{1,2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', sec):
        rows.append((m.group(1), clean(m.group(2)), clean(m.group(3))))
    return rows  # (code, 母题描述, 所属主线)


def expand_codes(cell, all_codes):
    """'G1–G6' / 'G1,G3' / '全' → 母题编号列表"""
    cell = cell.strip()
    if cell in (u'全', ''):
        return list(all_codes)
    out = []
    for part in re.split(r'[，,、/ ]+', cell):
        m = re.match(r'([A-Z]{1,2})(\d{1,2})[–\-~]([A-Z]{1,2})?(\d{1,2})$', part)
        if m:
            pre, a, pre2, b = m.group(1), int(m.group(2)), m.group(3) or m.group(1), int(m.group(4))
            if pre == pre2:
                out += ['%s%d' % (pre, i) for i in range(a, b + 1)]
            continue
        m = re.match(r'([A-Z]{1,2}\d{1,2})$', part)
        if m:
            out.append(m.group(1))
    return [c for c in out if c in all_codes]


def parse_question_list(sec, all_codes):
    qs = []  # (num, 题干, [codes])
    for m in re.finditer(r'\n\|\s*(\d{1,2})\s*\|\s*([^|]+?)\s*\|([^|]*?)\|\s*([^|]*?)\s*\|', sec):
        num, text, codes_cell = int(m.group(1)), clean(m.group(2)), m.group(4)
        qs.append((num, text, expand_codes(codes_cell, all_codes)))
    return qs


def parse_projects(sec):
    ps = []
    for m in re.finditer(r'\n### 5\.\d+ ([^\n(·]+)', sec):
        name = clean(m.group(1))
        end = sec.find('\n### ', m.end())
        block = sec[m.end():end if end > 0 else len(sec)]
        codes = re.findall(r'【([A-Z]{1,2}\d{1,2})】', block)
        if not codes:
            mm = re.search(r'对应母题\*\*[：:](.+)', block) or re.search(r'对应母题[：:](.+)', block)
            if mm:
                codes = re.findall(r'[A-Z]{1,2}\d{1,2}', mm.group(1))
        if not codes:
            for g in re.findall(r'【([^】]{2,30})】', block):
                cs = re.findall(r'[A-Z]{1,2}\d{1,2}', g)
                if cs:
                    codes += cs
        ps.append((name, codes))
    return ps


def parse_gate(sec):
    items = []
    for line in sec.split('\n'):
        m = re.match(r'\s*-\s*\[\s*\]\s*(.+)$', line)
        if m:
            items.append(clean(m.group(1), keep_bold=True))
    return items


def parse_boundary(sec):
    for line in sec.split('\n'):
        t = clean(line)
        if len(t) > 20:
            return t
    return u'（TODO：从模块卡第 0 节抄一句边界）'


def parse_mother_card(path):
    s = read(path)
    title = ''
    m = re.search(r'\n#\s*母题\s*([A-Z]{1,2}\d{1,2})\s*[·•]\s*(.+)', s)
    if m:
        title = clean(m.group(2))
    body = re.search(r'## 一、教材(.*?)\n## 二、自测', s, re.S)
    secs = []
    if body:
        for sub in re.split(r'\n### ', body.group(1))[1:]:
            st = clean(sub.split('\n')[0])
            pts = [clean(x[1]) for x in re.findall(
                r'【(事实|推导|推论|结论|取舍|推断|补充)】([\s\S]{0,300}?)(?=【|\n\n|\n>|\n```|$)', sub)]
            seen, keep = set(), []
            for t in pts:
                if len(t) < 8:
                    continue
                k = t[:40]
                if k in seen:
                    continue
                seen.add(k)
                keep.append(t[:150])
            if st and keep:
                secs.append((st, keep[:3]))
    st_sec = re.search(r'## 二、自测(.*?)(\n## 三、|\Z)', s, re.S)
    cues, myths = [], []
    if st_sec:
        for q in re.finditer(r'\*\*Q(\d)（[^）]*）\*\*(.{0,500}?)\*\*A\1\*\*', st_sec.group(1), re.S):
            seg = q.group(2)
            w = re.search(r'问：\*\*(.+?)\*\*', seg, re.S)
            stem = clean(w.group(1)) if w else clean(seg.split('\n')[0]).lstrip('：: ')
            if re.match(r'^下面这段话', stem):
                continue  # 纠错题题干在卡里是引用块，cue 里没有信息量
            if len(stem) < 8:
                stem = (u'纠错题（题干见母题卡二、自测 Q%s）' % q.group(1)) + (u'：%s' % stem if stem else '')
            if stem:
                cues.append(stem[:140])
        for m in re.finditer(r'「([^」]{8,80})」', st_sec.group(1)):
            pass  # 误判句在 render 时按题干挑选
    m = re.search(r'\*\*通过判据\*\*：(.*?)\n', s, re.S)
    crit = clean(m.group(1)) if m else u'（待补：母题卡缺「通过判据」）'
    return title, secs, cues, crit


def extract_misconceptions(mothers):
    """从自测题干里挑「指出问题/错在哪」题的引号句，作 06 节候选"""
    rows = []
    for code, path in mothers:
        s = read(path)
        st = re.search(r'## 二、自测(.*?)(\n## 三、|\Z)', s, re.S)
        if not st:
            continue
        for q in re.finditer(r'\*\*Q(\d)（[^）]*）\*\*([^\n]*)\n(问：[^\n]*)?', st.group(1)):
            seg = q.group(2) + '\n' + (q.group(3) or '')
            if not re.search(r'指出|错在|站不住|反驳|挑刺|为什么.{0,6}这句话', seg):
                continue
            m = re.search(r'[「"]([^」"]{8,60})[」"]', seg)
            if m:
                rows.append((code, m.group(1)))
    return rows[:8]


# ---------------------------------------------------------------- 模板

def page_css():
    # 与已定稿四页（2026-10-03 补丁后）一致：遮罩紧凑化 + 主线脊柱
    return u"""
:root{
  --blue:#1664FF; --blue-soft:#E8F0FF; --blue-deep:#0E42B5;
  --orange:#F59E0B; --orange-soft:#FEF3D6; --orange-deep:#B45309;
  --purple:#8B5CF6; --purple-soft:#F1ECFE; --purple-deep:#6D28D9;
  --green:#22C55E; --green-soft:#E8F8EE; --green-deep:#15803D;
  --red:#EF4444; --red-soft:#FDECEC;
  --grey:#86909C; --grey-soft:#F2F3F5;
  --line:#E5E6EB; --line2:#CDD0D6;
  --tx:#1D2129; --tx2:#4E5969; --tx3:#86909C;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;color:var(--tx);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  line-height:1.65;-webkit-font-smoothing:antialiased;font-size:13.5px}
svg text{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",system-ui,sans-serif}
.wrap{max-width:1440px;margin:0 auto;padding:0 28px 76px}

header{padding:40px 0 22px;border-bottom:2px solid var(--tx)}
.kicker{font-size:11.5px;letter-spacing:.24em;color:var(--blue);font-weight:800;margin-bottom:10px}
h1{font-size:30px;line-height:1.25;font-weight:800;letter-spacing:-.01em}
h1 small{display:block;font-size:13.5px;font-weight:400;color:var(--tx2);margin-top:8px}

.bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:18px;
  padding:10px 14px;background:#F7F8FA;border:1px solid var(--line);border-radius:10px}
.bar .lab{font-size:11.5px;font-weight:800;color:var(--tx3);letter-spacing:.08em}
button.m{font:inherit;font-size:12.5px;padding:5px 14px;border-radius:7px;cursor:pointer;
  border:1px solid var(--line2);background:#fff;color:var(--tx2);font-weight:700}
button.m.on{background:var(--blue);border-color:var(--blue);color:#fff}
button.m:hover{border-color:var(--blue)}
.bar .hint{font-size:11.5px;color:var(--tx3);margin-left:auto}

.self{margin-top:14px;border:1px dashed var(--line2);border-radius:10px;background:#FCFCFD;padding:12px 14px}
.self .lab{font-size:11.5px;font-weight:800;color:var(--tx3);letter-spacing:.08em;margin-bottom:6px}
.self textarea{width:100%;min-height:56px;font:inherit;font-size:13px;line-height:1.6;color:var(--tx);
  border:1px solid var(--line);border-radius:8px;padding:8px 10px;resize:vertical;background:#fff}
.self .ok{font-size:11.5px;color:var(--green-deep);margin-top:5px;min-height:16px}

section{margin-top:34px;position:relative}
section::before{content:"";position:absolute;left:-15px;top:2px;bottom:-26px;width:2px;
  background:linear-gradient(180deg,#C7DBFF,rgba(199,219,255,0))}
section:last-of-type::before{display:none}
h2{font-size:19px;font-weight:800;margin-bottom:4px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
h2 .num{font-size:11px;color:#fff;background:var(--blue);border-radius:5px;padding:3px 9px;letter-spacing:.08em;font-weight:800}
h2 .src{font-size:11px;font-weight:500;color:var(--tx3);margin-left:auto;font-family:Menlo,Consolas,monospace}
.h2sub{font-size:13px;color:var(--tx3);margin-bottom:14px}

.story{margin-top:12px;padding:12px 16px;border-radius:10px;background:#F7F8FA;border:1px solid var(--line);
  border-left:4px solid var(--blue);font-size:13.4px;line-height:1.85;color:var(--tx2)}
.story b{color:var(--tx)}

.todo{border:1.5px dashed var(--orange);border-radius:12px;background:var(--orange-soft);
  padding:16px 20px;font-size:13px;color:var(--orange-deep);line-height:1.8}
.todo b{color:var(--orange-deep)}

.fig{border:1px solid var(--line);border-radius:12px;background:#FBFBFD;padding:12px 10px;overflow-x:auto}
.fig svg{width:100%;min-width:1180px;height:auto;display:block}
.cap{font-size:12.5px;color:var(--tx2);padding:10px 8px 2px;line-height:1.75}
.cap b{color:var(--tx)}

table{width:100%;border-collapse:collapse;font-size:13px;margin-top:6px}
th,td{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--tx3);font-size:11.5px;letter-spacing:.08em;font-weight:800;background:#F7F8FA}
td.k{white-space:nowrap;font-weight:800}
tr:hover td{background:#FAFBFF}
td.ans{position:relative}
#mainTable.masked td.ans .a{display:none}
#mainTable.masked td.ans{white-space:nowrap}
#mainTable.masked td.ans:after{content:"▸ 已遮 · 点「对答案」";color:#C9CDD4;font-size:11px;letter-spacing:.03em}

.rec{border:1px solid #C7DBFF;background:var(--blue-soft);border-radius:12px;padding:14px 18px;margin-top:8px}
.rec .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.rec select{font:inherit;font-size:13px;padding:5px 10px;border-radius:7px;border:1px solid var(--line2);background:#fff;font-weight:700;color:var(--tx)}
.rec ol{list-style:none;counter-reset:r;font-size:13.5px;margin-top:10px}
.rec li{counter-increment:r;padding:6px 0 6px 0;display:flex;gap:10px;align-items:flex-start}
.rec li:before{content:counter(r);flex:none;width:20px;height:20px;border-radius:50%;background:var(--blue);color:#fff;
  font-size:11.5px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:2px}
#ansBox{display:none}
#ansBox.show{display:block}
.rec .crit{margin-top:10px;padding-top:10px;border-top:1px dashed #A9C6FF;font-size:12.8px;color:#123A82}
.rec .tip{font-size:11.5px;color:#123A82;margin-top:8px}
.rec button{font:inherit;font-size:12.5px;padding:5px 13px;border-radius:7px;cursor:pointer;
  border:1px solid var(--blue);background:var(--blue);color:#fff;font-weight:700}
.rec button.ghost{background:#fff;color:var(--blue)}
.ptT{margin-top:14px;font-size:11.5px;font-weight:800;letter-spacing:.06em;color:#123A82}
ol.pts{list-style:none;counter-reset:p;font-size:12.8px;margin-top:6px}
ol.pts li{counter-increment:p;padding:6px 0 6px 0;display:flex;gap:10px;align-items:flex-start;
  border-bottom:1px dashed #D9E3FB}
ol.pts li:last-child{border-bottom:none}
ol.pts li:before{content:counter(p);flex:none;min-width:20px;height:20px;border-radius:5px;background:#DCE8FF;color:#123A82;
  font-size:11px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:2px}

.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:11px;margin-top:6px}
.ncard{border:1px solid var(--line);border-radius:11px;padding:12px 14px;background:#fff}
.ncard .t{font-size:11.5px;color:var(--tx3);font-weight:800;letter-spacing:.06em}
.ncard .big{font-size:18px;font-weight:800;margin:4px 0 3px;letter-spacing:-.01em}
.ncard .d{font-size:12.2px;color:var(--tx2);line-height:1.6}
.ncard.o{background:var(--orange-soft);border-color:#F5DFAE} .ncard.o .big{color:var(--orange-deep)}
.ncard.b{background:var(--blue-soft);border-color:#C7DBFF} .ncard.b .big{color:var(--blue-deep)}

.mis{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:6px}
.mrow{border:1px solid var(--line);border-radius:10px;padding:11px 14px;background:#fff;font-size:12.8px}
.mrow .x{color:#B42318;font-weight:800}
.mrow .v{color:var(--green-deep);font-weight:700;margin-top:5px;display:block;line-height:1.62}

.gate{border:1px solid var(--line2);border-radius:12px;background:#F7F8FA;padding:14px 20px;margin-top:6px}
.gate ul{list-style:none;font-size:13.2px}
.gate li{padding:5px 0;display:flex;gap:9px;align-items:flex-start}
.gate li span{color:var(--blue);font-weight:800}

footer{margin-top:36px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--tx3);line-height:1.85}

body[data-mode="quick"] .lv-mid,body[data-mode="quick"] .lv-deep{display:none}
body[data-mode="mid"] .lv-deep{display:none}
@media print{
  .wrap{max-width:none;padding:0 6px} section{break-inside:avoid}
  .fig{overflow:visible} .fig svg{min-width:0}
  .bar{display:none} .lv-mid,.lv-deep{display:block!important}
  #mainTable.masked td.ans .a{display:inline} #mainTable.masked td.ans:after{content:""}
}
"""


def page_js(key, cards, order):
    # 与已定稿四页同一套交互（深度切换 / 遮罩 / 闭卷器 / 自填），只换数据
    return u"""
<script>
(function(){
  "use strict";
  var KEY = "__KEY__";
  var CARDS = __CARDS__;
  var ORDER = __ORDER__;

  var st = { mode:"mid", cue:true, card:ORDER[0], self:"", showAns:false };
  try {
    var raw = localStorage.getItem(KEY);
    if (raw) { var o = JSON.parse(raw); for (var k in o) { if (o.hasOwnProperty(k)) st[k] = o[k]; } }
  } catch (e) {}
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(st)); } catch(e){} }

  function apply(){
    document.body.setAttribute("data-mode", st.mode);
    var btns = document.querySelectorAll("[data-mode-btn]");
    for (var i=0;i<btns.length;i++){
      if (btns[i].getAttribute("data-mode-btn") === st.mode) btns[i].classList.add("on");
      else btns[i].classList.remove("on");
    }
    var tbl = document.getElementById("mainTable");
    if (tbl){ if (st.cue) tbl.classList.add("masked"); else tbl.classList.remove("masked"); }
    var ct = document.getElementById("cueToggle");
    if (ct) ct.textContent = st.cue ? "对答案" : "遮住答案";
  }

  function applyAns(){
    var box = document.getElementById("ansBox");
    if (box){ if (st.showAns) box.classList.add("show"); else box.classList.remove("show"); }
    var b = document.getElementById("critBtn");
    if (b) b.textContent = st.showAns ? "遮住答案" : "答完了，看知识点与判据";
  }

  function renderCues(){
    var sel = document.getElementById("cardSel");
    var list = document.getElementById("cueList");
    var box = document.getElementById("critBox");
    if (!sel || !list || !box) return;
    var c = CARDS[st.card];
    var html = "";
    for (var i=0;i<c.q.length;i++) html += "<li><div>" + c.q[i] + "</div></li>";
    list.innerHTML = html;
    var pl = document.getElementById("ptList");
    if (pl) { var h2 = ""; for (var j = 0; j < c.pts.length; j++) h2 += "<li><div>" + c.pts[j] + "</div></li>"; pl.innerHTML = h2; }
    box.textContent = "通过判据（教材原文）：" + c.crit;
    sel.value = st.card;
    applyAns();
  }

  var sel = document.getElementById("cardSel");
  if (sel){
    for (var i=0;i<ORDER.length;i++){
      var op = document.createElement("option");
      op.value = ORDER[i];
      op.textContent = ORDER[i] + " · " + CARDS[ORDER[i]].t;
      sel.appendChild(op);
    }
    sel.addEventListener("change", function(){ st.card = sel.value; st.showAns = false; save(); renderCues(); });
  }
  var btns = document.querySelectorAll("[data-mode-btn]");
  for (var b=0;b<btns.length;b++){
    btns[b].addEventListener("click", function(){ st.mode = this.getAttribute("data-mode-btn"); save(); apply(); });
  }
  var ct = document.getElementById("cueToggle");
  if (ct) ct.addEventListener("click", function(){ st.cue = !st.cue; save(); apply(); });
  var cb = document.getElementById("critBtn");
  if (cb) cb.addEventListener("click", function(){ st.showAns = !st.showAns; save(); applyAns(); });
  var rb = document.getElementById("resetBtn");
  if (rb) rb.addEventListener("click", function(){
    var idx = ORDER.indexOf(st.card);
    st.card = ORDER[(idx + 1) % ORDER.length]; st.showAns = false; save(); renderCues();
  });
  var ta = document.getElementById("self20");
  var ok = document.getElementById("selfOk");
  if (ta){
    ta.value = st.self || "";
    ta.addEventListener("input", function(){ st.self = ta.value; save(); if (ok) ok.textContent = "已存在本机（" + ta.value.length + " 字）"; });
    if (st.self && ok) ok.textContent = "已存在本机（" + st.self.length + " 字）";
  }

  apply();
  renderCues();
})();
</script>
</body>
</html>
""".replace('__KEY__', key).replace('__CARDS__', json.dumps(cards, ensure_ascii=False)) \
   .replace('__ORDER__', json.dumps(order, ensure_ascii=False))


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_html(mod, card_secs, mothers_data, mother_files, order, qlist, projects, gate, boundary):
    n_cards, n_q = len(order), len(qlist)
    codes = set(order)
    qby = {}
    for num, text, cs in qlist:
        for c in cs:
            qby.setdefault(c, []).append(str(num))
    proj_by = {}
    for name, cs in projects:
        for c in cs:
            proj_by.setdefault(c, []).append(name)

    rows = []
    for code in order:
        desc = mothers_data[code]['desc']
        short = re.split(r'[；;。]', desc)[0]
        if len(short) > 14:
            short = short[:14] + '…'
        qs = '、'.join(qby.get(code, [])) or '—'
        pj = ' / '.join(proj_by.get(code, []))
        proj_cell = (u'<span class="a"><b>%s</b> —— TODO：从素材包「项目映射」里抄一句话证据</span>' % esc(pj)) \
            if pj else u'<span class="a">TODO：素材包里没有映射到本母题的项目，从项目笔记里找一个</span>'
        rows.append(
            u'<tr><td class="k">%s %s</td><td>%s</td><td class="ans"><span class="a">TODO：一句话机制（说清因果，不说名词堆叠）</span></td>'
            u'<td>%s</td><td class="ans">%s</td></tr>'
            % (esc(code), esc(short), esc(desc), esc(qs), proj_cell))

    cards_js = {}
    for code in order:
        md = mothers_data[code]
        pts = []
        for st_, pp in md['secs']:
            for x in pp:
                pts.append(clean(st_ + '｜' + x, keep_bold=True))
        cards_js[code] = {
            "t": md['title'] or md['desc'][:20],
            "q": md['cues'][:5] or [u'（TODO：母题卡「二、自测」还没有可解析的题）'],
            "pts": pts[:12] or [u'（TODO：母题卡「一、教材」还没有带【标签】的要点句）'],
            "crit": md['crit'],
        }

    mis_rows = []
    for code, myth in extract_misconceptions(mother_files):
        mis_rows.append(u'<div class="mrow"><span class="x">✗「%s」（%s）</span>'
                        u'<span class="v">TODO：✓ 后半句判据——说对前半句没用，后半句才是判据。</span></div>'
                        % (esc(myth), esc(code)))
    if not mis_rows:
        mis_rows = [u'<div class="mrow"><span class="x">✗「TODO：从自测纠错题里抄原话」</span>'
                    u'<span class="v">TODO：✓ 判据</span></div>'] * 4

    gate_html = u'\n'.join(u'<li><span>☐</span><div>%s</div></li>' % g for g in gate) or \
        u'<li><span>☐</span><div>TODO：模块卡第 6 节没有解析到验收项</div></li>'

    todo_01 = u"""<div class="todo">
      <b>① 画主干图（本节是全页的骨架，最先做）。</b>打开 <b>%s-一页通-素材.md</b> 读「主线拆解」表，
      把 2–4 条主线画成一条从左到右的管道（或一个循环）：每层 2–4 个框、框内一行结论 + 一行关键数字；
      蓝线 = 主线流向，橙线 = 关键手段，紫线 = 评测归因，绿线 = 闭环回灌，灰虚线 = 拒答/分支。
      图层叠顺序参考已定稿页（RAG与检索 / Agent运行时与工具）的 01 节，直接改那份 SVG 结构最快。
    </div>""" % esc(mod)
    story_todo = u"""<div class="story"><b>主干叙事（TODO）</b>：用 150–250 字把上图串成一段话——
      每个环节一句「因为 X 所以 Y」，粗体只给关键词；结尾落在「这条线为什么能站住」。
      写完删掉本 TODO 框上的说明文字，保留段落。</div>"""
    fig_todo = u"""<div class="fig"><svg viewBox="0 0 1450 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%s 第二张图占位">
      <text x="60" y="70" font-size="15" font-weight="800" fill="#B45309">TODO：04 第二张图 —— 本模块最硬的一笔账</text>
      <text x="60" y="104" font-size="12.5" fill="#4E5969">从素材包里挑一个「不算不知道、一算吓一跳」的推导（数量级对比画成两根比例条），</text>
      <text x="60" y="128" font-size="12.5" fill="#4E5969">左面板画算力/成本账，右面板画延迟/收益账；格式参考已定稿页的 04 节。</text>
    </svg></div>""" % esc(mod)
    nums_todo = u"""<div class="nums">
      <div class="ncard b"><div class="t">TODO 数字 1（蓝）</div><div class="big">? = ?</div>
        <div class="d">每个数都要带推导，只报结果是会被追问倒的。挑能体现「数量级」的数。</div></div>
      <div class="ncard o"><div class="t">TODO 数字 2（橙）</div><div class="big">? → ?</div>
        <div class="d">口径不能混的数（绝对/相对/累计）最适合放这里。</div></div>
      <div class="ncard b"><div class="t">TODO 数字 3（蓝）</div><div class="big">? × ?</div>
        <div class="d">相乘/相加关系、上限/下界关系优先。</div></div>
    </div>"""

    html = u"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(mod)s · 一页复习舱</title>
<style>%(css)s</style>
</head>
<body data-mode="mid">
<!-- %(marker)s · 由 output/_gen_onepage.py 生成；TODO 桩补完后本页转为手工维护 -->
<div class="wrap">

<header>
  <div class="kicker">STUDY MODULE · P0 · 一页复习舱</div>
  <h1>%(mod)s
    <small>%(nc)d 张母题 · %(nq)d 道题 · %(np)d 个项目 —— 一条线：TODO（读完素材包「主线拆解」后写一句链式概括，替换本句）</small>
  </h1>

  <div class="bar">
    <span class="lab">深度</span>
    <button class="m" data-mode-btn="quick" type="button">30 秒</button>
    <button class="m" data-mode-btn="mid" type="button">3 分钟</button>
    <button class="m" data-mode-btn="deep" type="button">深挖</button>
    <span class="hint">默认 3 分钟层；选择会记住。打印时全部展开。</span>
  </div>

  <div class="self">
    <div class="lab">20 秒版（闭卷自填 · 自动存在本机）</div>
    <textarea id="self20" placeholder="先别翻页：用 20 秒把这一模块讲一遍，写在这里。填不出的那句 = 明天复训第一条。"></textarea>
    <div class="ok" id="selfOk"></div>
  </div>
</header>

<!-- 01 主干图 -->
<section class="lv-quick">
  <h2><span class="num">01</span>主干：TODO（用 6–10 个字写成一条链，如「存 → 取 → 用与证」）<span class="src">正本 wiki/topics/%(mod)s/</span></h2>
  <div class="h2sub">TODO：一句话说明分层走法与全页唯一主张。</div>
  <div class="fig">
  <svg viewBox="0 0 1450 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="%(mod)s 主干图占位">
    <text x="60" y="70" font-size="15" font-weight="800" fill="#B45309">TODO：01 主干图 —— 见上方说明与素材包</text>
    <text x="60" y="104" font-size="12.5" fill="#4E5969">图例行（蓝主线/橙手段/紫评测/绿回灌/灰虚分支）+ 3–5 层框，图层叠顺序参考已定稿页。</text>
  </svg>
  </div>
  %(story)s
</section>

<!-- 02 检索表 -->
<section class="lv-mid">
  <h2><span class="num">02</span>检索表：%(nc)d 张母题 ↔ 题号 ↔ 项目<span class="src">正本 模块卡 第 3/4/5 节</span></h2>
  <div class="h2sub">默认<b>遮住机制与证据</b>（康奈尔线索栏）—— 先看母题名和题号自己讲一遍，再点「对答案」。</div>
  <div class="bar" style="margin-top:0;margin-bottom:8px">
    <button class="m" id="cueToggle" type="button">对答案</button>
    <span class="hint">遮住时才是复习，展开时是检索。</span>
  </div>
  <table id="mainTable" class="masked">
    <thead><tr><th style="width:110px">母题</th><th style="width:120px">它回答什么</th><th>关键机制（一句话）</th><th style="width:70px">题号</th><th style="width:280px">项目证据</th></tr></thead>
    <tbody>
%(rows)s
    </tbody>
  </table>
</section>

<!-- 03 闭卷器 -->
<section class="lv-mid">
  <h2><span class="num">03</span>今日闭卷 · 选一张母题开讲<span class="src">cue 取自母题卡「二、自测」</span></h2>
  <div class="h2sub">口述作答，说完再点开知识点与判据对照。<b>别边看边答</b> —— 那是认读不是回忆。</div>
  <div class="rec">
    <div class="row">
      <select id="cardSel"></select>
      <button type="button" id="critBtn">答完了，看知识点与判据</button>
      <button type="button" class="ghost" id="resetBtn">换一张</button>
    </div>
    <ol id="cueList"></ol>
    <div id="ansBox">
      <div class="ptT">知识点清单 · 取自该母题卡「一、教材」</div>
      <ol id="ptList" class="pts"></ol>
      <div class="crit" id="critBox"></div>
    </div>
    <div class="tip">题面是教材自测题的压缩版；知识点与判据默认收起 —— 讲完再点开对照。<b>完整推导仍不在这一页</b>，在对应母题卡的「二、自测」与「一、教材」。</div>
  </div>
</section>

<!-- 04 第二张图 -->
<section class="lv-deep">
  <h2><span class="num">04</span>TODO：本模块最硬的一笔账<span class="src">正本 母题卡推导</span></h2>
  <div class="h2sub">TODO：一句话说明两笔账各是什么、为什么是数量级问题。</div>
  %(fig04)s
</section>

<!-- 05 数字板 -->
<section class="lv-deep">
  <h2><span class="num">05</span>要能现场算出来的数<span class="src">正本 母题卡「一、教材」推导</span></h2>
  <div class="h2sub">每个数都要带推导，只报结果是会被追问倒的。</div>
  %(nums)s
</section>

<!-- 06 误判 -->
<section class="lv-deep">
  <h2><span class="num">06</span>最容易说错的话<span class="src">正本 母题卡「二、自测」纠错题原话</span></h2>
  <div class="h2sub">说对前半句没用，后半句才是判据。</div>
  <div class="mis">
%(mis)s
  </div>
</section>

<!-- 07 验收门 -->
<section class="lv-deep">
  <h2><span class="num">07</span>验收门（全勾才算闭环）<span class="src">正本 模块卡 第 6 节</span></h2>
  <div class="gate">
    <ul>
%(gate)s
    </ul>
  </div>
</section>

<footer>
  边界：%(boundary)s —— 边界外的内容不进本页。
</footer>

</div>
%(js)s""" % {
        'mod': esc(mod), 'css': page_css(), 'nc': n_cards, 'nq': n_q, 'np': len(projects),
        'rows': '\n'.join(rows).rstrip('\n'), 'mis': '\n'.join(mis_rows).rstrip('\n'),
        'gate': gate_html, 'boundary': esc(boundary), 'marker': MARKER,
        'story': story_todo, 'fig04': fig_todo, 'nums': nums_todo,
        'js': page_js(u'mv.onepage.' + mod + u'.v1', cards_js, order),
    }
    return html


def build_material(mod, card_secs, mothers_data, order, qlist, projects, gate, boundary):
    L = []
    L.append(u'# %s · 一页通素材包\n' % mod)
    L.append(u'> 由 `output/_tools/_gen_onepage.py` 从正本抽取，只读参考；修改请回模块卡 / 母题卡。成品页在 `site/onepage/`。\n')
    L.append(u'## 0 · 模块边界（页脚用）\n\n%s\n' % boundary)
    L.append(u'## 2 · 主线拆解（画 01 主干图的骨架）\n')
    L.append(card_secs.get(2, u'（模块卡缺第 2 节）').strip() + '\n')
    L.append(u'## 3 · 母题清单 → 检索表\n')
    for code in order:
        md = mothers_data[code]
        qn = '、'.join(str(n) for n, t, cs in qlist if code in cs) or '—'
        pj = ' / '.join(name for name, cs in projects if code in cs) or '—'
        L.append(u'- **%s %s** ｜题号 %s ｜项目 %s' % (code, md['desc'], qn, pj))
    L.append(u'\n## 4 · 题单（覆盖度校验）\n')
    L.append(card_secs.get(4, u'（模块卡缺第 4 节）').strip() + '\n')
    L.append(u'## 5 · 项目映射（检索表「项目证据」列的来源）\n')
    L.append(card_secs.get(5, u'（模块卡缺第 5 节）').strip() + '\n')
    L.append(u'## 母题卡要点（03 闭卷器数据 + 05 数字板的来源）\n')
    for code in order:
        md = mothers_data[code]
        L.append(u'### %s %s\n' % (code, md['title'] or md['desc']))
        L.append(u'**判据**：%s\n' % md['crit'])
        for st_, pp in md['secs']:
            L.append(u'- %s：' % st_)
            for x in pp:
                L.append(u'  - %s' % x)
        if md['cues']:
            L.append(u'**自测 cue**：')
            for c in md['cues']:
                L.append(u'- %s' % c)
        L.append('')
    L.append(u'## 6 · 验收门\n')
    for g in gate:
        L.append(u'- [ ] %s' % g.replace('<b>', '**').replace('</b>', '**'))
    return u'\n'.join(L)


# ---------------------------------------------------------------- 主流程

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    if not args:
        mods = sorted(os.listdir(TOPICS))
        mods = [m for m in mods if os.path.isdir(os.path.join(TOPICS, m))]
        print(u'可用模块（wiki/topics/）：')
        for m in mods:
            p = os.path.join(OUT, m + u'-一页通.html')
            mark = 'scaffold' if os.path.exists(p) and MARKER in read(p) else \
                   ('done' if os.path.exists(p) else '----')
            print(u'  %-14s %s' % (m, mark))
        print(u'\n用法：python output/_gen_onepage.py <模块名> [--force]')
        return

    mod = args[0]
    d = find_module_dir(mod)
    card = read_module_card(d)
    secs = split_sections(card)
    mlist = parse_mother_list(secs.get(3, ''))
    if not mlist:
        sys.exit(u'模块卡第 3 节没有解析到母题清单行，请检查表格格式')
    all_codes = [c for c, _, _ in mlist]
    qlist = parse_question_list(secs.get(4, ''), set(all_codes))
    projects = parse_projects(secs.get(5, ''))
    gate = parse_gate(secs.get(6, ''))
    boundary = parse_boundary(secs.get(0, ''))

    mother_files = []
    mothers_data = {}
    for code, desc, line_no in mlist:
        fs = glob.glob(os.path.join(d, u'母题-%s-*.md' % code))
        if not fs:
            print(u'  ! 缺母题卡：%s（跳过其 cue/要点）' % code)
            mothers_data[code] = {'desc': desc, 'title': '', 'secs': [], 'cues': [], 'crit': u'（待补）'}
            continue
        title, ssecs, cues, crit = parse_mother_card(fs[0])
        mother_files.append((code, fs[0]))
        mothers_data[code] = {'desc': desc, 'title': title, 'secs': ssecs, 'cues': cues, 'crit': crit}
    order = [c for c in all_codes if c in mothers_data]

    mat = build_material(mod, secs, mothers_data, order, qlist, projects, gate, boundary)
    mat_p = os.path.join(OUT, mod + u'-一页通-素材.md')
    io.open(mat_p, 'w', encoding='utf-8', newline='\n').write(mat)

    html_p = os.path.join(SITE_ONEPAGE, mod + u'-一页通.html')
    if os.path.exists(html_p):
        old = read(html_p)
        if MARKER not in old and not force:
            sys.exit(u'%s 已是定稿页（无脚手架标记），不覆盖。确认要覆盖用 --force。' % html_p)
    html = build_html(mod, secs, mothers_data, mother_files, order, qlist, projects, gate, boundary)
    io.open(html_p, 'w', encoding='utf-8', newline='\n').write(html)
    print(u'written %s (%d chars, %d cards, %d questions)' % (html_p, len(html), len(order), len(qlist)))
    print(u'written %s' % mat_p)


if __name__ == '__main__':
    main()
