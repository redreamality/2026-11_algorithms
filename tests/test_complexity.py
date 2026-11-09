import pytest

from dsa.complexity import has_duplicate_fast, has_duplicate_slow, has_duplicate_sorted

ALL = [has_duplicate_slow, has_duplicate_sorted, has_duplicate_fast]

CASES = [
    ([], False),
    ([1], False),
    ([1, 2, 3], False),
    ([1, 2, 1], True),
    ([5, 5], True),
    ([3, -1, 4, 1, 5, 9, 2, 6, -1], True),
    (list(range(1000)), False),
    (list(range(1000)) + [999], True),
]


@pytest.mark.parametrize("fn", ALL)
@pytest.mark.parametrize("nums, expected", CASES)
def test_answers(fn, nums, expected):
    assert fn(nums) is expected


@pytest.mark.parametrize("fn", ALL)
def test_does_not_modify_input(fn):
    nums = [3, 1, 2, 1]
    fn(nums)
    assert nums == [3, 1, 2, 1]
