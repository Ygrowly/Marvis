'use strict';
/* 共享假 DOM 元素桩（审查 smell 修复：三份测试的同一字面量收拢到此）。
   remove/style 是今日页渲染 IIFE 需要的最小面；按需在测试里再扩。 */
function elStub(id) {
  return { id: id, innerHTML: '', textContent: '', hidden: true, value: '',
           remove: function () {}, style: {} };
}
module.exports = { elStub: elStub };
