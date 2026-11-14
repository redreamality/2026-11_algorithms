"""第 39 课：位运算技巧。讲解见 lessons/39-bit-manipulation.html

实际项目里用 enum.Flag 管权限和开关、int.bit_count() 数 1、ipaddress 处理掩码，小集合用整数做状态压缩
（完整例子见 examples/bit_manipulation_in_practice.py）。这里手写是为了看清这些工具底层在做什么。

规则：
- 只用位运算和普通的加减比较：& | ^ ~ << >>。不要用 bin(number).count("1")、
  int.bit_count() 这类现成的“数 1”函数，也不要用 itertools 生成子集。
- 除了 single_number 和 missing_number，输入都是非负整数（Python 的负数在位运算里
  相当于前面有无穷多个 1，会让“数 1”之类的循环停不下来）。
- 变量名用完整的英文单词，例如 bit_mask、remaining_bits、one_bit_count，
  不要写 res、tmp、cnt 这类缩写。
- 自查：uv run dsa/bit_manipulation.py，会对每个函数跑几个例子，打印「输入、期望、实际」。
"""


def single_number(numbers: list[int]) -> int:
    """只出现一次的数字（LeetCode 136）。

    numbers 里除了一个数只出现一次，其余每个数都恰好出现两次。找出那个只出现一次的数。

    例子：numbers = [4, 1, 2, 1, 2]，1 和 2 各出现两次，返回 4。

    要求：O(n) 时间、O(1) 额外空间（所以不能用 set 或 dict 计数）。
    提示：x ^ x = 0，x ^ 0 = x，而且异或可以随意交换顺序。把所有数异或起来会剩下什么？
    """
    raise NotImplementedError


def missing_number(numbers: list[int]) -> int:
    """（选做）丢失的数字（LeetCode 268）。

    numbers 里有 n 个互不相同的数，都在 0..n 之间，正好缺了一个。找出缺的那个。

    例子：numbers = [3, 0, 1]，n = 3，0..3 里缺 2，返回 2。

    要求：O(n) 时间、O(1) 额外空间。
    提示：把 0..n 这 n + 1 个数和 numbers 里的 n 个数全部异或起来，
    出现两次的都抵消掉了，剩下的就是只出现一次的那个——也就是缺的数。
    """
    raise NotImplementedError


def count_one_bits(number: int) -> int:
    """位 1 的个数（LeetCode 191）：number 的二进制里有几个 1。number ≥ 0。

    例子：number = 11，二进制 1011，有 3 个 1，返回 3。

    要求：用 number & (number - 1) 去掉最低位的 1，数一共能去几次。
    这样循环次数等于 1 的个数，而不是二进制的总位数。
    """
    raise NotImplementedError


def count_bits_up_to(limit: int) -> list[int]:
    """比特位计数（LeetCode 338）：返回一个长度为 limit + 1 的列表，
    第 i 项是 i 的二进制里 1 的个数。limit ≥ 0。

    例子：limit = 5
          0 → 0，1 → 1，10 → 1，11 → 2，100 → 1，101 → 2，返回 [0, 1, 1, 2, 1, 2]。

    要求：O(limit) 时间，不能对每个数单独去数（那是 O(limit × 位数)）。
    提示：这是一道一维 DP。one_bit_count[i] 和哪个更小的数有关？
      i >> 1 是把 i 的最后一位去掉，所以
      one_bit_count[i] = one_bit_count[i >> 1] + (i & 1)。
    """
    raise NotImplementedError


def is_power_of_two(number: int) -> bool:
    """2 的幂（LeetCode 231）：number 是不是 1、2、4、8、16 …… 中的一个。

    number 可以是 0 或负数，这时返回 False。

    例子：16 → True（二进制 10000），12 → False（二进制 1100），1 → True（2 的 0 次方）。

    要求：O(1)，不能写循环。
    提示：2 的幂的二进制恰好只有一个 1。去掉最低位的 1 之后会变成什么？
    """
    raise NotImplementedError


def subsets_by_bit_mask(items: list[int]) -> list[list[int]]:
    """用位掩码枚举子集（LeetCode 78 的另一种写法）。

    items 里有 n 个互不相同的数。用 0 到 2^n - 1 的每一个整数 bit_mask 表示一个子集：
    bit_mask 的第 k 位是 1，就表示选了 items[k]。

    返回顺序要求：按 bit_mask 从 0 到 2^n - 1 的顺序；每个子集内部按下标从小到大。
    例子：items = [1, 2, 3]，返回
          [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
          （bit_mask = 5 = 二进制 101，第 0 位和第 2 位是 1，所以是 [1, 3]。）

    提示：检查第 k 位是不是 1，写 (bit_mask >> k) & 1，或者 bit_mask & (1 << k)。
    目标复杂度：O(n × 2^n)。
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

    check(single_number, ([2, 2, 1],), 1)
    check(single_number, ([4, 1, 2, 1, 2],), 4)
    check(single_number, ([7],), 7)
    check(single_number, ([-3, 5, 5],), -3)

    check(missing_number, ([3, 0, 1],), 2)
    check(missing_number, ([0, 1],), 2)
    check(missing_number, ([9, 6, 4, 2, 3, 5, 7, 0, 1],), 8)

    check(count_one_bits, (11,), 3)
    check(count_one_bits, (128,), 1)
    check(count_one_bits, (0,), 0)
    check(count_one_bits, (2**31 - 1,), 31)

    check(count_bits_up_to, (2,), [0, 1, 1])
    check(count_bits_up_to, (5,), [0, 1, 1, 2, 1, 2])
    check(count_bits_up_to, (0,), [0])

    check(is_power_of_two, (1,), True)
    check(is_power_of_two, (16,), True)
    check(is_power_of_two, (12,), False)
    check(is_power_of_two, (0,), False)
    check(is_power_of_two, (-16,), False)

    check(subsets_by_bit_mask, ([1, 2, 3],), [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]])
    check(subsets_by_bit_mask, ([],), [[]])
    check(subsets_by_bit_mask, ([5, 9],), [[], [5], [9], [5, 9]])
