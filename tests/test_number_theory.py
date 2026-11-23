import math
import random
import time

import pytest

from dsa.number_theory import (
    MOD,
    CombinationTable,
    fraction_mod,
    gcd,
    is_prime,
    lcm,
    lucky_draw_probability,
    mod_inverse,
    mod_pow,
    primes_up_to,
)


def test_mod_is_the_usual_prime():
    assert MOD == 1_000_000_007


@pytest.mark.parametrize("first, second, expected", [
    (190, 28, 2), (28, 190, 2), (12, 18, 6), (17, 5, 1), (7, 0, 7), (0, 7, 7), (0, 0, 0), (1, 1, 1),
])
def test_gcd(first, second, expected):
    assert gcd(first, second) == expected


def test_gcd_matches_math_gcd_and_is_fast():
    rng = random.Random(40)
    for _ in range(500):
        first, second = rng.randrange(10**18), rng.randrange(10**18)
        assert gcd(first, second) == math.gcd(first, second)
    # 相邻斐波那契数是辗转相除最慢的情况，也只要约 90 步
    assert gcd(2880067194370816120, 4660046610375530309) == 1


@pytest.mark.parametrize("first, second, expected", [
    (190, 28, 2660), (4, 6, 12), (7, 1, 7), (5, 5, 5), (0, 9, 0), (9, 0, 0),
])
def test_lcm(first, second, expected):
    assert lcm(first, second) == expected


def test_is_prime_small_numbers():
    expected = [n for n in range(200) if n > 1 and all(n % d for d in range(2, n))]
    assert [n for n in range(200) if is_prime(n)] == expected


def test_is_prime_large():
    assert is_prime(MOD)
    assert is_prime(998_244_353)
    assert not is_prime(MOD * 3)
    assert not is_prime(31_607 * 31_627)  # 两个接近 √(10⁹) 的质数相乘
    assert not is_prime(10**9)


def test_primes_up_to_small():
    assert primes_up_to(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert primes_up_to(0) == []
    assert primes_up_to(1) == []
    assert primes_up_to(2) == [2]
    assert primes_up_to(9) == [2, 3, 5, 7]  # 9 = 3 * 3 要被划掉


def test_primes_up_to_matches_is_prime():
    assert primes_up_to(500) == [n for n in range(501) if is_prime(n)]


def test_sieve_is_fast():
    start = time.perf_counter()
    primes = primes_up_to(10**6)
    assert time.perf_counter() - start < 3, "筛到一百万应该一两秒内完成"
    assert len(primes) == 78_498
    assert primes[-1] == 999_983


@pytest.mark.parametrize("base, exponent, modulus", [
    (7, 9, 11), (2, 10, MOD), (95, 0, 11), (0, 0, 7), (0, 5, 7), (123, 1, 1000), (5, 3, 1),
    (10**12, 3, MOD), (3, 200, 13),
])
def test_mod_pow(base, exponent, modulus):
    assert mod_pow(base, exponent, modulus) == pow(base, exponent, modulus)


def test_mod_pow_is_log_n():
    # O(exponent) 的写法要循环 10¹⁸ 次，永远跑不完；O(log) 只要 60 步左右
    assert mod_pow(2, 10**18, MOD) == pow(2, 10**18, MOD)
    assert mod_pow(95, MOD - 2, MOD) == 231_578_949


def test_mod_pow_negative_exponent():
    with pytest.raises(ValueError):
        mod_pow(2, -1, MOD)


def test_mod_inverse():
    assert mod_inverse(7, 11) == 8
    assert mod_inverse(95, 11) == 8  # 95 % 11 == 7
    assert mod_inverse(95) == 231_578_949
    for value in range(1, 11):
        assert value * mod_inverse(value, 11) % 11 == 1
    for value in (2, 12345, MOD - 1, 10**18):
        inverse = mod_inverse(value)
        assert 0 <= inverse < MOD and value * inverse % MOD == 1


def test_mod_inverse_of_multiple_raises():
    with pytest.raises(ValueError):
        mod_inverse(0)
    with pytest.raises(ValueError):
        mod_inverse(22, 11)


def test_combination_table_small():
    table = CombinationTable(20)
    assert table.choose(20, 2) == 190
    assert table.choose(8, 2) == 28
    assert table.choose(0, 0) == 1
    assert table.choose(5, 0) == 1 and table.choose(5, 5) == 1
    for n in range(21):
        for k in range(n + 1):
            assert table.choose(n, k) == math.comb(n, k) % MOD


def test_combination_table_out_of_range():
    table = CombinationTable(10)
    assert table.choose(5, 7) == 0
    assert table.choose(5, -1) == 0
    with pytest.raises(ValueError):
        table.choose(11, 2)


def test_combination_table_other_modulus():
    table = CombinationTable(10, 13)
    for n in range(11):
        for k in range(n + 1):
            assert table.choose(n, k) == math.comb(n, k) % 13


def test_combination_table_large_and_fast():
    start = time.perf_counter()
    table = CombinationTable(10**5)
    assert table.choose(10**5, 3) == math.comb(10**5, 3) % MOD
    assert table.choose(10**5, 5 * 10**4) == 149_033_233
    assert time.perf_counter() - start < 3, "预处理应该是 O(n)，不要每个阶乘各做一次快速幂"


def test_fraction_mod():
    assert fraction_mod(14, 95, 11) == 2
    assert fraction_mod(14, 95) == 242_105_265
    assert fraction_mod(28, 190) == fraction_mod(14, 95)  # 约不约分结果一样
    assert fraction_mod(1, 2) == (MOD + 1) // 2
    assert fraction_mod(0, 5) == 0
    with pytest.raises(ValueError):
        fraction_mod(1, MOD)


def test_lucky_draw_probability():
    assert lucky_draw_probability(20, 2) == 242_105_265
    assert lucky_draw_probability(20, 0) == 1  # 一张不抽，“全是幸运卡”必然成立
    assert lucky_draw_probability(20, 9) == 0  # 只有 8 张幸运卡，抽 9 张不可能全是
    assert lucky_draw_probability(1, 1) == 0  # 1 不是质数
    assert lucky_draw_probability(2, 1) == fraction_mod(1, 2)
    # 1 - P 的取模写法：(1 - P + MOD) % MOD，对应 81 / 95
    assert (1 - lucky_draw_probability(20, 2) + MOD) % MOD == fraction_mod(81, 95)


def test_lucky_draw_probability_large():
    start = time.perf_counter()
    assert lucky_draw_probability(10**5, 3) == 859_555_632
    assert lucky_draw_probability(10**5, 2) == 344_717_780
    assert time.perf_counter() - start < 5
