## 
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

