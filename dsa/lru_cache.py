"""第 30 课：LRU 缓存。讲解见 lessons/30-lru-cache.html

LRU（Least Recently Used，最近最少使用）：缓存满了以后，淘汰“最久没有被用过”的那一项。

实际项目里一般直接用 functools.lru_cache 或 collections.OrderedDict（见 examples/lru_cache_in_practice.py）。
这里自己手写，接口和 dict 一样：cache[key] = value、cache[key]、cache.get(key, default)、
key in cache、len(cache)。LeetCode 146 的 put(key, value) 就是 cache[key] = value，
get(key) 就是 cache.get(key, -1)。

规则：
- 读和写都必须是 O(1)。结构是“哈希表 + 双向链表”：
  - 哈希表 key_to_node：key → 链表节点，用来 O(1) 找到节点；
  - 双向链表：按“最近用过”的顺序串起所有节点，越靠近 head_sentinel 越新，越靠近 tail_sentinel 越旧。
- 不要用 collections.OrderedDict，也不要用 list 存顺序（list 删除中间元素是 O(n)）。
- 用两个哨兵节点 head_sentinel、tail_sentinel 当链表的两端，它们不存数据。
  这样链表永远不会“空”，插入和删除都不用判断 None。
- cache[key] 和 cache[key] = value 都算“用过”，要把 key 挪到最前面；key in cache 只是看一眼，不算用过。
- 下面的 DoublyLinkedNode、get、keys_from_most_to_least_recent 是写好的，不是练习。

自查：在项目目录运行 uv run dsa/lru_cache.py，会逐个打印“输入、期望、实际”。
"""


class DoublyLinkedNode:
    """双向链表的节点：同时记住前一个和后一个。存 key 是为了淘汰时能反查哈希表。"""

    def __init__(self, key=None, value=None) -> None:
        self.key = key
        self.value = value
        self.previous: "DoublyLinkedNode | None" = None
        self.next: "DoublyLinkedNode | None" = None


class LRUCache:
    """容量固定的 LRU 缓存，用法和 dict 一样。

    例子（capacity = 2）：
        cache[1] = "a"        # 缓存：{1}
        cache[2] = "b"        # 缓存：{2, 1}
        cache[1]              # 返回 "a"；1 变成最近用过的
        cache[3] = "c"        # 满了，淘汰最久没用的 2；缓存：{3, 1}
        2 in cache            # False（已经被淘汰）
        cache.get(2, "没有")  # 返回 "没有"
        cache[2]              # 抛 KeyError(2)
    """

    def __init__(self, capacity: int) -> None:
        """建一个空缓存。capacity < 1 时抛 ValueError。

        需要建好这些属性（名字请保持一致，keys_from_most_to_least_recent 会用到）：
        - self.capacity：容量；
        - self.key_to_node：空字典，key → DoublyLinkedNode；
        - self.head_sentinel、self.tail_sentinel：两个哨兵节点，
          并且让 head_sentinel.next = tail_sentinel，tail_sentinel.previous = head_sentinel。
        """
        raise NotImplementedError

    def _remove_node(self, node: DoublyLinkedNode) -> None:
        """把 node 从双向链表里摘下来（不动哈希表）。O(1)。

        提示：让 node 前后两个节点直接相连：
        node.previous.next = node.next，node.next.previous = node.previous。
        因为有哨兵，node 前后一定都有节点，不用判断 None。
        """
        raise NotImplementedError

    def _add_to_front(self, node: DoublyLinkedNode) -> None:
        """把 node 插到 head_sentinel 后面，成为“最近用过的”（不动哈希表）。O(1)。

        提示：先记住原来的第一个节点 first_node = self.head_sentinel.next，
        然后改四个指针：node.previous、node.next、head_sentinel.next、first_node.previous。
        """
        raise NotImplementedError

    def __len__(self) -> int:
        """缓存里有几项。O(1)。"""
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        """key in cache。只查哈希表，不改变先后顺序。O(1)。"""
        raise NotImplementedError

    def __getitem__(self, key):
        """cache[key]：返回值，并把它挪到最前面。不存在抛 KeyError(key)，和 dict 一样。O(1)。"""
        raise NotImplementedError

    def __setitem__(self, key, value) -> None:
        """cache[key] = value。O(1)。

        - key 已经存在：更新值，并挪到最前面。
        - key 不存在：如果缓存已满（len(self) == capacity），先淘汰 tail_sentinel 前面的那个节点
          （最久没用过的）：从链表摘掉，并用它的 key 从 key_to_node 里删掉；
          然后新建节点，插到最前面，再登记进 key_to_node。
        """
        raise NotImplementedError

    # ---------- 写好的小工具（不是练习） ----------

    def get(self, key, default=None):
        """和 dict.get 一样：有就返回值（也算用过），没有就返回 default。"""
        try:
            return self[key]
        except KeyError:
            return default

    def keys_from_most_to_least_recent(self) -> list:
        """从 head_sentinel 往后走，按“最近用过 → 最久没用”的顺序列出所有 key，方便自查。"""
        keys = []
        current_node = self.head_sentinel.next
        while current_node is not self.tail_sentinel:
            keys.append(current_node.key)
            current_node = current_node.next
        return keys


