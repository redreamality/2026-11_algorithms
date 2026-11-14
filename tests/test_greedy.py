import random
from collections import Counter

from dsa.greedy import can_reach_end, make_change, merge_intervals, select_activities


def test_select_activities():
    activities = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (6, 10), (8, 11), (12, 16)]
    assert select_activities(activities) == [(1, 4), (5, 7), (8, 11), (12, 16)]


def test_select_activities_touching_is_ok():
    assert select_activities([(5, 7), (1, 3), (3, 5)]) == [(1, 3), (3, 5), (5, 7)]


def test_select_activities_long_one_loses():
    # 最早开始的那个最长，先选它只能选 1 个
    assert select_activities([(0, 10), (1, 2), (3, 4), (5, 6)]) == [(1, 2), (3, 4), (5, 6)]
    assert select_activities([]) == []


def test_select_activities_does_not_mutate():
    activities = [(3, 4), (1, 2)]
    select_activities(activities)
    assert activities == [(3, 4), (1, 2)]


def test_select_activities_count_is_optimal():
    """和暴力枚举所有子集比个数，确认贪心选得最多。"""
    rng = random.Random(18)
    for _ in range(200):
        activities = []
        for _ in range(rng.randrange(8)):
            start = rng.randrange(10)
            activities.append((start, start + rng.randrange(1, 5)))
        best = 0
        for mask in range(1 << len(activities)):
            chosen = sorted(activities[i] for i in range(len(activities)) if mask >> i & 1)
            if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
                best = max(best, len(chosen))
        picked = select_activities(activities)
        assert len(picked) == best
        assert all(picked[i][1] <= picked[i + 1][0] for i in range(len(picked) - 1))


def test_make_change_standard():
    assert make_change([1, 5, 10, 25], 63) == Counter({25: 2, 10: 1, 1: 3})
    assert make_change([100, 50, 20, 10, 5, 1], 188) == Counter({100: 1, 50: 1, 20: 1, 10: 1, 5: 1, 1: 3})
    assert make_change([10, 1, 5], 0) == Counter()


def test_make_change_returns_counter():
    change = make_change([1, 5], 7)
    assert isinstance(change, Counter)
    assert sum(value * count for value, count in change.items()) == 7


def test_make_change_greedy_is_not_optimal():
    assert make_change([1, 3, 4], 6) == Counter({4: 1, 1: 2})  # 最优是两个 3


def test_make_change_impossible():
    assert make_change([5, 10], 3) is None
    assert make_change([4, 3], 6) is None  # 贪心先拿 4 剩 2 就卡住了，虽然 3 + 3 可以


def test_make_change_large_amount_is_fast():
    assert make_change([1, 100], 10**12) == Counter({100: 10**10})


def test_can_reach_end():
    assert can_reach_end([2, 3, 1, 1, 4])
    assert not can_reach_end([3, 2, 1, 0, 4])


def test_can_reach_end_edges():
    assert can_reach_end([0])
    assert not can_reach_end([0, 1])


def test_merge_intervals():
    assert merge_intervals([(8, 10), (1, 3), (2, 6), (15, 18)]) == [(1, 6), (8, 10), (15, 18)]


def test_merge_intervals_touching_and_nested():
    assert merge_intervals([(1, 3), (3, 5)]) == [(1, 5)]
    assert merge_intervals([(1, 10), (2, 3)]) == [(1, 10)]
    assert merge_intervals([]) == []


def test_merge_intervals_does_not_mutate():
    intervals = [(3, 4), (1, 2)]
    merge_intervals(intervals)
    assert intervals == [(3, 4), (1, 2)]
