import bisect
import functools
import math
import random

import pytest

from dsa.binary_search import bisect_left, bisect_right, first_true, index, isqrt

A = [1, 3, 4, 7, 7, 7, 9, 12, 15, 18]


@functools.total_ordering
class Num:
    """会数比较次数的数字，用来检查是不是真的 O(log n)。"""

    count = 0

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        Num.count += 1
        return self.value == other.value

    def __lt__(self, other):
        Num.count += 1
        return self.value < other.value

    __hash__ = None


@pytest.mark.parametrize("target, left, right", [
    (7, 3, 6),     # 有重复
    (9, 6, 7),     # 只出现一次
    (8, 6, 6),     # 不存在：两者相等，都是插入位置
    (0, 0, 0),     # 比所有都小
    (99, 10, 10),  # 比所有都大
])
def test_bisect_left_right(target, left, right):
    assert bisect_left(A, target) == left
    assert bisect_right(A, target) == right


def test_bisect_empty():
    assert bisect_left([], 3) == 0
    assert bisect_right([], 3) == 0


def test_count_occurrences():
    items = [2, 2, 2, 2, 2]
    assert bisect_right(items, 2) - bisect_left(items, 2) == 5


def test_lo_hi_limit_the_range():
    assert bisect_left(A, 7, lo=4) == 4
    assert bisect_right(A, 7, hi=5) == 5
    assert bisect_left(A, 100, 2, 5) == 5
    assert bisect_left(A, 0, 2, 5) == 2
    with pytest.raises(ValueError):
        bisect_left(A, 1, lo=-1)


def test_key_applies_to_items_not_target():
    people = [("小明", 18), ("小红", 25), ("小刚", 25), ("小李", 40)]
    age = lambda person: person[1]  # noqa: E731
    assert bisect_left(people, 25, key=age) == 1
    assert bisect_right(people, 25, key=age) == 3
    assert bisect_left(people, 99, key=age) == 4


def test_matches_standard_library_random():
    rng = random.Random(6)
    for _ in range(300):
        items = sorted(rng.randint(0, 30) for _ in range(rng.randint(0, 25)))
        target = rng.randint(-2, 32)
        lo = rng.randint(0, len(items))
        hi = rng.randint(lo, len(items))
        assert bisect_left(items, target, lo, hi) == bisect.bisect_left(items, target, lo, hi)
        assert bisect_right(items, target, lo, hi) == bisect.bisect_right(items, target, lo, hi)


def test_bisect_is_logarithmic():
    items = [Num(2 * k) for k in range(1024)]
    for target in (0, 777, 1000, 2046, 2047):
        for search in (bisect_left, bisect_right):
            Num.count = 0
            search(items, Num(target))
            assert Num.count <= 40, f"找 {target} 比较了 {Num.count} 次，不像 O(log n)"


def test_index():
    for position, value in enumerate(A):
        if value != 7:
            assert index(A, value) == position
    assert index(A, 7) == 3  # 有重复时返回最左边那个
    assert index([("a", 1), ("b", 5)], 5, key=lambda pair: pair[1]) == 1


@pytest.mark.parametrize("target", [0, 2, 8, 100])
def test_index_missing_raises_value_error(target):
    with pytest.raises(ValueError):
        index(A, target)
    with pytest.raises(ValueError):
        index([], target)


def test_first_true():
    assert first_true(0, 100, lambda x: x >= 37) == 37
    assert first_true(0, 100, lambda x: True) == 0
    assert first_true(0, 100, lambda x: False) == 100  # 都为假返回 high
    assert first_true(5, 5, lambda x: True) == 5  # 空区间
    assert first_true(-50, 50, lambda x: x * 3 > -10) == -3


def test_first_true_calls_predicate_log_times():
    calls = []

    def is_broken(version):
        calls.append(version)
        return version >= 777_777

    assert first_true(0, 1_000_000, is_broken) == 777_777
    assert len(calls) <= 25, f"调用了 {len(calls)} 次"


@pytest.mark.parametrize("number", [0, 1, 2, 3, 4, 8, 9, 15, 16, 17, 99, 100, 10**12 - 1, 10**12])
def test_isqrt(number):
    assert isqrt(number) == math.isqrt(number)


def test_isqrt_huge():
    assert isqrt(10**30) == 10**15
    assert isqrt(10**30 - 1) == 10**15 - 1
    assert isqrt(10**80 + 12345) == 10**40


def test_isqrt_negative():
    with pytest.raises(ValueError):
        isqrt(-1)
