"""第 34 课实战：Python 项目里“区间”问题真正是怎么写的。

标准库没有现成的“区间合并”函数，但套路固定、几行就写完，关键是选对排序键：
1. 合并忙碌时段、求空闲时段 → 按开始时间 sorted，扫一遍合并，再取相邻两段之间的空隙。
2. 一个点落在哪个区间（IP 段归属、阶梯价格、时间段配置）→ 区间互不重叠时，
   把起点排好序，用 bisect 找“起点 <= 该点的最后一个区间”，再检查终点。查询 O(log n)。
3. 同时进行的最大数量（会议室、并发连接）→ heapq 维护“各自什么时候结束”。
4. 区间很多、还要频繁增删和查重叠 → 第三方库（如 portion、intervaltree），本项目不引入。

运行：uv run examples/intervals_in_practice.py
"""

import heapq
from bisect import bisect_right
from ipaddress import IPv4Address


def hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def parse(text: str) -> int:
    hours, minutes = text.split(":")
    return int(hours) * 60 + int(minutes)


def merge_busy(slots: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """把所有人的忙碌时段合并。端点相接（10:00 结束、10:00 开始）也并成一段。"""
    merged: list[tuple[int, int]] = []
    for start, end in sorted(slots):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def common_free_slots(busy: list[tuple[int, int]], day_start: int, day_end: int,
                      minimum_length: int) -> list[tuple[int, int]]:
    """工作时间内大家都有空、且不短于 minimum_length 分钟的时段。"""
    free_slots = []
    cursor = day_start
    for start, end in merge_busy(busy):
        if start - cursor >= minimum_length:
            free_slots.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= minimum_length:
        free_slots.append((cursor, day_end))
    return free_slots


def max_concurrent(meetings: list[tuple[int, int]]) -> int:
    """最多同时进行几场会议，也就是最少需要几间会议室。"""
    end_times: list[int] = []
    for start, end in sorted(meetings):
        if end_times and end_times[0] <= start:
            heapq.heappop(end_times)
        heapq.heappush(end_times, end)
    return len(end_times)


class IpRangeTable:
    """互不重叠的 IP 段 → 归属。查一个 IP 属于哪个段：bisect 找起点 <= 它的最后一段。"""

    def __init__(self, ranges: list[tuple[str, str, str]]) -> None:
        rows = sorted((int(IPv4Address(first)), int(IPv4Address(last)), owner) for first, last, owner in ranges)
        self._starts = [first for first, _, _ in rows]
        self._rows = rows

    def owner_of(self, address: str) -> str | None:
        value = int(IPv4Address(address))
        index = bisect_right(self._starts, value) - 1
        if index < 0:
            return None
        _, last, owner = self._rows[index]
        return owner if value <= last else None


def main() -> None:
    busy = [(parse(a), parse(b)) for a, b in [
        ("09:30", "10:00"), ("09:45", "11:00"),  # 小王和小李的会有重叠
        ("11:00", "11:30"),                      # 恰好接上
        ("13:00", "14:00"), ("15:30", "16:00"),
    ]]
    merged = merge_busy(busy)
    assert merged == [(parse("09:30"), parse("11:30")), (parse("13:00"), parse("14:00")),
                      (parse("15:30"), parse("16:00"))]
    print("合并后的忙碌时段：", [f"{hhmm(s)}-{hhmm(e)}" for s, e in merged])

    free = common_free_slots(busy, parse("09:00"), parse("18:00"), minimum_length=60)
    assert free == [(parse("11:30"), parse("13:00")), (parse("14:00"), parse("15:30")),
                    (parse("16:00"), parse("18:00"))]
    print("至少 1 小时的共同空闲：", [f"{hhmm(s)}-{hhmm(e)}" for s, e in free])

    assert max_concurrent(busy) == 2
    assert max_concurrent([(parse("09:00"), parse("10:00")), (parse("10:00"), parse("11:00"))]) == 1
    print("最少需要的会议室：", max_concurrent(busy))

    table = IpRangeTable([
        ("10.0.0.0", "10.0.255.255", "办公网"),
        ("10.1.0.0", "10.1.0.255", "测试机房"),
        ("192.168.1.0", "192.168.1.255", "访客 Wi-Fi"),
    ])
    assert table.owner_of("10.1.0.42") == "测试机房"
    assert table.owner_of("10.0.200.1") == "办公网"
    assert table.owner_of("10.1.1.1") is None  # 落在两段之间的空隙
    assert table.owner_of("1.1.1.1") is None   # 比第一段还小
    print("10.1.0.42 属于：", table.owner_of("10.1.0.42"))


if __name__ == "__main__":
    main()
