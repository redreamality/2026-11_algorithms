"""第 6 课：二分查找。讲解见 lessons/06-binary-search.html

实际项目里直接用标准库 bisect（见 examples/binary_search_in_practice.py）。
这里自己手写一遍，接口和 bisect 完全一样：可选的 lo、hi 限定查找范围，可选的 key 指定按什么比。
写完以后，你的 bisect_left 可以直接替换标准库的 bisect.bisect_left。

规则：
- 输入的 items 都已经按 key（没给 key 就按元素本身）从小到大排好序，可能有重复。
- 不要用现成的轮子：bisect 模块、list.index、in、math.isqrt、math.sqrt、** 0.5。
- 统一用“左闭右开”写法：答案始终在 [lo, hi) 里，循环条件 while lo < hi。
- 和 bisect 一样：key 只作用在 items 的元素上，target 本身已经是“key 之后的值”。
  例子：按年龄找人，bisect_left(people, 30, key=lambda person: person.age)。
- 和 bisect 一样：hi 为 None 表示 len(items)；lo < 0 抛 ValueError。
- 异常和标准库一致：index 找不到抛 ValueError（和 list.index 一样），isqrt 负数抛 ValueError。

写完后运行 uv run dsa/binary_search.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_binary_search.py。
"""

from collections.abc import Callable, Sequence


def bisect_left(items: Sequence, target, lo: int = 0, hi: int | None = None, *, key: Callable | None = None) -> int:
    """在 items[lo:hi] 里找第一个 key(元素) >= target 的下标；都比 target 小就返回 hi。O(log n)。

    也就是：把 target 插进去、并且排在所有相等元素前面时的位置。
    """
    raise NotImplementedError


def bisect_right(items: Sequence, target, lo: int = 0, hi: int | None = None, *, key: Callable | None = None) -> int:
    """在 items[lo:hi] 里找第一个 key(元素) > target 的下标；没有就返回 hi。O(log n)。

    小结论：target 出现的次数 = bisect_right - bisect_left。
    """
    raise NotImplementedError


def index(items: Sequence, target, *, key: Callable | None = None) -> int:
    """target 第一次出现的下标（有重复时返回最左边那个）。找不到抛 ValueError，和 list.index 一样。O(log n)。

    提示：先用 bisect_left 找位置，再看那个位置上是不是 target。
    """
    raise NotImplementedError


def first_true(low: int, high: int, predicate: Callable[[int], bool]) -> int:
    """在整数区间 [low, high) 里找第一个让 predicate 为真的数；都为假就返回 high。O(log(high - low)) 次调用。

    前提：predicate 是“单调”的，前面一段全假、后面一段全真（False False … True True）。
    这就是“在答案上二分”：不是在数组里找，而是在可能的答案范围里找。
    例子：第一个出问题的版本号、最少要几台服务器才扛得住、最小的够用的缓冲区大小。
    """
    raise NotImplementedError


def isqrt(number: int) -> int:
    """整数平方根：满足 x * x <= number 的最大整数 x。number < 0 抛 ValueError，和 math.isqrt 一样。

    提示：用 first_true 找第一个 x * x > number 的 x，再减 1。
    要求 O(log n)，number 很大（比如 10**30）也要很快，并且结果精确（不能经过浮点数）。
    """
    raise NotImplementedError


if __name__ == "__main__":
    from datetime import date

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景一：成绩分档。分数线排好序，bisect_right 就知道落在第几档。
    cutoffs = [60, 70, 80, 90]
    grades = "FDCBA"
    show("分数 [33, 60, 89, 90, 100] 的等级",
         lambda: [grades[bisect_right(cutoffs, score)] for score in [33, 60, 89, 90, 100]],
         ["F", "D", "B", "A", "A"])

    # 端到端场景二：按日期排好序的订单，查某一段日期里有几单。key 让我们不用另外建一个日期列表。
    orders = [(date(2026, 11, day), amount) for day, amount in [(1, 30), (3, 12), (3, 50), (7, 8), (9, 99)]]
    order_date = lambda order: order[0]  # noqa: E731
    show("11 月 3 日到 11 月 7 日（含）的订单数",
         lambda: bisect_right(orders, date(2026, 11, 7), key=order_date)
         - bisect_left(orders, date(2026, 11, 3), key=order_date), 3)
    show("11 月 3 日的第一单在第几个", lambda: index(orders, date(2026, 11, 3), key=order_date), 1)

    # 端到端场景三：第一个出问题的版本。只知道“某版之后全坏”，每次检查都很贵，所以要少查。
    first_broken_version = 4217
    show("在 1～9999 号版本里找第一个坏版本",
         lambda: first_true(1, 10_000, lambda version: version >= first_broken_version), 4217)

    # 端到端场景四：最少几台服务器能扛住 12345 QPS，每台扛 400。
    show("扛住 12345 QPS 最少要几台", lambda: first_true(0, 1_000, lambda servers: servers * 400 >= 12345), 31)
    show("isqrt(10**30)", lambda: isqrt(10**30), 10**15)
