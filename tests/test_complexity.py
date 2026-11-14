import pytest

from dsa.complexity import find_duplicates, has_duplicate_fast, has_duplicate_slow, has_duplicate_sorted

ALL = [has_duplicate_slow, has_duplicate_sorted, has_duplicate_fast]

CASES = [
    ([], False),
    ([1], False),
    ([1, 2, 3], False),
    ([1, 2, 1], True),
    ([5, 5], True),
    ([3, -1, 4, 1, 5, 9, 2, 6, -1], True),
    (["b@x.com", "a@x.com", "b@x.com"], True),
    (["a", "A"], False),
    (list(range(1000)), False),
    (list(range(1000)) + [999], True),
]


@pytest.mark.parametrize("function", ALL)
@pytest.mark.parametrize("items, expected", CASES)
def test_answers(function, items, expected):
    assert function(items) is expected


@pytest.mark.parametrize("function", ALL)
def test_does_not_modify_input(function):
    items = [3, 1, 2, 1]
    function(items)
    assert items == [3, 1, 2, 1]


def test_fast_accepts_generator_and_stops_early():
    consumed = []

    def stream():
        for value in [1, 2, 1, 3, 4]:
            consumed.append(value)
            yield value

    assert has_duplicate_fast(stream()) is True
    assert consumed == [1, 2, 1]  # 碰到第一个重复就停，不读后面的
    assert has_duplicate_fast(x % 5 for x in range(5)) is False


def test_find_duplicates_order_and_uniqueness():
    emails = ["a", "b", "a", "c", "b", "a", "c"]
    assert find_duplicates(emails) == ["a", "b", "c"]
    assert find_duplicates(["z", "y", "y", "z"]) == ["y", "z"]  # 按第二次出现的先后
    assert find_duplicates([]) == []
    assert find_duplicates(iter([1, 2, 3])) == []
    assert find_duplicates(word.lower() for word in ["Go", "go", "GO"]) == ["go"]
