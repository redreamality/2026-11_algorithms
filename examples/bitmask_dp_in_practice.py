"""第 44 课实战：状压 DP 在业务代码里长什么样。

状压 DP 的标志是“状态里要记住一个小集合”（哪些点去过、哪些单分出去了），而集合只有十几个元素。
真实代码里一般这样选：
1. n ≤ 8：直接 itertools.permutations 枚举所有顺序（8! = 40320），最不容易写错。
2. n 在 10～16：状压 DP。用一个整数 visited_mask 表示集合，配 functools.cache 写递归。
3. n 再大：精确解算不动了。分配问题换匈牙利算法（scipy.optimize.linear_sum_assignment，O(n³)），
   路线问题换启发式求近似解（Google OR-Tools）。这两个库本课程不装。

运行：uv run examples/bitmask_dp_in_practice.py
"""

import math
from functools import cache
from itertools import permutations


def assign_orders(riders: list[str], orders: list[str], minutes: list[list[int]]) -> tuple[int, dict[str, str]]:
    """场景一：n 个骑手接 n 单，minutes[r][o] = 骑手 r 送订单 o 要几分钟。总时间最少怎么分？

    返回 (最少总分钟数, {骑手: 订单})。
    best_from(assigned_mask) = 订单集合 assigned_mask 已经分出去后，剩下的骑手最少还要花多少分钟。
    分出去几单，就说明前几个骑手已经安排好：下一个骑手是 assigned_mask.bit_count()。
    """
    count = len(riders)
    everything = (1 << count) - 1

    @cache
    def best_from(assigned_mask: int) -> int:
        if assigned_mask == everything:
            return 0
        rider = assigned_mask.bit_count()
        return min(
            minutes[rider][order] + best_from(assigned_mask | (1 << order))
            for order in range(count)
            if not (assigned_mask >> order) & 1
        )

    plan = {}
    assigned_mask = 0
    while assigned_mask != everything:  # 倒推：每一步选让总时间等于最优值的那一单
        rider = assigned_mask.bit_count()
        for order in range(count):
            if not (assigned_mask >> order) & 1 and \
                    minutes[rider][order] + best_from(assigned_mask | (1 << order)) == best_from(assigned_mask):
                plan[riders[rider]] = orders[order]
                assigned_mask |= 1 << order
                break
    return best_from(0), plan


def assign_orders_by_permutations(minutes: list[list[int]]) -> int:
    """n ≤ 8 时的最省事写法：把“第 r 个骑手送第 order[r] 单”的所有排列都试一遍。"""
    count = len(minutes)
    return min(sum(minutes[rider][order[rider]] for rider in range(count)) for order in permutations(range(count)))


def plan_delivery_route(places: list[str], distance: list[list[int]], *, return_to_start: bool = True) -> tuple[int, list[str]]:
    """场景二：骑手从 places[0]（配送站）出发，每个点送一次，最短怎么走？

    return_to_start=False 时送完最后一单就下班，不用回站（只是终点的处理不同）。
    rest_of_trip(visited_mask, here) = 已经去过 visited_mask 里的点、现在在 here，走完剩下的点最少还要多远。
    """
    count = len(places)
    everything = (1 << count) - 1

    @cache
    def rest_of_trip(visited_mask: int, here: int) -> int:
        if visited_mask == everything:
            return distance[here][0] if return_to_start else 0
        best = math.inf
        for next_place in range(count):
            if not (visited_mask >> next_place) & 1:
                best = min(best, distance[here][next_place] + rest_of_trip(visited_mask | (1 << next_place), next_place))
        return best

    route = [0]
    visited_mask = 1
    while visited_mask != everything:  # 倒推：下一站选让剩余路程等于最优值的那个点
        here = route[-1]
        for next_place in range(count):
            if not (visited_mask >> next_place) & 1 and distance[here][next_place] + \
                    rest_of_trip(visited_mask | (1 << next_place), next_place) == rest_of_trip(visited_mask, here):
                route.append(next_place)
                visited_mask |= 1 << next_place
                break
    if return_to_start:
        route.append(0)
    return rest_of_trip(1, 0), [places[index] for index in route]


def main() -> None:
    riders = ["小王", "小李", "小张"]
    orders = ["奶茶", "快餐", "鲜花"]
    minutes = [[9, 2, 7], [6, 4, 3], [5, 8, 1]]
    total, plan = assign_orders(riders, orders, minutes)
    assert (total, plan) == (9, {"小王": "快餐", "小李": "奶茶", "小张": "鲜花"})
    assert assign_orders_by_permutations(minutes) == 9
    print("骑手分单：共", total, "分钟，", plan)

    places = ["配送站", "东门", "图书馆", "南门"]
    distance = [[0, 2, 9, 10], [2, 0, 6, 4], [9, 6, 0, 3], [10, 4, 3, 0]]
    length, route = plan_delivery_route(places, distance)
    assert length == 18 and route in (["配送站", "东门", "南门", "图书馆", "配送站"],
                                      ["配送站", "图书馆", "南门", "东门", "配送站"])
    print("配送路线：", " → ".join(route), "共", length)

    length, route = plan_delivery_route(places, distance, return_to_start=False)
    assert (length, route) == (9, ["配送站", "东门", "南门", "图书馆"])
    print("送完不回站：", " → ".join(route), "共", length)

    # 12 个点：枚举要 11! ≈ 4000 万条路线，状压只有 2^12 × 12 ≈ 5 万个状态
    many_places = [f"点{index}" for index in range(12)]
    grid_distance = [[abs(first % 4 - second % 4) + abs(first // 4 - second // 4) for second in range(12)]
                     for first in range(12)]
    length, route = plan_delivery_route(many_places, grid_distance)
    assert length == 12 and len(route) == 13
    print("12 个点围成 3×4 的格子：最短一圈", length)


if __name__ == "__main__":
    main()
