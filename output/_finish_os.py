# -*- coding: utf-8 -*-
"""操作系统 一页通定稿（一次性工具）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _onepage_lib import (B, O, P_, G, BD, OD, PD, GD, BS, OS, PS, GS, TX, TX2, TX3, GREY, LINE,
                          SVG_DEFS, legend, finish)

SVG01 = f'''<svg viewBox="0 0 1450 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="操作系统 主干图">
    {SVG_DEFS}
    {legend([(B, 'mB', '蓝 · 三笔成本（切换 → 内存 → IO）'),
             (O, 'mO', '橙 · 判据与数字'),
             (P_, 'mP', '紫 · 失效与坑'),
             (G, 'mG', '绿 · 项目落点与总判据')])}

    <g filter="url(#sh)">
      <rect x="90" y="100" width="1270" height="112" rx="8" fill="{BS}" stroke="{B}" stroke-width="1.6"/>
      <text x="106" y="124" font-size="13" font-weight="800" fill="{BD}">① 切换：谁在跑（O1）—— Linux 里没有「线程」：线程和进程都是 task_struct，线程 = 共享更多的进程</text>
      <text x="106" y="146" font-size="11.5" fill="{TX2}">切换六步，进程 / 线程唯一差别 = 换页表那步（线程共享页表整步跳过）；一次切换 1.3–4μs（lmbench lat_ctx 量级）</text>
      <text x="106" y="166" font-size="11.5" fill="{OD}">线程栈 8MB 是 ulimit 虚拟预留（64 位 128TB 不是瓶颈）；真实常驻 ~25KB（task_struct + 内核栈）——先撞 pid_max / pids.max</text>
      <text x="106" y="186" font-size="11.5" fill="{PD}">共享地址空间 = 竞态根源；死锁四条件缺一不可——所有解法都是从「破坏一个条件」出发；线程过拐点总吞吐反而下降</text>
      <text x="1344" y="204" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">EnergyOps：受控并发 + 并发配额（拐点依据）· 数驭穹图：IO 等待换上换下都要付切换成本 · RuleArena：进程崩 = 内存清零</text>
    </g>
    <line x1="725" y1="212" x2="725" y2="245" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="252" width="1270" height="130" rx="8" fill="{OS}" stroke="{O}" stroke-width="1.6"/>
      <text x="106" y="276" font-size="13" font-weight="800" fill="{TX}">② 内存：它看到的内存是什么（O2）—— 虚拟内存把「申请」和「占用」变成两件事</text>
      <text x="106" y="298" font-size="11.5" fill="{TX2}">两个内存分开：虚拟（宽敞、会缺页）vs 物理（真实、有限）——overcommit 让 malloc 成功 ≠ 有内存，OOM 爆在运行中不在启动时</text>
      <text x="106" y="318" font-size="11.5" fill="{OD}">缺页两档：次缺页（分配物理页）vs 主缺页（要读盘）——差两个数量级；量级表从寄存器到网络横跨五个数量级</text>
      <text x="106" y="338" font-size="11.5" fill="{TX2}">8GB 程序跑在 4GB 机器：能不能跑不取决于「要多少」，取决于「实际碰了多少」——free 看 available，进程看 RSS 不是 VSZ</text>
      <text x="106" y="358" font-size="11.5" fill="{PD}">OOM 在所有回收手段用尽后触发：oom_badness 按 RSS 打分杀最高——容器里先分清整机 OOM 还是 cgroup OOM</text>
      <text x="1344" y="376" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">RuleArena：Redis 容器被 cgroup 限制（256–512MB）——cgroup 级 OOM 杀容器内进程，排查方向与整机 OOM 完全不同</text>
    </g>
    <line x1="725" y1="382" x2="725" y2="415" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="422" width="1270" height="130" rx="8" fill="{PS}" stroke="{P_}" stroke-width="1.6"/>
      <text x="106" y="446" font-size="13" font-weight="800" fill="{PD}">③ IO：慢在哪、内核能省什么（O3）—— 一次 IO 分两段：「等就绪」+「拷数据」，所有 IO 模型都在说改造了哪一段</text>
      <text x="106" y="468" font-size="11.5" fill="{TX2}">epoll_wait 通知「可读」后，read 仍阻塞在拷贝段——按 POSIX 判据多路复用也是同步 IO（异步要看拷贝段是否内核代劳）</text>
      <text x="106" y="488" font-size="11.5" fill="{OD}">select O(n)：每次拷全量 fd 集 + 全遍历 → poll 只解了数量上限 → epoll：注册一次（interest list）+ 只返回就绪（ready list）= O(k)</text>
      <text x="106" y="508" font-size="11.5" fill="{TX2}">零拷贝：传统读+写拷 4 次（磁盘→页缓存→用户缓冲→socket 缓冲→网卡）；sendfile 一个系统调用省掉 2 次「白干」的用户态搬运</text>
      <text x="106" y="528" font-size="11.5" fill="{TX2}">一次系统调用 ~105ns：每秒 100 万次小 IO ≈ 0.1 秒纯系统调用开销——io_uring 的动机是批量提交</text>
      <text x="1344" y="546" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">EnergyOps / 数驭穹图：IO 等待为主 → 事件循环 + 异步；Kafka / Nginx 的零拷贝 = 数据根本没进用户态</text>
    </g>
    <line x1="725" y1="552" x2="725" y2="585" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="592" width="1270" height="72" rx="8" fill="{GS}" stroke="{G}" stroke-width="1.6"/>
      <text x="725" y="622" font-size="14.5" font-weight="800" fill="{GD}" text-anchor="middle">这个模块反向解释整个后端基本盘——所有模块的追问最终都落到这里</text>
      <text x="725" y="646" font-size="11.5" fill="{TX2}" text-anchor="middle">Redis 单线程快（IO 密集 + 事件循环）· Kafka 用零拷贝（省 2 次拷贝）· MySQL 连接不能无限开（每连接一线程）· 容器 Java 被 OOM（cgroup + oom_score）—— 9.9「计算机基础」12.4 分的根就在这</text>
    </g>
  </svg>'''

STORY = u'''<b>主干叙事（一段读完）</b>：操作系统的一条线是高并发服务端的三笔成本：「<b>切换（谁在跑）→ 内存（它看到什么）→ IO（等的时候干什么）</b>」。
    <b>切换</b>：Linux 里线程和进程都是 task_struct，<b>线程 = 共享更多的进程</b> —— 切换六步里唯一差别是换页表那步；一次切换 1.3–4μs，<b>线程过拐点总吞吐反而下降</b>（EnergyOps「受控并发」的依据）；线程栈 8MB 是虚拟预留，真实常驻 ~25KB，先撞 pid 上限。
    <b>内存</b>：虚拟内存把「申请」和「占用」变成两件事 —— malloc 成功 ≠ 有内存（overcommit），8GB 程序跑在 4GB 机器取决于<b>实际碰了多少</b>；OOM 在所有回收手段用尽后按 RSS 打分杀最高，<b>容器里先分清整机 OOM 还是 cgroup OOM</b>（排查方向完全不同）。
    <b>IO</b>：一次 IO 分「等就绪」+「拷数据」两段 —— epoll 的强是<b>注册一次 + 只返回就绪（O(k)）</b>，但 read 仍阻塞在拷贝段，多路复用还是同步 IO；零拷贝省的是「内核 → 用户 → 内核」两次白干搬运（sendfile）。
    这个模块<b>反向解释整个后端基本盘</b>：Redis 单线程、Kafka 零拷贝、MySQL 连接上限、容器 OOM，追问到最后都落到这里（9.9 计算机基础 12.4 分的根）。'''

CAP = u'''<b>读法</b>：三个大框就是三笔成本；橙字是判据与数字（要能现场算），紫字是失效与坑（毒教材高发区都在这）；绿字是三个项目的落点。<b>底部横幅是本模块存在的理由</b>：反向解释整个后端基本盘。'''

ROWS = [
    (u'O1 CPU 与切换', u'进程线程差在哪、为什么线程不是越多越好', u'Linux 无「线程」概念——都是 task_struct，线程 = 共享更多的进程；切换六步、唯一差别 = 换页表；一次切换 1.3–4μs；线程栈 8MB 是虚拟预留（真实常驻 ~25KB，先撞 pid_max / pids.max）；共享地址空间 = 竞态根源，死锁四条件缺一不可；线程过拐点总吞吐下降', u'1–11', u'EnergyOps：受控并发 + 并发配额（拐点的量化判据）；数驭穹图：IO 等待换上换下都付切换成本——IO 密集别用线程池硬扛；RuleArena：进程崩 = 内存清零，状态必须落库'),
    (u'O2 内存与 OOM', u'8GB 怎么跑在 4GB 上、OOM 杀谁', u'两个内存分开：虚拟（申请）vs 物理（占用）——overcommit 让 malloc 成功 ≠ 有内存；缺页两档（次 / 主）差两个数量级；能不能跑取决于「实际碰了多少」，爆在运行中；OOM 在回收手段用尽后按 oom_badness（RSS 打分）杀最高；VSZ 无参考价值看 RSS / anon-rss；free 看 available', u'12–21', u'RuleArena：Redis 容器被 cgroup 限制——cgroup 级 OOM 杀容器内进程，与整机 OOM 的排查方向完全不同'),
    (u'O3 IO 模型与零拷贝', u'IO 为什么慢、内核省了什么', u'一次 IO 两段（等就绪 + 拷数据），所有模型都在说改造哪段——epoll_wait 后 read 仍阻塞拷贝段，多路复用是同步 IO；select O(n)（全量拷 fd 集 + 全遍历）→ epoll 注册一次 + 只返回就绪（O(k)）；零拷贝省「内核→用户→内核」两次白干搬运（sendfile）；一次系统调用 ~105ns（io_uring 批量提交）', u'22–30', u'EnergyOps / 数驭穹图：IO 等待为主 → 事件循环 + 异步（N3 的底层依据）；Kafka / Nginx 零拷贝 = 数据没进用户态'),
]

SVG04 = f'''<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="操作系统 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="{BD}">「线程开多了反而慢」的账</text>
      <text x="80" y="78" font-size="11.5" fill="{TX2}">vmstat 显示每秒 50 万次上下文切换，绝大多数是非自愿（时间片被抢）：</text>
      <rect x="80" y="92" width="470" height="22" rx="4" fill="{O}" opacity="0.9"/>
      <text x="88" y="108" font-size="12" font-weight="800" fill="#fff">　500,000 次/s × ~2μs ≈ 每秒 1 秒 CPU —— 全花在切换上，业务没跑</text>
      <text x="80" y="150" font-size="12" font-weight="800" fill="{TX}">内存的算法错在哪：10 万线程 × 8MB = 800GB？</text>
      <text x="80" y="176" font-size="11.5" fill="{TX2}">8MB 是 ulimit -s 的虚拟预留，64 位有 128TB——不是瓶颈；真实常驻 = 10 万 × ~25KB ≈ 2.5GB（内核侧，不计 RSS）</text>
      <text x="80" y="202" font-size="11.5" fill="{PD}">先撞的是 pid_max / threads-max / 容器的 pids.max——不是内存，所以报错形态是「创建失败」不是「变慢」</text>
      <text x="80" y="228" font-size="11.5" fill="{TX2}">过了拐点总吞吐下降：切换 + 缓存失效吃掉有效算力——EnergyOps「受控并发」的量化依据</text>
      <text x="80" y="260" font-size="11.5" font-weight="700" fill="{OD}">判据：并发单元数按「CPU 核数 × 等待比」配，不是按任务数开</text>
      <text x="80" y="292" font-size="10.5" fill="{GREY}">RuleArena 对应：进程崩 = 内存清零——所以状态落库、Checkpoint 只是恢复线索不是事实</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="{OD}">epoll 的账与零拷贝的账</text>
      <text x="760" y="78" font-size="11.5" fill="{TX2}">10000 个连接、每秒 1000 次事件、每次平均 10 个就绪——两种就绪通知的工作量：</text>
      <g font-size="11.5" fill="{TX2}">
        <text x="760" y="106">select / poll：1000 × 10000 = 1000 万次检查（O(n)）</text>
        <rect x="1105" y="96" width="255" height="12" rx="3" fill="{O}"/>
        <text x="760" y="132">epoll：1000 × 10 = 1 万次（O(k)，只与就绪数有关）</text>
        <rect x="1105" y="122" width="18" height="12" rx="3" fill="{G}"/>
      </g>
      <text x="760" y="166" font-size="11.5" fill="{TX2}">省的是两件事：每次拷全量 fd 集 → 注册一次；每次遍历全部 fd → 只返回就绪。连接少时差别不大</text>
      <text x="760" y="192" font-size="11.5" fill="{TX2}">零拷贝：1GB 文件传统读+写拷 4 次，sendfile 省 2 次用户态搬运——1000 并发下载每次省 2GB 的白干搬运</text>
      <text x="760" y="218" font-size="11.5" fill="{PD}">注意：epoll_wait 仍要把就绪事件拷回用户数组——省的是「全量」，不是「拷贝本身」（毒教材高发区）</text>
      <text x="760" y="244" font-size="11.5" fill="{TX2}">一次系统调用 ~105ns：每秒 100 万次小 IO ≈ 10% CPU 纯开销——io_uring 批量提交的动机</text>
      <text x="760" y="270" font-size="11.5" font-weight="700" fill="{OD}">判据：IO 密集（等待为主）→ 事件循环；连接多且就绪稀疏 → epoll 的优势才显现</text>
      <text x="760" y="292" font-size="10.5" fill="{GREY}">数驭穹图 / EnergyOps：IO 等待为主 → 异步 + 事件循环（N3 的操作系统层依据）</text>
    </g>
  </svg>'''

NUMS = [
    ('b', u'一次上下文切换', u'1.3–4 μs', u'lmbench lat_ctx 与公开基准的量级；50 万次/s ≈ 每秒 1 秒 CPU——切换风暴下业务没跑。'),
    ('o', u'线程真实常驻', u'~25 KB/线程', u'task_struct + 内核栈，不计入 RSS；10 万线程 ≈ 2.5GB——先撞 pid_max / pids.max，不是内存。'),
    ('b', u'线程栈 8MB', u'虚拟预留', u'ulimit -s 默认 8192KB；64 位 128TB 虚拟空间根本不缺——毒教材「10 万线程 800GB」错在这。'),
    ('b', u'缺页两档', u'差两个数量级', u'次缺页（分配物理页）vs 主缺页（读盘）；全量级表从寄存器到网络横跨五个数量级。'),
    ('o', u'malloc 成功 ≠ 有内存', u'overcommit', u'8GB 申请在 4GB 机器返回成功：物理页首次访问才分配——OOM 爆在运行中，不在启动时。'),
    ('b', u'select vs epoll', u'1000 万 vs 1 万', u'10000 连接、10 就绪：O(n) 全遍历 vs O(k) 只看就绪——差 1000 倍，连接少时差别不大。'),
    ('o', u'零拷贝', u'4 次 → 2 次', u'省掉「内核→用户→内核」两次白干搬运；1GB 文件 × 1000 并发 = 每次省 2GB 搬运。'),
    ('b', u'一次系统调用', u'~105 ns', u'每秒 100 万次小 IO ≈ 0.1 秒纯系统调用开销——io_uring 批量提交的动机。'),
    ('o', u'OOM 打分', u'按 RSS', u'oom_badness 杀分最高者；容器里先分清整机 OOM 还是 cgroup OOM——排查方向完全不同。'),
]

MIS = [
    (u'✗「10 万线程要 800GB 内存（8MB×10万）」', u'✓ 8MB 是虚拟预留；真实 ~25KB/线程 ≈ 2.5GB——先撞 pid_max / threads-max，报错形态是创建失败。'),
    (u'✗「进程切换贵是因为寄存器多」', u'✓ 寄存器是小头：贵在换页表（进程间）与缓存失效；线程共享页表，正好跳过那一步。'),
    (u'✗「malloc 成功就有内存了」', u'✓ 只拿到虚拟地址空间，物理页首次访问（缺页）才分配——OOM 发生在运行中，不在申请时。'),
    (u'✗「top 里 VSZ 很大，肯定内存泄漏了」', u'✓ VSZ 含 mmap 文件与地址预留，基本没参考价值；看 RSS，排查 OOM 更看 anon-rss。'),
    (u'✗「free 显示内存用满 90%，要爆了」', u'✓ 其中很多是可随时回收的页缓存；看 available / MemAvailable，不是 used。'),
    (u'✗「被 OOM 杀了就是内存不够，加内存」', u'✓ 先分清整机 OOM 还是 cgroup OOM（容器内超限）——两者排查方向完全不同。'),
    (u'✗「epoll 用 mmap 共享内存，实现零拷贝」', u'✓ man-page：interest / ready 列表都在内核态，epoll_wait 仍拷就绪事件——省的是全量拷贝与全遍历。'),
    (u'✗「epoll 通知后不阻塞，所以是异步 IO」', u'✓ read 仍阻塞在「内核→用户」拷贝段——按 POSIX 判据多路复用是同步 IO；异步要看拷贝段是否内核代劳。'),
]

CRITS = [
    u'能说出「线程 = 共享更多的进程」并推出全部差异；能背切换六步并指出进程/线程唯一差别；能算切换风暴的 CPU 占比；能纠正线程栈的虚拟预留误区；能用死锁四条件给解法分类。',
    u'能分开「申请」与「占用」并解释 overcommit；能区分次 / 主缺页的量级；能解释 OOM 的触发时机与打分公式；能用 RSS / available 纠正 VSZ / used 的误读。',
    u'能用「两段」框架归类五种 IO 模型并说清多路复用为何是同步 IO；能算 select 与 epoll 的检查次数差；能说出零拷贝省的是哪两次拷贝；能解释一次系统调用的开销与 io_uring 的动机。',
]

finish('操作系统',
       headline=u'3 张母题 · 30 道题 · 3 个项目 —— 一条线：三笔成本（切换 → 内存 → IO），反向解释整个后端基本盘',
       sec01_title=u'主干：切换 → 内存 → IO（高并发服务端的三笔成本）',
       sec01_sub=u'三个大框各是一笔成本，<b>每笔都要能现场算出数量级</b>；这个模块是唯一能「反向解释整个后端基本盘」的模块——9.9 计算机基础 12.4 分的根。',
       svg01=SVG01, story=STORY, cap=CAP, rows=ROWS,
       sec04_title=u'两笔账：线程开多了反而慢的账，epoll 与零拷贝的账',
       sec04_sub=u'左边是「并发单元不是越多越好」的量化依据，右边是「IO 就绪通知与拷贝省在哪」——都是数量级问题。',
       sec04_src=u'正本 母题-O1 · 母题-O3',
       svg04=SVG04, nums=NUMS, mis=MIS, crits=CRITS)
