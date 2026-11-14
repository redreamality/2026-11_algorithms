"""第 7 课实战：Python 项目里“排序”真正是怎么写的。

业务代码里排序一律用内置的 sorted() / list.sort()（Timsort：稳定，O(n log n)，近乎有序时接近 O(n)）。
要会的是怎么“用好”它：
1. 按字段排 → key=operator.itemgetter / attrgetter 或 lambda。
2. 多个字段、方向不同 → 利用稳定性分两趟排（先次要、后主要），或者数字字段取负号拼成元组。
3. 只要返回新列表、不改原数据 → sorted()；就地排、省内存 → list.sort()，返回 None。
4. 不区分大小写、按自然语言习惯 → key=str.casefold。

运行：uv run examples/simple_sorts_in_practice.py
"""

from dataclasses import dataclass
from datetime import date
from operator import attrgetter, itemgetter


@dataclass
class Ticket:
    id: int
    priority: int
    created: date


def triage(tickets: list[Ticket]) -> list[int]:
    """场景一：工单按“优先级从高到低，同优先级按创建日期从早到晚”。两趟稳定排序，不用拼复杂的 key。"""
    ordered = sorted(tickets, key=attrgetter("created"))
    ordered.sort(key=attrgetter("priority"), reverse=True)
    return [ticket.id for ticket in ordered]


def triage_one_pass(tickets: list[Ticket]) -> list[int]:
    """同样的需求一趟写完：数字字段可以取负号反向，元组按字段依次比较。"""
    return [ticket.id for ticket in sorted(tickets, key=lambda ticket: (-ticket.priority, ticket.created))]


def main() -> None:
    tickets = [
        Ticket(101, 2, date(2026, 11, 3)),
        Ticket(102, 3, date(2026, 11, 5)),
        Ticket(103, 2, date(2026, 11, 1)),
        Ticket(104, 3, date(2026, 11, 2)),
        Ticket(105, 1, date(2026, 11, 4)),
    ]
    assert triage(tickets) == triage_one_pass(tickets) == [104, 102, 103, 101, 105]
    print("工单处理顺序：", triage(tickets))

    rows = [{"name": "小红", "score": 90}, {"name": "小明", "score": 80}, {"name": "小刚", "score": 90}]
    ranked = sorted(rows, key=itemgetter("score"), reverse=True)
    assert [row["name"] for row in ranked] == ["小红", "小刚", "小明"]  # reverse 也稳定：小红仍在小刚前
    assert rows[0]["name"] == "小红"  # sorted 不改原列表
    print("成绩排名：", [row["name"] for row in ranked])

    files = ["readme.md", "Makefile", "app.py", "Dockerfile"]
    assert sorted(files) == ["Dockerfile", "Makefile", "app.py", "readme.md"]  # 默认大写字母排在前面
    assert sorted(files, key=str.casefold) == ["app.py", "Dockerfile", "Makefile", "readme.md"]
    print("不区分大小写：", sorted(files, key=str.casefold))

    prices = [399, 59, 1299, 5]
    assert prices.sort() is None  # 就地排序返回 None，别写 prices = prices.sort()
    assert prices == [5, 59, 399, 1299]
    print("就地排好的价格：", prices)


if __name__ == "__main__":
    main()
