---
type: topic
topic: 算法
created: 2026-09-08
updated: 2026-09-13
status: integrated
human_reviewed: true
---

# 母题 34 · LRU 缓存

> **模块**：哈希表 + 双向链表
> **关联母题**：[[母题-33-合并K个有序链表]]
> **底库**：[[母题池-36道推导与手写指南]] · [[母题池-Hot100剩余22道]]（只查不练）

## 一、母题与主线

**题目**：实现一个容量固定的缓存，两个操作都要求 O(1)：`get(key)` 命中时返回并把该项标记为最近使用；`put(key, value)` 写入或更新，容量超限时淘汰最久未使用的项。

**母题**：如何同时做到 O(1) 查找和 O(1) 维护淘汰顺序？

**为什么重要**：系统设计高频题，且能直接迁移到 Redis / 本地缓存 / 查询缓存的真实实现。纯考数据结构组合能力。

**一句话结论**：哈希表负责定位、双向链表负责排序；访问或更新移到头部，超容量淘汰尾部。

**恢复关键词**：哈希定位 / 双向链表排序 / 访问移到头 / 超容量删尾

::figure lru-two-views.svg | 同一份缓存状态的两个视图 | 哈希表负责 O(1) 定位、双向链表负责 O(1) 调序，两者指向同一批 Node 实体。只删一边会留下幽灵节点——这就是"两个结构是同一状态的两个视图"的图。

---

**题目要求**：

实现一个缓存，要求：

```plain
get(key)       # 查询，存在则变为最近使用
put(key, val)  # 新增或更新，超过容量时删除最久未使用项
```

并且两种操作都要达到 `O(1)`。

例如容量为 `2`：

```plain
put(1, 1)  → {1}
put(2, 2)  → {1, 2}
get(1)     → 1 成为最近使用
put(3, 3)  → 淘汰最久未使用的 2
```



组合后各自负责：

```plain
哈希表：O(1) 根据 key 定位节点
双向链表：O(1) 调整节点的使用顺序
```

之所以使用双向链表，是因为删除任意节点时，需要同时找到它的前驱和后继：

```plain
node.prev.next = node.next
node.next.prev = node.prev
```

单链表不能 `O(1)` 获得前驱节点。

通常设置两个虚拟节点：

```plain
head ⇄ 最近使用 ⇄ ... ⇄ 最久未使用 ⇄ tail
```

因此：

```plain
访问已有节点 → 移动到 head 后面
缓存已满     → 删除 tail 前面的节点
```

现在先完成两个基础操作。





```python
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}

        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head

    def remove_node(self, node):
        prev_node = node.prev
        next_node = node.next

        prev_node.next = next_node
        next_node.prev = prev_node

    def add_to_front(self, node):
        first = self.head.next

        node.prev = self.head
        node.next = first
        self.head.next = node
        first.prev = node

    def move_to_front(self, node):
        self.remove_node(node)
        self.add_to_front(node)

    def get(self, key):
        if key not in self.cache:
            return -1

        node = self.cache[key]
        self.move_to_front(node)

        return node.value

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.move_to_front(node)
            return

        node = Node(key, value)
        self.cache[key] = node
        self.add_to_front(node)

        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self.remove_node(lru)
            del self.cache[lru.key]
```



循环不变量：

哈希表中的每个键都唯一对应链表中的一个真实节点；越靠近 `head` 使用时间越近，`tail.prev` 始终是最久未使用节点。

复杂度：

```plain
get：O(1)
put：O(1)
空间：O(capacity)
```





因为同一份缓存状态同时存在于两个结构中：

```plain
双向链表：维护使用顺序
哈希表：维护 key → node 的查询入口
```

只删链表，哈希表会留下已淘汰节点；只删哈希表，链表会留下无效节点。两边必须同步删除。

母题 34 恢复脚本：

哈希表负责定位，双向链表负责排序；访问或更新移到头部，新增也放头部，超容量淘汰尾部。

```plain
get：查哈希表 → 移到头部 → 返回值
put 已存在：更新值 → 移到头部
put 不存在：新建 → 放到头部 → 超容量删尾部
```

## 二、扩展：类似题与两层追问

**同类变体**

- LC 460 LFU 缓存（把「使用次数」也纳入淘汰判据，需要频次桶）
- 变体：要求支持过期时间 TTL（加一层时间轮或有序集合）
- 面试延伸：Redis 的近似 LRU 为什么不用严格链表

**两层追问**（能答完这两层才算通过）

1. 为什么必须是双向链表？——要在 O(1) 内删除任意已知节点，需要同时拿到前驱和后继，单链表做不到
2. 临界区在哪？——哈希表和链表是同一份状态的两个视图，必须同步增删，只删一边会留下幽灵节点

## 三、拼接：关联、迁移与复训

**关联母题**：[[母题-33-合并K个有序链表]]

**可迁移场景**：任何「既要快速命中、又要控制容量」的本地缓存；EnergyOps 的查询结果缓存与 RuleArena 的世界状态快照都可以用它做淘汰层。

**本次断点**：写过只删一边导致幽灵节点的版本；对「两个结构是同一状态的两个视图」没有自觉

**通过证据**：闭卷写出本题代码 + 说出不变量 + 答完两层追问

**下次复训**：D1 ____ ｜ D3 ____ ｜ D7 ____ ｜ D14 ____ ｜ D30 ____
