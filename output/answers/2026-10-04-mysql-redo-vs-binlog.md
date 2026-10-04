---
template: sheet
theme: blueprint
title: MySQL 为什么有了 binlog 还要 redo log？
subtitle: 两种日志各管一件事，缺一个就出事故
source: Marvis · MySQL 主线 · 面试高频
cols: 3
---
一句话结论：**redo log 保证崩溃后数据不丢（crash-safe），binlog 保证主从复制与备份归档。两者职责不同，不能互相替代。**

## A 分工对照 {meta="先看职责"}
| 维度 | redo log | binlog |
|---|---|---|
| 所属层 | InnoDB 引擎层 | Server 层 |
| 日志性质 | 物理日志：某页某处改了什么 | 逻辑日志：语句或行怎么变 |
| 写入方式 | 固定大小，循环写 | 追加写，不覆盖 |
| 核心用途 | 崩溃恢复（crash-safe） | 主从复制、备份恢复 |

## B 只留 binlog 会怎样 {meta="反事实一"}
| 场景 | 后果 | 判定 |
|---|---|---|
| 崩溃恢复 | 逻辑日志重放慢，恢复不精确 | no |
| 两阶段协调 | 没有 prepare 状态，判不了提交还是回滚 | no |

## C 只留 redo log 会怎样 {meta="反事实二"}
| 场景 | 后果 | 判定 |
|---|---|---|
| 主从复制 | 从库没日志，数据发散 | no |
| 备份归档 | 循环写会覆盖，回不到过去 | no |

## D 提交时的两阶段配合 {span=2 meta="MySQL 内部 XA"}
```sequence
InnoDB -> InnoDB: redo log 落盘，标记 prepare
InnoDB -> Server: 写 binlog
Server -> InnoDB: 通知提交，redo log 标记 commit
note InnoDB, Server: binlog 完整则提交，否则回滚
```
prepare 和 commit 之间只夹一步写 binlog。这保证两份日志要么都有，要么都能判废。

## E 30 秒面试答法
```callout ok 答题骨架
先说分工：redo log 在 InnoDB 层管崩溃恢复，binlog 在 Server 层管复制和归档。再说配合：两阶段提交把两者绑在一起，崩溃恢复时对照 binlog 决定提交或回滚。最后补反事实：去掉哪个，哪个场景就出事故。
```
