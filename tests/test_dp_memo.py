from collections import Counter

import pytest

from dsa.dp_memo import (
    CacheInfo,
    climb_stairs,
    fibonacci_memo,
    fibonacci_table,
    memoize,
    min_coins,
    unique_paths,
)

FIBONACCI = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]


def test_memoize_calls_function_once_per_argument():
    calls = []

    @memoize
    def square(number):
        calls.append(number)
        return number * number

    assert [square(3), square(4), square(3), square(3)] == [9, 16, 9, 9]
    assert calls == [3, 4]
    assert square.cache_info() == CacheInfo(hits=2, misses=2, currsize=2)


def test_memoize_keyword_arguments_are_part_of_the_key():
    @memoize
    def power(base, exponent=2):
        return base**exponent

    assert power(3) == 9
    assert power(3, exponent=3) == 27
    assert power(3, exponent=3) == 27
    assert power.cache_info().hits == 1


def test_memoize_recursive_function_counts_like_functools():
    @memoize
    def fibonacci(n):
        return n if n <= 1 else fibonacci(n - 1) + fibonacci(n - 2)

    assert fibonacci(30) == 832040
    assert fibonacci.cache_info() == CacheInfo(hits=28, misses=31, currsize=31)


def test_memoize_cache_clear():
    @memoize
    def double(number):
        return 2 * number

    double(1)
    double(1)
    double.cache_clear()
    assert double.cache_info() == CacheInfo(hits=0, misses=0, currsize=0)
    assert double(1) == 2
    assert double.cache_info() == CacheInfo(hits=0, misses=1, currsize=1)


def test_memoize_keeps_name_and_rejects_unhashable_arguments():
    @memoize
    def total(numbers):
        """求和。"""
        return sum(numbers)

    assert total.__name__ == "total"
    assert total.__doc__ == "求和。"
    assert total((1, 2, 3)) == 6
    with pytest.raises(TypeError):
        total([1, 2, 3])  # list 不可哈希，functools.cache 也会这样报错


@pytest.mark.parametrize("fibonacci", [fibonacci_memo, fibonacci_table])
def test_fibonacci_small(fibonacci):
    assert [fibonacci(n) for n in range(len(FIBONACCI))] == FIBONACCI


@pytest.mark.parametrize("fibonacci", [fibonacci_memo, fibonacci_table])
def test_fibonacci_is_fast(fibonacci):
    # 朴素递归算 fibonacci(80) 要跑到天荒地老；O(n) 一眨眼。
    assert fibonacci(80) == 23416728348467685


def test_fibonacci_memo_no_shared_state():
    assert fibonacci_memo(30) == 832040
    assert fibonacci_memo(30) == 832040


def test_fibonacci_table_large_no_recursion_limit():
    # 填表没有递归，n 很大也不会 RecursionError
    assert fibonacci_table(5000) == fibonacci_table(4999) + fibonacci_table(4998)
    assert fibonacci_table(100) == 354224848179261915075


def test_climb_stairs():
    assert [climb_stairs(n) for n in range(6)] == [1, 1, 2, 3, 5, 8]
    assert climb_stairs(45) == 1836311903


def check_change(change, denominations, amount, expected_count):
    assert isinstance(change, Counter)
    assert set(change) <= set(denominations)
    assert sum(value * count for value, count in change.items()) == amount
    assert sum(change.values()) == expected_count


def test_min_coins_basic():
    assert min_coins([1, 2, 5], 11) == Counter({5: 2, 1: 1})
    assert min_coins([1], 0) == Counter()
    assert min_coins([1], 7) == Counter({1: 7})


def test_min_coins_greedy_fails():
    assert min_coins([1, 3, 4], 6) == Counter({3: 2})


def test_min_coins_impossible():
    assert min_coins([2], 3) is None
    assert min_coins([5, 10], 7) is None


def test_min_coins_large_amount():
    check_change(min_coins([1, 7, 10], 10_000), [1, 7, 10], 10_000, 1000)


def test_min_coins_against_brute_force():
    for denominations in ([1, 3, 4], [2, 5], [3, 7, 11], [1, 5, 6, 9]):
        for amount in range(40):
            fewest = {0: 0}
            for value in range(1, amount + 1):
                options = [fewest[value - coin] + 1 for coin in denominations if coin <= value and value - coin in fewest]
                if options:
                    fewest[value] = min(options)
            change = min_coins(denominations, amount)
            if amount in fewest:
                check_change(change, denominations, amount, fewest[amount])
            else:
                assert change is None


def test_unique_paths():
    assert unique_paths(1, 1) == 1
    assert unique_paths(1, 5) == 1
    assert unique_paths(3, 2) == 3
    assert unique_paths(3, 7) == 28
    assert unique_paths(10, 10) == 48620


def test_unique_paths_with_blocked_cells():
    assert unique_paths(3, 4, frozenset({(1, 1)})) == 4
    assert unique_paths(3, 3, frozenset({(0, 1), (1, 0)})) == 0  # 起点被围死
    assert unique_paths(2, 2, frozenset({(0, 0)})) == 0  # 起点被堵
    assert unique_paths(2, 2, frozenset({(1, 1)})) == 0  # 终点被堵
