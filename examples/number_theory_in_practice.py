"""第 40 课实战：数论在 Python 里怎么写。

主线题目：抽奖箱里有编号 1..20 的卡，编号是质数的是幸运卡（8 张）。随机抽 2 张，
两张都是幸运卡的概率 = C(8, 2) / C(20, 2) = 28 / 190 = 14 / 95。

1. 精确的分数 → fractions.Fraction，自动用 gcd 约分。
2. gcd / lcm / 组合数 → math.gcd、math.lcm、math.comb。
3. 笔试要求“输出 P · Q⁻¹ mod (10**9 + 7)” → pow(Q, MOD - 2, MOD) 或 pow(Q, -1, MOD) 求逆元。
4. 同一个模数下要算很多次组合数 → 预处理阶乘和阶乘的逆元，每次 O(1)。
5. 为什么要取模：大整数的乘法不是 O(1)，下面会实际计时对比。

运行：uv run examples/number_theory_in_practice.py
"""

import math
import time
from fractions import Fraction

MOD = 10**9 + 7


def lucky_cards(card_count: int) -> list[int]:
    """埃氏筛：1..card_count 里编号是质数的卡。标准库没有现成的质数函数，这几行要自己写。"""
    is_prime_flags = [True] * (card_count + 1)
    is_prime_flags[0] = False
    if card_count >= 1:
        is_prime_flags[1] = False
    prime = 2
    while prime * prime <= card_count:
        if is_prime_flags[prime]:
            for multiple in range(prime * prime, card_count + 1, prime):
                is_prime_flags[multiple] = False
        prime += 1
    return [number for number, flag in enumerate(is_prime_flags) if flag]


def exact_probability(card_count: int, draw_count: int) -> Fraction:
    """不取模的精确答案，适合数字不大、需要给人看的场景。"""
    lucky_count = len(lucky_cards(card_count))
    return Fraction(math.comb(lucky_count, draw_count), math.comb(card_count, draw_count))


def probability_mod(card_count: int, draw_count: int) -> int:
    """笔试要的格式：P · Q⁻¹ mod MOD。三个参数的 pow 就是带取模的快速幂。"""
    lucky_count = len(lucky_cards(card_count))
    favorable = math.comb(lucky_count, draw_count) % MOD
    total = math.comb(card_count, draw_count) % MOD
    return favorable * pow(total, MOD - 2, MOD) % MOD


class CombinationTable:
    """预处理 0..max_n 的阶乘和阶乘的逆元，之后每个 C(n, k) mod MOD 都是 O(1)。"""

    def __init__(self, max_n: int):
        self.factorials = [1] * (max_n + 1)
        for number in range(1, max_n + 1):
            self.factorials[number] = self.factorials[number - 1] * number % MOD
        self.inverse_factorials = [1] * (max_n + 1)
        self.inverse_factorials[max_n] = pow(self.factorials[max_n], MOD - 2, MOD)
        for number in range(max_n, 0, -1):  # 1 / (i-1)! = i / i!
            self.inverse_factorials[number - 1] = self.inverse_factorials[number] * number % MOD

    def choose(self, n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        return self.factorials[n] * self.inverse_factorials[k] % MOD * self.inverse_factorials[n - k] % MOD


def main() -> None:
    # 1. 幸运卡和精确概率
    assert lucky_cards(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    exact = exact_probability(20, 2)
    assert exact == Fraction(28, 190) == Fraction(14, 95)
    assert (exact.numerator, exact.denominator) == (14, 95)  # Fraction 已经用 gcd 约过分
    print("20 张卡抽 2 张都是幸运卡的概率：", exact)

    # 2. gcd 和 lcm
    assert math.gcd(190, 28) == 2
    assert math.lcm(190, 28) == 2660  # 通分 1/190 + 1/28 的公分母
    assert Fraction(1, 190) + Fraction(1, 28) == Fraction(2660 // 190 + 2660 // 28, 2660)

    # 3. 取模输出：约不约分结果一样；两种求逆元的写法结果一样
    answer = probability_mod(20, 2)
    assert answer == 14 * pow(95, MOD - 2, MOD) % MOD == 28 * pow(190, -1, MOD) % MOD
    assert answer * 95 % MOD == 14  # 逆元的定义：乘回分母就得到分子
    assert (1 - answer + MOD) % MOD == 81 * pow(95, -1, MOD) % MOD  # 1 - 14/95 = 81/95
    print("按笔试格式输出 14/95 mod (10^9+7)：", answer)

    # 4. 小模数手算版：mod 11 下 7 的逆元是 8，14/95 ≡ 2
    assert pow(7, 9, 11) == 8 and 7 * 8 % 11 == 1
    assert 14 * pow(95, 11 - 2, 11) % 11 == 2

    # 5. 一万次组合数查询：预处理一次，每次 O(1)
    table = CombinationTable(10**5)
    assert table.choose(20, 2) == 190 and table.choose(8, 2) == 28
    assert table.choose(10**5, 3) == math.comb(10**5, 3) % MOD
    lucky_count = len(lucky_cards(10**5))
    assert lucky_count == 9592
    big_answer = table.choose(lucky_count, 3) * pow(table.choose(10**5, 3), MOD - 2, MOD) % MOD
    assert big_answer == probability_mod(10**5, 3)
    print("10^5 张卡抽 3 张都是幸运卡的概率（取模后）：", big_answer)

    # 6. 为什么 Python 也要边算边取模：大整数越乘越慢
    start = time.perf_counter()
    factorial_mod = 1
    for number in range(1, 30_001):
        factorial_mod = factorial_mod * number % MOD
    mod_seconds = time.perf_counter() - start
    start = time.perf_counter()
    factorial_exact = 1
    for number in range(1, 30_001):
        factorial_exact *= number
    exact_seconds = time.perf_counter() - start
    assert factorial_exact % MOD == factorial_mod
    print(f"30000! 边乘边取模 {mod_seconds:.3f} 秒，大整数直接乘 {exact_seconds:.3f} 秒，"
          f"后者有 {factorial_exact.bit_length()} 个二进制位")


if __name__ == "__main__":
    main()
