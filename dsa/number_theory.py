"""第 40 课：数论模板。讲解见 lessons/40-number-theory.html

主线题目：抽奖箱里有编号 1..card_count 的卡，编号是质数的叫幸运卡。随机抽 draw_count 张，
全是幸运卡的概率是多少？按笔试的惯例，输出 P · Q⁻¹ mod (10**9 + 7)。
例子：20 张卡里有 8 张幸运卡，抽 2 张，概率 = C(8, 2) / C(20, 2) = 28 / 190 = 14 / 95。

实际项目里直接用 math.gcd、math.lcm、math.comb、pow(base, exponent, modulus)、
pow(value, -1, modulus)、fractions.Fraction（完整例子见 examples/number_theory_in_practice.py）。
这里手写是为了看清它们底层在做什么，笔试里也常要默写。

规则：
- 不要用 math.gcd、math.lcm、math.comb、math.factorial，也不要用三个参数的 pow。
  普通的 + - * // % 和比较随便用；第 05 课写过的快速幂思路、第 39 课的 & 和 >> 也可以用。
- 所有输入都是非负整数（mod_inverse 的 value 也是）。
- 变量名用完整的英文单词，例如 remainder、exponent、is_prime_flags、factorials，
  不要写 res、tmp、fac 这类缩写。
- 自查：uv run dsa/number_theory.py，会对每个函数跑几个例子，打印「输入、期望、实际」；
  正式测试：uv run pytest tests/test_number_theory.py。
"""

MOD = 10**9 + 7


def gcd(first: int, second: int) -> int:
    """最大公约数（辗转相除法）。

    gcd(a, b) = gcd(b, a % b)，一直做到第二个数是 0，这时第一个数就是答案。
    约定 gcd(a, 0) = a，gcd(0, 0) = 0（和 math.gcd 一致）。

    例子：gcd(190, 28) == 2（190 % 28 = 22，28 % 22 = 6，22 % 6 = 4，6 % 4 = 2，4 % 2 = 0）。
    要求：O(log min(a, b))，用 while 循环写（递归也行，但循环不受递归深度限制）。
    """
    raise NotImplementedError


def lcm(first: int, second: int) -> int:
    """最小公倍数：lcm(a, b) = a // gcd(a, b) * b。有一个是 0 时返回 0（和 math.lcm 一致）。

    例子：lcm(190, 28) == 2660。
    提示：先除后乘（a // gcd * b），中间结果更小；在会溢出的语言里这一点很重要。
    """
    raise NotImplementedError


def is_prime(number: int) -> bool:
    """质数判断（试除法）。0 和 1 不是质数，2 是质数。

    只要试到 divisor * divisor <= number：如果 number 有一个大于 √number 的因数，
    它一定配着一个小于 √number 的因数，前面已经试到了。

    例子：is_prime(19) == True，is_prime(20) == False，is_prime(10**9 + 7) == True。
    要求：O(√n)。不要用浮点数开方（number ** 0.5），用 divisor * divisor <= number 判断。
    """
    raise NotImplementedError


def primes_up_to(limit: int) -> list[int]:
    """埃氏筛：返回 [2, limit] 里的所有质数，从小到大。limit < 2 时返回 []。

    做法：先假设 0..limit 都是质数（0 和 1 先划掉），从 2 开始，
    遇到一个还没被划掉的数 prime，就把它的倍数 prime*prime, prime*prime + prime, ... 全部划掉。
    prime * prime > limit 时就可以停了。

    例子：primes_up_to(20) == [2, 3, 5, 7, 11, 13, 17, 19]（主线里的 8 张幸运卡）。
    要求：O(n log log n)。primes_up_to(10**6) 要在一两秒内跑完。
    """
    raise NotImplementedError


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """带取模的快速幂（迭代版）：返回 base ** exponent % modulus。

    看 exponent 的二进制：从最低位开始，每一步 base 自己平方一次（base, base², base⁴, base⁸ ...），
    当前位是 1 就把 base 乘进结果。每次乘法之后都 % modulus。
    exponent < 0 抛 ValueError；modulus == 1 时任何数取模都是 0。

    例子：mod_pow(7, 9, 11) == 8（9 = 二进制 1001，所以 7⁹ = 7⁸ · 7¹）。
    要求：O(log exponent)，不许用三个参数的 pow；mod_pow(2, 10**18, MOD) 要瞬间算完。
    """
    raise NotImplementedError


