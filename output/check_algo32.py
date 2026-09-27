# -*- coding: utf-8 -*-
# 回归测试：校验《算法手撕-32题闭卷清单》里的代码脊柱是否真能跑通
# 用法（改清单里的任一代码脊柱后必须跑）：
#   PYTHONIOENCODING=utf-8 python output/check_algo32.py
# 产出：逐题 OK / 末尾失败数（必须为 0）
import heapq
from collections import OrderedDict, deque


class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next


def to_list(h):
    r = []
    while h:
        r.append(h.val); h = h.next
    return r


def mk(vals):
    d = cur = ListNode(0)
    for v in vals:
        cur.next = ListNode(v); cur = cur.next
    return d.next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


fails = []


def eq(name, got, want):
    if got != want:
        fails.append("%s: got %r want %r" % (name, got, want))
    else:
        print("OK   %-28s %r" % (name, got))


# ---------- S1 两数之和 ----------
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return None


eq("S1 两数之和", two_sum([2, 7, 11, 15], 9), [0, 1])
eq("S1 同元素不可复用", two_sum([3, 2, 4], 6), [1, 2])
eq("S1 无解", two_sum([1, 2], 9), None)


# ---------- S2 无重复最长子串 ----------
def len_longest(s):
    pos, left, ans = {}, 0, 0
    for right, c in enumerate(s):
        if c in pos and pos[c] >= left:
            left = pos[c] + 1
        pos[c] = right
        ans = max(ans, right - left + 1)
    return ans


eq("S2 abcabcbb", len_longest("abcabcbb"), 3)
eq("S2 bbbbb", len_longest("bbbbb"), 1)
eq("S2 pwwkew", len_longest("pwwkew"), 3)
eq("S2 空串", len_longest(""), 0)
eq("S2 abba", len_longest("abba"), 2)


# ---------- S3 反转链表 ----------
def reverse(head):
    prev, cur = None, head
    while cur:
        cur.next, prev, cur = prev, cur, cur.next
    return prev


eq("S3 反转链表", to_list(reverse(mk([1, 2, 3, 4, 5]))), [5, 4, 3, 2, 1])
eq("S3 单节点", to_list(reverse(mk([1]))), [1])


# ---------- S4 合并两个有序链表 ----------
def merge2(l1, l2):
    d = cur = ListNode(0)
    while l1 and l2:
        if l1.val <= l2.val:
            cur.next, l1 = l1, l1.next
        else:
            cur.next, l2 = l2, l2.next
        cur = cur.next
    cur.next = l1 or l2
    return d.next


eq("S4 合并有序链表", to_list(merge2(mk([1, 2, 4]), mk([1, 3, 4]))), [1, 1, 2, 3, 4, 4])
eq("S4 一侧空", to_list(merge2(None, mk([0]))), [0])


# ---------- S5 环形链表 II ----------
def detect_cycle(head, pos):
    if pos >= 0:
        # 造环
        nodes = [mk([i]) for i in range(5)]
        for i in range(4):
            nodes[i].next = nodes[i + 1]
        nodes[4].next = nodes[pos]
        head = nodes[0]
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            p = head
            while p is not slow:
                p, slow = p.next, slow.next
            return p.val
    return None


eq("S5 入环点", detect_cycle(None, 1), 1)
eq("S5 无环", detect_cycle(mk([1]), -1), None)


# ---------- S6 遍历 ----------
def inorder(r):
    return inorder(r.left) + [r.val] + inorder(r.right) if r else []


def level_order(root):
    if not root:
        return []
    res, q = [], [root]
    while q:
        lvl, nq = [], []
        for x in q:
            lvl.append(x.val)
            nq += [c for c in (x.left, x.right) if c]
        res.append(lvl); q = nq
    return res


t = TreeNode(1, None, TreeNode(2, TreeNode(3)))
eq("S6 中序", inorder(t), [1, 3, 2])
eq("S6 层序", level_order(t), [[1], [2], [3]])


# ---------- S7 直径 / 深度 ----------
def diameter(root):
    ans = [0]

    def dfs(r):
        if not r:
            return 0
        L, R = dfs(r.left), dfs(r.right)
        ans[0] = max(ans[0], L + R)
        return 1 + max(L, R)

    dfs(root)
    return ans[0]


a = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
eq("S7 直径", diameter(a), 3)


