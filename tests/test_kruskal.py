import random

import pytest

from dsa.kruskal import cluster, minimum_spanning_tree

# 讲解页动画里的图：6 个村子，MST 总权 18
VILLAGES = "ABCDEF"
ROADS = [("A", "B", 4), ("B", "C", 6), ("A", "D", 2), ("B", "D", 5), ("B", "E", 3), ("E", "C", 1),
         ("D", "E", 7), ("C", "F", 8), ("E", "F", 9)]


def total(tree):
    return sum(weight for _, _, weight in tree)


def is_spanning_tree(nodes, tree):
    """节点数 - 1 条边、把所有点连成一块（于是必然无环）。"""
    nodes = list(nodes)
    assert len(tree) == len(nodes) - 1
    neighbors = {node: [] for node in nodes}
    for start, end, _ in tree:
        neighbors[start].append(end)
        neighbors[end].append(start)
    seen, stack = {nodes[0]}, [nodes[0]]
    while stack:
        for neighbor in neighbors[stack.pop()]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(nodes)


def test_empty_and_single():
    assert minimum_spanning_tree([], []) == []
    assert minimum_spanning_tree(["only"], []) == []


def test_single_edge():
    assert minimum_spanning_tree(["a", "b"], [("a", "b", 7)]) == [("a", "b", 7)]


def test_villages():
    tree = minimum_spanning_tree(VILLAGES, ROADS)
    assert tree == [("E", "C", 1), ("A", "D", 2), ("B", "E", 3), ("A", "B", 4), ("C", "F", 8)]
    assert total(tree) == 18
    assert is_spanning_tree(VILLAGES, tree)


def test_triangle_skips_heaviest():
    tree = minimum_spanning_tree([0, 1, 2], [(0, 1, 3), (1, 2, 1), (0, 2, 2)])
    assert total(tree) == 3
    assert (0, 1, 3) not in tree


def test_equal_weights_keep_input_order():
    tree = minimum_spanning_tree(range(4), [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 0, 1)])
    assert tree == [(0, 1, 1), (1, 2, 1), (2, 3, 1)]


def test_unorderable_nodes_with_equal_weights():
    # 同权时如果 sorted 去比较节点，会抛 TypeError
    first, second, third = frozenset({1}), frozenset({2}), frozenset({3})
    tree = minimum_spanning_tree([first, second, third], [(first, second, 1), (second, third, 1)])
    assert total(tree) == 2


def test_parallel_edges_and_self_loop():
    assert minimum_spanning_tree(["x", "y"], [("x", "y", 5), ("y", "y", 0), ("y", "x", 2)]) == [("y", "x", 2)]


def test_endpoints_not_in_nodes_are_included():
    with pytest.raises(ValueError):
        minimum_spanning_tree(["a", "b"], [("a", "b", 1), ("b", "c", 1), ("d", "e", 1)])
    assert minimum_spanning_tree(["a"], [("a", "b", 1)]) == [("a", "b", 1)]


def test_disconnected_raises():
    with pytest.raises(ValueError):
        minimum_spanning_tree(VILLAGES, [road for road in ROADS if "F" not in road[:2]])


def test_isolated_node_raises():
    with pytest.raises(ValueError):
        minimum_spanning_tree([0, 1, 2], [(0, 1, 1)])


def test_accepts_generator_and_does_not_modify_edges():
    roads = list(ROADS)
    minimum_spanning_tree(VILLAGES, roads)
    assert roads == ROADS
    assert total(minimum_spanning_tree(VILLAGES, (road for road in ROADS))) == 18


def test_matches_brute_force_on_random_graphs():
    from itertools import combinations

    rng = random.Random(17)
    for _ in range(40):
        nodes = list(range(5))
        edges = [(start, end, rng.randint(1, 9)) for start, end in combinations(nodes, 2) if rng.random() < 0.8]
        best = None
        for subset in combinations(edges, len(nodes) - 1):
            if is_spanning_tree(nodes, subset):
                best = total(subset) if best is None else min(best, total(subset))
        if best is None:
            with pytest.raises(ValueError):
                minimum_spanning_tree(nodes, edges)
        else:
            tree = minimum_spanning_tree(nodes, edges)
            assert is_spanning_tree(nodes, tree)
            assert total(tree) == best


def test_cluster():
    points = ["a", "b", "c", "d", "e"]
    distances = [("a", "b", 1), ("c", "d", 2), ("b", "c", 10), ("d", "e", 3), ("a", "e", 20)]
    assert cluster(points, distances, 2) == [{"a", "b"}, {"c", "d", "e"}]
    assert cluster(points, distances, 5) == [{"a"}, {"b"}, {"c"}, {"d"}, {"e"}]
    assert cluster(points, distances, 1) == [set(points)]


def test_cluster_villages():
    assert cluster(VILLAGES, ROADS, 3) == [{"A", "D"}, {"B", "C", "E"}, {"F"}]


def test_cluster_invalid_count():
    with pytest.raises(ValueError):
        cluster(["a", "b"], [("a", "b", 1)], 0)
    with pytest.raises(ValueError):
        cluster(["a", "b"], [("a", "b", 1)], 3)
    with pytest.raises(ValueError):
        cluster(["a", "b", "c"], [("a", "b", 1)], 1)  # 边不够，合并不到 1 组
