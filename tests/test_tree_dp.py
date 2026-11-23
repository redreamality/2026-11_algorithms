import random
from collections import deque
from itertools import combinations

from dsa.tree_dp import build_adjacency_list, build_tree, max_non_adjacent_total, rob_tree, tree_diameter

EXAMPLE_EDGES = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]


# ---------- 工具：随机树和暴力对照 ----------

def random_tree_edges(generator, node_count):
    """随机生成一棵树：先让第 i 个节点挂在前面某个节点下面，再把编号打乱、边的方向随机翻转。"""
    labels = list(range(node_count))
    generator.shuffle(labels)
    edges = []
    for child in range(1, node_count):
        parent = generator.randrange(child)
        edge = (labels[parent], labels[child])
        edges.append(edge if generator.random() < 0.5 else edge[::-1])
    generator.shuffle(edges)
    return edges


def brute_non_adjacent(values, edges) -> int:
    best = 0
    for size in range(len(values) + 1):
        for chosen in combinations(range(len(values)), size):
            picked = set(chosen)
            if all(not (first in picked and second in picked) for first, second in edges):
                best = max(best, sum(values[node] for node in chosen))
    return best


def brute_diameter(node_count, edges) -> int:
    adjacency = [[] for _ in range(node_count)]
    for first, second in edges:
        adjacency[first].append(second)
        adjacency[second].append(first)
    farthest = 0
    for start in range(node_count):  # 每个点 BFS 一次，取最远的距离
        distance = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency[node]:
                if neighbor not in distance:
                    distance[neighbor] = distance[node] + 1
                    queue.append(neighbor)
        farthest = max(farthest, max(distance.values()))
    return farthest


def tree_list_to_edges(values):
    """把层序列表里的非空节点按出现顺序编号，返回 (values, edges)，用来和 rob_tree 对照。"""
    root = build_tree(values)
    if root is None:
        return [], []
    node_values, edges = [], []
    queue = deque([(root, -1)])
    while queue:
        node, parent_id = queue.popleft()
        node_id = len(node_values)
        node_values.append(node.val)
        if parent_id >= 0:
            edges.append((parent_id, node_id))
        for child in (node.left, node.right):
            if child is not None:
                queue.append((child, node_id))
    return node_values, edges


# ---------- 邻接表 ----------

def test_build_adjacency_list():
    assert build_adjacency_list(4, [(0, 1), (0, 2), (2, 3)]) == [[1, 2], [0], [0, 3], [2]]
    assert build_adjacency_list(1, []) == [[]]
    assert build_adjacency_list(0, []) == []
    assert build_adjacency_list(3, [(2, 0), (1, 2)]) == [[2], [2], [0, 1]]


# ---------- 打家劫舍 III ----------

def test_rob_tree_examples():
    assert rob_tree(build_tree([3, 4, 5, 1, 3, None, 1])) == 9
    assert rob_tree(build_tree([3, 2, 3, None, 3, None, 1])) == 7
    assert rob_tree(None) == 0
    assert rob_tree(build_tree([7])) == 7


def test_rob_tree_skip_two_levels():
    # 4 → 1 → 2 → 3 一条链：偷 4 和 3（中间隔了两层）最好，得 7
    assert rob_tree(build_tree([4, 1, None, 2, None, 3])) == 7


def test_rob_tree_random_against_brute_force():
    generator = random.Random(337)
    for _ in range(60):
        values = [generator.randint(0, 9) if generator.random() < 0.8 or index == 0 else None
                  for index in range(generator.randint(1, 12))]
        node_values, edges = tree_list_to_edges(values)
        assert rob_tree(build_tree(values)) == brute_non_adjacent(node_values, edges), values


# ---------- 一般的树：选不相邻的节点 ----------

def test_non_adjacent_example():
    assert max_non_adjacent_total([3, 4, 5, 1, 3, 1], EXAMPLE_EDGES) == 9


def test_non_adjacent_small():
    assert max_non_adjacent_total([], []) == 0
    assert max_non_adjacent_total([6], []) == 6
    assert max_non_adjacent_total([5, 1, 1, 1, 1], [(0, 1), (0, 2), (0, 3), (0, 4)]) == 5
    assert max_non_adjacent_total([1, 2, 2, 2, 2], [(0, 1), (0, 2), (0, 3), (0, 4)]) == 8  # 孩子可以不止两个


def test_non_adjacent_random_against_brute_force():
    generator = random.Random(4545)
    for _ in range(60):
        node_count = generator.randint(1, 11)
        values = [generator.randint(0, 9) for _ in range(node_count)]
        edges = random_tree_edges(generator, node_count)
        assert max_non_adjacent_total(values, edges) == brute_non_adjacent(values, edges), (values, edges)


def test_non_adjacent_deep_chain():
    # 2 万个节点连成一条链：递归写法会超过默认的递归深度
    chain = [(index, index + 1) for index in range(19999)]
    assert max_non_adjacent_total([1] * 20000, chain) == 10000


# ---------- 树的直径 ----------

def test_diameter_examples():
    assert tree_diameter(6, EXAMPLE_EDGES) == 4
    assert tree_diameter(5, [(0, 1), (0, 2), (0, 3), (0, 4)]) == 2
    assert tree_diameter(0, []) == 0
    assert tree_diameter(1, []) == 0
    assert tree_diameter(2, [(1, 0)]) == 1


def test_diameter_not_through_root():
    # 根 0 只挂了一个孩子 1，最长路径 2 → 4 → 3 → 1 → 5 → 6 有 5 条边，不经过 0（经过 0 的最长只有 4 条）
    edges = [(0, 1), (1, 3), (3, 4), (4, 2), (1, 5), (5, 6)]
    assert tree_diameter(7, edges) == 5


def test_diameter_random_against_brute_force():
    generator = random.Random(1245)
    for _ in range(60):
        node_count = generator.randint(1, 30)
        edges = random_tree_edges(generator, node_count)
        assert tree_diameter(node_count, edges) == brute_diameter(node_count, edges), edges


def test_diameter_deep_chain():
    chain = [(index, index + 1) for index in range(19999)]
    assert tree_diameter(20000, chain) == 19999
