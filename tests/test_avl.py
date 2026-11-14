import random

import pytest

from dsa.avl import AVLNode, AVLTreeMap, rebalance, rotate_left, rotate_right


def real_height(node):
    return 0 if node is None else 1 + max(real_height(node.left), real_height(node.right))


def check_heights(node):
    """每个节点存的 height 都要和真实高度一致。"""
    if node is None:
        return
    assert node.height == real_height(node), f"节点 {node.key} 的 height 不对"
    check_heights(node.left)
    check_heights(node.right)


def chain(*keys, side):
    """手工搭一条往 side 方向歪的链，height 设好。"""
    nodes = [AVLNode(key) for key in keys]
    for parent, child in zip(nodes, nodes[1:]):
        setattr(parent, side, child)
    for position, node in enumerate(nodes):
        node.height = len(nodes) - position
    return nodes[0]


def test_empty():
    tree = AVLTreeMap()
    assert len(tree) == 0
    assert tree.height() == 0
    assert list(tree) == []
    assert tree.is_balanced()
    assert 1 not in tree
    with pytest.raises(KeyError):
        tree[1]


def test_rotate_right():
    top = rotate_right(chain(3, 2, 1, side="left"))
    assert top.key == 2
    assert top.left.key == 1 and top.right.key == 3
    assert top.right.left is None
    check_heights(top)


def test_rotate_left_moves_middle_subtree():
    node = AVLNode(1)
    node.right = AVLNode(3)
    node.right.left = AVLNode(2)  # 中间那棵子树 B
    node.right.right = AVLNode(4)
    node.right.height, node.height = 2, 3
    top = rotate_left(node)
    assert top.key == 3
    assert top.left.key == 1 and top.left.right.key == 2  # B 挂到了 1 的右边
    check_heights(top)


def test_rebalance_lr():
    node = AVLNode(3)
    node.left = AVLNode(1)
    node.left.right = AVLNode(2)
    node.left.height = 2
    top = rebalance(node)
    assert (top.key, top.left.key, top.right.key) == (2, 1, 3)
    check_heights(top)


def test_rebalance_leaves_balanced_node_alone():
    node = AVLNode(2)
    node.left = AVLNode(1)
    assert rebalance(node) is node
    assert node.height == 2  # 但 height 要更新


def test_works_like_a_dict():
    tree = AVLTreeMap({5: "e", 3: "c"})
    tree[8] = "h"
    tree[3] = "C"  # 已有的键只改值
    assert len(tree) == 3
    assert tree[3] == "C"
    assert tree.get(4, "?") == "?"
    assert list(tree.items()) == [(3, "C"), (5, "e"), (8, "h")]
    assert tree == {3: "C", 5: "e", 8: "h"}


def test_rr_left_rotation():
    tree = AVLTreeMap.fromkeys([1, 2, 3])
    assert tree.root.key == 2 and tree.height() == 2


def test_ll_right_rotation():
    tree = AVLTreeMap.fromkeys([3, 2, 1])
    assert tree.root.key == 2 and tree.height() == 2


def test_lr_double_rotation():
    tree = AVLTreeMap.fromkeys([3, 1, 2])
    assert tree.root.key == 2
    assert tree.root.left.key == 1 and tree.root.right.key == 3


def test_rl_double_rotation():
    tree = AVLTreeMap.fromkeys([1, 3, 2])
    assert tree.root.key == 2
    assert tree.root.left.key == 1 and tree.root.right.key == 3


def test_values_follow_keys_through_rotations():
    tree = AVLTreeMap((key, str(key)) for key in [3, 1, 2, 5, 4])
    assert all(tree[key] == str(key) for key in range(1, 6))


def test_sequential_1_to_100_stays_short():
    tree = AVLTreeMap.fromkeys(range(1, 101))
    assert len(tree) == 100
    assert tree.height() <= 8
    assert tree.is_balanced()
    assert list(tree) == list(range(1, 101))
    check_heights(tree.root)


def test_random_inserts():
    rng = random.Random(24)
    keys = rng.sample(range(10_000), 500)
    tree = AVLTreeMap.fromkeys(keys)
    assert list(tree) == sorted(keys)
    assert tree.is_balanced()
    assert tree.height() <= 13  # AVL 保证 h < 1.44 log2(n)
    check_heights(tree.root)
    assert all(key in tree for key in keys[:50])
    assert -1 not in tree


def test_is_balanced_detects_chain():
    tree = AVLTreeMap()
    tree.root = chain(1, 2, 3, side="right")  # 绕过插入硬塞一条链
    assert not tree.is_balanced()


def test_delete_optional():
    """选做：删除后仍然平衡。"""
    tree = AVLTreeMap.fromkeys(range(1, 33))
    for key in range(1, 17):
        del tree[key]
        assert tree.is_balanced()
        check_heights(tree.root)
    assert list(tree) == list(range(17, 33))
    assert len(tree) == 16
    with pytest.raises(KeyError):
        del tree[1]


def test_random_against_dict_optional():
    """选做：随机增删，和 dict 对照。"""
    rng = random.Random(7)
    tree, reference = AVLTreeMap(), {}
    for step in range(1500):
        key = rng.randrange(200)
        if rng.random() < 0.6:
            tree[key] = reference[key] = step
        elif key in reference:
            del tree[key]
            del reference[key]
    assert list(tree.items()) == sorted(reference.items())
    assert len(tree) == len(reference)
    assert tree.is_balanced()
    check_heights(tree.root)
