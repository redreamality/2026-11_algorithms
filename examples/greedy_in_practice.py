"""第 18 课实战：Python 项目里贪心真正是怎么写的。

贪心在业务代码里几乎从不“调库”，就是 sorted(..., key=...) 加一次遍历：
1. 排会议室 / 排任务 → 按结束时间排序，能放就放。
2. 合并时间段（日历忙闲、日志里的在线时段）→ 按开始时间排序，能接上就延长。
3. 找零、拆包、装箱 → 先拿最大的。只有在标准币制这种“已经证明贪心是对的”场景下才可以这么写，
   任意面值要换成 DP（第 19、20 课）。

运行：uv run examples/greedy_in_practice.py
"""

from collections import Counter
from datetime import time  # time(9, 30) 表示 9 点 30 分；time 对象之间可以直接用 <、<= 比先后
from operator import attrgetter
from typing import NamedTuple


class Booking(NamedTuple):
    title: str
    start: time
    end: time


def schedule_one_room(bookings: list[Booking]) -> list[Booking]:
    """一间会议室，尽量多接预约：按结束时间排序，和上一个不冲突就接。"""
    accepted: list[Booking] = []
    for booking in sorted(bookings, key=attrgetter("end")):
        if not accepted or accepted[-1].end <= booking.start:
            accepted.append(booking)
    return accepted


def free_slots(busy: list[tuple[time, time]], day_start: time, day_end: time) -> list[tuple[time, time]]:
    """先合并忙碌时段，再取它们之间的空档。"""
    merged: list[list[time]] = []
    for start, end in sorted(busy):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    slots = []
    cursor = day_start
    for start, end in merged:
        if cursor < start:
            slots.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < day_end:
        slots.append((cursor, day_end))
    return slots


def make_change_in_cents(amount_in_cents: int, denominations: tuple[int, ...] = (10000, 5000, 2000, 1000, 500, 100, 50, 10, 1)) -> Counter[int]:
    """收银找零（人民币，单位：分）。标准币制下贪心就是张数最少。divmod 一次算出每种面值拿几张。"""
    change: Counter[int] = Counter()
    remaining = amount_in_cents
    for value in sorted(denominations, reverse=True):
        count, remaining = divmod(remaining, value)
        if count:
            change[value] = count
    if remaining:
        raise ValueError(f"凑不出 {amount_in_cents} 分")
    return change


def main() -> None:
    bookings = [
        Booking("周会", time(9), time(12)),
        Booking("站会", time(9), time(10)),
        Booking("面试", time(10), time(11)),
        Booking("评审", time(11), time(13)),
        Booking("1:1", time(13), time(14)),
        Booking("培训", time(12), time(15)),
    ]
    accepted = schedule_one_room(bookings)
    assert [booking.title for booking in accepted] == ["站会", "面试", "评审", "1:1"]
    print("会议室接下的预约：", [booking.title for booking in accepted])

    busy = [(time(14), time(16)), (time(9), time(10)), (time(9, 30), time(11)), (time(15), time(17))]
    slots = free_slots(busy, time(9), time(18))
    assert slots == [(time(11), time(14)), (time(17), time(18))]
    # f-string 里的 :%H:%M 是给时间对象用的格式：按“时:分”打印，比如 11:00
    print("空闲时段：", [f"{start:%H:%M}-{end:%H:%M}" for start, end in slots])

    change = make_change_in_cents(18830)  # 188.30 元
    assert change == Counter({10000: 1, 5000: 1, 2000: 1, 1000: 1, 500: 1, 100: 3, 10: 3})
    print("找零 188.30 元：", {f"{value / 100:g} 元": count for value, count in sorted(change.items(), reverse=True)})

    # 反例：面值 [1, 3, 4] 凑 6，贪心拿 4+1+1 共 3 张，最优是 3+3 共 2 张。
    weird = make_change_in_cents(6, denominations=(1, 3, 4))
    assert sum(weird.values()) == 3
    print("面值 [1, 3, 4] 凑 6，贪心用了", sum(weird.values()), "张（最优是 2 张）")


if __name__ == "__main__":
    main()