# ---------- S8 最近公共祖先 ----------
def lca(r, p, q):
    if not r or r is p or r is q:
        return r
    L, R = lca(r.left, p, q), lca(r.right, p, q)
    return r if L and R else (L or R)


p, q = a.left, a.right
eq("S8 LCA", lca(a, p, q).val, 1)


# ---------- S9 有效括号 ----------
def valid(s):
    pair = {')': '(', ']': '[', '}': '{'}
    st = []
    for c in s:
        if c in '([{':
            st.append(c)
        elif not st or st.pop() != pair[c]:
            return False
    return not st


eq("S9 ()[]{}", valid("()[]{}"), True)
eq("S9 ([)]", valid("([)]"), False)
eq("S9 (]", valid("(]"), False)
eq("S9 空", valid(""), True)
eq("S9 (", valid("("), False)


# ---------- S10 LRU ----------
class LRUCache:
    def __init__(self, cap):
        self.cap, self.d = cap, OrderedDict()

    def get(self, k):
        if k not in self.d:
            return -1
        self.d.move_to_end(k)
        return self.d[k]

    def put(self, k, v):
        self.d[k] = v
        self.d.move_to_end(k)
        if len(self.d) > self.cap:
            self.d.popitem(last=False)


c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
eq("S10 LRU get1", c.get(1), 1)
c.put(3, 3)
eq("S10 LRU 淘汰2", c.get(2), -1)
c.put(4, 4)
eq("S10 LRU 淘汰1", c.get(1), -1)
eq("S10 LRU get3", c.get(3), 3)
eq("S10 LRU get4", c.get(4), 4)


# ---------- S11 第K大 / TopK ----------
def kth(nums, k):
    heap = nums[:k]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]


eq("S11 第K大", kth([3, 2, 1, 5, 6, 4], 2), 5)
eq("S11 第K大 k=1", kth([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4)
eq("S11 含负数", kth([-1, -2, 3], 1), 3)


def topk(nums, k):
    from collections import Counter
    heap = []
    for num, cnt in Counter(nums).items():
        heapq.heappush(heap, (cnt, num))
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([n for _, n in heap])


eq("S11 TopK", topk([1, 1, 1, 2, 2, 3], 2), [1, 2])


# ---------- S12 搜索旋转数组 ----------
def search_rot(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


eq("S12 旋转搜索", search_rot([4, 5, 6, 7, 0, 1, 2], 0), 4)
eq("S12 不存在", search_rot([4, 5, 6, 7, 0, 1, 2], 3), -1)
eq("S12 单元素", search_rot([1], 0), -1)
eq("S12 未旋转", search_rot([1, 2, 3], 3), 2)
eq("S12 两元素", search_rot([3, 1], 1), 1)


# ---------- S13 岛屿数量 ----------
def num_islands(grid):
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])

    def sink(i, j):
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != '1':
            return 0
        grid[i][j] = '0'
        return 1 + sink(i + 1, j) + sink(i - 1, j) + sink(i, j + 1) + sink(i, j - 1)

    return sum(1 for i in range(m) for j in range(n) if grid[i][j] == '1' and sink(i, j) > 0)


g1 = [list("11110"), list("11010"), list("11000"), list("00000")]
eq("S13 岛屿数", num_islands(g1), 1)
g2 = [list("11000"), list("11000"), list("00100"), list("00011")]
eq("S13 三岛", num_islands(g2), 3)


# ---------- S14 合并区间 ----------
def merge_iv(ivs):
    ivs = sorted(ivs)
    res = [ivs[0][:]]
    for s, e in ivs[1:]:
        if s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res


eq("S14 合并区间", merge_iv([[1, 3], [2, 6], [8, 10], [15, 18]]), [[1, 6], [8, 10], [15, 18]])
eq("S14 相邻", merge_iv([[1, 4], [4, 5]]), [[1, 5]])


# ---------- S15 三数之和 ----------
def three_sum(nums):
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if i and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            t = nums[i] + nums[l] + nums[r]
            if t < 0:
                l += 1
            elif t > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
    return res


eq("S15 三数和", three_sum([-1, 0, 1, 2, -1, -4]), [[-1, -1, 2], [-1, 0, 1]])
eq("S15 全零", three_sum([0, 0, 0, 0]), [[0, 0, 0]])
eq("S15 无解", three_sum([1, 2, 3]), [])


# ---------- A1 最小覆盖子串 ----------
def min_window(s, t):
    from collections import Counter
    need, cnt = Counter(t), {}
    have, total = 0, len(need)
    best, left = None, 0
    for right, ch in enumerate(s):
        if ch in need:
            cnt[ch] = cnt.get(ch, 0) + 1
            if cnt[ch] == need[ch]:
                have += 1
        while have == total:
            if best is None or right - left + 1 < len(best):
                best = s[left:right + 1]
            lc = s[left]
            if lc in need:
                cnt[lc] -= 1
                if cnt[lc] < need[lc]:
                    have -= 1
            left += 1
    return best or ""


eq("A1 最小覆盖", min_window("ADOBECODEBANC", "ABC"), "BANC")
eq("A1 单字符", min_window("a", "a"), "a")
eq("A1 无解", min_window("a", "aa"), "")


# ---------- A2 Kadane ----------
def max_sub(nums):
    cur = best = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


eq("A2 Kadane", max_sub([-2, 1, -3, 4, -1, 2, 1, -5, 4]), 6)
eq("A2 全负", max_sub([-3, -1, -2]), -1)


# ---------- A3 和为K的子数组 ----------
def subarray_sum(nums, k):
    cnt, pre, ans = {0: 1}, 0, 0
    for x in nums:
        pre += x
        ans += cnt.get(pre - k, 0)
        cnt[pre] = cnt.get(pre, 0) + 1
    return ans


eq("A3 和为K", subarray_sum([1, 1, 1], 2), 2)
eq("A3 k=0", subarray_sum([0, 0, 0], 0), 6)
eq("A3 含负", subarray_sum([1, 2, 3], 3), 2)


# ---------- A5 验证 BST ----------
def is_bst(r, lo=float('-inf'), hi=float('inf')):
    if not r:
        return True
    return lo < r.val < hi and is_bst(r.left, lo, r.val) and is_bst(r.right, r.val, hi)


eq("A5 合法BST", is_bst(TreeNode(2, TreeNode(1), TreeNode(3))), True)
eq("A5 非法BST", is_bst(TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))), False)
eq("A5 等值非法", is_bst(TreeNode(2, TreeNode(2), TreeNode(3))), False)


