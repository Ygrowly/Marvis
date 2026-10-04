# -*- coding: utf-8 -*-
"""网络 一页通定稿（一次性工具）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _onepage_lib import (B, O, P_, G, BD, OD, PD, GD, BS, OS, PS, GS, TX, TX2, TX3, GREY, LINE,
                          SVG_DEFS, legend, finish)

SVG01 = f'''<svg viewBox="0 0 1450 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="网络 主干图">
    {SVG_DEFS}
    {legend([(B, 'mB', '蓝 · 主线（怎么进来 → 怎么出去 → 怎么扛住）'),
             (O, 'mO', '橙 · 判据与数字'),
             (P_, 'mP', '紫 · 生产坑与失效'),
             (G, 'mG', '绿 · 项目落点与总判据')])}

    <g filter="url(#sh)">
      <rect x="90" y="100" width="1270" height="112" rx="8" fill="{BS}" stroke="{B}" stroke-width="1.6"/>
      <text x="106" y="124" font-size="13" font-weight="800" fill="{BD}">① 一次请求怎么走完（N1）—— 请求穿过的是一条链路，不是一个函数；每段失败的样子不一样</text>
      <text x="106" y="146" font-size="11.5" fill="{TX2}">DNS → TCP 三次握手 → HTTP → 网关 → 应用 → 上游；三次 = 可靠的最少次数，四次挥手 = 全双工两方向各自关</text>
      <text x="106" y="166" font-size="11.5" fill="{OD}">502 = 上游「活着但答得不对」；504 = 网关等上游超时——「慢」和「挂」排查方向完全不同（9.9 说反的那句）</text>
      <text x="106" y="186" font-size="11.5" fill="{TX2}">超时分层：每往里一层设得更短——超时总由最内层先触发，错误信息直接读出是哪一层放弃</text>
      <text x="1344" y="204" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">数驭穹图：网关超时=应用超时 → 两边同时放弃、无法归因——外层略长，让内层先超时留下自己的错误</text>
    </g>
    <line x1="725" y1="212" x2="725" y2="245" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="252" width="1270" height="130" rx="8" fill="{OS}" stroke="{O}" stroke-width="1.6"/>
      <text x="106" y="276" font-size="13" font-weight="800" fill="{TX}">② 数据怎么出去（N2）—— 短轮询 / 长轮询 / SSE / WebSocket：判据是「客户端要什么」，不是哪个更先进</text>
      <text x="106" y="298" font-size="11.5" fill="{OD}">SSE 精确定义：基于 HTTP 的长连接、单向（服务端→客户端）、text/event-stream——「是长连接」（9.9 当场答错）</text>
      <text x="106" y="318" font-size="11.5" fill="{PD}">生产三坑：代理默认缓冲（X-Accel-Buffering: no）· 不发心跳被空闲超时掐断 · 断线重连要 Last-Event-ID + 递增 sequence 才不漏事件</text>
      <text x="106" y="338" font-size="11.5" fill="{TX2}">选 SSE 的两个理由：① 只需单向推送 ② 复用现有 HTTP 网关（WebSocket 要动网关 / 负载均衡 / 鉴权）</text>
      <text x="106" y="358" font-size="11.5" fill="{TX2}">HTTP/1.1 同域约 6 条并发连接：1 个 SSE + 8 个接口请求 → 3 个排队——HTTP/2 多路复用解决</text>
      <text x="1344" y="376" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">EnergyOps：长任务进度选 SSE；RuleArena：要的是「能查最新状态」→ 轮询更简单——实时只在延迟有业务意义时才值得付</text>
    </g>
    <line x1="725" y1="382" x2="725" y2="415" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="422" width="1270" height="130" rx="8" fill="{PS}" stroke="{P_}" stroke-width="1.6"/>
      <text x="106" y="446" font-size="13" font-weight="800" fill="{PD}">③ 怎么扛住很多连接（N3）—— 先问时间花在哪：不是风格问题，是「在等还是在算」</text>
      <text x="106" y="468" font-size="11.5" fill="{TX2}">100ms 请求 CPU 只占 2ms → 98% 在等，等待期 CPU 空闲 → 单核理论可「同时」处理 50 个；IO 密集异步收益极大</text>
      <text x="106" y="488" font-size="11.5" fill="{TX2}">进程 / 线程 / 协程的差异全从「谁调度」推出：内核调度贵、用户态切换 ns 级；epoll 一次系统调用拿到全部就绪连接</text>
      <text x="106" y="508" font-size="11.5" fill="{OD}">协程省两笔：等待时间被利用起来 + 单位内存开销小两个数量级（线程 8MB 虚拟栈 vs 协程 KB 级；先撞 pid 上限不是内存）</text>
      <text x="106" y="528" font-size="11.5" fill="{PD}">致命坑：协程里跑阻塞代码 = 整个事件循环停摆——CPU 不高、日志无异常、单测都快、高峰整体变慢</text>
      <text x="1344" y="546" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">数驭穹图 / RuleArena：asyncio 服务 + 至少一次投递；CPU 密集（图像压缩 95% CPU）不进协程，进线程 / 进程池</text>
    </g>
    <line x1="725" y1="552" x2="725" y2="585" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="592" width="1270" height="72" rx="8" fill="{GS}" stroke="{G}" stroke-width="1.6"/>
      <text x="725" y="622" font-size="14.5" font-weight="800" fill="{GD}" text-anchor="middle">三步判据：请求失败先归因到层 · 推送先问客户端要什么 · 并发先问「在等还是在算」</text>
      <text x="725" y="646" font-size="11.5" fill="{TX2}" text-anchor="middle">连接复用（省握手）vs 连接被占住 / 超时设几层 · 单向够用选简单的 · 阻塞代码会拖垮整个事件循环</text>
    </g>
  </svg>'''

STORY = u'''<b>主干叙事（一段读完）</b>：网络的一条线是「<b>请求怎么进来 → 数据怎么出去 → 用什么姿势扛住很多连接</b>」。
    <b>进来</b>：请求穿过的是一条链路（DNS → TCP 三次握手 → HTTP → 网关 → 应用 → 上游），<b>每段失败的样子不一样</b> —— 502 是上游活着但答错、504 是网关等上游超时，「慢」和「挂」排查方向完全不同；超时分层（内短外长）让错误信息直接告诉你哪层放弃。
    <b>出去</b>：推送四选一的判据是<b>客户端要什么</b> —— 短轮询、长轮询、SSE（HTTP 长连接、单向）、WebSocket（协议升级全双工）；SSE 的生产难度在三个坑：代理缓冲、心跳保活、断线重连要 Last-Event-ID + 递增 sequence 才不漏事件。
    <b>扛连接</b>：先问时间花在哪 —— 98% 在等就是 IO 密集，异步收益极大；协程省两笔（等待被利用 + 单位开销小两个数量级），致命坑是<b>协程里跑阻塞代码 = 事件循环停摆</b>（CPU 不高、日志无异、高峰整体变慢）；CPU 密集进线程 / 进程池，GIL 挡不住多进程。'''

CAP = u'''<b>读法</b>：三个大框就是三条主线（怎么进来 / 怎么出去 / 怎么扛住）；橙字是判据与数字（要能现场算），紫字是生产坑（要能举出自己踩过的）；绿字是三个项目的落点。<b>底部一行是三条线的总判据</b>。'''

ROWS = [
    (u'N1 请求的路径', u'从 URL 到响应、哪层失败', u'链路 DNS → TCP（3 次握手 / 4 次挥手）→ HTTP → 网关 → 应用 → 上游；502 = 上游活着但答错、504 = 网关等上游超时；超时分层内短外长 → 从错误信息读出哪层放弃；HTTP 无状态 ≠ 短连接（Keep-Alive / 连接池复用）；HTTP/2 多路复用省连接数', u'1–7', u'EnergyOps：30 个 MCP Tool 的超时与重试；数驭穹图：网关=应用超时导致无法归因——外层略长让内层先超时；权限前置多一次串行调用，换掉整类泄露风险'),
    (u'N2 推送模型', u'轮询 / SSE / WS 怎么选', u'判据 = 客户端要什么：短轮询（反复短请求）、长轮询（挂住到有数据）、SSE（HTTP 长连接单向 text/event-stream）、WebSocket（协议升级全双工）；SSE 三坑：代理缓冲、心跳保活、断线重连要 Last-Event-ID + 递增 sequence；HTTP/1.1 同域 6 连接会被 SSE + 接口挤占 → HTTP/2', u'8–12', u'EnergyOps：长任务进度选 SSE（单向够用 + 复用现有网关，两个理由）；RuleArena：要的是「能查最新状态」→ 轮询更简单——「实时」只在延迟有业务意义时才值得付'),
    (u'N3 并发模型', u'进程 / 线程 / 协程', u'先问时间花在哪（98% 在等 → IO 密集异步收益大）；差异从「谁调度」推出：进程隔离贵、线程内核调度、协程用户态 ns 级切换；epoll 一次系统调用拿全就绪连接；协程省两笔：等待被利用 + 单位开销小两个数量级；致命坑 = 协程跑阻塞代码（事件循环停摆）；GIL：IO 密集无碍，CPU 密集进进程池；背压不处理 = 队列无限涨', u'13–18', u'数驭穹图 / RuleArena：asyncio 服务 + 至少一次投递；CPU 密集（图像压缩 95% CPU）不进协程，进线程 / 进程池'),
]

SVG04 = f'''<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="网络 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="{BD}">轮询的浪费账与连接的排队账</text>
      <text x="80" y="78" font-size="11.5" fill="{TX2}">进度页 1000 个在线用户：短轮询每 1 秒问一次 → 1000 QPS；而后端每 100 秒才产生 1 条新进度</text>
      <rect x="80" y="92" width="8" height="22" rx="2" fill="{G}"/>
      <text x="96" y="108" font-size="12" font-weight="800" fill="{GD}">真实需求：1 条 / 100 秒</text>
      <rect x="80" y="124" width="480" height="22" rx="4" fill="{O}" opacity="0.9"/>
      <text x="88" y="140" font-size="12" font-weight="800" fill="#fff">　轮询流量：10 万次请求换 1 条新进度（×100,000）</text>
      <text x="80" y="180" font-size="12" font-weight="800" fill="{TX}">HTTP/1.1 的连接排队：同域约 6 条并发连接</text>
      <text x="80" y="206" font-size="11.5" fill="{TX2}">1 个 SSE 已占 1 条，页面再发 8 个接口请求 → 3 个排队（队头阻塞）——HTTP/2 多路复用一条连接跑多个流</text>
      <text x="80" y="232" font-size="11.5" fill="{TX2}">TLS 握手约 2 RTT：跨机房 RTT 50ms → 每次新建连接多付 100ms——长连接 / 连接池复用的理由</text>
      <text x="80" y="264" font-size="11.5" font-weight="700" fill="{OD}">「要不要推送」先算无效流量：延迟没有业务意义时，轮询的简单性 > 推送的实时性</text>
      <text x="80" y="292" font-size="10.5" fill="{GREY}">RuleArena 的选择：Worker 跑长任务，客户端要的是「能查到最新状态」→ 状态查询接口，不上 SSE</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="{OD}">等待占比的账（异步值不值）</text>
      <text x="760" y="78" font-size="11.5" fill="{TX2}">一次请求 100ms：CPU 2ms + 等待 IO 98ms——等待期 CPU 空闲，单核理论「同时」处理 100÷2 = 50 个</text>
      <g font-size="11.5" fill="{TX2}">
        <text x="760" y="106">同步（一连接一线程）：10 万并发 → 10 万线程</text>
        <rect x="1060" y="96" width="300" height="12" rx="3" fill="{O}"/>
        <text x="760" y="132">异步（事件循环 + 协程）：10 万协程，KB 级</text>
        <rect x="1060" y="122" width="20" height="12" rx="3" fill="{G}"/>
      </g>
      <text x="760" y="166" font-size="11.5" fill="{TX2}">线程栈 8MB 是 Linux 默认（ulimit -s）且是虚拟预留：真实常驻 ~25KB/线程——先撞 pid 上限，不是内存</text>
      <text x="760" y="192" font-size="11.5" fill="{PD}">反例：图像压缩 400ms（CPU 占 380ms = 95%）→ 协程零收益，CPU 密集进线程 / 进程池</text>
      <text x="760" y="218" font-size="11.5" fill="{PD}">协程里一行阻塞调用（requests / time.sleep）= 事件循环停摆：高峰整体变慢、无异常、难定位</text>
      <text x="760" y="244" font-size="11.5" fill="{TX2}">GIL：IO 密集无所谓（等的时候会放锁）；CPU 密集多核只能多进程</text>
      <text x="760" y="270" font-size="11.5" font-weight="700" fill="{OD}">判据：先测等待占比，再决定要不要异步；阻塞代码用 run_in_executor 挪走</text>
      <text x="760" y="292" font-size="10.5" fill="{GREY}">数驭穹图 / RuleArena：asyncio 服务；背压不处理 = 生产快过消费、队列无限涨——限流 + 有界队列</text>
    </g>
  </svg>'''

NUMS = [
    ('b', u'等待占比', u'98 / 100', u'CPU 2ms、IO 98ms：单核理论「同时」处理 50 个——「要不要异步」先测这个数。'),
    ('o', u'轮询浪费', u'×100,000', u'1000 用户每秒轮询 = 1000 QPS，新进度 1 条/100s：10 万次请求换 1 条——轮询的无效流量账。'),
    ('b', u'同域连接数', u'≈ 6 条', u'HTTP/1.1 浏览器每域名 6 条：1 个 SSE + 8 个请求 → 3 个排队；HTTP/2 多路复用解决。'),
    ('o', u'TLS 握手', u'2 RTT ≈ 100ms', u'跨机房 RTT 50ms：每次新建连接多付 100ms——长连接 / 连接池复用的理由。'),
    ('b', u'线程栈', u'8MB（虚拟）', u'Linux 默认 ulimit -s = 8192KB，虚拟预留按需提交；真实常驻 ~25KB——先撞 pid 上限不是内存。'),
    ('b', u'三次握手', u'3 次 = 最少', u'可靠的最少次数（双方确认能收能发）；四次挥手 = 全双工两方向各自关闭，不能合并。'),
    ('o', u'502 vs 504', u'答错 vs 超时', u'502 = 上游活着但响应无效；504 = 网关等上游超时——「慢」和「挂」排查方向完全不同。'),
    ('b', u'CPU 密集反例', u'95% CPU', u'图像压缩 400ms 里 CPU 占 380ms——协程零收益，进线程 / 进程池，别塞事件循环。'),
    ('o', u'心跳保活', u'注释行', u'SSE 不发心跳会被空闲超时掐断：定期发注释行（: ping）保活，长任务跑一半连接就没了。'),
]

MIS = [
    (u'✗「502 = 上游不可用」', u'✓ 502 是上游活着但答得不对；完全没起来通常是 504 或连接拒绝——9.9 说反的那句。'),
    (u'✗「接口 504 就是服务端挂了，重启就行」', u'✓ 504 是网关等上游超时——服务端可能只是慢；「慢」和「挂」排查方向完全不同。'),
    (u'✗「HTTP 无状态，所以每次请求都新建 TCP 连接」', u'✓ 无状态 ≠ 短连接：协议不保存会话状态，但 Keep-Alive / 连接池复用传输层连接。'),
    (u'✗「SSE 是短连接 / 普通 HTTP 响应」', u'✓ SSE 是基于 HTTP 的长连接（服务端保持响应不结束）、单向——9.9 当场答错的那句。'),
    (u'✗「SSE 自带重连，所以不会丢消息」', u'✓ 能重连 ≠ 不漏事件：要 Last-Event-ID + 递增 sequence，服务端从那里补齐。'),
    (u'✗「SSE 就是普通 HTTP 响应，过网关不用配置」', u'✓ 代理默认缓冲（攒着不发）→ 显式关缓冲；不发心跳会被空闲超时掐断。'),
    (u'✗「线程默认栈 1MB，10 万线程要 100GB」', u'✓ Linux 默认 8MB 且是虚拟预留、按需提交，真实常驻 ~25KB——先撞 pid 上限不是内存。'),
    (u'✗「上 WebSocket 因为它更强」', u'✓ 判据是客户端要什么：单向够用选 SSE、要状态查询选轮询——双向全双工才值 WebSocket。'),
]

CRITS = [
    u'能画出完整链路并说出每段失败的样子；能说对 502 / 504 的归因（9.9 丢分点）；能给出超时分层的设法与理由；能分清「无状态」与「短连接」。',
    u'能一句话定义 SSE（HTTP 长连接、单向、text/event-stream）；能按「客户端要什么」在四者里选型；能给出生产三坑与对策；能用项目讲「选 SSE 的两个理由」和「轮询也行」的反例。',
    u'能从等待占比算单核并发上限；能从「谁调度」推出三种执行单元的全部差异；能解释 epoll 与协程省的两笔；能说清阻塞代码在协程里的故障形态与 GIL 边界。',
]

finish('网络',
       headline=u'3 张母题 · 18 道题 · 3 个项目 —— 一条线：请求怎么进来 → 数据怎么出去 → 用什么姿势扛住很多连接',
       sec01_title=u'主干：怎么进来 → 怎么出去 → 怎么扛住',
       sec01_sub=u'三条主线共享一个习惯：<b>先归因（哪一层）→ 再选型（客户端要什么 / 在等还是在算）→ 最后才谈手段</b>。502/504 的归因和 SSE 的定义是 9.9 丢过分的两处。',
       svg01=SVG01, story=STORY, cap=CAP, rows=ROWS,
       sec04_title=u'两笔账：轮询的浪费账，等待占比的账',
       sec04_sub=u'左边是「无效流量怎么算出来」，右边是「异步值不值怎么算出来」——都是数量级问题。',
       sec04_src=u'正本 母题-N2 · 母题-N3',
       svg04=SVG04, nums=NUMS, mis=MIS, crits=CRITS)
