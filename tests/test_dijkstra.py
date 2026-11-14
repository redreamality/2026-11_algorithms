import copy
import random
from itertools import islice

import pytest

from dsa.dijkstra import shortest_path, shortest_paths, walk_by_distance


def undirected(*edges):
    graph = {}
    for start, end, weight in edges:
        graph.setdefault(start, {})[end] = weight
        graph.setdefault(end, {})[start] = weight
    return graph


# 讲解页动画里的那张图
DEMO = undirected(("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 1), ("C", "D", 2), ("D", "E", 3))


def path_length(graph, path):
    return sum(graph[node][next_node] for node, next_node in zip(path, path[1:]))


def test_single_node():
    assert shortest_paths({"A": {}}, "A") == ({"A": 0}, {})
    assert list(walk_by_distance({"A": {}}, "A")) == [("A", 0)]


def test_demo_graph():
    distances, previous = shortest_paths(DEMO, "A")
    assert distances == {"A": 0, "B": 3, "C": 1, "D": 3, "E": 6}
    assert previous["B"] == "C" and previous["C"] == "A" and previous["E"] == "D"
    assert "A" not in previous


def test_walk_by_distance_is_sorted_and_lazy():
    walk = walk_by_distance(DEMO, "A")
    assert next(walk) == ("A", 0)
    assert next(walk) == ("C", 1)
    order = list(walk_by_distance(DEMO, "A"))
    assert [distance for _, distance in order] == sorted(distance for _, distance in order)
    assert dict(order) == {"A": 0, "B": 3, "C": 1, "D": 3, "E": 6}
    assert len(order) == 5  # 每个点只产出一次，过期记录要跳过


def test_detour_beats_direct_edge():
    graph = {0: {1: 10, 2: 1}, 2: {1: 2}}
    assert shortest_paths(graph, 0)[0][1] == 3
    assert shortest_path(graph, 0, 1) == (3, [0, 2, 1])


def test_directed_edges_one_way():
    graph = {0: {1: 5}, 1: {}}
    assert shortest_paths(graph, 1) == ({1: 0}, {})


def test_unreachable_nodes_are_absent():
    graph = undirected((0, 1, 2), (2, 3, 1))
    distances, _ = shortest_paths(graph, 0)
    assert distances == {0: 0, 1: 2}


def test_node_only_as_neighbor_counted():
    graph = {0: {1: 4}}  # 1 不是键
    assert shortest_paths(graph, 0) == ({0: 0, 1: 4}, {1: 0})


def test_zero_weights():
    graph = {0: {1: 5, 2: 0}, 2: {1: 0}}
    assert shortest_paths(graph, 0)[0] == {0: 0, 1: 0, 2: 0}


def test_float_weights():
    graph = undirected(("x", "y", 0.5), ("y", "z", 0.25), ("x", "z", 1.0))
    assert shortest_path(graph, "x", "z") == (0.75, ["x", "y", "z"])


def test_unorderable_nodes_do_not_break_heap():
    # 两个节点距离相同，如果堆里直接比节点会抛 TypeError
    graph = {"start": {(1, 2): 1, frozenset({3}): 1}}
    assert shortest_paths(graph, "start")[0] == {"start": 0, (1, 2): 1, frozenset({3}): 1}


def test_negative_weight_raises():
    with pytest.raises(ValueError):
        shortest_paths({"a": {"b": -1}}, "a")


def test_graph_not_modified():
    before = copy.deepcopy(DEMO)
    shortest_paths(DEMO, "A")
    shortest_path(DEMO, "A", "E")
    list(walk_by_distance(DEMO, "A"))
    assert DEMO == before


def test_shortest_path_demo():
    assert shortest_path(DEMO, "A", "E") == (6, ["A", "C", "D", "E"])


def test_shortest_path_is_valid():
    graph = undirected(*[(index, index + 1, 1) for index in range(20)], (0, 20, 25), (5, 15, 3))
    distance, path = shortest_path(graph, 0, 20)
    assert distance == 13
    assert path[0] == 0 and path[-1] == 20
    assert path_length(graph, path) == distance


def test_shortest_path_same_node():
    assert shortest_path(DEMO, "C", "C") == (0, ["C"])


def test_shortest_path_unreachable():
    graph = {0: {1: 1}, 1: {}, 2: {}}
    assert shortest_path(graph, 0, 2) is None
    assert shortest_path(graph, 0, "not in graph") is None


def test_shortest_path_stops_early():
    """target 一被确定就返回：只要取出前两个点，后面的长链不该被展开。"""

    class CountingGraph(dict):
        visited = 0

        def get(self, key, default=None):
            CountingGraph.visited += 1
            return super().get(key, default)

    chain = CountingGraph({index: {index + 1: 1} for index in range(10_000)})
    chain[0][-1] = 1  # 0 旁边有一个 1 分钟就到的点
    assert shortest_path(chain, 0, -1) == (1, [0, -1])
    assert CountingGraph.visited < 10


def test_random_graphs_against_brute_force():
    rng = random.Random(16)
    for _ in range(30):
        size = 8
        graph = {node: {} for node in range(size)}
        for _ in range(16):
            start, end = rng.randrange(size), rng.randrange(size)
            if start != end:
                graph[start][end] = rng.randint(0, 9)
        # Bellman-Ford 当标准答案
        expected = {0: 0}
        for _ in range(size):
            for start, edges in graph.items():
                for end, weight in edges.items():
                    if start in expected and expected[start] + weight < expected.get(end, float("inf")):
                        expected[end] = expected[start] + weight
        distances, previous = shortest_paths(graph, 0)
        assert distances == expected
        for node in distances:
            path = [node]
            while path[-1] in previous:
                path.append(previous[path[-1]])
            assert path[-1] == 0
            assert path_length(graph, path[::-1]) == distances[node]
        assert dict(islice(walk_by_distance(graph, 0), 100)) == expected
