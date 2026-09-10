/* Marvis 知识宫殿 · 组件库 v0.1
   七个组件：flip-card / timer-ring / check-list / review-deck / palace-map / stat-bars / metric-strip
   零依赖，classic script（不是 module），因此 file:// 双击直接可用。
   所有用户数据存 localStorage，键名前缀 mv.
*/
(function () {
  'use strict';

  // ---------- 工具 ----------
  var store = {
    get: function (k, d) {
      try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; }
      catch (e) { return d; }
    },
    set: function (k, v) {
      try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {}
    }
  };

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    }).replace(/\r?\n/g, '&#10;');
  }
  function pad(n) { return String(n).padStart(2, '0'); }
  function today() { var d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function addDays(s, n) {
    var d = new Date(s + 'T00:00:00'); d.setDate(d.getDate() + n);
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }
  function beep(times) {
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      var ctx = new Ctx();
      for (var i = 0; i < (times || 3); i++) {
        (function (i) {
          var o = ctx.createOscillator(), g = ctx.createGain();
          o.connect(g); g.connect(ctx.destination);
          o.type = 'sine'; o.frequency.value = 880;
          var t0 = ctx.currentTime + i * 0.22;
          g.gain.setValueAtTime(0.0001, t0);
          g.gain.exponentialRampToValueAtTime(0.18, t0 + 0.02);
          g.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.18);
          o.start(t0); o.stop(t0 + 0.2);
        })(i);
      }
    } catch (e) {}
  }

  // ---------- 1. flip-card 翻转卡 ----------
  // <flip-card q="问题" a="答案" tag="MySQL" gradable></flip-card>
  class FlipCard extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var q = this.getAttribute('q') || '';
      var a = this.getAttribute('a') || '';
      var tag = this.getAttribute('tag') || '';
      var gradable = this.hasAttribute('gradable');
      this.innerHTML =
        '<div class="mv-fc">' +
          '<div class="mv-face mv-face-front">' +
            (tag ? '<div class="mv-fc-tag">' + esc(tag) + '</div>' : '') +
            '<p class="mv-fc-q">' + esc(q) + '</p>' +
            '<div class="mv-fc-hint">先闭卷说出答案，再点击翻面</div>' +
          '</div>' +
          '<div class="mv-face mv-face-back">' +
            (tag ? '<div class="mv-fc-tag">' + esc(tag) + ' · 答案</div>' : '') +
            '<p class="mv-fc-a">' + esc(a) + '</p>' +
            (gradable
              ? '<div class="mv-fc-actions">' +
                  '<button class="mv-btn mv-btn-bad" data-g="0">忘了</button>' +
                  '<button class="mv-btn mv-btn-ok" data-g="1">过关</button>' +
                '</div>'
              : '<div class="mv-fc-hint">点击翻回正面</div>') +
          '</div>' +
        '</div>';
      var fc = this.querySelector('.mv-fc');
      fc.addEventListener('click', function () { fc.classList.toggle('is-flip'); });
      if (gradable) {
        var self = this;
        this.querySelectorAll('.mv-fc-actions button').forEach(function (b) {
          b.addEventListener('click', function (e) {
            e.stopPropagation();
            self.dispatchEvent(new CustomEvent('mv-grade', {
              bubbles: true,
              detail: { id: self.getAttribute('card-id'), ok: b.getAttribute('data-g') === '1' }
            }));
          });
        });
      }
    }
  }

  // ---------- 2. timer-ring 计时环 ----------
  // <timer-ring seconds="90" label="项目 90 秒口述" note="超时即不合格"></timer-ring>
  class TimerRing extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var total = parseInt(this.getAttribute('seconds') || '60', 10);
      var label = this.getAttribute('label') || '计时';
      var note = this.getAttribute('note') || '';
      var C = 2 * Math.PI * 36;
      this.innerHTML =
        '<div class="mv-timer">' +
          '<div class="mv-timer-ring">' +
            '<svg width="84" height="84" viewBox="0 0 84 84">' +
              '<circle class="mv-timer-bg" cx="42" cy="42" r="36"></circle>' +
              '<circle class="mv-timer-fg" cx="42" cy="42" r="36" ' +
                'stroke-dasharray="' + C.toFixed(1) + '" stroke-dashoffset="0"></circle>' +
            '</svg>' +
            '<div class="mv-timer-num">' + this._fmt(total) + '</div>' +
          '</div>' +
          '<div class="mv-timer-body">' +
            '<div class="mv-timer-label">' + esc(label) + '</div>' +
            (note ? '<div class="mv-timer-note">' + esc(note) + '</div>' : '') +
            '<div class="mv-timer-actions">' +
              '<button class="mv-btn mv-btn-primary" data-a="start">开始</button>' +
              '<button class="mv-btn" data-a="reset">重置</button>' +
            '</div>' +
          '</div>' +
        '</div>';
      this._total = total; this._left = total; this._t = null;
      var self = this;
      this.querySelectorAll('button').forEach(function (b) {
        b.addEventListener('click', function () {
          var a = b.getAttribute('data-a');
          if (a === 'start') self.toggle(b); else self.reset(b);
        });
      });
    }
    _fmt(s) {
      var m = Math.floor(Math.abs(s) / 60), r = Math.abs(s) % 60;
      return (s < 0 ? '-' : '') + m + ':' + pad(r);
    }
    _paint() {
      var C = 2 * Math.PI * 36;
      var ratio = Math.max(0, this._left) / this._total;
      this.querySelector('.mv-timer-fg').setAttribute('stroke-dashoffset', (C * (1 - ratio)).toFixed(1));
      this.querySelector('.mv-timer-num').textContent = this._fmt(this._left);
      var box = this.querySelector('.mv-timer');
      box.classList.toggle('is-warn', this._left <= this._total * 0.25 && this._left > 0);
      box.classList.toggle('is-over', this._left <= 0);
    }
    toggle(btn) {
      var self = this;
      if (this._t) {
        clearInterval(this._t); this._t = null; btn.textContent = '继续';
        return;
      }
      btn.textContent = '暂停';
      var end = Date.now() + this._left * 1000;
      this._t = setInterval(function () {
        self._left = Math.round((end - Date.now()) / 1000);
        self._paint();
        if (self._left <= 0) {
          clearInterval(self._t); self._t = null;
          btn.textContent = '开始'; beep(3);
        }
      }, 200);
    }
    reset(btn) {
      if (this._t) { clearInterval(this._t); this._t = null; }
      this._left = this._total; this._paint();
      var b = this.querySelector('[data-a="start"]'); if (b) b.textContent = '开始';
    }
  }

  // ---------- 3. check-list 待办 ----------
  // <check-list key="daily" title="今日保底" reset="daily"><li>文本</li></check-list>
  class CheckList extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var key = 'mv.check.' + (this.getAttribute('key') || 'default');
      var title = this.getAttribute('title') || '待办';
      var reset = this.getAttribute('reset');
      var items = [].map.call(this.querySelectorAll('li'), function (li) {
        return {
          text: (li.childNodes[0] && li.childNodes[0].nodeType === 3 ? li.childNodes[0].textContent : li.textContent).trim(),
          sub: li.querySelector('em') ? li.querySelector('em').textContent : ''
        };
      });
      var saved = store.get(key, null);
      var states = (saved && saved.states && saved.states.length === items.length &&
                    (!reset || saved.date === today()))
        ? saved.states : items.map(function () { return false; });

      var self = this;
      function save() { store.set(key, { date: today(), states: states }); self._repaint(); }

      this.innerHTML =
        '<div class="mv-cl">' +
          '<div class="mv-cl-head"><span class="mv-cl-title">' + esc(title) + '</span>' +
          '<span class="mv-cl-count"></span></div>' +
          items.map(function (it, i) {
            return '<div class="mv-cl-item" data-i="' + i + '">' +
              '<span class="mv-cl-box">&#10003;</span>' +
              '<span><span class="mv-cl-text">' + esc(it.text) + '</span>' +
              (it.sub ? '<br><span class="mv-cl-sub">' + esc(it.sub) + '</span>' : '') +
              '</span></div>';
          }).join('') +
        '</div>';
      this._items = items; this._states = states; this._save = save;
      this.querySelectorAll('.mv-cl-item').forEach(function (el) {
        el.addEventListener('click', function () {
          var i = +el.getAttribute('data-i');
          self._states[i] = !self._states[i]; self._save();
        });
      });
      this._repaint();
    }
    _repaint() {
      var st = this._states, n = 0, self = this;
      this.querySelectorAll('.mv-cl-item').forEach(function (el) {
        var on = st[+el.getAttribute('data-i')];
        el.classList.toggle('on', !!on); if (on) n++;
      });
      this.querySelector('.mv-cl-count').textContent = n + ' / ' + st.length;
    }
  }

  // ---------- 4. review-deck 间隔复训牌组（1-3-7-14-30） ----------
  // <review-deck src="#deck-data" title="今日复训"></review-deck>
  var LADDER = [1, 3, 7, 14, 30];

  // 评分写回调度：训练台与母题页共用同一份状态
  function gradeCard(cardId, ok) {
    if (!cardId) return null;
    var all = store.get('mv.review', {});
    var s = all[cardId] || { idx: 0 };
    if (ok) s.idx = (s.idx || 0) + 1; else s.idx = 0;
    s.next = addDays(today(), LADDER[Math.min(Math.max(s.idx - 1, 0), LADDER.length - 1)]);
    s.last = today();
    all[cardId] = s;
    store.set('mv.review', all);
    return s;
  }
  class ReviewDeck extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      this.decks = ReviewDeck.readDecks();
      this.deckIdx = 0;
      this.state = store.get('mv.review', {});
      this.queue = []; this.idx = -1;
      var self = this;
      this.innerHTML =
        '<div class="mv-rd">' +
          '<div class="mv-rd-head"><span class="mv-rd-title">' +
            esc(this.getAttribute('title') || '间隔复训') + '</span>' +
            '<span class="mv-rd-stat"></span></div>' +
          '<div class="mv-rd-tabs"></div>' +
          '<div class="mv-rd-slot"></div>' +
          '<div class="mv-rd-actions" style="margin-top:12px;display:flex;gap:8px">' +
            '<button class="mv-btn mv-btn-primary" data-a="start">开始今日复训</button>' +
            '<button class="mv-btn" data-a="reset">重置进度</button>' +
          '</div>' +
          '<div class="mv-rd-ladder"></div>' +
        '</div>';
      this.querySelectorAll('button[data-a]').forEach(function (b) {
        b.addEventListener('click', function () {
          if (b.getAttribute('data-a') === 'start') self.start();
          else { if (confirm('清空所有复训进度？不可恢复。')) { store.set('mv.review', {}); self.state = {}; self.render(); } }
        });
      });
      this._slot = this.querySelector('.mv-rd-slot');
      this._slot.addEventListener('mv-grade', function (e) { self.grade(e.detail.ok); });
      this.render();
    }
    // 数据来源：window.MARVIS_DECKS = [{id,name,cards:[…]}]；兼容旧的 MARVIS_DECK
    static readDecks() {
      if (Array.isArray(window.MARVIS_DECKS) && window.MARVIS_DECKS.length) return window.MARVIS_DECKS;
      if (Array.isArray(window.MARVIS_DECK) && window.MARVIS_DECK.length) {
        return [{ id: 'all', name: '全部', cards: window.MARVIS_DECK }];
      }
      return [];
    }
    get deck() { return this.decks[this.deckIdx] || { cards: [] }; }
    dueOf(d) {
      var t = today(), st = this.state;
      return ((d && d.cards) || []).filter(function (c) {
        var s = st[c.id]; return !s || !s.next || s.next <= t;
      });
    }
    render() {
      var self = this;

      var tabs = this.querySelector('.mv-rd-tabs');
      if (this.decks.length > 1) {
        tabs.innerHTML = this.decks.map(function (dk, i) {
          var n = self.dueOf(dk).length;
          return '<button class="mv-rd-tab' + (i === self.deckIdx ? ' on' : '') + '" data-d="' + i + '">' +
            esc(dk.name || dk.id) + '<span class="n">' + n + '/' + ((dk.cards || []).length) + '</span></button>';
        }).join('');
        tabs.querySelectorAll('.mv-rd-tab').forEach(function (b) {
          b.addEventListener('click', function () {
            self.deckIdx = +b.getAttribute('data-d');
            self.queue = []; self.idx = -1;
            self.render();
          });
        });
      } else {
        tabs.innerHTML = '';
      }

      var dk = this.deck;
      var due = this.dueOf(dk);
      this.querySelector('.mv-rd-stat').textContent =
        '今日到期 ' + due.length + ' · 本牌组 ' + ((dk.cards || []).length) + ' 个';

      if (this.idx < 0 || this.idx >= this.queue.length) {
        this._slot.innerHTML = '<div class="mv-rd-empty">' +
          (due.length ? '点「开始今日复训」，一次一个母题，先说后翻。' : '今天没有到期内容。') +
          '</div>';
      } else {
        var c = this.queue[this.idx];
        this._slot.innerHTML =
          '<flip-card gradable card-id="' + esc(c.id) + '" tag="' + esc(c.tag || '') +
          '" q="' + esc(c.q) + '" a="' + esc(c.a) + '"></flip-card>' +
          (c.href ? '<p class="mv-note" style="text-align:right"><a href="' + esc(c.href) +
            '" style="color:var(--mv-accent)">打开母题页 →</a></p>' : '');
      }

      var cur = this.idx >= 0 ? this.queue[this.idx] : null;
      var lvl = cur && this.state[cur.id] ? (this.state[cur.id].idx || 0) : 0;
      this.querySelector('.mv-rd-ladder').innerHTML = LADDER.map(function (v, i) {
        return '<span class="mv-rd-step' + (cur && i === Math.min(lvl, 4) ? ' on' : '') + '">' + v + '天</span>';
      }).join('') + '<span class="mv-rd-step" style="border:none;color:var(--mv-muted)">忘了归零重来</span>';
    }
    start() {
      this.queue = this.dueOf(this.deck).slice();
      this.idx = this.queue.length ? 0 : -1;
      this.render();
    }
    grade(ok) {
      var c = this.queue[this.idx];
      if (!c) return;
      gradeCard(c.id, ok);
      this.state = store.get('mv.review', {});
      this.idx++;
      this.render();
    }
  }

  // ---------- 5. palace-map 宫殿地图 ----------
  // <palace-map vault="Marvis"><li data-name data-file data-desc data-cellar></li></palace-map>
  class PalaceMap extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var vault = this.getAttribute('vault') || 'Marvis';
      var rooms = [].map.call(this.querySelectorAll('li'), function (li) {
        return {
          name: li.getAttribute('data-name') || '',
          file: li.getAttribute('data-file') || '',
          desc: li.getAttribute('data-desc') || '',
          icon: li.getAttribute('data-icon') || '',
          cellar: li.hasAttribute('data-cellar')
        };
      });
      var layout = this.getAttribute('layout') || 'grid';
      var wrapCls = layout === 'bar' ? 'mv-pm-bar' : 'mv-grid mv-grid-3';
      this.innerHTML = '<div class="' + wrapCls + '">' + rooms.map(function (r) {
        var href = r.file
          ? 'obsidian://open?vault=' + encodeURIComponent(vault) + '&file=' + encodeURIComponent(r.file)
          : '#';
        return '<a class="mv-pm-room' + (r.cellar ? ' cellar' : '') + '" href="' + href + '"' +
          (r.desc ? ' title="' + esc(r.desc) + '"' : '') + '>' +
          (r.icon ? '<div class="mv-pm-icon">' + esc(r.icon) + '</div>' : '') +
          '<div class="mv-pm-name">' + esc(r.name) + '</div>' +
          '<div class="mv-pm-desc">' + esc(r.desc) + '</div></a>';
      }).join('') + '</div>';
    }
  }

  // ---------- 6. stat-bars 数据条 ----------
  // <stat-bars title="" data="标签:值,标签:值" max="100" unit=""></stat-bars>
  class StatBars extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var title = this.getAttribute('title') || '';
      var max = parseFloat(this.getAttribute('max') || '100');
      var unit = this.getAttribute('unit') || '';
      var rows = (this.getAttribute('data') || '').split(',').filter(Boolean).map(function (s) {
        var p = s.split(':'); return { label: p[0], value: parseFloat(p[1]) || 0 };
      });
      this.innerHTML = '<div class="mv-sb">' +
        (title ? '<div class="mv-sb-title">' + esc(title) + '</div>' : '') +
        rows.map(function (r) {
          var pct = Math.min(100, (r.value / max) * 100).toFixed(0);
          return '<div class="mv-sb-row"><span class="mv-sb-label">' + esc(r.label) + '</span>' +
            '<span class="mv-sb-track"><span class="mv-sb-fill" style="width:' + pct + '%"></span></span>' +
            '<span class="mv-sb-val">' + r.value + unit + '</span></div>';
        }).join('') + '</div>';
    }
  }

  // ---------- 7. metric-strip 指标条 ----------
  // <metric-strip><li data-label data-value data-unit data-tone="ok|warn"></li></metric-strip>
  class MetricStrip extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var items = [].map.call(this.querySelectorAll('li'), function (li) {
        return {
          label: li.getAttribute('data-label') || '',
          value: li.getAttribute('data-value') || '',
          unit: li.getAttribute('data-unit') || '',
          tone: li.getAttribute('data-tone') || ''
        };
      });
      this.innerHTML = '<div class="mv-ms">' + items.map(function (it) {
        return '<div class="mv-ms-item"><div class="mv-ms-label">' + esc(it.label) + '</div>' +
          '<div class="mv-ms-value ' + (it.tone === 'ok' ? 'ok' : it.tone === 'warn' ? 'warn' : '') + '">' +
          esc(it.value) + (it.unit ? '<small> ' + esc(it.unit) + '</small>' : '') + '</div></div>';
      }).join('') + '</div>';
    }
  }

  // ---------- 8. collapse-panel 折叠分组 ----------
  // <collapse-panel title="两层追问" open>…内容…</collapse-panel>
  class CollapsePanel extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var title = this.getAttribute('title') || '展开';
      var open = this.hasAttribute('open');
      var body = this.innerHTML;
      this.innerHTML =
        '<div class="mv-cp' + (open ? ' is-open' : '') + '">' +
          '<button class="mv-cp-head" type="button">' +
            '<span>' + esc(title) + '</span><span class="mv-cp-mark"></span>' +
          '</button>' +
          '<div class="mv-cp-body">' + body + '</div>' +
        '</div>';
      var box = this.querySelector('.mv-cp');
      this.querySelector('.mv-cp-head').addEventListener('click', function () {
        box.classList.toggle('is-open');
      });
    }
  }

  // ---------- 9. figure-box 图容器 ----------
  // <figure-box num="1" title="标题" note="说明">…svg…</figure-box>
  class FigureBox extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var title = this.getAttribute('title') || '';
      var note = this.getAttribute('note') || '';
      var num = this.getAttribute('num') || '';
      var body = this.innerHTML;
      this.innerHTML =
        '<figure class="mv-fb">' +
          (title || num
            ? '<figcaption class="mv-fb-cap">' +
                (num ? '<span class="mv-fb-num">图 ' + esc(num) + '</span>' : '') +
                '<span class="mv-fb-title">' + esc(title) + '</span>' +
              '</figcaption>'
            : '') +
          '<div class="mv-fb-body">' + body + '</div>' +
          (note ? '<div class="mv-fb-note">' + esc(note) + '</div>' : '') +
        '</figure>';
    }
  }

  customElements.define('flip-card', FlipCard);
  customElements.define('timer-ring', TimerRing);
  customElements.define('check-list', CheckList);
  customElements.define('review-deck', ReviewDeck);
  customElements.define('palace-map', PalaceMap);
  customElements.define('stat-bars', StatBars);
  customElements.define('metric-strip', MetricStrip);
  customElements.define('collapse-panel', CollapsePanel);
  customElements.define('figure-box', FigureBox);

  window.Marvis = {
    store: store, today: today, addDays: addDays, LADDER: LADDER,
    gradeCard: gradeCard,
  };
})();
