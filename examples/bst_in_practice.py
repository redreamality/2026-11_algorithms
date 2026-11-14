"""第 11 课实战：Python 项目里“有序查找”真正是怎么写的。

很少有人在业务代码里手写二叉搜索树。按场景选：
1. 数据基本不变、只查询 → 排好序的 list + 标准库 bisect。查找 O(log n)，但插入要挪元素，O(n)。
2. 边查边改 → sortedcontainers.SortedDict / SortedList（纯 Python、很稳定的第三方库）。
   增删查都约 O(log n)，用法和 dict / list 一样，还多了按范围取、按排名取。

运行：uv run examples/bst_in_practice.py
"""

from bisect import bisect_left, bisect_right
from datetime import datetime

from sortedcontainers import SortedDict


def config_at(history: list[tuple[datetime, str]], moment: datetime) -> str | None:
    """场景一：配置变更历史（按时间排好序），问“某个时刻生效的是哪个版本”。

    就是 floor：找时间 <= moment 的最后一条。bisect_right 返回第一个 > moment 的位置，减 1 即可。
    """
    times = [changed_at for changed_at, _ in history]
    index = bisect_right(times, moment) - 1
    return history[index][1] if index >= 0 else None


class PriceIndex:
    """场景二：商品按价格建索引，要能随时上下架，还要按价格区间筛选。"""

    def __init__(self) -> None:
        self._by_price: SortedDict[int, set[str]] = SortedDict()  # 价格（分） -> 这个价格的商品

    def add(self, name: str, price: int) -> None:
        self._by_price.setdefault(price, set()).add(name)

    def remove(self, name: str, price: int) -> None:
        names = self._by_price[price]
        names.discard(name)
        if not names:
            del self._by_price[price]

    def between(self, low: int, high: int) -> list[str]:
        """价格在 [low, high] 之间的商品，从便宜到贵。irange 只走范围内的部分，不扫全表。"""
        return [name for price in self._by_price.irange(low, high) for name in sorted(self._by_price[price])]

    def best_within_budget(self, budget: int) -> str | None:
        """预算内最贵的商品：floor。bisect_right 找到第一个超预算的位置，往前一格就是。"""
        index = self._by_price.bisect_right(budget) - 1
        if index < 0:
            return None
        price = self._by_price.peekitem(index)[0]
        return sorted(self._by_price[price])[0]

    def cheapest(self) -> str:
        return sorted(self._by_price.peekitem(0)[1])[0]


def main() -> None:
    history = [
        (datetime(2026, 11, 1, 9, 0), "v1"),
        (datetime(2026, 11, 3, 14, 30), "v2"),
        (datetime(2026, 11, 8, 20, 0), "v3"),
    ]
    assert config_at(history, datetime(2026, 11, 5)) == "v2"
    assert config_at(history, datetime(2026, 11, 3, 14, 30)) == "v2"  # 恰好在变更那一刻
    assert config_at(history, datetime(2026, 10, 1)) is None  # 第一次配置之前
    print("11 月 5 日生效的配置：", config_at(history, datetime(2026, 11, 5)))

    sorted_scores = [55, 61, 61, 78, 90, 97]
    passed = len(sorted_scores) - bisect_left(sorted_scores, 60)
    assert passed == 5
    print("60 分及以上的人数：", passed)

    index = PriceIndex()
    for name, price in [("鼠标", 1999), ("显示器", 8999), ("键盘", 4599), ("笔记本", 29900), ("鼠标垫", 699)]:
        index.add(name, price)
    index.add("U 盘", 4599)  # 同价商品
    assert index.between(2000, 9000) == ["U 盘", "键盘", "显示器"]
    assert index.best_within_budget(5000) == "U 盘"
    assert index.best_within_budget(500) is None
    print("20～90 元：", index.between(2000, 9000))

    index.remove("鼠标垫", 699)
    assert index.cheapest() == "鼠标"
    print("鼠标垫下架后最便宜的：", index.cheapest())


if __name__ == "__main__":
    main()
