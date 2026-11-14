"""第 4 课：哈希表（拉链法）。讲解见 lessons/04-hash-table.html

Python 的 dict 本身就是哈希表，实际项目里直接用 dict / set / Counter / defaultdict
（见 examples/hash_table_in_practice.py）。这里自己造一个用法和 dict 一样的 HashMap，
看清楚 table[key] = value、table[key] 为什么平均是 O(1)：
scores = HashMap({"alice": 90}); scores["bob"] = 85; scores["alice"]; del scores["bob"];
"alice" in scores、len(scores)、for name in scores、scores.get("carol", 0)、scores.items()。

规则：
- self._buckets 是一个 list，每个元素是一个“桶”；每个桶是一个 list，里面放 [key, value] 对。
  不要在内部用 dict 或 set 存数据，否则就等于借用了 Python 自己的哈希表。
- key 放进哪个桶：self._index(key)，即 hash(key) % 桶的个数。
- 两个 key 落进同一个桶（冲突）没关系，挨个挂在这个桶的 list 后面就行。
- 负载因子 = 元素个数 / 桶的个数。放入新 key 之后，如果负载因子超过 0.75（严格大于），
  就把桶的个数翻倍，并把所有 [key, value] 重新算下标、放进新桶（rehash）。
- key 不存在时，读和删都抛 KeyError(key)，和 dict 一样。

继承 MutableMapping 以后，只要写好 __getitem__、__setitem__、__delitem__、__iter__、__len__，
Python 会自动送你 get、pop、setdefault、update、keys、values、items、in、== 这些方法。
（送的 in 是靠调用 __getitem__ 再接住 KeyError 实现的，所以 __getitem__ 找不到时一定要抛 KeyError。）

写完后运行 uv run dsa/hash_table.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_hash_table.py。
"""

from collections.abc import Iterator, MutableMapping

LOAD_FACTOR = 0.75


class HashMap(MutableMapping):
    def __init__(self, items=(), capacity: int = 8) -> None:
        self._buckets: list[list[list]] = [[] for _ in range(capacity)]
        self._size = 0
        self.update(items)  # MutableMapping 自带的 update，内部会调用 __setitem__

    @property
    def capacity(self) -> int:
        """桶的个数。"""
        return len(self._buckets)

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"HashMap({dict(self.items())!r})"

    def _index(self, key) -> int:
        """key 应该放进第几个桶。O(1)。"""
        raise NotImplementedError

    def __setitem__(self, key, value) -> None:
        """table[key] = value。key 已存在就覆盖 value（个数不变）。平均 O(1)。

        放入新 key 后负载因子超过 0.75，就调用 self._resize(2 * capacity)。
        """
        raise NotImplementedError

    def __getitem__(self, key):
        """table[key]。平均 O(1)。key 不存在抛 KeyError(key)。"""
        raise NotImplementedError

    def __delitem__(self, key) -> None:
        """del table[key]。平均 O(1)。key 不存在抛 KeyError(key)。"""
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        """for key in table：一个桶一个桶地产出所有 key。顺序和插入顺序、大小都无关。O(n + 桶数)。"""
        raise NotImplementedError

    def _resize(self, new_capacity: int) -> None:
        """换成 new_capacity 个新桶，把所有 [key, value] 重新算下标放进去。O(n)。"""
        raise NotImplementedError


if __name__ == "__main__":

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景：统计一段访问日志里每个页面被访问了几次，再按用户 ID 查资料。
    visits = ["/home", "/cart", "/home", "/pay", "/home", "/cart"]

    def count_visits():
        counts = HashMap()
        for path in visits:
            counts[path] = counts.get(path, 0) + 1
        return sorted(counts.items())

    show("每个页面的访问次数", count_visits, [("/cart", 2), ("/home", 3), ("/pay", 1)])

    def user_lookup():
        users = HashMap({1001: "alice", 1002: "bob"})
        users[1003] = "carol"
        users[1002] = "bobby"  # 改名：覆盖，个数不变
        del users[1001]  # 注销
        return users[1002], 1001 in users, users.get(1001, "已注销"), len(users)

    show("增、改、删、查用户", user_lookup, ("bobby", False, "已注销", 2))

    def missing_key():
        try:
            HashMap()["nobody"]
        except KeyError:
            return "KeyError"
        return "没抛异常"

    show("查一个不存在的 key", missing_key, "KeyError")

    def grows():
        table = HashMap()
        for number in range(100):
            table[f"user{number}"] = number
        return table.capacity, table["user42"]

    show("放入 100 个 key 之后：桶数、user42", grows, (256, 42))
