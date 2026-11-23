"""第 44 课：状压 DP。讲解见 lessons/44-bitmask-dp.html

实际项目里常用 functools.cache 写递归 best(visited_mask, ...)，再倒推出方案（骑手分单、配送路线，
完整例子见 examples/bitmask_dp_in_practice.py）。这里按笔试要求用填表写，练的是“用一个整数表示一个集合”。

规则：
- 位掩码（第 39 课）：mask 的第 k 位是 1，表示第 k 个元素在集合里。
  检查：(mask >> k) & 1；加入：mask | (1 << k)；去掉：mask ^ (1 << k)（前提是第 k 位原来是 1）；
  全集：(1 << n) - 1；集合里有几个元素：mask.bit_count()。
- 每道题动手前，先写下四步法的答案（第 37 课）：状态里的 mask 代表“哪些已经用过 / 访问过”。
- 用填表（自底向上）写，不要用 functools.cache / lru_cache。
- 变量名用完整的英文单词，例如 visited_mask、assigned_mask、next_city，不要写 res、tmp、cnt。
- 自查：uv run dsa/bitmask_dp.py；测试：uv run pytest tests/test_bitmask_dp.py
"""


def min_assignment_cost(cost: list[list[int]]) -> int:
    """分配任务：n 个骑手、n 个订单，cost[worker][task] = 第 worker 个骑手送第 task 单的花费。
    每个骑手正好送一单、每单正好一个人送，总花费最少是多少？

    例子：cost = [[9, 2, 7],
                  [6, 4, 3],
                  [5, 8, 1]]
          骑手 0 送单 1（2），骑手 1 送单 0（6），骑手 2 送单 2（1），总花费 9，返回 9。
          贪心地让每个骑手挑剩下最便宜的：2 + 3 + 5 = 10，不对。
          n = 0（空列表）返回 0。

    思路提示：
      状态：best[assigned_mask] = 骑手 0、1、……按顺序接单，订单集合 assigned_mask 已经分出去时的最少花费。
            分出去几单，就说明前几个骑手已经安排好了：一共 assigned_mask.bit_count() 个。
      转移：最后安排的是骑手 worker = assigned_mask.bit_count() - 1，他送的是集合里的某一单 task：
            best[assigned_mask] = min(best[assigned_mask ^ (1 << task)] + cost[worker][task]，task 在集合里)
      初始值：best[0] = 0（一单都没分，不花钱）。
      遍历顺序：mask 从 1 到 2^n - 1 从小到大。去掉一个元素后整数一定变小，所以用到的状态都已经算好。
      答案：best[(1 << n) - 1]。

    目标复杂度：O(2^n × n) 时间，O(2^n) 空间。n ≤ 20 都能跑。
    """
    raise NotImplementedError


def shortest_round_trip(distance: list[list[int]]) -> int:
    """旅行商问题（TSP）：从 0 号点（配送站）出发，每个点正好经过一次，最后回到 0 号点，最短要走多远？

    distance[a][b] = 从 a 到 b 的距离（不一定对称）。点数 n ≤ 15。
    例子：distance = [[0, 2, 9, 10],
                      [2, 0, 6, 4],
                      [9, 6, 0, 3],
                      [10, 4, 3, 0]]
          最短路线 0 → 1 → 3 → 2 → 0，长度 2 + 4 + 3 + 9 = 18，返回 18。
          只有一个点（只有配送站）时不用走，返回 0。

    思路提示：
      状态：shortest[visited_mask][last] = 从 0 出发，正好走过 visited_mask 里的点，现在停在 last，最短走了多远。
            visited_mask 一定包含 0 和 last。
      转移：上一步停在 previous（在 visited_mask 里、不是 last），
            shortest[visited_mask][last] = min(shortest[visited_mask ^ (1 << last)][previous] + distance[previous][last])
      初始值：shortest[1][0] = 0（只走过 0 号点，停在 0），其他是 math.inf。
      遍历顺序：visited_mask 从小到大。
      答案：所有点都走过后，从 last 回到 0：min(shortest[全集][last] + distance[last][0])。

    目标复杂度：O(2^n × n²) 时间，O(2^n × n) 空间。
    """
    raise NotImplementedError


def shortest_round_trip_route(distance: list[list[int]]) -> list[int]:
    """（选做）返回 shortest_round_trip 对应的一条路线，从 0 开始、回到 0 结束。

    例子：上面的 distance 返回 [0, 1, 3, 2, 0]（反方向 [0, 2, 3, 1, 0] 一样长，也算对）。
          只有一个点时返回 [0, 0]。
    思路提示：先把 shortest 表填满。从“全集、最后停在哪”开始倒推：
    每一步找一个 previous，使得 shortest[去掉 last 的集合][previous] + distance[previous][last]
    正好等于 shortest[当前集合][last]，它就是上一站。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def check(function, arguments, expected):
        """跑一个例子，打印「输入、期望、实际」。还没实现的函数会提示一下，不会让脚本中断。"""
        shown_input = ", ".join(repr(argument) for argument in arguments)
        try:
            actual = function(*arguments)
        except NotImplementedError:
            print(f"[未实现] {function.__name__}({shown_input})")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {function.__name__}({shown_input})  期望 {expected!r}，实际 {actual!r}")

    check(min_assignment_cost, ([[9, 2, 7], [6, 4, 3], [5, 8, 1]],), 9)
    check(min_assignment_cost, ([[4]],), 4)
    check(min_assignment_cost, ([],), 0)

    city_distance = [[0, 2, 9, 10], [2, 0, 6, 4], [9, 6, 0, 3], [10, 4, 3, 0]]
    check(shortest_round_trip, (city_distance,), 18)
    check(shortest_round_trip, ([[0, 5], [5, 0]],), 10)
    check(shortest_round_trip, ([[0]],), 0)

    def length_of_route(distance):
        """路线不止一条（正反方向一样长），所以检查倒推出来的路线总长对不对。"""
        route = shortest_round_trip_route(distance)
        return sum(distance[here][there] for here, there in zip(route, route[1:]))

    check(length_of_route, (city_distance,), 18)
    check(shortest_round_trip_route, ([[0]],), [0, 0])
