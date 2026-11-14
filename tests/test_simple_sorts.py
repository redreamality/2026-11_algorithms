import random

import pytest

from dsa.simple_sorts import insertion_sort, selection_sort

SORTS = [selection_sort, insertion_sort]


@pytest.mark.parametrize("sort", SORTS)
def test_basic(sort):
    items = [5, 2, 4, 6, 1, 3]
    assert sort(items) is None  # 原地排序，返回 None
    assert items == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize("items", [[], [7], [2, 1], [1, 2]])
def test_tiny(sort, items):
    expected = sorted(items)
    sort(items)
    assert items == expected


@pytest.mark.parametrize("sort", SORTS)
def test_duplicates_and_negatives(sort):
    items = [3, -1, 3, 0, -1, 2]
    sort(items)
    assert items == [-1, -1, 0, 2, 3, 3]


@pytest.mark.parametrize("sort", SORTS)
def test_strings(sort):
    words = ["pear", "apple", "fig"]
    sort(words)
    assert words == ["apple", "fig", "pear"]


@pytest.mark.parametrize("sort", SORTS)
def test_key_and_reverse_are_keyword_only(sort):
    with pytest.raises(TypeError):
        sort([2, 1], len)


@pytest.mark.parametrize("sort", SORTS)
def test_key(sort):
    words = ["ccc", "a", "bb"]
    sort(words, key=len)
    assert words == ["a", "bb", "ccc"]


@pytest.mark.parametrize("sort", SORTS)
def test_reverse(sort):
    items = [3, 1, 4, 1, 5, 9, 2, 6]
    sort(items, reverse=True)
    assert items == [9, 6, 5, 4, 3, 2, 1, 1]


@pytest.mark.parametrize("sort", SORTS)
def test_random_matches_sorted(sort):
    rng = random.Random(7)
    for _ in range(50):
        items = [rng.randint(0, 20) for _ in range(rng.randint(0, 30))]
        reverse = rng.random() < 0.5
        expected = sorted(items, reverse=reverse)
        sort(items, reverse=reverse)
        assert items == expected


@pytest.mark.parametrize("sort", SORTS)
def test_key_called_once_per_element(sort):
    calls = []

    def slow_key(value):
        calls.append(value)
        return -value

    items = list(range(30))
    sort(items, key=slow_key)
    assert items == list(range(29, -1, -1))
    assert sorted(calls) == list(range(30)), "key 应该对每个元素恰好调用一次"


def test_insertion_sort_is_stable():
    people = [("小红", 90), ("小明", 80), ("小刚", 90), ("小李", 80)]
    insertion_sort(people, key=lambda person: person[1])
    assert people == [("小明", 80), ("小李", 80), ("小红", 90), ("小刚", 90)]


def test_insertion_sort_reverse_is_still_stable():
    people = [("小红", 90), ("小明", 80), ("小刚", 90), ("小李", 80)]
    insertion_sort(people, key=lambda person: person[1], reverse=True)
    assert people == [("小红", 90), ("小刚", 90), ("小明", 80), ("小李", 80)]  # 和 list.sort 一致


def test_insertion_sort_matches_list_sort_with_key_and_reverse():
    rng = random.Random(3)
    for _ in range(50):
        records = [(rng.randint(0, 5), index) for index in range(rng.randint(0, 25))]
        reverse = rng.random() < 0.5
        expected = sorted(records, key=lambda record: record[0], reverse=reverse)
        insertion_sort(records, key=lambda record: record[0], reverse=reverse)
        assert records == expected


def test_insertion_sort_multi_pass_sorting():
    tickets = [(101, 2, "11-03"), (102, 3, "11-05"), (103, 2, "11-01"), (104, 3, "11-02"), (105, 1, "11-04")]
    insertion_sort(tickets, key=lambda ticket: ticket[2])
    insertion_sort(tickets, key=lambda ticket: ticket[1], reverse=True)
    assert [ticket[0] for ticket in tickets] == [104, 102, 103, 101, 105]
