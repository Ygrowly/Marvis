# -*- coding: utf-8 -*-
"""给 test_render.js 加「总纲题不能消失」的守卫断言（CRLF 安全写入）。"""
import pathlib

P = pathlib.Path(r'E:/notes/Marvis/site/_tests/test_render.js')
b = P.read_bytes()
assert b.count(b'\r\n') == b.count(b'\n'), '行尾不统一'

old = "console.log('\\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));"
old_b = old.encode('utf-8').replace(b'\n', b'\r\n')

new = r"""
console.log('\n【总纲题：归属主线不是行号的题不能消失】');
/* 2026-09-27 审查发现：md 题单里「归属主线」写的是「全 / 前提 / ——」的题，
   _by_line 按行号分组时归不到任何主线页 —— 6 道总纲题（如何评测一个 Agent、
   设计一个生产级 RAG、MQ 三大作用…）一直没露面。现在它们落到模块概览页。 */
const Z1 = ['MySQL', 'LLM与上下文', 'Agent运行时与工具', 'Redis', 'RAG与检索',
  '网络基础', '评测观测与治理', '消息队列', '并发与锁', 'Linux与部署'];
const reEsc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const idRe = new RegExp('card-id="(' + Z1.map(reEsc).join('|') + ')-q\\d+"', 'g');
const ids = new Set();
fs.readdirSync(MOD).forEach(f => {
  const h = fs.readFileSync(path.join(MOD, f), 'utf8');
  (h.match(idRe) || []).forEach(x => ids.add(x.slice(9, -1)));
});
ok('一档十模块 253 道题全部都能翻到', ids.size === 253, ids.size + ' 道');
ok('原先消失的总纲题已露出（Redis 分布式锁 / 如何评测一个 Agent / 设计生产级 RAG）',
  ids.has('Redis-q19') && ids.has('评测观测与治理-q1') && ids.has('RAG与检索-q1'), '');
ok('总纲题带「不属于某一条主线」的说明',
  fs.readFileSync(path.join(MOD, '评测观测与治理.html'), 'utf8')
    .includes('本模块的题 · 总纲'));

console.log('\n' + (fails ? '❌ ' + fails + ' 项失败' : '✅ 全部通过'));""".lstrip('\n')
new_b = new.encode('utf-8').replace(b'\n', b'\r\n')

assert b.count(old_b) == 1, b.count(old_b)
P.write_bytes(b.replace(old_b, new_b))
print('ok')