# ---------- A7 全排列 ----------
def permute(nums):
    n = len(nums)
    res = []

    def bt(path, used):
        if len(path) == n:
            res.append(path[:]); return
        for i in range(n):
            if not used[i]:
                used[i] = True
                path.append(nums[i])
                bt(path, used)
                path.pop(); used[i] = False

    bt([], [False] * n)
    return res


eq("A7 全排列数", len(permute([1, 2, 3])), 6)
eq("A7 不重复", len(set(map(tuple, permute([1, 2, 3])))), 6)


# ---------- A8 每日温度 ----------
def daily_t(T):
    st, ans = [], [0] * len(T)
    for i, t in enumerate(T):
        while st and T[st[-1]] < t:
            j = st.pop()
            ans[j] = i - j
        st.append(i)
    return ans


eq("A8 每日温度", daily_t([73, 74, 75, 71, 69, 72, 76, 73]), [1, 1, 4, 2, 1, 1, 0, 0])


# ---------- A9 跳跃游戏 ----------
def can_jump(nums):
    far = 0
    for i, x in enumerate(nums):
        if i > far:
            return False
        far = max(far, i + x)
    return True


eq("A9 可达", can_jump([2, 3, 1, 1, 4]), True)
eq("A9 不可达", can_jump([3, 2, 1, 0, 4]), False)
eq("A9 单元素", can_jump([0]), True)


# ---------- A10 打家劫舍 ----------
def rob(nums):
    pp = p = 0
    for v in nums:
        pp, p = p, max(p, pp + v)
    return p


eq("A10 打家劫舍", rob([2, 7, 9, 3, 1]), 12)
eq("A10 两个", rob([2, 1]), 2)
eq("A10 一个", rob([5]), 5)


# ---------- B1 零钱兑换 ----------
def coin_change(coins, amount):
    inf = float('inf')
    dp = [0] + [inf] * amount
    for c in coins:
        for a in range(c, amount + 1):
            if dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return -1 if dp[amount] == inf else dp[amount]


