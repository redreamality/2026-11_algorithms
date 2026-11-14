"""第 32 课实战：Python 项目里“二分”真正是怎么写的。

1. 在有序记录里找边界（某段时间内的日志、某个分数段的人）→ 标准库 bisect。
   Python 3.10 起 bisect_left / bisect_right 支持 key=，可以直接对对象列表按字段二分，
   不用另外抽一个键列表。bisect_left 就是本课的“第一个 >= target”，bisect_right 是“第一个 > target”。
2. “最少要多少资源才能按时完成”（几台机器、多大带宽、多大批次）→ 二分答案：
   答案越大越容易满足，满足条件的答案是一段连续的右半边，找它的第一个位置。
3. “从哪个版本开始坏的”→ git bisect 的思路：版本从好变坏只变一次，二分找第一个坏版本，
   每一步要跑一次很贵的检查，所以 O(log n) 次检查比逐个试省很多。

运行：uv run examples/binary_search_advanced_in_practice.py
"""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass


@dataclass(frozen=True)
class LogEntry:
    timestamp: int  # 秒
    message: str


def entries_between(log: list[LogEntry], start: int, end: int) -> list[LogEntry]:
    """log 已按时间排好序，取 start <= 时间 <= end 的那一段。两次二分，O(log n + 结果个数)。"""
    first = bisect_left(log, start, key=lambda entry: entry.timestamp)
    after_last = bisect_right(log, end, key=lambda entry: entry.timestamp)
    return log[first:after_last]


def first_true(low: int, high: int, condition) -> int:
    """[low, high] 里第一个让 condition 成立的整数。约定 condition(high) 一定成立，且成立的是一段右半边。"""
    while low < high:
        middle = (low + high) // 2
        if condition(middle):
            high = middle
        else:
            low = middle + 1
    return low


def busiest_machine_minutes(job_minutes: list[int], workers: int) -> int:
    """把任务按顺序分给 workers 台机器（每台一段连续的任务），让最忙那台尽量闲，返回它要跑几分钟。

    也是二分答案：给定上限 limit，贪心地往一台机器上装，装不下就换下一台，看机器够不够用。
    """
    if workers <= 0:
        raise ValueError("workers must be positive")

    def fits(limit: int) -> bool:
        machines_used, current_load = 1, 0
        for minutes in job_minutes:
            if current_load + minutes > limit:
                machines_used += 1
                current_load = 0
            current_load += minutes
        return machines_used <= workers

    return first_true(max(job_minutes), sum(job_minutes), fits)


def min_workers(job_minutes: list[int], deadline_minutes: int) -> int:
    """容量规划：至少要几台机器，才能让最忙的那台在 deadline 内跑完。机器越多越容易满足，二分机器数。"""
    if max(job_minutes) > deadline_minutes:
        raise ValueError("单个任务就超过了截止时间，加机器也没用")
    return first_true(1, len(job_minutes),
                      lambda workers: busiest_machine_minutes(job_minutes, workers) <= deadline_minutes)


def first_bad_version(versions: list[str], is_bad) -> str | None:
    """git bisect 的思路：versions 从旧到新，从某个版本开始一直是坏的。返回第一个坏版本，全好返回 None。"""
    index = first_true(0, len(versions), lambda position: position == len(versions) or is_bad(versions[position]))
    return versions[index] if index < len(versions) else None


def main() -> None:
    log = [LogEntry(t, m) for t, m in [
        (100, "启动"), (130, "登录"), (130, "查询"), (175, "下单"), (240, "支付"), (300, "退出"),
    ]]
    window = entries_between(log, 130, 240)
    assert [entry.message for entry in window] == ["登录", "查询", "下单", "支付"]  # 两端都包含
    assert entries_between(log, 301, 400) == []
    print("130～240 秒的日志：", [entry.message for entry in window])

    jobs = [30, 20, 50, 10, 40, 30, 20]  # 每个任务要跑几分钟，必须按顺序分段分给机器
    assert busiest_machine_minutes(jobs, 1) == 200
    assert busiest_machine_minutes(jobs, 3) == 90  # 最优分法之一：[30, 20] [50, 10] [40, 30, 20]
    assert min_workers(jobs, 90) == 3
    assert min_workers(jobs, 50) == 4  # 以上期望值都用仓库外的暴力枚举核对过
    print("要在 90 分钟内跑完，至少需要机器：", min_workers(jobs, 90))

    versions = [f"v1.{minor}" for minor in range(20)]
    checked = []

    def is_bad(version: str) -> bool:
        checked.append(version)  # 真实场景里这一步是“编译 + 跑测试”，很贵
        return int(version.split(".")[1]) >= 13

    assert first_bad_version(versions, is_bad) == "v1.13"
    assert len(checked) <= 5  # 20 个版本，二分最多检查 5 次
    assert first_bad_version(versions, lambda version: False) is None
    print(f"第一个坏版本：v1.13，只检查了 {len(checked)} 个版本：{checked}")


if __name__ == "__main__":
    main()
