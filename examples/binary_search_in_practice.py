"""第 6 课实战：Python 项目里“二分查找”真正是怎么写的。

几乎没人手写二分。按场景选：
1. 有序列表里找位置、数个数、分档 → 标准库 bisect.bisect_left / bisect_right，3.10 起支持 key=。
2. 往有序列表里插入并保持有序 → bisect.insort。查 O(log n)，但插入要挪元素 O(n)；改得多就换 sortedcontainers。
3. “在答案上二分”（第一个坏版本、最少几台机器）→ 对 range 用 bisect + key，不用自己写循环。
4. 只查一次、数据没排序 → 直接 in / list.index，O(n) 反而比先排序更快。

运行：uv run examples/binary_search_in_practice.py
"""

import bisect
from dataclasses import dataclass
from datetime import datetime


def grade(score: int, cutoffs=(60, 70, 80, 90), grades="FDCBA") -> str:
    """场景一：分数分档，官方文档里的经典例子。"""
    return grades[bisect.bisect_right(cutoffs, score)]


@dataclass
class LogLine:
    at: datetime
    message: str


def logs_between(logs: list[LogLine], start: datetime, end: datetime) -> list[LogLine]:
    """场景二：日志按时间排好序，取 [start, end) 这一段。key 让我们不用另建一个时间列表。"""
    first = bisect.bisect_left(logs, start, key=lambda line: line.at)
    last = bisect.bisect_left(logs, end, key=lambda line: line.at)
    return logs[first:last]


def first_broken(versions: range, is_broken) -> int | None:
    """场景三：第一个坏版本。range 支持下标访问，bisect 直接在它上面二分，不会生成整个列表。"""
    position = bisect.bisect_left(versions, True, key=is_broken)
    return versions[position] if position < len(versions) else None


def main() -> None:
    assert [grade(score) for score in [33, 99, 77, 70, 89, 90, 100]] == ["F", "A", "C", "C", "B", "A", "A"]
    print("分档：", [grade(score) for score in [33, 99, 77, 70, 89, 90, 100]])

    logs = [LogLine(datetime(2026, 11, 10, hour, minute), text) for hour, minute, text in [
        (9, 0, "启动"), (9, 15, "登录"), (10, 2, "下单"), (10, 40, "支付"), (11, 5, "退出"),
    ]]
    window = logs_between(logs, datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
    assert [line.message for line in window] == ["下单", "支付"]
    print("10 点到 11 点的日志：", [line.message for line in window])

    leaderboard = [12, 30, 30, 55]
    bisect.insort(leaderboard, 31)
    assert leaderboard == [12, 30, 30, 31, 55]
    count_30 = bisect.bisect_right(leaderboard, 30) - bisect.bisect_left(leaderboard, 30)
    assert count_30 == 2
    print("插入 31 后：", leaderboard, "，30 分的有", count_30, "人")

    checks = []

    def is_broken(version: int) -> bool:
        checks.append(version)  # 真实场景里每次检查都要跑一遍测试，很贵
        return version >= 4217

    assert first_broken(range(1, 10_000), is_broken) == 4217
    assert len(checks) <= 14
    print("第一个坏版本：4217，只检查了", len(checks), "次")

    servers = bisect.bisect_left(range(1_000), True, key=lambda count: count * 400 >= 12345)
    assert servers == 31
    print("扛住 12345 QPS 最少要", servers, "台")


if __name__ == "__main__":
    main()
