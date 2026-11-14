import io
import random
from functools import total_ordering

import pytest

from dsa.merge_sort import count_inversions, merge, merge_sort


@total_ordering
class Card:
    """只按 key 比大小；tag 用来看相等的元素有没有换位置。"""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __eq__(self, other):
        return self.key == other.key

    def __lt__(self, other):
        return self.key < other.key


def test_merge():
    assert list(merge([1, 4, 6], [2, 3, 7, 8])) == [1, 2, 3, 4, 6, 7, 8]


def test_merge_with_empty():
    assert list(merge([], [1, 2])) == [1, 2]
    assert list(merge([1, 2], [])) == [1, 2]
    assert list(merge([], [])) == []


def test_merge_is_lazy_and_accepts_iterators():
    def numbers(*values):
        yield from values

    result = merge(numbers(1, 5), numbers(2, 3))
    assert iter(result) is result  # 返回迭代器，不是一次性建好的 list
    assert next(result) == 1
    assert list(result) == [2, 3, 5]


def test_merge_works_on_infinite_streams():
    def multiples(step):
        value = 0
        while True:
            yield value
            value += step

    merged = merge(multiples(3), multiples(5))
    assert [next(merged) for _ in range(8)] == [0, 0, 3, 5, 6, 9, 10, 12]


def test_merge_files():
    left = io.StringIO("09:00 a\n09:30 a\n")
    right = io.StringIO("09:10 b\n09:30 b\n")
    assert [line.strip() for line in merge(left, right, key=lambda line: line[:5])] == [
        "09:00 a", "09:10 b", "09:30 a", "09:30 b"
    ]


def test_merge_takes_left_first_on_tie():
    left, right = [Card(1, "a")], [Card(1, "b")]
    assert [card.tag for card in merge(left, right)] == ["a", "b"]
    assert [card.tag for card in merge(left, right, reverse=True)] == ["a", "b"]


def test_merge_reverse():
    assert list(merge([9, 5, 1], [8, 5, 2], reverse=True)) == [9, 8, 5, 5, 2, 1]


@pytest.mark.parametrize("values", [[], [1], [1, 2, 3], [3, 2, 1], [5, -1, 5, 0, -1]])
def test_merge_sort_small(values):
    assert merge_sort(values) == sorted(values)


@pytest.mark.parametrize("seed", range(5))
def test_merge_sort_random(seed):
    rng = random.Random(seed)
    values = [rng.randint(-50, 50) for _ in range(rng.randint(0, 200))]
    assert merge_sort(values) == sorted(values)
    assert merge_sort(values, reverse=True) == sorted(values, reverse=True)


def test_merge_sort_accepts_any_iterable():
    assert merge_sort((3, 1, 2)) == [1, 2, 3]
    assert merge_sort("cab") == ["a", "b", "c"]
    assert merge_sort(value * 2 for value in [3, 1]) == [2, 6]


def test_merge_sort_returns_new_list():
    values = [3, 1, 2]
    result = merge_sort(values)
    assert values == [3, 1, 2]
    assert result == [1, 2, 3] and result is not values
    single = [7]
    assert merge_sort(single) is not single


def test_merge_sort_is_stable():
    cards = [Card(key, index) for index, key in enumerate([2, 1, 2, 1, 2, 1])]
    assert [card.tag for card in merge_sort(cards)] == [1, 3, 5, 0, 2, 4]
    assert [card.tag for card in merge_sort(cards, reverse=True)] == [0, 2, 4, 1, 3, 5]


def test_merge_sort_key_matches_sorted():
    rng = random.Random(8)
    for _ in range(30):
        records = [(rng.randint(0, 5), index) for index in range(rng.randint(0, 40))]
        reverse = rng.random() < 0.5
        assert merge_sort(records, key=lambda record: record[0], reverse=reverse) == sorted(
            records, key=lambda record: record[0], reverse=reverse
        )


def test_merge_sort_key_called_once_per_element():
    calls = []

    def slow_key(value):
        calls.append(value)
        return -value

    assert merge_sort(range(50), key=slow_key) == list(range(49, -1, -1))
    assert sorted(calls) == list(range(50)), "key 应该对每个元素恰好调用一次"


def test_merge_sort_large_is_fast():
    values = list(range(50_000, 0, -1))  # O(n²) 的写法在这里会慢得明显
    assert merge_sort(values) == list(range(1, 50_001))


def test_count_inversions():
    assert count_inversions([2, 4, 1, 3, 5]) == 3  # (2,1) (4,1) (4,3)
    assert count_inversions([]) == 0
    assert count_inversions([1, 2, 3]) == 0
    assert count_inversions([5, 4, 3, 2, 1]) == 10
    assert count_inversions([1, 1, 1]) == 0  # 相等不算
    assert count_inversions(["b", "a"]) == 1
    assert count_inversions([("x", 3), ("y", 1)], key=lambda pair: pair[1]) == 1


def test_count_inversions_random():
    rng = random.Random(42)
    values = [rng.randint(0, 20) for _ in range(150)]
    brute = sum(values[i] > values[j] for i in range(len(values)) for j in range(i + 1, len(values)))
    assert count_inversions(values) == brute
    assert count_inversions(iter(values)) == brute
