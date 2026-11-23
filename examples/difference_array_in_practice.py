"""第 41 课实战：差分数组在真实代码里出现在哪。

1. 酒店每晚住了多少间房：每张订单是“入住日到离店前一晚都 +1”，
   全部订单记成差分，再用 itertools.accumulate 一次还原。
2. 同一时刻最多有几个会议在开（要几间会议室）：时间戳很大、很稀疏，开不了长度为“最大时间戳”的数组。
   这时把差分存在 dict 里，只记“哪个时刻变化了多少”，按时刻排序后累加，这种写法也叫扫描线。
3. 批量调价：几十条“第 a～b 号商品统一涨 / 降 x 元”的规则，一次性应用到价格表上。

运行：uv run examples/difference_array_in_practice.py
"""

from collections import defaultdict
from datetime import date, timedelta
from itertools import accumulate


def nightly_occupancy(bookings: list[tuple[date, date]], first_night: date, night_count: int) -> list[int]:
    """场景一：bookings 里每项是 (入住日, 离店日)。返回从 first_night 起每晚住着几间房。"""
    difference = [0] * (night_count + 1)  # 多一格，接住“最后一晚之后”的减回去
    for check_in, check_out in bookings:
        difference[(check_in - first_night).days] += 1
        difference[(check_out - first_night).days] -= 1  # 离店那晚已经不住了：第 41 课的 right + 1
    return list(accumulate(difference[:night_count]))


def rooms_needed(meetings: list[tuple[int, int]]) -> int:
    """场景二：meetings 里每项是 (开始时间戳, 结束时间戳)，单位秒。返回同一时刻最多有几个会议在开。"""
    change_at = defaultdict(int)  # 时刻 → 这一刻在开的会议数变化多少
    for start, end in meetings:
        change_at[start] += 1
        change_at[end] -= 1  # 结束时刻已经不占房间
    # 同一时刻先结束再开始：dict 里同一时刻的 +1 和 -1 已经合并成一个数，自然满足
    return max(accumulate(change for _, change in sorted(change_at.items())), default=0)


def apply_price_rules(prices: list[int], rules: list[tuple[int, int, int]]) -> list[int]:
    """场景三：rules 里每项是 (第一个商品下标, 最后一个商品下标, 调价金额)，两端都包含。"""
    difference = [0] * (len(prices) + 1)
    for first, last, change in rules:
        difference[first] += change
        difference[last + 1] -= change
    return [price + adjustment for price, adjustment in zip(prices, accumulate(difference))]


def main() -> None:
    first_night = date(2026, 12, 24)
    bookings = [
        (date(2026, 12, 24), date(2026, 12, 27)),  # 住 24、25、26 三晚
        (date(2026, 12, 25), date(2026, 12, 26)),  # 只住 25 晚
        (date(2026, 12, 25), date(2026, 12, 28)),  # 住 25、26、27 三晚
    ]
    occupancy = nightly_occupancy(bookings, first_night, 5)
    assert occupancy == [1, 3, 2, 1, 0]
    busiest = max(range(5), key=lambda night: occupancy[night])
    assert first_night + timedelta(days=busiest) == date(2026, 12, 25)
    print("每晚入住：", occupancy, "，最忙的一晚：", first_night + timedelta(days=busiest))

    hour = 3600
    meetings = [
        (1_767_225_600, 1_767_225_600 + hour),          # 9:00～10:00
        (1_767_225_600 + hour // 2, 1_767_225_600 + 2 * hour),  # 9:30～11:00
        (1_767_225_600 + hour, 1_767_225_600 + 3 * hour),       # 10:00～12:00：9:00 那个刚好结束
    ]
    assert rooms_needed(meetings) == 2
    assert rooms_needed([]) == 0
    print("至少要几间会议室：", rooms_needed(meetings))

    prices = [3, 1, 4, 1, 5, 9, 2, 6]  # 和讲解页的主线例子同一个数组
    adjusted = apply_price_rules(prices, [(2, 5, 2), (4, 7, 3)])
    assert adjusted == [3, 1, 6, 3, 10, 14, 5, 9]
    print("调价后：", adjusted)


if __name__ == "__main__":
    main()
