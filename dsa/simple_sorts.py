"""第 7 课：简单排序（选择、插入）。讲解见 lessons/07-simple-sorts.html

实际项目里排序一律用 sorted() / list.sort()（见 examples/simple_sorts_in_practice.py），它们又快又稳定。
这里自己手写两种 O(n²) 排序，接口和 list.sort 完全一样：原地排序，返回 None，
只接受关键字参数 key= 和 reverse=。写完以后，调用方式和 items.sort(key=..., reverse=...) 没有区别。

规则：
- 不要用 sorted()、list.sort()、heapq，自己写。
- 原地排序：直接改传进来的列表，返回 None（和 list.sort() 一样）。
- key 是可选的函数：给了就按 key(元素) 比大小，没给就直接比元素。
- 和 list.sort 一样，key 对每个元素只调用一次：先算出所有 key，排序时让 key 跟着元素一起移动。
  key 可能很贵（比如要查数据库、解析日期），反复调用会让排序慢很多倍。
- reverse=True 时从大到小排，并且和 list.sort 一样仍然要保持稳定：key 相等的元素保持原来的先后次序。
  （所以不能“先正着排再整个反转”，那样相等元素的次序也被反过来了。）
- insertion_sort 必须稳定。提示：往左挪的条件用“严格大于”，不要用“大于等于”。
- 签名里的裸 `*`（如 *, key, reverse）：它后面的参数只能按关键字传（key=...），不能按位置传。

写完后运行 uv run dsa/simple_sorts.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_simple_sorts.py。
"""

from collections.abc import Callable


def selection_sort(items: list, *, key: Callable | None = None, reverse: bool = False) -> None:
    """选择排序：每轮从未排序部分选出最小的（reverse 时选最大的），和未排序部分的第一个交换。

    原地，不稳定（reverse=True 时也不要求稳定）。时间 O(n²)（不管输入长什么样），额外空间 O(n)（存 key）。
    优点：交换次数最多 n - 1 次。
    """
    raise NotImplementedError


def insertion_sort(items: list, *, key: Callable | None = None, reverse: bool = False) -> None:
    """插入排序：像整理手里的牌，把每个新元素往左挪到合适的位置。

    原地，稳定（reverse=True 时也稳定）。最坏 O(n²)；输入近乎有序时接近 O(n)。额外空间 O(n)（存 key）。
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

    # 端到端场景：一张工单表，要按“优先级从高到低，同优先级按创建日期从早到晚”展示。
    def build_tickets():
        return [
            {"id": 101, "priority": 2, "created": date(2026, 11, 3)},
            {"id": 102, "priority": 3, "created": date(2026, 11, 5)},
            {"id": 103, "priority": 2, "created": date(2026, 11, 1)},
            {"id": 104, "priority": 3, "created": date(2026, 11, 2)},
            {"id": 105, "priority": 1, "created": date(2026, 11, 4)},
        ]

    def two_pass_with(sort):
        """利用稳定性分两趟排：先按次要字段排，再按主要字段排，主要字段相同时次要字段的顺序被保留。"""
        tickets = build_tickets()
        sort(tickets, key=lambda ticket: ticket["created"])
        sort(tickets, key=lambda ticket: ticket["priority"], reverse=True)
        return [ticket["id"] for ticket in tickets]

    show("insertion_sort 两趟：优先级降序，同优先级按日期升序", lambda: two_pass_with(insertion_sort),
         [104, 102, 103, 101, 105])

    def by_name_length():
        names = ["Tom", "Alexandra", "Li", "Bob", "Eve"]
        insertion_sort(names, key=len)
        return names

    show("按名字长度排，长度相同保持原顺序", by_name_length, ["Li", "Tom", "Bob", "Eve", "Alexandra"])

    def selection_numbers():
        prices = [399, 59, 1299, 5, 59]
        selection_sort(prices, reverse=True)
        return prices

    show("selection_sort(prices, reverse=True)", selection_numbers, [1299, 399, 59, 59, 5])
    show("返回值和 list.sort 一样是 None", lambda: insertion_sort([3, 1, 2]), None)
