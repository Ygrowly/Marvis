/* 由 site/build.py 生成，别手改 —— 改 build.py 里的 mmd_boot() 再重跑。
   浏览器端 mermaid 渲染：优先站点自带的 mermaid.min.js，取不到再走 CDN。 */
(function () {
  var CDN = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js";
  /* 本脚本放在 _data/ 下，用它自己的 src 反推站点根，各层目录的页面都能拿到对的路径 */
  var me = document.currentScript;
  var LOCAL = ((me && me.src) ? me.src.replace(/_data\/mmd-boot\.js.*$/, "") : "")
    + "_build/mermaid/mermaid.min.js";
  /* mermaid 要量文字尺寸：图若躺在折叠面板（display:none）里，量出来是 0，
     只会渲一个 16×16 的空图。渲染前把隐藏的祖先临时搬到屏幕外「显形」，渲完原样还原。 */
  function reveal(el) {
    var out = [], p = el.parentElement;
    while (p && p !== document.documentElement) {
      var cs = getComputedStyle(p);
      if (cs.display === "none" || cs.visibility === "hidden") {
        out.push([p, p.getAttribute("style") || ""]);
        p.style.cssText = "display:block !important; visibility:hidden !important;" +
          "position:absolute !important; left:-99999px !important; top:0 !important;" +
          "width:1600px !important;";
      }
      p = p.parentElement;
    }
    return out;
  }
  function restore(chain) {
    chain.forEach(function (x) {
      if (x[1]) x[0].setAttribute("style", x[1]); else x[0].removeAttribute("style");
    });
  }
  function boot() {
    if (!window.mermaid) return;
    window.mermaid.initialize({
      startOnLoad: false, theme: "neutral", securityLevel: "loose",
      fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
      flowchart: { useMaxWidth: false }, sequence: { useMaxWidth: false },
      gantt: { useMaxWidth: false }, class: { useMaxWidth: false },
      state: { useMaxWidth: false }, er: { useMaxWidth: false },
      journey: { useMaxWidth: false }, pie: { useMaxWidth: false }
    });
    var nodes = [].slice.call(document.querySelectorAll(".mermaid"));
    var chains = nodes.map(reveal);
    /* 宽图会被容器裁掉右边——跟构建期内联那条路一样，给一句「可左右拖动」的提示 */
    function hint() {
      nodes.forEach(function (d) {
        var svg = d.querySelector("svg");
        if (!svg) return;
        var w = parseFloat(svg.getAttribute("width")) || 0;
        if (w <= 880) return;
        var prev = d.previousElementSibling;
        if (prev && prev.className === "mv-mmd-hint") return;
        var p = document.createElement("p");
        p.className = "mv-mmd-hint";
        p.textContent = "图较宽，可左右拖动看全";
        d.parentNode.insertBefore(p, d);
      });
    }
    var fin = function () { chains.forEach(restore); hint(); };
    try {
      var r = window.mermaid.run({ querySelector: ".mermaid" });
      if (r && r.then) r.then(fin, fin); else fin();
    } catch (e) { fin(); console.error("[mermaid]", e); }
  }
  function go(url, next) {
    var s = document.createElement("script");
    s.src = url;
    s.onload = function () { boot(); };
    s.onerror = function () {
      if (s.parentNode) s.parentNode.removeChild(s);
      if (next) go(next, null);
      else console.warn("[mermaid] 本地与 CDN 都没取到，图保留源码");
    };
    document.head.appendChild(s);
  }
  go(LOCAL, CDN);
})();
