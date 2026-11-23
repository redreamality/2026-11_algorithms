"""第 46 课：最短路变种（0-1 BFS、Floyd-Warshall、Bellman-Ford）。讲解见 lessons/46-shortest-path-variants.html

实际项目里怎么写见 examples/shortest_path_variants_in_practice.py。

规则：
- graph 和第 16 课一样是 dict 套 dict：{点: {邻点: 权重, ...}}，表示一条单向边。无向图两个方向各存一条。
  有的点只出现在别人的邻居里、自己不是 graph 的键，当作它没有出边（用 graph.get(node, {})）。
  graph 里没有自环（u 到 u 的边）。
- 单源的函数（zero_one_bfs、bellman_ford）：走不到的点不出现在结果里，调用方用 distances.get(node, math.inf)。
- 全源的 floyd_warshall 返回一张填满的表：table[u][v] 对所有点 u、v 都有值，走不到的是 math.inf，
  table[u][u] 是 0。“所有点”= graph 的键 + 只出现在邻居里的点。
- 0-1 BFS 只用 collections.deque，不用 heapq；Floyd 只用三重循环。
- 不要改动传进来的 graph / grid。V 是点数，E 是边数。

写完后运行 uv run dsa/shortest_path_variants.py，看端到端的例子是否和期望一致；
再跑 uv run pytest tests/test_shortest_path_variants.py。
"""

from collections.abc import Hashable, Mapping

# 类型别名：{点: {邻点: 权重}}
Graph = Mapping[Hashable, Mapping[Hashable, float]]


def zero_one_bfs(graph: Graph, source) -> dict:
    """边权只有 0 和 1 时的单源最短路，返回 {点: 最短距离}（source 是 0）。

    碰到不是 0 也不是 1 的权重，抛 ValueError。
    做法：deque 里放 (距离, 点)。从队头取出一个点；走 0 边变短的邻居放回队头（appendleft），
    走 1 边变短的邻居放到队尾（append）。同一个点可能进队好几次，取出时已经确定过的就跳过。
    O(V + E)。
    """
    raise NotImplementedError


def min_walls_to_break(grid: list[str]) -> int:
    """网格里 "." 是空地，"#" 是墙。从左上角走到右下角，上下左右走，最少要打穿几堵墙。（LeetCode 2290 的字符版）

    走进一格空地代价 0，走进一格墙代价 1（打穿它）；起点自己不算。
    网格至少 1 行 1 列，每行一样长。例子：
        ".#."
        "##."
        "..."
    → 1（起点右边和下边都是墙，至少打穿一堵；打穿 (0, 1) 后沿右边走下来就不用再打）。
    这就是一张边权只有 0/1 的隐式图（第 35 课），用 0-1 BFS。O(行数 × 列数)。
    """
    raise NotImplementedError


def floyd_warshall(graph: Graph) -> dict:
    """全源最短路：返回 table，table[u][v] 是 u 到 v 的最短距离（走不到是 math.inf，table[u][u] 是 0）。

    允许负权边；有负环（绕一圈总和 < 0）时最短路没有意义，抛 ValueError。
    判断办法：三重循环跑完后，某个 table[u][u] < 0。
    三重循环里中转点 k 必须在最外层。O(V³)，适合 V 不超过几百的图。
    """
    raise NotImplementedError


def bellman_ford(graph: Graph, source) -> dict:
    """允许负权边的单源最短路，返回 {点: 最短距离}（走不到的点不出现）。

    做法：把所有边松弛 V - 1 轮（某一轮什么都没变就可以提前停）；
    再松弛一轮，还有边能让距离变短，说明 source 能走到一个负环，抛 ValueError。
    O(V × E)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    import math

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        except ValueError as error:
            actual = f"ValueError({error})"
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 主线例子：五座城之间的路，收费路权重 1（过一次收费站），免费路权重 0。双向。
    def toll_roads():
        roads = [("A", "B", 1), ("A", "C", 0), ("C", "B", 0), ("B", "D", 1), ("C", "E", 1), ("D", "E", 0)]
        graph: dict[str, dict[str, int]] = {}
        for start, end, toll in roads:
            graph.setdefault(start, {})[end] = toll
            graph.setdefault(end, {})[start] = toll
        return graph

    show("从 A 出发，到各城最少过几次收费站（0-1 BFS）", lambda: zero_one_bfs(toll_roads(), "A"),
         {"A": 0, "C": 0, "B": 0, "E": 1, "D": 1})
    show("任意两城之间最少过几次收费站，看 D 这一行（Floyd）", lambda: floyd_warshall(toll_roads())["D"],
         {"A": 1, "B": 1, "C": 1, "D": 0, "E": 0})
    show("地图打穿最少几堵墙", lambda: min_walls_to_break([".#..", "##.#", "#..#", "###."]), 2)
    show("有一条不用打墙的路", lambda: min_walls_to_break(["..#", "#.#", "#.."]), 0)
    show("有一条负权边（C 到 B 返现 2，Dijkstra 会把 D 算成 3）",
         lambda: bellman_ford({"A": {"B": 2, "C": 3}, "C": {"B": -2}, "B": {"D": 1}}, "A"),
         {"A": 0, "B": 1, "C": 3, "D": 2})
    show("Floyd 里走不到的格子是 math.inf", lambda: floyd_warshall({"A": {"B": 5}})["B"]["A"], math.inf)
