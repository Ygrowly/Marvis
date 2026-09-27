# -*- coding: utf-8 -*-
"""更新 test_render.js 里那条已过时的断言（CRLF 安全写入）。

原断言：「没补答案的模块页面不出现空答案块」——母题层已全库补齐（87/87），
这条反了。改成正向断言：13 个模块概览页都要挂上母题完整回答。
"""
import pathlib

P = pathlib.Path(r'E:/notes/Marvis/site/_tests/test_render.js')
b = P.read_bytes()
assert b.count(b'\r\n') == b.count(b'\n'), '行尾不统一'

old = """
ok('没补答案的模块页面不出现空答案块',
  !fs.readFileSync(path.join(MOD, 'Redis.html'), 'utf8').includes('完整回答 · 口述稿'));"""
new = """
/* 母题层已全库补齐（2026-09-28：87/87），断言反过来：每个模块都要有完整回答块 */
const ALLMODS = ['MySQL', 'LLM与上下文', 'Agent运行时与工具', 'Redis', 'RAG与检索', '网络基础',
  '评测观测与治理', '消息队列', '并发与锁', 'Linux与部署', 'PostgreSQL', '操作系统', '数据存储选型'];
const noAns = ALLMODS.filter(m => !fs.readFileSync(path.join(MOD, m + '.html'), 'utf8')
  .includes('完整回答 · 口述稿'));
ok('13 个模块概览页都挂上了母题完整回答', noAns.length === 0, noAns.join('/') || '全部有');"""

ob = old.lstrip('\n').encode('utf-8').replace(b'\n', b'\r\n')
nb = new.encode('utf-8').replace(b'\n', b'\r\n')
assert b.count(ob) == 1, b.count(ob)
P.write_bytes(b.replace(ob, nb))
print('ok')
