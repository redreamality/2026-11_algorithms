import copy
import math
import random

import pytest

from dsa.shortest_path_variants import bellman_ford, floyd_warshall, min_walls_to_break, zero_one_bfs


def undirected(*edges):
    graph = {}
    for start, end, weight in edges:
        graph.setdefault(start, {})[end] = weight
        graph.setdefault(end, {})[start] = weight
    return graph


# 讲解页的主线例子：收费路 1，免费路 0
TOLL = undirected(("A", "B", 1), ("A", "C", 0), ("C", "B", 0), ("B", "D", 1), ("C", "E", 1), ("D", "E", 0))


def brute_force(graph, source):
    """标准答案：反复松弛所有边直到不再变化（不能有负环）。"""
    distances = {source: 0}
    changed = True
    while changed:
        changed = False
        for start, edges in graph.items():
            for end, weight in edges.items():
                if start in distances and distances[start] + weight < distances.get(end, math.inf):
                    distances[end] = distances[start] + weight
                    changed = True
    return distances


def random_graph(rng, size, edge_count, weights):
    graph = {node: {} for node in range(size)}
    for _ in range(edge_count):
        start, end = rng.randrange(size), rng.randrange(size)
        if start != end:
            graph[start][end] = rng.choice(weights)
    return graph


# ---------- 0-1 BFS ----------

def test_zero_one_bfs_toll_roads():
    assert zero_one_bfs(TOLL, "A") == {"A": 0, "B": 0, "C": 0, "D": 1, "E": 1}


def test_zero_one_bfs_zero_edge_beats_earlier_one_edge():
    # 先从 A 走 1 边碰到 B（距离 1），后来经过 C 走 0 边把 B 改成 0
    graph = {"A": {"B": 1, "C": 0}, "C": {"B": 0}, "B": {"D": 0}}
    assert zero_one_bfs(graph, "A") == {"A": 0, "B": 0, "C": 0, "D": 0}


def test_zero_one_bfs_not_plain_bfs():
    # 普通 BFS 数边数会说 D 最近（1 条边），但那条边收费
    graph = {"S": {"D": 1, "X": 0}, "X": {"Y": 0}, "Y": {"D": 0}}
    assert zero_one_bfs(graph, "S")["D"] == 0


def test_zero_one_bfs_unreachable_and_neighbor_only_nodes():
    graph = {0: {1: 1}, 2: {3: 0}}  # 1 不是键
    assert zero_one_bfs(graph, 0) == {0: 0, 1: 1}
    assert zero_one_bfs({"lonely": {}}, "lonely") == {"lonely": 0}


def test_zero_one_bfs_rejects_other_weights():
    with pytest.raises(ValueError):
        zero_one_bfs({"A": {"B": 2}}, "A")


def test_zero_one_bfs_random_against_brute_force():
    rng = random.Random(46)
    for _ in range(50):
        graph = random_graph(rng, 9, 20, [0, 1])
        assert zero_one_bfs(graph, 0) == brute_force(graph, 0)


# ---------- 网格：最少打穿几堵墙 ----------

def test_min_walls_examples():
    assert min_walls_to_break([".#.", "##.", "..."]) == 1
    assert min_walls_to_break(["..#", "#.#", "#.."]) == 0
    assert min_walls_to_break([".#..", "##.#", "#..#", "###."]) == 2
    assert min_walls_to_break([".##", "###", "##."]) == 3


def test_min_walls_single_cell_and_single_row():
    assert min_walls_to_break(["."]) == 0
    assert min_walls_to_break([".#.#."]) == 2


def test_min_walls_detour_beats_breaking():
    # 直着走要打 1 堵墙，绕一大圈不用打
    grid = ["...",
            ".#.",
            "##.",
            "..."]
    assert min_walls_to_break(grid) == 0


def test_min_walls_random_against_brute_force():
    rng = random.Random(2290)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for _ in range(40):
        row_count, col_count = rng.randint(1, 6), rng.randint(1, 6)
        grid = ["".join(rng.choice(".#") for _ in range(col_count)) for _ in range(row_count)]
        grid[0] = "." + grid[0][1:]
        graph = {}
        for row in range(row_count):
            for col in range(col_count):
                for row_step, col_step in directions:
                    next_row, next_col = row + row_step, col + col_step
                    if 0 <= next_row < row_count and 0 <= next_col < col_count:
                        graph.setdefault((row, col), {})[(next_row, next_col)] = int(grid[next_row][next_col] == "#")
        before = list(grid)
        expected = brute_force(graph, (0, 0)).get((row_count - 1, col_count - 1), 0)
        assert min_walls_to_break(grid) == expected
        assert grid == before


