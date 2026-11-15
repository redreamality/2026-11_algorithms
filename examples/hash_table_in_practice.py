"""第 4 课实战：Python 项目里哈希表真正是怎么用的。

dict 和 set 就是哈希表，没人另造一个。要会的是按场景挑对工具：
1. 按 key 查 / 改 → dict，平均 O(1)。
2. 计数 → collections.Counter，most_common(k) 直接拿前 k 名。
3. 分组 → collections.defaultdict(list)，不用先判断 key 在不在。
4. 去重 / 判断“见没见过” → set。
5. 缓存函数结果 → functools.lru_cache / functools.cache（底层就是 dict）。
6. 自定义对象当 key → 用 @dataclass(frozen=True)，自动生成 __hash__ 和 __eq__。
   frozen=True 表示对象建好后字段不能再改；不可变，Python 才敢替它算 hash。

运行：uv run examples/hash_table_in_practice.py
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache

ACCESS_LOG = [
    ("alice", "/home"),
    ("bob", "/cart"),
    ("alice", "/cart"),
    ("carol", "/home"),
    ("alice", "/home"),
    ("bob", "/pay"),
]


def top_pages(log: list[tuple[str, str]], count: int) -> list[tuple[str, int]]:
    """访问量前 count 名的页面。Counter 一遍 O(n) 计数。"""
    return Counter(path for _, path in log).most_common(count)


def pages_by_user(log: list[tuple[str, str]]) -> dict[str, list[str]]:
    """每个用户依次访问了哪些页面。defaultdict(list) 在 key 第一次出现时自动建空列表。"""
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for user, path in log:
        groups[user].append(path)
    return dict(groups)


@dataclass(frozen=True)
class Location:
    """不可变的值对象可以当 dict 的 key 或放进 set。"""

    city: str
    district: str


shipping_fee_calls = 0


@cache
def shipping_fee(location: Location) -> int:
    """模拟一个很慢的运费查询；同一个地址只真正算一次，之后直接从缓存的 dict 里拿。"""
    global shipping_fee_calls
    shipping_fee_calls += 1
    return 0 if location.city == "上海" else 12


def main() -> None:
    assert top_pages(ACCESS_LOG, 2) == [("/home", 3), ("/cart", 2)]
    print("最热门的两个页面：", top_pages(ACCESS_LOG, 2))

    groups = pages_by_user(ACCESS_LOG)
    assert groups["alice"] == ["/home", "/cart", "/home"]
    print("alice 的访问路径：", groups["alice"])

    visitors = {user for user, _ in ACCESS_LOG}
    assert visitors == {"alice", "bob", "carol"}
    paying_users = {user for user, path in ACCESS_LOG if path == "/pay"}
    assert visitors - paying_users == {"alice", "carol"}  # 集合运算：逛了但没付款的人
    print("逛了没付款：", sorted(visitors - paying_users))

    home = Location("上海", "浦东")
    orders = [home, Location("北京", "海淀"), Location("上海", "浦东"), home]
    fees = [shipping_fee(location) for location in orders]
    assert fees == [0, 12, 0, 0]
    assert shipping_fee_calls == 2  # 4 次调用，只有 2 个不同的地址
    print(f"4 笔订单的运费 {fees}，实际只查询了 {shipping_fee_calls} 次")


if __name__ == "__main__":
    main()
