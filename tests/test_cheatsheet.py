import itertools
import random

from dsa.cheatsheet import (
    complete_tree_shape,
    count_pop_sequences,
    is_valid_pop_sequence,
    postorder_from_preorder_inorder,
    preorder_from_postorder_inorder,
)

# ---------- 出栈序列 ----------


def test_pop_sequence_examples():
    assert is_valid_pop_sequence([1, 2, 3, 4, 5], [4, 5, 3, 2, 1])
    assert not is_valid_pop_sequence([1, 2, 3, 4, 5], [4, 3, 5, 1, 2])
    assert is_valid_pop_sequence([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])  # 进一个弹一个
    assert is_valid_pop_sequence([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])  # 全进再全弹
    assert not is_valid_pop_sequence(list("abc"), list("cab"))
    assert is_valid_pop_sequence([], [])


def test_pop_sequence_mismatched_inputs():
    assert not is_valid_pop_sequence([1, 2, 3], [1, 2])
    assert not is_valid_pop_sequence([1, 2, 3], [1, 2, 4])


def test_pop_sequence_does_not_modify_inputs():
    push_order, pop_order = [1, 2, 3], [3, 2, 1]
    is_valid_pop_sequence(push_order, pop_order)
    assert push_order == [1, 2, 3] and pop_order == [3, 2, 1]


def all_pop_sequences(values):
    """暴力枚举：每一步要么进栈、要么出栈，收集所有能得到的出栈序列。"""
    results = set()

    def walk(index, stack, popped):
        if index == len(values) and not stack:
            results.add(tuple(popped))
            return
        if index < len(values):
            walk(index + 1, stack + [values[index]], popped)
        if stack:
            walk(index, stack[:-1], popped + [stack[-1]])

    walk(0, [], [])
    return results


def test_pop_sequence_against_brute_force():
    for n in range(1, 7):
        values = list(range(1, n + 1))
        reachable = all_pop_sequences(values)
        for permutation in itertools.permutations(values):
            assert is_valid_pop_sequence(values, list(permutation)) == (permutation in reachable)


def test_count_pop_sequences():
    assert [count_pop_sequences(n) for n in range(8)] == [1, 1, 2, 5, 14, 42, 132, 429]
    for n in range(1, 7):
        assert count_pop_sequences(n) == len(all_pop_sequences(list(range(n))))


# ---------- 二叉树还原 ----------

LESSON_10_TREE = {"pre": [1, 2, 4, 5, 3, 6], "in": [4, 2, 5, 1, 3, 6], "post": [4, 5, 2, 6, 3, 1]}


def random_tree(rng, size):
    """随机二叉树，返回三种遍历。节点值 0..size-1 打乱后分配，保证各不相同。"""
    labels = list(range(size))
    rng.shuffle(labels)

    def build(nodes):
        if not nodes:
            return None
        root_position = rng.randrange(len(nodes))
        return (nodes[root_position], build(nodes[:root_position]), build(nodes[root_position + 1:]))

    tree = build(labels)  # labels 的顺序就是中序

    def pre(node):
        return [] if node is None else [node[0], *pre(node[1]), *pre(node[2])]

    def post(node):
        return [] if node is None else [*post(node[1]), *post(node[2]), node[0]]

    return pre(tree), labels, post(tree)


def test_rebuild_lesson_10_tree():
    assert postorder_from_preorder_inorder(LESSON_10_TREE["pre"], LESSON_10_TREE["in"]) == LESSON_10_TREE["post"]
    assert preorder_from_postorder_inorder(LESSON_10_TREE["post"], LESSON_10_TREE["in"]) == LESSON_10_TREE["pre"]


def test_rebuild_small_cases():
    assert postorder_from_preorder_inorder([], []) == []
    assert postorder_from_preorder_inorder(["A"], ["A"]) == ["A"]
    # 只有左孩子 vs 只有右孩子：中序能把它们分开
    assert postorder_from_preorder_inorder([1, 2], [2, 1]) == [2, 1]
    assert postorder_from_preorder_inorder([1, 2], [1, 2]) == [2, 1]
    assert preorder_from_postorder_inorder([2, 1], [2, 1]) == [1, 2]
    # 一条往右斜的链
    assert postorder_from_preorder_inorder([1, 2, 3, 4], [1, 2, 3, 4]) == [4, 3, 2, 1]


def test_rebuild_letters():
    preorder, inorder = list("ABDECF"), list("DBEACF")
    assert postorder_from_preorder_inorder(preorder, inorder) == list("DEBFCA")
    assert preorder_from_postorder_inorder(list("DEBFCA"), inorder) == preorder


def test_rebuild_does_not_modify_inputs():
    preorder, inorder = list(LESSON_10_TREE["pre"]), list(LESSON_10_TREE["in"])
    postorder_from_preorder_inorder(preorder, inorder)
    assert preorder == LESSON_10_TREE["pre"] and inorder == LESSON_10_TREE["in"]


def test_rebuild_random_trees():
    rng = random.Random(10)
    for size in range(0, 40):
        preorder, inorder, postorder = random_tree(rng, size)
        assert postorder_from_preorder_inorder(preorder, inorder) == postorder
        assert preorder_from_postorder_inorder(postorder, inorder) == preorder


# ---------- 完全二叉树 ----------


def test_complete_tree_shape_examples():
    assert complete_tree_shape(1) == (1, 1)
    assert complete_tree_shape(6) == (3, 3)
    assert complete_tree_shape(7) == (3, 4)
    assert complete_tree_shape(8) == (4, 4)
    assert complete_tree_shape(1000) == (10, 500)


def test_complete_tree_shape_by_counting():
    """用堆的下标关系数：下标 i（从 0 开始）有左孩子当且仅当 2i + 1 < n。"""
    for n in range(1, 300):
        leaf_count = sum(1 for index in range(n) if 2 * index + 1 >= n)
        level_count = 0
        while (1 << level_count) - 1 < n:  # 前 level_count 层最多 2^level_count - 1 个节点
            level_count += 1
        assert complete_tree_shape(n) == (level_count, leaf_count)
