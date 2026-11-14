import random
import statistics

import pytest

from dsa.quick_sort import partition, quick_sort, select


def check_partition(items, low, high):
    """分区 items[low..high]，检查返回值和左右两边的大小关系，返回 (分区后的列表, pivot_index)。"""
    before = list(items)
    pivot_index = partition(items, low, high)
    assert low <= pivot_index <= high
    assert items[pivot_index] == before[high], "基准应该是原来的 items[high]"
    assert all(value <= items[pivot_index] for value in items[low:pivot_index])
    assert all(value >= items[pivot_index] for value in items[pivot_index + 1 : high + 1])
    assert sorted(items[low : high + 1]) == sorted(before[low : high + 1]), "元素只能交换，不能丢或多"
    return items, pivot_index


def test_partition_basic():
    _, pivot_index = check_partition([5, 2, 8, 1, 9, 3, 6, 4], 0, 7)
    assert pivot_index == 3


def test_partition_pivot_is_min_or_max():
    assert check_partition([3, 2, 1], 0, 2)[1] == 0
    assert check_partition([1, 2, 3], 0, 2)[1] == 2


def test_partition_single_element():
    assert partition([7], 0, 0) == 0


def test_partition_only_touches_range():
    items = [9, 9, 5, 1, 3, 0, 0]
    check_partition(items, 2, 4)
    assert items[:2] == [9, 9] and items[5:] == [0, 0]


@pytest.mark.parametrize("values", [[], [1], [2, 1], [1, 2, 3], [3, 2, 1], [5, -1, 5, 0, -1], [4, 4, 4, 4]])
def test_quick_sort_small(values):
    items = list(values)
    quick_sort(items)
    assert items == sorted(values)


@pytest.mark.parametrize("seed", range(5))
def test_quick_sort_random(seed):
    rng = random.Random(seed)
    values = [rng.randint(-50, 50) for _ in range(rng.randint(0, 300))]
    items = list(values)
    quick_sort(items)
    assert items == sorted(values)
    quick_sort(items, reverse=True)
    assert items == sorted(values, reverse=True)


def test_quick_sort_is_in_place():
    items = [3, 1, 2]
    alias = items
    assert quick_sort(items) is None
    assert alias == [1, 2, 3]


def test_quick_sort_key_and_reverse_are_keyword_only():
    with pytest.raises(TypeError):
        quick_sort([2, 1], len)


def test_quick_sort_with_key():
    players = [("小红", 88), ("小明", 95), ("小刚", 72), ("小李", 99)]
    quick_sort(players, key=lambda player: player[1], reverse=True)
    assert players == [("小李", 99), ("小明", 95), ("小红", 88), ("小刚", 72)]


def test_quick_sort_key_does_not_compare_items():
    class Opaque:
        """自己不能比大小，只能通过 key 排。"""

        def __init__(self, weight):
            self.weight = weight

    items = [Opaque(weight) for weight in [3, 1, 3, 2]]
    quick_sort(items, key=lambda item: item.weight)
    assert [item.weight for item in items] == [1, 2, 3, 3]


def test_quick_sort_key_called_once_per_element():
    calls = []

    def slow_key(value):
        calls.append(value)
        return -value

    items = list(range(40))
    quick_sort(items, key=slow_key)
    assert items == list(range(39, -1, -1))
    assert sorted(calls) == list(range(40)), "key 应该对每个元素恰好调用一次"


def test_quick_sort_sorted_input_is_fast():
    # 固定拿最后一个当基准，这里会退化成 O(n²)，递归也会太深；随机基准没问题
    items = list(range(20_000))
    quick_sort(items)
    assert items == list(range(20_000))


def test_select():
    assert select([7, 2, 9, 4, 1], 0) == 1
    assert select([7, 2, 9, 4, 1], 2) == 4
    assert select([7, 2, 9, 4, 1], 4) == 9
    assert select([5], 0) == 5
    assert select((value for value in [3, 1, 2]), 1) == 2  # 任何可迭代对象都行


def test_select_does_not_modify_input():
    values = [7, 2, 9, 4, 1]
    select(values, 2)
    assert values == [7, 2, 9, 4, 1]


def test_select_with_key():
    products = [("显示器", 899), ("鼠标", 59), ("键盘", 199)]
    assert select(products, 0, key=lambda product: product[1]) == ("鼠标", 59)
    assert select(products, 2, key=lambda product: product[1]) == ("显示器", 899)


def test_select_random_and_median():
    rng = random.Random(7)
    values = [rng.randint(0, 30) for _ in range(101)]
    for k in (0, 17, 50, 100):
        assert select(values, k) == sorted(values)[k]
    assert select(values, (len(values) - 1) // 2) == statistics.median_low(values)


def test_select_large_sorted_input_is_fast():
    values = list(range(50_000))
    assert select(values, 25_000) == 25_000


def test_select_out_of_range():
    with pytest.raises(IndexError):
        select([1, 2, 3], 3)
    with pytest.raises(IndexError):
        select([1, 2, 3], -1)
    with pytest.raises(IndexError):
        select([], 0)
