import json
import random
from collections.abc import Iterator

import pytest

from dsa.binary_tree import (
    TreeNode,
    build_from_list,
    count_nodes,
    from_dict,
    height,
    inorder,
    level_order,
    postorder,
    preorder,
    to_dict,
    to_list,
)

TRAVERSALS = [preorder, inorder, postorder, level_order]


def sample():
    """讲解页里那棵树：
          1
         / \\
        2   3
       / \\   \\
      4   5   6
    """
    return TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, None, TreeNode(6)))


def test_preorder():
    assert list(preorder(sample())) == [1, 2, 4, 5, 3, 6]


def test_inorder():
    assert list(inorder(sample())) == [4, 2, 5, 1, 3, 6]


def test_postorder():
    assert list(postorder(sample())) == [4, 5, 2, 6, 3, 1]


def test_level_order_groups_by_level():
    assert list(level_order(sample())) == [[1], [2, 3], [4, 5, 6]]


@pytest.mark.parametrize("traversal", TRAVERSALS)
def test_traversals_are_lazy_generators(traversal):
    result = traversal(sample())
    assert isinstance(result, Iterator)  # 返回生成器，不是 list
    first = next(result)
    assert first in (1, 4, [1])  # 只取第一个也能工作


def test_preorder_can_stop_early():
    """生成器的好处：找到就停，后面的节点不会被访问。"""
    visited = []

    class Recording(TreeNode):
        @property
        def left(self):
            visited.append(self.val)
            return self.__dict__["left"]

        @left.setter
        def left(self, node):
            self.__dict__["left"] = node

    root = Recording(1, Recording(2), Recording(3, Recording(4), Recording(5)))
    assert next(value for value in preorder(root) if value == 2) == 2
    assert 3 not in visited


def test_empty_tree():
    for traversal in TRAVERSALS:
        assert list(traversal(None)) == []
    assert height(None) == 0
    assert count_nodes(None) == 0


def test_single_node():
    node = TreeNode(7)
    assert list(preorder(node)) == list(inorder(node)) == list(postorder(node)) == [7]
    assert list(level_order(node)) == [[7]]
    assert height(node) == 1
    assert count_nodes(node) == 1


def test_height_and_count():
    assert height(sample()) == 3
    assert count_nodes(sample()) == 6


def test_height_of_chain():
    chain = TreeNode(1, TreeNode(2, None, TreeNode(3, TreeNode(4))))  # 一条斜着的链
    assert height(chain) == 4
    assert count_nodes(chain) == 4


def test_build_from_list():
    assert build_from_list([1, 2, 3, 4, 5, None, 6]) == sample()


def test_build_skips_children_of_none():
    tree = build_from_list([1, None, 2, 3])  # 3 是 2 的左孩子，不是 None 的孩子
    assert tree.left is None
    assert tree.right.val == 2
    assert tree.right.left.val == 3
    assert height(tree) == 3


def test_build_empty():
    assert build_from_list([]) is None
    assert build_from_list([None]) is None


@pytest.mark.parametrize(
    "values",
    [[], [1], [1, 2, 3, 4, 5, None, 6], [1, None, 2, 3], [1, 2, None, 3, None, 4], [1, 2, 3, None, 4]],
)
def test_to_list_round_trip(values):
    assert to_list(build_from_list(values)) == values


def test_to_list_strips_trailing_none():
    assert to_list(TreeNode(1, TreeNode(2))) == [1, 2]
    assert to_list(TreeNode(1, None, TreeNode(2))) == [1, None, 2]


def test_to_dict_shape():
    assert to_dict(TreeNode(1, None, TreeNode(2))) == {
        "val": 1,
        "left": None,
        "right": {"val": 2, "left": None, "right": None},
    }
    assert to_dict(None) is None
    assert from_dict(None) is None


def test_json_round_trip():
    text = json.dumps(to_dict(sample()))
    assert from_dict(json.loads(text)) == sample()


def random_tree(rng, depth):
    if depth == 0 or rng.random() < 0.25:
        return None
    return TreeNode(rng.randrange(100), random_tree(rng, depth - 1), random_tree(rng, depth - 1))


def test_random_round_trips():
    rng = random.Random(10)
    for _ in range(200):
        tree = random_tree(rng, 6)
        assert build_from_list(to_list(tree)) == tree
        assert from_dict(to_dict(tree)) == tree
        assert count_nodes(tree) == len(list(preorder(tree))) == sum(map(len, level_order(tree)))
        assert height(tree) == len(list(level_order(tree)))