if __name__ == "__main__":
    def check(description, compute, expected):
        try:
            actual = compute()
        except NotImplementedError:
            actual = "还没实现"
        verdict = "[对]" if actual == expected else "[错]"
        print(f"{verdict} {description}")
        print(f"    期望：{expected!r}")
        print(f"    实际：{actual!r}")

    def run_operations(capacity, operations):
        """按 LeetCode 146 的写法执行操作：put 是 cache[key] = value，get 是 cache.get(key, -1)。
        返回每一步的返回值（put 返回 None），最后附上从新到旧的 key 顺序。"""
        cache = LRUCache(capacity)
        results = []
        for operation in operations:
            if operation[0] == "put":
                cache[operation[1]] = operation[2]
                results.append(None)
            else:
                results.append(cache.get(operation[1], -1))
        return results, cache.keys_from_most_to_least_recent()

    leetcode_example = [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2),
                        ("put", 4, 4), ("get", 1), ("get", 3), ("get", 4)]
    check(f"capacity=2，操作 {leetcode_example}",
          lambda: run_operations(2, leetcode_example),
          ([None, None, 1, None, -1, None, -1, 3, 4], [4, 3]))

    update_existing = [("put", 1, 1), ("put", 2, 2), ("put", 1, 10), ("put", 3, 3), ("get", 1), ("get", 2)]
    check(f"capacity=2，更新已有的 key 也算“用过”：{update_existing}",
          lambda: run_operations(2, update_existing),
          ([None, None, None, None, 10, -1], [1, 3]))

    capacity_one = [("put", 2, 1), ("get", 2), ("put", 3, 2), ("get", 2), ("get", 3)]
    check(f"capacity=1：{capacity_one}",
          lambda: run_operations(1, capacity_one),
          ([None, 1, None, -1, 2], [3]))

    get_changes_order = [("put", 1, 1), ("put", 2, 2), ("put", 3, 3), ("get", 1), ("put", 4, 4),
                         ("get", 2), ("get", 3), ("get", 1), ("get", 4)]
    check(f"capacity=3，读取会把 key 挪到最前面：{get_changes_order}",
          lambda: run_operations(3, get_changes_order),
          ([None, None, None, 1, None, -1, 3, 1, 4], [4, 1, 3]))

    # 端到端场景：缓存最近查过的用户资料，最多存 2 个，避免反复查数据库。
    def user_profile_cache():
        database = {"u1": "张三", "u2": "李四", "u3": "王五"}
        database_reads = []

        def load_profile(user_id):
            if user_id in cache:
                return cache[user_id]
            database_reads.append(user_id)  # 缓存没有才去查数据库
            cache[user_id] = database[user_id]
            return cache[user_id]

        cache = LRUCache(2)
        names = [load_profile(user_id) for user_id in ["u1", "u2", "u1", "u3", "u2", "u1"]]
        return names, database_reads, "u3" in cache, len(cache)

    check("用户资料缓存：依次访问 u1 u2 u1 u3 u2 u1，capacity=2",
          user_profile_cache,
          (["张三", "李四", "张三", "王五", "李四", "张三"], ["u1", "u2", "u3", "u2", "u1"], False, 2))

    def missing_key_raises():
        cache = LRUCache(1)
        cache["a"] = 1
        try:
            cache["b"]
        except KeyError as error:
            return f"KeyError({error.args[0]!r})"
        return "没有抛异常"

    check("cache['b'] 不存在时抛 KeyError", missing_key_raises, "KeyError('b')")
