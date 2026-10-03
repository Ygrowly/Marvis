# -*- coding: utf-8 -*-
"""Linux与部署 一页通定稿（一次性工具）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _onepage_lib import (B, O, P_, G, BD, OD, PD, GD, BS, OS, PS, GS, TX, TX2, TX3, GREY, LINE,
                          SVG_DEFS, legend, finish)

SVG01 = f'''<svg viewBox="0 0 1450 700" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Linux与部署 主干图">
    {SVG_DEFS}
    {legend([(B, 'mB', '蓝 · 运维日常顺序（盒子 → 上线 → 排查）'),
             (O, 'mO', '橙 · 判据与数字'),
             (P_, 'mP', '紫 · 失效与误判'),
             (G, 'mG', '绿 · 项目落点与共享前提')])}

    <g filter="url(#sh)">
      <rect x="90" y="100" width="1270" height="112" rx="8" fill="{BS}" stroke="{B}" stroke-width="1.6"/>
      <text x="106" y="124" font-size="13" font-weight="800" fill="{BD}">① 盒子（X1）—— 容器是被「重新布置过视角」的普通进程：namespace 改视野、cgroup 设额度；共享内核，隔离强度弱于虚拟机</text>
      <text x="106" y="146" font-size="11.5" fill="{OD}">关键推论：内存没有 namespace——free 看到的是宿主机视图；容器上限在 memory.max，超了 = cgroup OOM，与宿主机剩多少无关</text>
      <text x="106" y="166" font-size="11.5" fill="{OD}">CPU 配额是「每周期预算」：0.5 核 = 每 100ms 周期允许 50ms CPU 时间——用完后即使核空闲也用不了 → CPU 不高但延迟抖动</text>
      <text x="106" y="186" font-size="11.5" fill="{PD}">证据在 cpu.stat：nr_throttled / throttled_usec——「利用率不高 ≠ 有余量」，先查限流再谈加核</text>
      <text x="1344" y="204" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">RuleArena：Redis 容器 256–512MB = cgroup 限制 · 老 JVM 不感知容器按宿主机 1/4 设堆 → 直接撞 memory.max 被 cgroup OOM</text>
    </g>
    <line x1="725" y1="212" x2="725" y2="245" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="252" width="1270" height="130" rx="8" fill="{OS}" stroke="{O}" stroke-width="1.6"/>
      <text x="106" y="276" font-size="13" font-weight="800" fill="{TX}">② 上线（X2）—— 起与停难点完全不同：起 = 依赖就绪，停 = 优雅退出；上线的成败往往取决于「怎么退出」</text>
      <text x="106" y="298" font-size="11.5" fill="{TX2}">SIGTERM ≠ SIGKILL：宽限期一到就是 KILL——所以长任务必须设计成「可中断 + 可恢复」，不指望一定能优雅退完</text>
      <text x="106" y="318" font-size="11.5" fill="{PD}">优雅退出四步顺序不能乱：摘流量（最易漏）→ 等在途排空 → 关依赖 → 退出；发版后千分之几错误率抬升 = 没做优雅退出，是 bug 不是发版成本</text>
      <text x="106" y="338" font-size="11.5" fill="{OD}">时间窗要能算：LB 摘流 1s + 在途 P99.9 800ms + 清理 200ms = 2s &lt; 宽限期 10s ✓——在途有 30s 长任务就是设计问题</text>
      <text x="106" y="358" font-size="11.5" fill="{TX2}">探针设计：存活探针别查 DB——DB 抖 3s → 探针失败 → 重启好容器 → 连锁重启；配置三分支：环境变量 / 文件 / 配置中心</text>
      <text x="1344" y="376" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">EnergyOps：重启后扫描七天缺口、低优先级回补——重启 ≠ 状态清零，能恢复的只有落库的部分 · RuleArena：先读 Receipt 再校准 Checkpoint</text>
    </g>
    <line x1="725" y1="382" x2="725" y2="415" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="422" width="1270" height="130" rx="8" fill="{PS}" stroke="{P_}" stroke-width="1.6"/>
      <text x="106" y="446" font-size="13" font-weight="800" fill="{PD}">③ 排查（X3）—— 排查的能力体现在「顺序」，不在记得多少命令：两个是非问题先把可能性砍掉大半</text>
      <text x="106" y="468" font-size="11.5" fill="{TX2}">全站还是单机？CPU 密集还是 IO 等待？——四个组合各指明下一步；同一指标看趋势、两个指标看关系</text>
      <text x="106" y="488" font-size="11.5" fill="{OD}">load 高 + CPU 低 = 大量任务卡在不可中断等待（多为磁盘 IO）的签名；PSI 比 load 准——直接给「资源压力」百分比</text>
      <text x="106" y="508" font-size="11.5" fill="{TX2}">内存看 available（used 里很大部分是可回收页缓存）；磁盘 df 100% 但 du 60% = 已删未释放句柄；TIME_WAIT 多 ≠ 故障</text>
      <text x="106" y="528" font-size="11.5" fill="{PD}">容器内第一嫌疑是限流（throttled）——CPU 不高但延迟抖，查 cpu.stat，不是加核；数驭穹图判据：限额配额优先于加机器</text>
      <text x="1344" y="546" font-size="10.5" font-weight="700" fill="{GD}" text-anchor="end">数驭穹图：超时 / 扫描量 / 行数 / 并发 / 取消——容器级限制在业务层的对应物，防「一个请求拖垮整个服务」 · 权限不确定 fail closed</text>
    </g>
    <line x1="725" y1="552" x2="725" y2="585" stroke="{B}" stroke-width="2.4" marker-end="url(#mB)"/>

    <g filter="url(#sh)">
      <rect x="90" y="592" width="1270" height="72" rx="8" fill="{GS}" stroke="{G}" stroke-width="1.6"/>
      <text x="725" y="622" font-size="14.5" font-weight="800" fill="{GD}" text-anchor="middle">共享前提：现代服务都是「被管起来的」——被容器、编排系统、信号和探针管理着</text>
      <text x="725" y="646" font-size="11.5" fill="{TX2}" text-anchor="middle">不知道这层管理，很多现象无法解释：进程「莫名」被杀（cgroup OOM）· SIGTERM 没处理完就没了（宽限期）· CPU 不高但延迟抖（限流）</text>
    </g>
  </svg>'''

STORY = u'''<b>主干叙事（一段读完）</b>：Linux与部署的一条线是运维的日常顺序：「<b>它被关在什么盒子里 → 它怎么上线怎么退出 → 它坏了怎么查</b>」，共享前提：<b>现代服务都是被管起来的</b> —— 被容器、编排、信号和探针管理。
    <b>盒子</b>：容器是被重新布置过视角的普通进程（namespace 改视野、cgroup 设额度，共享内核弱于 VM）；<b>内存没有 namespace</b> —— free 看到的是宿主机，上限在 memory.max，超了就是 cgroup OOM；CPU 配额是每周期预算（0.5 核 = 每 100ms 用 50ms），<b>用完后核空闲也用不了</b> —— 「CPU 不高但延迟抖」先查 nr_throttled。
    <b>上线</b>：起难在依赖就绪（探针别查 DB），停难在优雅退出 —— 四步顺序不能乱（<b>摘流量最易漏</b>）；SIGTERM 宽限期到就 SIGKILL，长任务必须可中断 + 可恢复；时间窗要能算（摘流 + 在途 P99.9 + 清理 &lt; 宽限期）。
    <b>排查</b>：用两个是非问题缩范围（全站 / 单机 × CPU / IO）；<b>load 高 + CPU 低 = 在等 IO 的签名</b>；内存看 available、磁盘 df / du 对不上是已删未释放句柄、容器内先查限流再谈加核——「限额配额优先于加机器」。'''

CAP = u'''<b>读法</b>：三个大框就是运维日常顺序；橙字是判据与数字（0.5 核 / 时间窗都要能算），紫字是失效与误判（毒教材高发区）；绿字是三个项目的落点。<b>底部横幅解释了三个「灵异现象」</b>：莫名被杀、SIGTERM 没处理完、CPU 不高但抖。'''

ROWS = [
    (u'X1 容器是什么', u'namespace 与 cgroup 各管什么', u'容器 = 被重新布置过视角的普通进程：namespace（PID/NET/MNT/UTS/IPC/USER）改视野、cgroup 设额度——共享内核，隔离强度弱于 VM；内存没有 namespace：free 看到宿主机视图，上限在 memory.max，超了 = cgroup OOM；CPU 配额是每周期预算（0.5 核 = 每 100ms 用 50ms），用完即限流——看 nr_throttled / throttled_usec', u'1–6', u'RuleArena：Redis 容器 256–512MB 是 cgroup 限制（cgroup OOM ≠ 宿主机 OOM，排查方向完全不同）；老 JVM 按宿主机 1/4 设堆 → 直接撞 memory.max'),
    (u'X2 上线与退出', u'从镜像到能服务要过哪几关', u'起 = 依赖就绪（探针别查 DB：DB 抖 3s → 探针失败 → 重启好容器 → 连锁重启）；停 = 优雅退出四步：摘流量（最易漏）→ 等在途排空 → 关依赖 → 退出；SIGTERM 宽限期到就 SIGKILL——长任务必须可中断 + 可恢复；时间窗要能算（摘流 + 在途 P99.9 + 清理 &lt; 宽限期）；错误率抬升 = 没做优雅退出，是 bug', u'7–12', u'EnergyOps：重启后扫描七天缺口、低优先级回补——重启 ≠ 状态清零，自检必须存在；RuleArena：Worker 起来先读 AttackRun + 最后 Receipt 校准 Checkpoint'),
    (u'X3 排查定位', u'变慢了先看哪里', u'两个是非问题缩范围（全站 / 单机 × CPU 密集 / IO 等待）——四个组合各有下一步；load 高 + CPU 低 = 不可中断等待（磁盘 IO）的签名；PSI 比 load 准（直接给资源压力）；内存看 available 不是 used；df 100% 但 du 60% = 已删未释放句柄；TIME_WAIT 多 ≠ 故障；容器内第一嫌疑是限流（throttled）', u'13–22', u'数驭穹图：限额与配额优先于加机器——加机器不解决单个请求无上界；权限不确定 fail closed；EnergyOps：重启后自检必须有（不能假设没报错就跑过）'),
]

SVG04 = f'''<svg viewBox="0 0 1450 340" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Linux与部署 两笔账">
    <g>
      <rect x="60" y="24" width="640" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="80" y="52" font-size="13" font-weight="800" fill="{BD}">容器里的两笔错账（0.5 核限流 + JVM 撞墙）</text>
      <text x="80" y="78" font-size="11.5" fill="{TX2}">cpu.max = "50000 100000"（0.5 核）：每 100ms 周期预算 50ms CPU 时间；单请求 50ms、8 req/s</text>
      <text x="80" y="104" font-size="11.5" fill="{TX2}">平均需求 400ms/s = 0.4 核 &lt; 0.5 核「够」——但突发 2 个请求落进同一周期 = 100ms &gt; 50ms → 被限流 50ms</text>
      <rect x="80" y="118" width="300" height="20" rx="4" fill="{O}" opacity="0.9"/>
      <text x="88" y="132" font-size="12" font-weight="800" fill="#fff">　表现：CPU 利用率只 40%，延迟抖 50ms+</text>
      <text x="80" y="170" font-size="12" font-weight="800" fill="{TX}">内存：memory.max = 512MB，宿主机 16GB，老 JVM 不感知容器</text>
      <text x="80" y="196" font-size="11.5" fill="{TX2}">JVM 按「宿主机物理内存的 1/4」设最大堆 = 4GB → 进程 RSS 涨到 512MB 就被 cgroup OOM 杀</text>
      <rect x="80" y="210" width="440" height="20" rx="4" fill="{O}" opacity="0.9"/>
      <text x="88" y="224" font-size="12" font-weight="800" fill="#fff">　free 显示还有 15GB——救不了它（内存没有 namespace）</text>
      <text x="80" y="256" font-size="11.5" font-weight="700" fill="{OD}">判据：平均利用率够 ≠ 不被限流（要看突发周期）；容器内 JVM 必须显式设堆 / 用容器感知版本</text>
      <text x="80" y="292" font-size="10.5" fill="{GREY}">证据链：cpu.stat 的 nr_throttled / throttled_usec · memory.events 的 oom_kill——数字都有出处</text>
    </g>
    <g>
      <rect x="740" y="24" width="650" height="292" rx="10" fill="#fff" stroke="{LINE}"/>
      <text x="760" y="52" font-size="13" font-weight="800" fill="{OD}">优雅退出的时间窗（能算才敢设）</text>
      <text x="760" y="78" font-size="11.5" fill="{TX2}">在途 P99.9 = 800ms · LB 摘流生效 1s · 清理 200ms · 平台宽限期 10s：</text>
      <g font-size="11.5" fill="{TX2}">
        <text x="760" y="106">需要 = 1s + 0.8s + 0.2s = 2s &lt; 10s ✓ 退得完</text>
        <rect x="1080" y="96" width="80" height="12" rx="3" fill="{G}"/>
        <text x="760" y="132">在途有 30s 长任务：30s &gt; 10s → 宽限期到 SIGKILL，在途作废</text>
        <rect x="1080" y="122" width="240" height="12" rx="3" fill="{O}"/>
      </g>
      <text x="760" y="166" font-size="11.5" fill="{TX2}">所以长任务不进退出路径：设计成「可中断 + 可恢复」——Checkpoint 只是恢复线索，不是完成证明</text>
      <text x="760" y="192" font-size="11.5" fill="{PD}">探针反例：/health 里查 DB，DB 抖 3s → 存活探针失败 → 重启本来健康的容器 → 全体连锁重启</text>
      <text x="760" y="218" font-size="11.5" fill="{TX2}">排查签名：load 48 / 8 核 + CPU 45% + 内存磁盘充足 → 在等 IO（不可中断等待）——不是加核</text>
      <text x="760" y="244" font-size="11.5" fill="{TX2}">磁盘签名：df 100% 但 du 60% → 已删除但句柄未释放——lsof 找进程，重启或截断</text>
      <text x="760" y="270" font-size="11.5" font-weight="700" fill="{OD}">顺序判据：先缩范围（全站/单机 × CPU/IO）再动手——「把命令全敲一遍看哪个大」既慢又漏</text>
      <text x="760" y="292" font-size="10.5" fill="{GREY}">数驭穹图：限额与配额优先于加机器——加机器不解决「单个请求无上界」</text>
    </g>
  </svg>'''

NUMS = [
    ('b', u'0.5 核的真义', u'100ms / 50ms', u'每周期预算 50ms CPU 时间，不是半个物理核——突发周期超预算即限流，核空闲也用不了。'),
    ('o', u'限流证据', u'nr_throttled', u'cpu.stat 的限流次数与时长——「CPU 不高但延迟抖」的第一嫌疑，先查它再谈加核。'),
    ('b', u'JVM 容器错配', u'4GB 堆 vs 512MB', u'老 JVM 按宿主机 1/4 设堆：RSS 涨到 memory.max 即被 cgroup OOM——free 还有 15GB 救不了。'),
    ('b', u'退出时间窗', u'2s < 10s', u'摘流 1s + 在途 P99.9 800ms + 清理 200ms：能算才敢设；在途 30s 长任务 = 设计问题。'),
    ('o', u'错误率抬升', u'千分之几 = bug', u'发版后错误率小幅抬升通常就是没摘流量 / 没优雅退出——是 bug，不是发版成本。'),
    ('b', u'load 签名', u'load 48 / 8 核 + CPU 45%', u'load 高 + CPU 低 = 大量任务卡在不可中断等待（多为磁盘 IO）——不是 CPU 不够。'),
    ('o', u'内存看哪个', u'available', u'used 里很大部分是可回收页缓存——「用满」不是问题，「回收不动」才是。'),
    ('b', u'df vs du 对不上', u'100% vs 60%', u'已删除但句柄未释放的文件占着空间——lsof 找到进程，重启或截断才释放。'),
    ('o', u'探针反例', u'DB 抖 3s', u'/health 查库 + 存活探针 3s 超时 → 重启本来健康的容器 → 全体连锁重启——探针只测进程自身。'),
]

MIS = [
    (u'✗「容器是轻量虚拟机」', u'✓ 共享内核：namespace 改视野、cgroup 设额度——隔离的是视图与资源，强度弱于 VM。'),
    (u'✗「容器里 free 还有内存，所以不会 OOM」', u'✓ 内存没有 namespace：上限在 memory.max，超了就是 cgroup OOM，与宿主机剩多少无关。'),
    (u'✗「CPU 利用率不高，说明还有余量」', u'✓ 容器里配额是每周期预算，用完后核空闲也用不了——看 cpu.stat 的 nr_throttled。'),
    (u'✗「收到停止信号 exit(0) 就行」', u'✓ 优雅退出四步：摘流量（最易漏）→ 等在途排空 → 关依赖 → 退出；顺序不能乱。'),
    (u'✗「进程活着就是服务可用」', u'✓ 存活探针查 DB 时 DB 抖动会重启好容器——探针只测进程自身，依赖就绪用就绪探针。'),
    (u'✗「load 高就是 CPU 忙」', u'✓ load 高 + CPU 低 = 大量任务卡在不可中断等待（多为磁盘 IO）——IO 等待的签名。'),
    (u'✗「free 显示用满就是要爆了」', u'✓ 页缓存可随时回收，看 available / MemAvailable——「回收不动」才是问题。'),
    (u'✗「磁盘告警就是空间要满了」', u'✓ 也可能是 inode 耗尽或已删未释放句柄（df 100% 但 du 60%）——lsof 找进程。'),
]

CRITS = [
    u'能用「namespace 改视野、cgroup 设额度」一句话讲容器；能解释为什么内存没有 namespace；能算 0.5 核的周期预算并解释限流；能用 nr_throttled 判断「CPU 不高但抖」。',
    u'能按顺序背优雅退出四步并说出最易漏的一步；能算时间窗并判断宽限期够不够；能设计不查 DB 的存活探针；能把长任务讲成「可中断 + 可恢复」而不是「一定能退完」。',
    u'能用两个是非问题缩排查范围；能解读 load 高 CPU 低、df / du 对不上、TIME_WAIT 多三个签名；能给出容器限流的第一嫌疑与证据；能把「限额优先于加机器」讲成判据。',
]

finish('Linux与部署',
       headline=u'3 张母题 · 22 道题 · 3 个项目 —— 一条线：被关在什么盒子里 → 怎么上线怎么退出 → 坏了怎么查（前提：服务都是被管起来的）',
       sec01_title=u'主干：盒子 → 上线 → 排查（运维的日常顺序）',
       sec01_sub=u'先理解边界（X1）、再理解生命周期（X2）、最后才是排障（X3）；<b>不知道「被管起来」这层，三个灵异现象都无法解释</b>。',
       svg01=SVG01, story=STORY, cap=CAP, rows=ROWS,
       sec04_title=u'两笔账：容器里的两笔错账，优雅退出的时间窗',
       sec04_sub=u'左边是「平均够 ≠ 不被限流」与「free 救不了 cgroup OOM」，右边是「时间窗要能算才敢设」——都是数量级问题。',
       sec04_src=u'正本 母题-X1 · 母题-X2',
       svg04=SVG04, nums=NUMS, mis=MIS, crits=CRITS)
