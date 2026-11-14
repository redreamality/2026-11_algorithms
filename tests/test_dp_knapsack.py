import random
from itertools import combinations

from dsa.dp_knapsack import (
    Item,
    choose_items,
    diff_lines,
    edit_distance,
    longest_common_subsequence,
    longest_increasing_subsequence,
)


def is_subsequence(short, long) -> bool:
    iterator = iter(long)
    return all(element in iterator for element in short)


def total_value(items) -> int:
    return sum(item.value for item in items)


def total_cost(items) -> int:
    return sum(item.cost for item in items)


def make_items(costs, values):
    return [Item(f"item{index}", cost, value) for index, (cost, value) in enumerate(zip(costs, values))]


# ---------- 0-1 背包 ----------

def check_choice(items, budget, expected_value):
    chosen = choose_items(items, budget)
    assert total_value(chosen) == expected_value
    assert total_cost(chosen) <= budget
    assert len(set(chosen)) == len(chosen)  # 每件最多一次
    assert [item for item in items if item in chosen] == chosen  # 保持原来的先后顺序


def test_choose_items_basic():
    items = make_items([1, 3, 4], [15, 20, 30])
    assert choose_items(items, 4) == [items[0], items[1]]


def test_choose_items_each_once():
    items = make_items([2], [3])
    assert choose_items(items, 10) == items  # 不能把同一件拿 5 次


def test_choose_items_too_heavy_or_empty():
    assert choose_items(make_items([5, 6], [10, 20]), 4) == []
    assert choose_items([], 10) == []
    assert choose_items(make_items([1, 2], [5, 6]), 0) == []


def test_choose_items_greedy_by_ratio_fails():
    backlog = [
        Item("导出 Excel", 5, 50),
        Item("暗色模式", 4, 30),
        Item("单点登录", 6, 66),
        Item("消息推送", 2, 10),
        Item("搜索提速", 5, 50),
    ]
    assert [item.name for item in choose_items(backlog, 10)] == ["导出 Excel", "搜索提速"]


def test_choose_items_larger():
    weights = [12, 7, 11, 8, 9, 6, 5, 14, 3, 10, 4, 13, 2, 15, 1, 16, 7, 9, 5, 8]
    values = [24, 13, 23, 15, 16, 11, 9, 29, 5, 19, 8, 26, 3, 31, 1, 33, 14, 17, 10, 16]
    check_choice(make_items(weights, values), 50, 103)


def test_choose_items_against_brute_force():
    rng = random.Random(20)
    for _ in range(100):
        items = make_items([rng.randrange(1, 8) for _ in range(7)], [rng.randrange(1, 20) for _ in range(7)])
        budget = rng.randrange(15)
        best = max(
            total_value(subset)
            for size in range(len(items) + 1)
            for subset in combinations(items, size)
            if total_cost(subset) <= budget
        )
        check_choice(items, budget, best)


# ---------- LCS ----------

def reference_lcs_length(first, second) -> int:
    """用另一种 O(n·m) 的写法算长度，只用来核对。"""
    previous = [0] * (len(second) + 1)
    for element in first:
        current = [0]
        for index, other in enumerate(second):
            current.append(previous[index] + 1 if element == other else max(previous[index + 1], current[index]))
        previous = current
    return previous[-1]


def test_longest_common_subsequence_strings():
    for first, second, length in [("ABCBDAB", "BDCABA", 4), ("ABCB", "BDCAB", 3), ("AGGTAB", "GXTXAYB", 4)]:
        common = longest_common_subsequence(first, second)
        assert isinstance(common, list)
        assert len(common) == length
        assert is_subsequence(common, first) and is_subsequence(common, second)


def test_longest_common_subsequence_edges():
    assert longest_common_subsequence("", "ABC") == []
    assert longest_common_subsequence("ABC", "XYZ") == []
    assert longest_common_subsequence("SAME", "SAME") == list("SAME")


def test_longest_common_subsequence_of_lines():
    old = ["import os", "def main():", "    print(1)", "main()"]
    new = ["import os", "import sys", "def main():", "    print(2)", "main()"]
    assert longest_common_subsequence(old, new) == ["import os", "def main():", "main()"]


def test_longest_common_subsequence_random():
    rng = random.Random(7)
    for _ in range(100):
        first = "".join(rng.choice("ABC") for _ in range(rng.randrange(12)))
        second = "".join(rng.choice("ABC") for _ in range(rng.randrange(12)))
        common = longest_common_subsequence(first, second)
        assert len(common) == reference_lcs_length(first, second)
        assert is_subsequence(common, first) and is_subsequence(common, second)


# ---------- diff ----------

def apply_diff(diff):
    old = [line[2:] for line in diff if line[:2] in ("  ", "- ")]
    new = [line[2:] for line in diff if line[:2] in ("  ", "+ ")]
    return old, new


def test_diff_lines_example():
    assert diff_lines(["a", "b", "c"], ["a", "c", "d"]) == ["  a", "- b", "  c", "+ d"]


def test_diff_lines_replace_puts_minus_first():
    assert diff_lines(["host=db1", "port=5432"], ["host=db2", "port=5432"]) == [
        "- host=db1",
        "+ host=db2",
        "  port=5432",
    ]


def test_diff_lines_edges():
    assert diff_lines([], []) == []
    assert diff_lines([], ["x"]) == ["+ x"]
    assert diff_lines(["x"], []) == ["- x"]
    assert diff_lines(["same"], ["same"]) == ["  same"]


def test_diff_lines_is_minimal_and_reconstructs_both_sides():
    rng = random.Random(42)
    for _ in range(100):
        old = [rng.choice("abcd") for _ in range(rng.randrange(10))]
        new = [rng.choice("abcd") for _ in range(rng.randrange(10))]
        diff = diff_lines(old, new)
        assert apply_diff(diff) == (old, new)
        kept = sum(line.startswith("  ") for line in diff)
        assert kept == reference_lcs_length(old, new)
        # 每行都只有这三种前缀，和 difflib.ndiff 的习惯一样
        assert all(line[:2] in ("  ", "- ", "+ ") for line in diff)


# ---------- LIS ----------

def check_increasing(numbers, expected_length):
    result = longest_increasing_subsequence(numbers)
    assert len(result) == expected_length
    assert is_subsequence(result, numbers)
    assert all(result[index] < result[index + 1] for index in range(len(result) - 1))


def test_longest_increasing_subsequence_basic():
    check_increasing([10, 9, 2, 5, 3, 7, 101, 18], 4)


def test_longest_increasing_subsequence_strict_and_edges():
    assert longest_increasing_subsequence([]) == []
    check_increasing([2, 2, 2], 1)  # 严格递增，相等不算
    check_increasing([5, 4, 3, 2, 1], 1)
    assert longest_increasing_subsequence(list(range(300))) == list(range(300))


# ---------- 编辑距离（选做） ----------

def test_edit_distance():
    assert edit_distance("kitten", "sitting") == 3
    assert edit_distance("", "abc") == 3
    assert edit_distance("same", "same") == 0
    assert edit_distance("recieve", "receive") == 2
