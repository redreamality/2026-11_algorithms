import random
from functools import cache
from itertools import combinations, permutations

from dsa.interval_dp import (
    longest_palindromic_subsequence,
    max_coins_bursting_balloons,
    merge_plan,
    merge_stones_min_cost,
    min_insertions_to_palindrome,
)


# ---------- 暴力对照：直接模拟所有合并顺序 / 戳破顺序 ----------

def brute_merge_cost(piles) -> int:
    @cache
    def best(state: tuple) -> int:
        if len(state) <= 1:
            return 0
        return min(
            state[k] + state[k + 1] + best(state[:k] + (state[k] + state[k + 1],) + state[k + 2:])
            for k in range(len(state) - 1)
        )

    return best(tuple(piles))


def brute_palindromic_subsequence(text: str) -> int:
    for size in range(len(text), 0, -1):
        for positions in combinations(range(len(text)), size):
            picked = "".join(text[position] for position in positions)
            if picked == picked[::-1]:
                return size
    return 0


def brute_balloons(numbers) -> int:
    best = 0
    for order in permutations(range(len(numbers))):
        remaining = list(range(len(numbers)))
        coins = 0
        for index in order:
            position = remaining.index(index)
            left = numbers[remaining[position - 1]] if position > 0 else 1
            right = numbers[remaining[position + 1]] if position + 1 < len(remaining) else 1
            coins += left * numbers[index] * right
            remaining.pop(position)
        best = max(best, coins)
    return best


# ---------- 石子合并 ----------

def test_merge_stones_example():
    assert merge_stones_min_cost([3, 4, 2, 4]) == 26


def test_merge_stones_greedy_is_wrong():
    # 每次合最小的相邻两堆：先合 1 + 2 = 3，总代价 15；最优是先合两对，总代价 14
    assert merge_stones_min_cost([2, 2, 1, 2]) == 14


def test_merge_stones_small_cases():
    assert merge_stones_min_cost([]) == 0
    assert merge_stones_min_cost([5]) == 0
    assert merge_stones_min_cost([5, 7]) == 12
    assert merge_stones_min_cost([1, 2, 3]) == 9


def test_merge_stones_random_against_brute_force():
    generator = random.Random(43)
    for _ in range(60):
        piles = [generator.randint(1, 9) for _ in range(generator.randint(1, 7))]
        assert merge_stones_min_cost(piles) == brute_merge_cost(piles), piles


def test_merge_stones_large_input_is_fast():
    piles = [(index * 37) % 50 + 1 for index in range(80)]
    assert merge_stones_min_cost(piles) > 0  # O(n³) = 51 万次，很快；暴力枚举顺序跑不完


# ---------- 合并方案 ----------

def flatten(plan) -> list:
    if isinstance(plan, tuple):
        left, right = plan
        return flatten(left) + flatten(right)
    return [plan]


def plan_cost(plan) -> int:
    """方案里每一次合并的代价 = 合出来的那一堆的石子数。"""
    if isinstance(plan, tuple):
        left, right = plan
        return plan_cost(left) + plan_cost(right) + sum(flatten(plan))
    return 0


def test_merge_plan_example():
    assert merge_plan([3, 4, 2, 4]) == ((3, 4), (2, 4))
    assert merge_plan([5]) == 5


def test_merge_plan_random_is_valid_and_optimal():
    generator = random.Random(4343)
    for _ in range(40):
        piles = [generator.randint(1, 9) for _ in range(generator.randint(1, 7))]
        plan = merge_plan(piles)
        assert flatten(plan) == piles  # 只能合相邻的：从左到右读出来还是原来的顺序
        assert plan_cost(plan) == brute_merge_cost(piles), piles


# ---------- 最长回文子序列 ----------

def test_longest_palindromic_subsequence_examples():
    assert longest_palindromic_subsequence("bbbab") == 4
    assert longest_palindromic_subsequence("cbbd") == 2
    assert longest_palindromic_subsequence("character") == 5  # "carac"


def test_longest_palindromic_subsequence_edges():
    assert longest_palindromic_subsequence("") == 0
    assert longest_palindromic_subsequence("a") == 1
    assert longest_palindromic_subsequence("ab") == 1
    assert longest_palindromic_subsequence("aa") == 2
    assert longest_palindromic_subsequence("racecar") == 7


def test_longest_palindromic_subsequence_random():
    generator = random.Random(516)
    for _ in range(80):
        text = "".join(generator.choice("abc") for _ in range(generator.randint(0, 9)))
        assert longest_palindromic_subsequence(text) == brute_palindromic_subsequence(text), text


def test_longest_palindromic_subsequence_long_input():
    text = "ab" * 500 + "c"
    assert longest_palindromic_subsequence(text) == 999  # O(n²) 一百万格


# ---------- 最少插入 ----------

def test_min_insertions():
    assert min_insertions_to_palindrome("mbadm") == 2
    assert min_insertions_to_palindrome("zzazz") == 0
    assert min_insertions_to_palindrome("leetcode") == 5
    assert min_insertions_to_palindrome("") == 0


# ---------- 戳气球 ----------

def test_balloons_examples():
    assert max_coins_bursting_balloons([3, 1, 5, 8]) == 167
    assert max_coins_bursting_balloons([1, 5]) == 10
    assert max_coins_bursting_balloons([7]) == 7
    assert max_coins_bursting_balloons([]) == 0


def test_balloons_random_against_brute_force():
    generator = random.Random(312)
    for _ in range(40):
        numbers = [generator.randint(0, 9) for _ in range(generator.randint(0, 6))]
        assert max_coins_bursting_balloons(numbers) == brute_balloons(numbers), numbers
