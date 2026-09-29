/* 校验 three.min.js 是否完整可用：语法通过 + UMD 全局挂载 + REVISION 正确 */
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const p = path.join(__dirname, '..', 'site', '_build', 'three', 'three.min.js');
const s = fs.readFileSync(p, 'utf8');
console.log('bytes = ' + s.length);
console.log('tail  = ' + JSON.stringify(s.slice(-24)));
try {
  new vm.Script(s, { filename: 'three.min.js' });
  console.log('syntax = OK');
} catch (e) {
  console.log('syntax = FAIL: ' + e.message.slice(0, 200));
  process.exit(1);
}
const ctx = { window: {}, self: {}, globalThis: {} };
ctx.globalThis = ctx;
vm.createContext(ctx);
try {
  vm.runInContext(s, ctx, { timeout: 20000 });
  const T = ctx.THREE || ctx.window.THREE;
  console.log('THREE = ' + typeof T + (T ? ', REVISION = ' + T.REVISION : ''));
  if (!T) { console.log('结果 = 未挂载全局 THREE'); process.exit(1); }
  console.log('结果 = 可用');
} catch (e) {
  console.log('run = FAIL: ' + e.message.slice(0, 200));
  process.exit(1);
}
