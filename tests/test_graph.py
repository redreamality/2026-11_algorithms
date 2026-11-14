import copy

from dsa.graph import bfs, build_graph, connected_components, dfs, shortest_path

# 讲解页动画里的那张图：
#     1       4
#   /   \   / |
# 0       3   |
#   \   /   \ |
#     2       5
EDGES = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]


def demo():
    return build_graph(EDGES)


def path_is_valid(graph, path):
    return all(next_node in graph[node] for node, next_node in zip(path, path[1:]))


def test_build_undirected():
    assert build_graph([(0, 1), (0, 2), (1, 2)]) == {0: [1, 2], 1: [0, 2], 2: [0, 1]}


def test_build_directed():
    graph = build_graph([("a", "b"), ("b", "c")], directed=True)
    assert graph == {"a": ["b"], "b": ["c"], "c": []}
    assert type(graph) is dict


def test_build_empty_and_from_generator():
    assert build_graph([]) == {}
    assert build_graph((pair for pair in [("x", "y")])) == {"x": ["y"], "y": ["x"]}


def test_any_hashable_nodes():
    graph = build_graph([((0, 0), (0, 1)), ((0, 1), (1, 1))])
    assert list(bfs(graph, (0, 0))) == [(0, 0), (0, 1), (1, 1)]


def test_bfs_order():
    assert list(bfs(demo(), 0)) == [0, 1, 2, 3, 4, 5]
    assert list(bfs(demo(), 3)) == [3, 1, 2, 4, 5, 0]


def test_dfs_order():
    # 0 → 1 → 3 → 2（走到底），退回 3 → 4 → 5
    assert list(dfs(demo(), 0)) == [0, 1, 3, 2, 4, 5]
    assert list(dfs(demo(), 5)) == [5, 3, 1, 0, 2, 4]


def test_traversals_are_lazy_generators():
    graph = demo()
    walk = bfs(graph, 0)
    assert next(walk) == 0  # 生成器：可以只取一部分
    assert next(walk) == 1
    assert next(node for node in dfs(graph, 0) if node > 2) == 3


def test_traversal_only_reaches_own_component():
    graph = build_graph([(0, 1), (2, 3)])
    assert list(bfs(graph, 2)) == [2, 3]
    assert list(dfs(graph, 0)) == [0, 1]


def test_traversal_directed():
    graph = build_graph([(0, 1), (1, 2), (2, 0), (3, 0)], directed=True)
    assert list(bfs(graph, 0)) == [0, 1, 2]
    assert list(dfs(graph, 3)) == [3, 0, 1, 2]


def test_node_missing_from_keys_has_no_neighbors():
    graph = {"a": ["b"]}  # b 不是键
    assert list(bfs(graph, "a")) == ["a", "b"]
    assert list(dfs(graph, "a")) == ["a", "b"]
    assert list(bfs(graph, "zzz")) == ["zzz"]


def test_dfs_handles_long_chain_without_recursion():
    length = 50_000
    graph = build_graph([(index, index + 1) for index in range(length)])
    order = list(dfs(graph, 0))
    assert order == list(range(length + 1))


def test_shortest_path():
    graph = demo()
    assert shortest_path(graph, 0, 3) in ([0, 1, 3], [0, 2, 3])
    path = shortest_path(graph, 0, 5)
    assert len(path) == 4 and path[0] == 0 and path[-1] == 5 and path_is_valid(graph, path)
    assert shortest_path(graph, 4, 2) == [4, 3, 2]


def test_shortest_path_same_node():
    assert shortest_path(demo(), 3, 3) == [3]


def test_shortest_path_unreachable():
    assert shortest_path(build_graph([(0, 1), (2, 3)]), 0, 3) is None


def test_shortest_path_takes_fewer_edges_not_first_found():
    # DFS 会先走 0-1-2-3-4（4 条边），BFS 才能找到 0-4（1 条边）
    graph = build_graph([(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)])
    assert shortest_path(graph, 0, 4) == [0, 4]


def test_connected_components():
    assert connected_components(demo()) == [{0, 1, 2, 3, 4, 5}]
    graph = build_graph([("b", "a"), ("c", "d"), ("d", "e")])
    graph["lonely"] = []
    assert connected_components(graph) == [{"a", "b"}, {"c", "d", "e"}, {"lonely"}]
    assert connected_components({}) == []


def test_graph_not_modified():
    graph = demo()
    before = copy.deepcopy(graph)
    list(bfs(graph, 0))
    list(dfs(graph, 0))
    shortest_path(graph, 0, 5)
    connected_components(graph)
    assert graph == before
