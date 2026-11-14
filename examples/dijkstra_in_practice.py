"""第 16 课实战：Python 项目里最短路真正是怎么写的。

标准库没有现成的 Dijkstra，但 dict 存图 + heapq 做优先队列，二三十行就够：
- 图用 dict 套 dict：{站点: {邻站: 分钟数}}，查某条边 O(1)，节点直接用站名。
- 堆里放 (距离, 序号, 节点)：序号避免距离相同时去比较节点。
- 记 previous 表就能复原整条路线，不只是一个数字。
- 要的是“按远近一个个来、够了就停”时，写成生成器，配合 itertools.takewhile。
图特别大、或要 A*、多源、K 短路这类变体时，再考虑 networkx 或专门的路网引擎。

运行：uv run examples/dijkstra_in_practice.py
"""

import heapq
from itertools import count, takewhile

SEGMENTS = [  # (起点, 终点, 分钟)，双向
    ("人民广场", "南京西路", 2), ("南京西路", "静安寺", 2), ("人民广场", "陆家嘴", 6),
    ("陆家嘴", "世纪大道", 3), ("静安寺", "世纪大道", 14), ("人民广场", "世纪大道", 11),
    ("世纪大道", "龙阳路", 5), ("静安寺", "徐家汇", 6), ("徐家汇", "龙阳路", 13),
]


def build_network(segments: list[tuple[str, str, int]]) -> dict[str, dict[str, int]]:
    network: dict[str, dict[str, int]] = {}
    for start, end, minutes in segments:
        network.setdefault(start, {})[end] = minutes
        network.setdefault(end, {})[start] = minutes
    return network


def stations_by_travel_time(network: dict[str, dict[str, int]], origin: str):
    """按到达时间从早到晚 yield (站名, 分钟数, 路线)。调用方拿够了就可以停。"""
    best_minutes = {origin: 0}
    previous: dict[str, str] = {}
    finished: set[str] = set()
    sequence = count()
    heap = [(0, next(sequence), origin)]
    while heap:
        minutes, _, station = heapq.heappop(heap)
        if station in finished:  # 过期记录：这个站早就以更短的时间确定了
            continue
        finished.add(station)
        route = [station]
        while route[-1] != origin:
            route.append(previous[route[-1]])
        yield station, minutes, route[::-1]
        for neighbor, segment_minutes in network.get(station, {}).items():
            arrival = minutes + segment_minutes
            if arrival < best_minutes.get(neighbor, float("inf")):
                best_minutes[neighbor] = arrival
                previous[neighbor] = station
                heapq.heappush(heap, (arrival, next(sequence), neighbor))


def plan_route(network: dict[str, dict[str, int]], origin: str, destination: str) -> tuple[int, list[str]] | None:
    """场景一：起点到终点最快的路线。终点一确定就停，不算整张图。"""
    for station, minutes, route in stations_by_travel_time(network, origin):
        if station == destination:
            return minutes, route
    return None


def reachable_within(network: dict[str, dict[str, int]], origin: str, budget: int) -> list[str]:
    """场景二：“通勤 10 分钟以内能住哪些站”。按远近来，超过预算就停。"""
    nearby = takewhile(lambda item: item[1] <= budget, stations_by_travel_time(network, origin))
    return [station for station, _, _ in nearby]


def main() -> None:
    network = build_network(SEGMENTS)

    minutes, route = plan_route(network, "静安寺", "龙阳路")
    assert (minutes, route) == (18, ["静安寺", "南京西路", "人民广场", "陆家嘴", "世纪大道", "龙阳路"])
    print(f"静安寺 → 龙阳路：{minutes} 分钟，{' → '.join(route)}")

    assert plan_route(network, "静安寺", "虹桥机场") is None

    nearby = reachable_within(network, "人民广场", 10)
    assert nearby == ["人民广场", "南京西路", "静安寺", "陆家嘴", "世纪大道", "徐家汇"]
    print("人民广场 10 分钟内能到：", "、".join(nearby))


if __name__ == "__main__":
    main()