def mod_inverse(value: int, prime_modulus: int = MOD) -> int:
    """乘法逆元：返回 0..prime_modulus-1 里满足 value * x % prime_modulus == 1 的 x。

    prime_modulus 必须是质数。由费马小定理，value 不是 prime_modulus 的倍数时，
    value ** (prime_modulus - 2) 就是逆元，用上面的 mod_pow 算。
    value 是 prime_modulus 的倍数（包括 0）时没有逆元，抛 ValueError。

    例子：mod_inverse(7, 11) == 8（7 * 8 = 56 = 5 * 11 + 1）。
    """
    raise NotImplementedError


class CombinationTable:
    """预处理阶乘和阶乘的逆元，之后每次 C(n, k) mod modulus 都是 O(1)。

    用法：
        table = CombinationTable(20)
        table.choose(20, 2)   # 190
        table.choose(8, 2)    # 28

    __init__ 里建两张表（都要 % modulus）：
        factorials[i] = i!
        inverse_factorials[i] = (i!) 的逆元
    inverse_factorials[max_n] 用 mod_inverse 算一次，再从大往小推：
        inverse_factorials[i - 1] = inverse_factorials[i] * i
    （因为 1 / (i-1)! = i / i!），这样只做一次快速幂，整体 O(max_n + log modulus)。

    modulus 必须是质数，而且要大于 max_n（否则某个 i! 是 modulus 的倍数，没有逆元）。
    """

    def __init__(self, max_n: int, modulus: int = MOD):
        raise NotImplementedError

    def choose(self, n: int, k: int) -> int:
        """C(n, k) mod modulus = n! / (k! (n-k)!)，用乘逆元代替除法。

        k < 0 或 k > n 时返回 0（选不出来，方案数是 0）。
        n > max_n（表不够大）时抛 ValueError。
        """
        raise NotImplementedError


def fraction_mod(numerator: int, denominator: int, modulus: int = MOD) -> int:
    """把分数 numerator / denominator 表示成 numerator · denominator⁻¹ mod modulus。

    分数先约分还是不约分，结果都一样：fraction_mod(28, 190) == fraction_mod(14, 95)。
    denominator 是 modulus 的倍数时抛 ValueError（分母没有逆元）。

    例子：fraction_mod(14, 95, 11) == 2，因为 95 * 2 = 190，190 % 11 == 14 % 11 == 3。
    """
    raise NotImplementedError


def lucky_draw_probability(card_count: int, draw_count: int) -> int:
    """主线题目：卡片编号 1..card_count，编号是质数的是幸运卡。随机抽 draw_count 张（不放回），
    全是幸运卡的概率，按 P · Q⁻¹ mod MOD 输出。

    步骤：用 primes_up_to 数出幸运卡 lucky_count 张；
         概率 = C(lucky_count, draw_count) / C(card_count, draw_count)；
         两个组合数用 CombinationTable 算，再交给 fraction_mod。
    约定 0 <= draw_count <= card_count，card_count >= 1。

    例子：lucky_draw_probability(20, 2) == fraction_mod(14, 95) == 242105265。
    要求：card_count = 10**5 也要在一秒左右算完。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def check(function, arguments, expected):
        """跑一个例子，打印「输入、期望、实际」。还没实现的函数会提示一下，不会让脚本中断。"""
        shown_input = ", ".join(repr(argument) for argument in arguments)
        try:
            actual = function(*arguments)
        except NotImplementedError:
            print(f"[未实现] {function.__name__}({shown_input})")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {function.__name__}({shown_input})  期望 {expected!r}，实际 {actual!r}")

    check(gcd, (190, 28), 2)
    check(gcd, (28, 190), 2)
    check(gcd, (7, 0), 7)
    check(lcm, (190, 28), 2660)
    check(lcm, (4, 6), 12)

    check(is_prime, (19,), True)
    check(is_prime, (20,), False)
    check(is_prime, (1,), False)
    check(is_prime, (MOD,), True)
    check(primes_up_to, (20,), [2, 3, 5, 7, 11, 13, 17, 19])
    check(primes_up_to, (1,), [])

    check(mod_pow, (7, 9, 11), 8)
    check(mod_pow, (2, 10, MOD), 1024)
    check(mod_pow, (95, 0, 11), 1)
    check(mod_inverse, (7, 11), 8)
    check(mod_inverse, (95, MOD), 231578949)

    def choose(max_n, n, k):
        return CombinationTable(max_n).choose(n, k)

    check(choose, (20, 20, 2), 190)
    check(choose, (20, 8, 2), 28)
    check(choose, (20, 5, 7), 0)

    check(fraction_mod, (14, 95, 11), 2)
    check(fraction_mod, (28, 190), 242105265)
    check(lucky_draw_probability, (20, 2), 242105265)
    check(lucky_draw_probability, (10**5, 3), 859555632)
