import random

import pytest

from dsa.bst import TreeMap


def check(tree, expected: dict):
    """内容、顺序、长度都要对：迭代顺序必须是键从小到大。"""
    assert list(tree.items()) == sorted(expected.items())
    assert len(tree) == len(expected)


def test_empty():
    tree = TreeMap()
    check(tree, {})
    assert tree.height() == 0
    assert 1 not in tree
    assert tree.root is None
    with pytest.raises(KeyError):
        tree[1]
    with pytest.raises(KeyError):
        del tree[1]


def test_works_like_a_dict():
    tree = TreeMap({5: "e", 3: "c", 8: "h"})
    tree[1] = "a"
    assert tree[5] == "e"
    assert 3 in tree and 2 not in tree
    assert tree.get(2) is None and tree.get(2, "?") == "?"
    assert list(tree) == [1, 3, 5, 8]
    assert list(tree.values()) == ["a", "c", "e", "h"]
    assert tree == {1: "a", 3: "c", 5: "e", 8: "h"}
    assert tree.pop(3) == "c"
    assert tree.setdefault(4, "d") == "d"
    check(tree, {1: "a", 4: "d", 5: "e", 8: "h"})


def test_insert_shape():
    tree = TreeMap([(5, None), (3, None), (8, None)])
    assert tree.root.key == 5
    assert tree.root.left.key == 3
    assert tree.root.right.key == 8


def test_existing_key_updates_value_only():
    tree = TreeMap({2: "old", 1: "x"})
    tree[2] = "new"
    check(tree, {1: "x", 2: "new"})


def test_min_max():
    tree = TreeMap.fromkeys([5, 3, 8, 1, 9])
    assert tree.min_key() == 1
    assert tree.max_key() == 9
    with pytest.raises(ValueError):
        TreeMap().min_key()
    with pytest.raises(ValueError):
        TreeMap().max_key()


def test_floor_and_ceiling():
    tree = TreeMap.fromkeys([20, 10, 30])
    assert tree.floor_key(25) == 20
    assert tree.floor_key(20) == 20
    assert tree.floor_key(5) is None
    assert tree.floor_key(99) == 30
    assert tree.ceiling_key(25) == 30
    assert tree.ceiling_key(10) == 10
    assert tree.ceiling_key(31) is None
    assert tree.ceiling_key(-1) == 10
    assert TreeMap().floor_key(1) is None


def test_items_between():
    tree = TreeMap({k: str(k) for k in [50, 30, 70, 20, 40, 60, 80]})
    assert list(tree.items_between(35, 65)) == [(40, "40"), (50, "50"), (60, "60")]
    assert list(tree.items_between(20, 30)) == [(20, "20"), (30, "30")]  # 两端都包含
    assert list(tree.items_between(81, 99)) == []
    assert list(tree.items_between(0, 100)) == sorted(tree.items())


def test_items_between_skips_subtrees():
    """范围之外的子树不该被访问：数一下读了多少次节点的 key。"""

    class CountingKey(int):
        reads = 0

        def __lt__(self, other):
            CountingKey.reads += 1
            return int(self) < int(other)

        def __le__(self, other):
            CountingKey.reads += 1
            return int(self) <= int(other)

        def __gt__(self, other):
            CountingKey.reads += 1
            return int(self) > int(other)

        def __ge__(self, other):
            CountingKey.reads += 1
            return int(self) >= int(other)

    keys = list(range(1023))
    tree = TreeMap()

    def insert_balanced(low, high):
        if low > high:
            return
        middle = (low + high) // 2
        tree[CountingKey(keys[middle])] = None
        insert_balanced(low, middle - 1)
        insert_balanced(middle + 1, high)

    insert_balanced(0, len(keys) - 1)
    CountingKey.reads = 0
    assert [int(k) for k, _ in tree.items_between(500, 502)] == [500, 501, 502]
    assert CountingKey.reads < 200  # 遍历整棵树要比较上千次


def test_height():
    assert TreeMap.fromkeys([1]).height() == 1
    assert TreeMap.fromkeys([4, 2, 6, 1, 3, 5, 7]).height() == 3
    assert TreeMap.fromkeys([1, 2, 3, 4, 5, 6, 7]).height() == 7  # 有序插入退化成链表


def test_remove_leaf():
    tree = TreeMap.fromkeys([5, 3, 8])
    del tree[3]
    check(tree, {5: None, 8: None})
    assert tree.root.left is None


def test_remove_one_child():
    tree = TreeMap.fromkeys([5, 3, 8, 9])
    del tree[8]  # 8 只有右孩子 9
    check(tree, dict.fromkeys([3, 5, 9]))
    assert tree.root.right.key == 9


def test_remove_two_children_uses_successor():
    tree = TreeMap({k: str(k) for k in [5, 3, 8, 7, 9, 6]})
    del tree[5]  # 后继是右子树里最小的 6
    check(tree, {k: str(k) for k in [3, 6, 7, 8, 9]})
    assert tree.root.key == 6
    assert tree.root.value == "6"  # 值要跟着键一起搬
    assert tree.root.right.left.key == 7
    assert tree.root.right.left.left is None  # 6 原来的位置空了出来


def test_remove_until_empty_then_reuse():
    tree = TreeMap.fromkeys([2, 1, 3])
    for key in (2, 1, 3):
        del tree[key]
    check(tree, {})
    assert tree.root is None
    tree[4] = "d"
    check(tree, {4: "d"})


def test_random_against_dict():
    rng = random.Random(11)
    tree, reference = TreeMap(), {}
    for step in range(1000):
        key = rng.randrange(60)
        if rng.random() < 0.6:
            tree[key] = reference[key] = step
        elif key in reference:
            del tree[key]
            del reference[key]
        else:
            with pytest.raises(KeyError):
                del tree[key]
        assert (key in tree) == (key in reference)
        low = rng.randrange(60)
        smaller_or_equal = [k for k in reference if k <= low]
        assert tree.floor_key(low) == (max(smaller_or_equal) if smaller_or_equal else None)
    check(tree, reference)