# ---------- Floyd-Warshall ----------

def test_floyd_toll_roads_full_table():
    table = floyd_warshall(TOLL)
    expected_rows = {"A": [0, 0, 0, 1, 1], "B": [0, 0, 0, 1, 1], "C": [0, 0, 0, 1, 1],
                     "D": [1, 1, 1, 0, 0], "E": [1, 1, 1, 0, 0]}
    for start, row in expected_rows.items():
        assert [table[start][end] for end in "ABCDE"] == row


def test_floyd_fills_unreachable_with_inf():
    table = floyd_warshall({"A": {"B": 5}})  # B 只出现在邻居里
    assert table == {"A": {"A": 0, "B": 5}, "B": {"A": math.inf, "B": 0}}


def test_floyd_order_of_k_matters():
    # B → D → C → A 一条链。k 放在最里层的写法会把 table["B"]["A"] 算成 inf
    graph = {"A": {}, "B": {"D": 1}, "C": {"A": 1}, "D": {"C": 1}}
    assert floyd_warshall(graph)["B"]["A"] == 3


def test_floyd_negative_edge_without_cycle():
    graph = {"A": {"B": 4, "C": 2}, "C": {"B": -3}, "B": {"D": 1}}
    table = floyd_warshall(graph)
    assert table["A"] == {"A": 0, "B": -1, "C": 2, "D": 0}
    assert table["C"]["D"] == -2


def test_floyd_negative_cycle_raises():
    with pytest.raises(ValueError):
        floyd_warshall({"A": {"B": 1}, "B": {"C": -2}, "C": {"A": 0}})


def test_floyd_does_not_modify_graph():
    before = copy.deepcopy(TOLL)
    floyd_warshall(TOLL)
    assert TOLL == before


def test_floyd_random_against_brute_force():
    rng = random.Random(1962)
    for _ in range(30):
        graph = random_graph(rng, 7, 15, list(range(10)))
        table = floyd_warshall(graph)
        for source in graph:
            reachable = brute_force(graph, source)
            assert {end: distance for end, distance in table[source].items() if distance != math.inf} == reachable


# ---------- Bellman-Ford ----------

def test_bellman_ford_negative_edge():
    graph = {"A": {"B": 4, "C": 2}, "C": {"B": -3}, "B": {"D": 1}}
    assert bellman_ford(graph, "A") == {"A": 0, "B": -1, "C": 2, "D": 0}


def test_bellman_ford_where_dijkstra_fails():
    # 讲解页的例子：B 先以 2 被 Dijkstra 确定，之后才被负边改成 1，D 应该是 2 而不是 3
    graph = {"A": {"B": 2, "C": 3}, "C": {"B": -2}, "B": {"D": 1}}
    assert bellman_ford(graph, "A") == {"A": 0, "B": 1, "C": 3, "D": 2}


def test_bellman_ford_matches_zero_one_on_toll_roads():
    assert bellman_ford(TOLL, "A") == {"A": 0, "B": 0, "C": 0, "D": 1, "E": 1}


def test_bellman_ford_negative_cycle_raises():
    with pytest.raises(ValueError):
        bellman_ford({"S": {"A": 1}, "A": {"B": 1}, "B": {"A": -3}}, "S")


def test_bellman_ford_ignores_unreachable_negative_cycle():
    # 负环在 S 走不到的地方，不影响 S 的答案
    graph = {"S": {"A": 2}, "X": {"Y": -5}, "Y": {"X": 1}}
    assert bellman_ford(graph, "S") == {"S": 0, "A": 2}


def test_bellman_ford_random_against_brute_force():
    rng = random.Random(1958)
    for _ in range(40):
        graph = random_graph(rng, 7, 12, list(range(10)))
        # 加几条负权边，但保证没有负环：只从编号大的点指向编号小的点时才给负权
        for start in range(7):
            for end in list(graph[start]):
                if end < start and rng.random() < 0.3:
                    graph[start][end] = -rng.randint(1, 3)
        try:
            table = floyd_warshall(graph)
        except ValueError:
            with pytest.raises(ValueError):
                bellman_ford(graph, 0)
            continue
        expected = {end: distance for end, distance in table[0].items() if distance != math.inf}
        assert bellman_ford(graph, 0) == expected
