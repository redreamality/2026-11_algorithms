"""第 46 课实战：最短路的三个变种在真实代码里怎么用。

1. 0-1 BFS：地铁“最少换乘”。把 (站, 线路) 当成一个点：坐同一条线到下一站代价 0，
   在同一站换到别的线代价 1。边权只有 0/1，用 collections.deque 头插尾插，O(V + E)，不用堆。
2. Floyd-Warshall：配送站之间的“距离表”。点只有几十个，一次 O(n³) 把任意两点的最短距离
   和“下一跳”都算好，之后每次查询 O(1)，还能复原路线。
3. Bellman-Ford：汇率套利检测。把汇率 rate 换成边权 -log(rate)，
   “乘起来大于 1 的一圈兑换”就变成“加起来小于 0 的一圈”，也就是负环。

图更大或者要更多功能时用 networkx（本项目不引入）。

运行：uv run examples/shortest_path_variants_in_practice.py
"""

import math
from collections import deque

# ---------- 1. 0-1 BFS：最少换乘 ----------

LINES = {  # 线路 -> 按顺序经过的站
    "1号线": ["莘庄", "徐家汇", "人民广场", "上海火车站"],
    "2号线": ["静安寺", "南京西路", "人民广场", "陆家嘴", "世纪大道"],
    "9号线": ["徐家汇", "世纪大道"],
}


def fewest_transfers(lines: dict[str, list[str]], origin: str, destination: str) -> int | None:
    """从 origin 到 destination 最少换乘几次；到不了返回 None。"""
    lines_at_station: dict[str, list[str]] = {}
    for line, stations in lines.items():
        for station in stations:
            lines_at_station.setdefault(station, []).append(line)

    def neighbors(state):
        """yield (下一个状态, 代价)。状态是 (站, 正在坐的线)。"""
        station, line = state
        stations = lines[line]
        position = stations.index(station)
        for next_position in (position - 1, position + 1):
            if 0 <= next_position < len(stations):
                yield (stations[next_position], line), 0      # 坐一站：不算换乘
        for other_line in lines_at_station[station]:
            if other_line != line:
                yield (station, other_line), 1                # 站内换乘：算一次

    best = {}
    queue = deque()
    for line in lines_at_station.get(origin, []):             # 起点站的每条线都可以直接上车
        best[(origin, line)] = 0
        queue.append((0, (origin, line)))
    finished = set()
    while queue:
        transfers, state = queue.popleft()
        if state in finished:
            continue
        finished.add(state)
        if state[0] == destination:                           # 第一次取出终点站：就是最少换乘
            return transfers
        for next_state, cost in neighbors(state):
            candidate = transfers + cost
            if candidate < best.get(next_state, math.inf):
                best[next_state] = candidate
                if cost == 0:
                    queue.appendleft((candidate, next_state))
                else:
                    queue.append((candidate, next_state))
    return None


# ---------- 2. Floyd：距离表 + 下一跳 ----------

ROADS = [  # (配送站, 配送站, 公里)，双向
    ("仓库", "东站", 4), ("仓库", "西站", 2), ("西站", "东站", 1),
    ("东站", "北站", 5), ("西站", "北站", 8), ("北站", "南站", 3),
]


def distance_table(roads: list[tuple[str, str, float]]):
    """返回 (distance, next_hop)：distance[u][v] 最短公里数，next_hop[u][v] 是从 u 去 v 第一步走到哪。"""
    sites = sorted({site for start, end, _ in roads for site in (start, end)})
    distance = {u: {v: (0 if u == v else math.inf) for v in sites} for u in sites}
    next_hop = {u: {v: (v if u == v else None) for v in sites} for u in sites}
    for start, end, kilometers in roads:
        for u, v in ((start, end), (end, start)):
            distance[u][v] = kilometers
            next_hop[u][v] = v
    for middle in sites:                                      # 中转点放在最外层
        for u in sites:
            for v in sites:
                through_middle = distance[u][middle] + distance[middle][v]
                if through_middle < distance[u][v]:
                    distance[u][v] = through_middle
                    next_hop[u][v] = next_hop[u][middle]      # 去 v 的第一步 = 去 middle 的第一步
    return distance, next_hop


def route(next_hop, start: str, end: str) -> list[str]:
    path = [start]
    while path[-1] != end:
        path.append(next_hop[path[-1]][end])
    return path


# ---------- 3. Bellman-Ford：套利检测 ----------

RATES = [  # (从, 到, 1 单位能换多少)
    ("USD", "EUR", 0.9), ("EUR", "GBP", 0.8), ("GBP", "USD", 1.4),   # 0.9 × 0.8 × 1.4 = 1.008 > 1
    ("USD", "JPY", 150.0), ("JPY", "USD", 0.0066),
]


def has_arbitrage(rates: list[tuple[str, str, float]]) -> bool:
    """存在一圈兑换下来钱变多的路线吗？等价于 -log(rate) 图里有负环。"""
    currencies = {currency for start, end, _ in rates for currency in (start, end)}
    edges = [(start, end, -math.log(rate)) for start, end, rate in rates]
    distance = {currency: 0.0 for currency in currencies}    # 全部从 0 出发 = 一个虚拟起点连到每种货币
    for _ in range(len(currencies) - 1):
        for start, end, weight in edges:
            if distance[start] + weight < distance[end] - 1e-12:
                distance[end] = distance[start] + weight
    return any(distance[start] + weight < distance[end] - 1e-12 for start, end, weight in edges)


def main() -> None:
    assert fewest_transfers(LINES, "静安寺", "陆家嘴") == 0
    assert fewest_transfers(LINES, "莘庄", "陆家嘴") == 1          # 1号线到人民广场换 2号线
    assert fewest_transfers(LINES, "莘庄", "世纪大道") == 1        # 1号线到徐家汇换 9号线（不用经过人民广场）
    assert fewest_transfers(LINES, "上海火车站", "南京西路") == 1
    assert fewest_transfers(LINES, "莘庄", "虹桥机场") is None
    print("莘庄 → 世纪大道 最少换乘", fewest_transfers(LINES, "莘庄", "世纪大道"), "次")

    distance, next_hop = distance_table(ROADS)
    assert distance["仓库"]["北站"] == 8
    assert route(next_hop, "仓库", "北站") == ["仓库", "西站", "东站", "北站"]
    assert distance["南站"]["仓库"] == 11
    assert route(next_hop, "南站", "仓库") == ["南站", "北站", "东站", "西站", "仓库"]
    print("仓库 → 北站：", distance["仓库"]["北站"], "公里，", " → ".join(route(next_hop, "仓库", "北站")))

    assert has_arbitrage(RATES)
    fair_rates = [(start, end, rate) for start, end, rate in RATES if (start, end) != ("GBP", "USD")]
    fair_rates.append(("GBP", "USD", 1.38))                    # 0.9 × 0.8 × 1.38 = 0.9936 < 1
    assert not has_arbitrage(fair_rates)
    print("USD → EUR → GBP → USD 一圈下来变成", round(0.9 * 0.8 * 1.4, 3), "倍：有套利")


if __name__ == "__main__":
    main()