eq("B1 零钱兑换", coin_change([1, 2, 5], 11), 3)
eq("B1 不可凑", coin_change([2], 3), -1)
eq("B1 0元", coin_change([1], 0), 0)


# ---------- B2 LCS ----------
def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


eq("B2 LCS", lcs("abcde", "ace"), 3)
eq("B2 无公共", lcs("abc", "def"), 0)


# ---------- B3 课程表 ----------
def can_finish(n, prereq):
    ind = [0] * n
    g = [[] for _ in range(n)]
    for a, b in prereq:
        g[b].append(a); ind[a] += 1
    q, seen = [i for i in range(n) if not ind[i]], 0
    while q:
        u = q.pop(); seen += 1
        for v in g[u]:
            ind[v] -= 1
            if not ind[v]:
                q.append(v)
    return seen == n


eq("B3 无环", can_finish(2, [[1, 0]]), True)
eq("B3 有环", can_finish(2, [[1, 0], [0, 1]]), False)


# ---------- B4 腐烂橘子 ----------
def oranges(grid):
    m, n = len(grid), len(grid[0])
    q, fresh = deque(), 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1
    if fresh == 0:
        return 0
    minute = -1
    while q:
        minute += 1
        for _ in range(len(q)):
            i, j = q.popleft()
            for x, y in ((i + 1, j), (i - 1, j), (i, j + 1), (i, j - 1)):
                if 0 <= x < m and 0 <= y < n and grid[x][y] == 1:
                    grid[x][y] = 2
                    fresh -= 1
                    q.append((x, y))
    return minute if fresh == 0 else -1


eq("B4 腐烂橘子", oranges([[2, 1, 1], [1, 1, 0], [0, 1, 1]]), 4)
eq("B4 全连通", oranges([[2, 1, 0], [0, 1, 0], [0, 0, 0]]), 2)
eq("B4 真孤岛", oranges([[2, 0, 0], [0, 0, 0], [0, 0, 1]]), -1)
eq("B4 无鲜橘", oranges([[0, 2]]), 0)


# ---------- B6 柱状图最大矩形 ----------
def largest_rect(heights):
    st, ans = [], 0
    hs = heights + [0]
    for i, h in enumerate(hs):
        while st and heights[st[-1]] > h:
            top = st.pop()
            left = st[-1] if st else -1
            ans = max(ans, heights[top] * (i - left - 1))
        st.append(i)
    return ans


eq("B6 最大矩形", largest_rect([2, 1, 5, 6, 2, 3]), 10)
eq("B6 递增", largest_rect([1, 2, 3, 4]), 6)
eq("B6 单柱", largest_rect([5]), 5)


# ---------- B7 合并K个升序链表 ----------
def merge_k(lists):
    heap = []
    for idx, h in enumerate(lists):
        if h:
            heapq.heappush(heap, (h.val, idx, h))
    d = cur = ListNode(0)
    while heap:
        _, idx, node = heapq.heappop(heap)
        cur.next = node; cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))
    return d.next


eq("B7 合并K链表", to_list(merge_k([mk([1, 4, 5]), mk([1, 3, 4]), mk([2, 6])])), [1, 1, 2, 3, 4, 4, 5, 6])
eq("B7 含空表", to_list(merge_k([None, mk([1])])), [1])


# ---------- A4 K个一组翻转（清单未给代码，验证常用写法可复用） ----------
def reverse_k(head, k):
    def end_of(node):                 # 返回本组第 k 个节点，不足 k 个返回 None
        p = node
        for _ in range(k - 1):
            if not p or not p.next:
                return None
            p = p.next
        return p

    d = ListNode(0, head)
    group_prev = d
    while True:
        kth = end_of(group_prev.next)
        if not kth:
            break
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            cur.next, prev, cur = prev, cur, cur.next
        tmp = group_prev.next
        group_prev.next = kth
        group_prev = tmp
    return d.next


eq("A4 K组翻转", to_list(reverse_k(mk([1, 2, 3, 4, 5]), 2)), [2, 1, 4, 3, 5])
eq("A4 K=3", to_list(reverse_k(mk([1, 2, 3, 4, 5]), 3)), [3, 2, 1, 4, 5])


print()
print("=" * 46)
print("失败数: %d" % len(fails))
for f in fails:
    print("  FAIL " + f)
print("=" * 46)
