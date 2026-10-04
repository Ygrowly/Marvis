---
type: brain-cards
kind: ground
module: PostgreSQL
status: candidate
human_reviewed: false
created: 2026-10-04
updated: 2026-10-04
---

## ground ground-postgresql · PostgreSQL 地基包

**定位**：与 MySQL 平行的关系库第二主干——面试里常作「对比数据库」出现，答出实现差异才是加分项。范围：索引、执行、事务 MVCC、WAL、VACUUM、复制；不含扩展生态（PostGIS 等）与 DBA 调优。

**心智模型**：与 MySQL 共用同一条根判据（磁盘随机 IO 慢约 5 个数量级），但多版本 answers 不同：**MySQL 把旧版本存 undo，PostgreSQL 把旧版本存在表里（元组多版本），靠 VACUUM 回收**。只抓住「多版本存哪、谁回收」这一条，七条主线的差异全能推出来：长事务拖 VACUUM → 表膨胀与事务 ID 回卷；索引里也存旧版本 → 膨胀；写 = 追加新元组 → 写放大。

**必会清单**：
- 索引家族比 MySQL 宽：B-tree 同款判据之外，GIN（JSONB / 全文倒排）、部分索引都是选型项 [@PostgreSQL-1]
- 执行器：代价估算决定 Seq Scan 还是 Index Scan，统计信息过期是慢查询第一嫌疑 [@PostgreSQL-2]
- MVCC：元组带 xmin/xmax，快照判可见性；RC 与 RR 的差别仍是快照生成时机（与 MySQL 同构不同实现）[@PostgreSQL-3]
- WAL：先写日志再刷数据页，与 MySQL redo 同理；checkpoint 在平衡恢复时长与刷页压力 [@PostgreSQL-4]
- 长事务的 PG 特有代价：阻塞 VACUUM → 死元组堆积 → 表膨胀，极端时事务 ID 回卷（强制停机）[@PostgreSQL-5]
- 复制两形态：流复制（物理，整实例）与逻辑复制（按表），主从切换靠它 [@PostgreSQL-6]

**学习路径**：
1. 先当「第二个 MySQL」学共同概念（索引/事务/WAL），共用底层直觉 [@PostgreSQL-1]
2. 再逐条对照差异点：MVCC 实现、VACUUM、索引家族、复制形态 [@PostgreSQL-3]
3. 然后长事务与高可用：PG 的稳定性问题几乎都从 VACUUM 派生 [@PostgreSQL-5]
4. 最后业务并发场景：把 MySQL 主线七的题目用 PG 的机制重答一遍 [@PostgreSQL-7]

**验收门**：
- 说出 PG 与 MySQL 的三个实现差异（多版本存哪、日志、复制形态）及各自代价 [@PostgreSQL-3]
- 能讲清 VACUUM 为什么必须存在、长事务怎么把它拖垮 [@PostgreSQL-5]
