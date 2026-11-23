import random

import pytest

from dsa.fenwick_tree import FenwickTree, RangeAddPointQuery, count_inversions, lowbit

NUMBERS = [3, 1, 4, 1, 5, 9, 2, 6]  # 第 41、42 课共用的主线例子


def test_lowbit():
    assert [lowbit(position) for position in range(1, 13)] == [1, 2, 1, 4, 1, 2, 1, 8, 1, 2, 1, 4]


def test_tree_layout_of_running_example():
    fenwick_tree = FenwickTree(NUMBERS)
    assert fenwick_tree.tree == [0, 3, 4, 4, 9, 5, 14, 2, 31]
    assert len(fenwick_tree) == 8


def test_add_walks_up():
    fenwick_tree = FenwickTree(NUMBERS)
    fenwick_tree.add(4, 3)  # 内部位置 5 → 6 → 8
    assert fenwick_tree.tree == [0, 3, 4, 4, 9, 8, 17, 2, 34]


def test_prefix_sum():
    fenwick_tree = FenwickTree(NUMBERS)
    assert [fenwick_tree.prefix_sum(count) for count in range(9)] == [0, 3, 4, 8, 9, 14, 23, 25, 31]
    fenwick_tree.add(4, 3)
    assert fenwick_tree.prefix_sum(7) == 28
    assert fenwick_tree.prefix_sum(4) == 9  # 位置 5 之前的不受影响


def test_range_sum_and_item_access():
    fenwick_tree = FenwickTree(NUMBERS)
    fenwick_tree.add(4, 3)
    assert fenwick_tree.range_sum(2, 5) == 22
    assert fenwick_tree.range_sum(0, 7) == 34
    assert fenwick_tree.range_sum(3, 2) == 0
    assert [fenwick_tree[index] for index in range(8)] == [3, 1, 4, 1, 8, 9, 2, 6]
    fenwick_tree[4] = 5
    assert fenwick_tree.tree == [0, 3, 4, 4, 9, 5, 14, 2, 31]


def test_does_not_modify_input():
    numbers = [1, 2, 3]
    fenwick_tree = FenwickTree(numbers)
    fenwick_tree.add(0, 10)
    assert numbers == [1, 2, 3]


def test_empty():
    fenwick_tree = FenwickTree([])
    assert len(fenwick_tree) == 0
    assert fenwick_tree.prefix_sum(0) == 0
    assert fenwick_tree.tree == [0]


def test_out_of_range_raises_index_error():
    fenwick_tree = FenwickTree(NUMBERS)
    for bad_call in (
        lambda: fenwick_tree.add(8, 1),
        lambda: fenwick_tree.add(-1, 1),
        lambda: fenwick_tree.prefix_sum(9),
        lambda: fenwick_tree.prefix_sum(-1),
        lambda: fenwick_tree[8],
        lambda: fenwick_tree.range_sum(0, 8),
    ):
        with pytest.raises(IndexError):
            bad_call()


def test_matches_brute_force():
    rng = random.Random(42)
    for _ in range(100):
        numbers = [rng.randint(-20, 20) for _ in range(rng.randint(1, 20))]
        fenwick_tree = FenwickTree(numbers)
        for _ in range(30):
            index = rng.randrange(len(numbers))
            if rng.random() < 0.5:
                delta = rng.randint(-10, 10)
                numbers[index] += delta
                fenwick_tree.add(index, delta)
            else:
                left = rng.randrange(len(numbers))
                right = rng.randrange(left, len(numbers))
                assert fenwick_tree.range_sum(left, right) == sum(numbers[left:right + 1])
            assert fenwick_tree.prefix_sum(index) == sum(numbers[:index])


def test_operations_are_logarithmic():
    size = 100_000
    fenwick_tree = FenwickTree([1] * size)
    total = 0
    for index in range(size):  # 每次都查整段：O(n) 的写法要 10¹⁰ 步
        fenwick_tree.add(index, 1)
        total += fenwick_tree.prefix_sum(size)
    assert fenwick_tree.prefix_sum(size) == 2 * size
    assert total == sum(size + index + 1 for index in range(size))


def test_range_add_point_query_running_example():
    values = RangeAddPointQuery(NUMBERS)
    values.add(2, 5, 2)
    assert values[5] == 11
    values.add(4, 7, 3)
    assert values[5] == 14
    assert len(values) == 8
    assert list(values) == [3, 1, 6, 3, 10, 14, 5, 9]


def test_range_add_point_query_errors():
    values = RangeAddPointQuery([1, 2, 3])
    with pytest.raises(IndexError):
        values[3]
    with pytest.raises(IndexError):
        values[-1]
    with pytest.raises(IndexError):
        values.add(2, 1, 5)
    with pytest.raises(IndexError):
        values.add(0, 3, 5)


def test_range_add_point_query_matches_brute_force():
    rng = random.Random(43)
    for _ in range(100):
        numbers = [rng.randint(-9, 9) for _ in range(rng.randint(1, 15))]
        values = RangeAddPointQuery(numbers)
        expected = list(numbers)
        for _ in range(20):
            left = rng.randrange(len(numbers))
            right = rng.randrange(left, len(numbers))
            delta = rng.randint(-5, 5)
            values.add(left, right, delta)
            for index in range(left, right + 1):
                expected[index] += delta
            probe = rng.randrange(len(numbers))
            assert values[probe] == expected[probe]
        assert list(values) == expected


def test_count_inversions():
    assert count_inversions(NUMBERS) == 8
    assert count_inversions([]) == 0
    assert count_inversions([1, 2, 3]) == 0
    assert count_inversions([3, 2, 1]) == 3
    assert count_inversions([2, 2, 2]) == 0  # 相等的不算
    assert count_inversions([10**9, -10**9, 0]) == 2  # 值很大、有负数：要离散化


def test_count_inversions_matches_brute_force():
    rng = random.Random(44)
    for _ in range(100):
        numbers = [rng.randint(-5, 5) for _ in range(rng.randint(0, 30))]
        expected = sum(
            numbers[first] > numbers[second]
            for first in range(len(numbers))
            for second in range(first + 1, len(numbers))
        )
        assert count_inversions(numbers) == expected


def test_count_inversions_is_fast():
    size = 100_000
    assert count_inversions(list(range(size, 0, -1))) == size * (size - 1) // 2
