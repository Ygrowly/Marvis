/* Marvis 知识宫殿 · 组件库 v0.1
   八个组件：flip-card / timer-ring / check-list / palace-map / stat-bars / metric-strip
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
  // 可选子元素 <div class="mv-fc-more">…</div>：背面下半段（2026-09-26 加，
  // 用来挂「所属母题的完整回答 + 单卡入口」，内容由构建脚本生成，原样插入不转义）
  class FlipCard extends HTMLElement {
    connectedCallback() {
      if (this._built) return; this._built = true;
      var q = this.getAttribute('q') || '';
      var a = this.getAttribute('a') || '';
      var tag = this.getAttribute('tag') || '';
      var gradable = this.hasAttribute('gradable');
      var moreEl = this.querySelector('.mv-fc-more');
      var more = moreEl ? moreEl.outerHTML : '';
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
            more +
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
      // 下半段有自己的交互（折叠、链接），别让点击冒泡去翻面
      var m2 = this.querySelector('.mv-fc-more');
      if (m2) m2.addEventListener('click', function (e) { e.stopPropagation(); });
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

  customElements.define('palace-map', PalaceMap);
  customElements.define('stat-bars', StatBars);
  customElements.define('metric-strip', MetricStrip);
  customElements.define('collapse-panel', CollapsePanel);
  customElements.define('figure-box', FigureBox);

  window.Marvis = {
    store: store, today: today, addDays: addDays,
  };

  /* 云同步层（2026-10-01）：动态挂在自己旁边，165 个引用页面不用改一行。
     用 currentScript 推出同目录，相对路径在根目录页和 modules/ 页都对。 */
  (function () {
    try {
      var cur = document.currentScript;
      if (!cur || !cur.src) return;
      if (window.MarvisSync) return;
      var s = document.createElement('script');
      s.src = cur.src.replace(/marvis\.js(\?.*)?$/, 'sync.js');
      document.head.appendChild(s);
    } catch (e) {}
  })();
})();
