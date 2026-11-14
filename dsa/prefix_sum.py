"""第 27 课：前缀和与哈希计数。讲解见 lessons/27-prefix-sum.html

规则：
- 前缀和数组比原数组多一格：prefix_sum[0] = 0，prefix_sum[i] = numbers[0] + ... + numbers[i - 1]。
  这样下标 left 到 right（两端都包含）这一段的和就是 prefix_sum[right + 1] - prefix_sum[left]，不用特判开头。
- “找另一个数”或“找另一个前缀和”时，用 dict 记录见过的值，一次查找是 O(1)，不要回头再扫一遍数组。
- 不要用 itertools.accumulate，自己写循环累加。
- 写完后运行 uv run dsa/prefix_sum.py，看每个例子的“期望”和“实际”是否一致。
"""


class RangeSumQuery:
    """区域和检索 - 数组不可变（LeetCode 303）。

    构造时传入数组 numbers，之后会被反复调用 sum_range(left, right)，
    返回 numbers[left] + numbers[left + 1] + ... + numbers[right]（两端都包含）。

    例子：numbers = [-2, 0, 3, -5, 2, -1]
          sum_range(0, 2) 返回 1（-2 + 0 + 3）
          sum_range(2, 5) 返回 -1（3 - 5 + 2 - 1）

    思路提示：构造时算好前缀和数组 self.prefix_sum（长度 n + 1），
    查询时只做一次减法。

    目标复杂度：构造 O(n)，每次查询 O(1)，额外空间 O(n)。
    """

    def __init__(self, numbers: list[int]):
        raise NotImplementedError

    def sum_range(self, left: int, right: int) -> int:
        raise NotImplementedError


def subarray_sum_equals_k(numbers: list[int], k: int) -> int:
    """和为 K 的子数组（LeetCode 560）。

    返回 numbers 中和恰好等于 k 的连续子数组的个数。numbers 里可以有负数和 0。

    例子：numbers = [1, 1, 1]，k = 2，返回 2（[1, 1] 出现在下标 0～1 和 1～2 两个位置）。
          numbers = [1, 2, 3]，k = 3，返回 2（[1, 2] 和 [3]）。

    思路提示：一边从左到右累加 prefix_sum，一边用 dict count_by_prefix_sum 记录
    “到目前为止，每个前缀和出现过几次”，开始前先放入 {0: 1}（代表一个数都不取的空前缀）。
    走到某个位置时，以它结尾、和为 k 的子数组个数，就等于之前出现过的前缀和里
    值为 prefix_sum - k 的个数。先查、再把当前 prefix_sum 记进 dict。

    目标复杂度：时间 O(n)，额外空间 O(n)。
    """
    raise NotImplementedError


def two_sum(numbers: list[int], target: int) -> list[int]:
    """两数之和（LeetCode 1）。

    numbers 没有排序。找出两个不同位置的数，使它们的和等于 target，
    返回下标 [first_index, second_index]，first_index < second_index。题目保证恰好有一个答案。

    例子：numbers = [2, 7, 11, 15]，target = 9，返回 [0, 1]。
          numbers = [3, 3]，target = 6，返回 [0, 1]。

    思路提示：用 dict index_by_value 记录“已经看过的数 → 它的下标”。
    走到下标 i 时，先查 target - numbers[i] 在不在 dict 里，在就找到了；
    不在再把 numbers[i] 记进去。先查后记，可以避免同一个数和自己配对。

    目标复杂度：时间 O(n)，额外空间 O(n)。
    """
    raise NotImplementedError


if __name__ == "__main__":

    def show(title, compute, expected):
        """运行一个例子，打印输入、期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected}\n    实际：{actual}")

    def range_sum_results(numbers, queries):
        """用 numbers 构造 RangeSumQuery，依次执行 queries 里的每个 (left, right)，返回结果列表。"""
        range_sum_query = RangeSumQuery(numbers)
        return [range_sum_query.sum_range(left, right) for left, right in queries]

    show("RangeSumQuery([-2, 0, 3, -5, 2, -1])，查询 (0, 2) (2, 5) (0, 5)",
         lambda: range_sum_results([-2, 0, 3, -5, 2, -1], [(0, 2), (2, 5), (0, 5)]), [1, -1, -3])
    show("RangeSumQuery([5])，查询 (0, 0)",
         lambda: range_sum_results([5], [(0, 0)]), [5])
    show("RangeSumQuery([1, 2, 3, 4])，查询 (1, 1) (1, 3) (0, 3)",
         lambda: range_sum_results([1, 2, 3, 4], [(1, 1), (1, 3), (0, 3)]), [2, 9, 10])

    show("subarray_sum_equals_k([1, 1, 1], 2)",
         lambda: subarray_sum_equals_k([1, 1, 1], 2), 2)
    show("subarray_sum_equals_k([1, 2, 3], 3)",
         lambda: subarray_sum_equals_k([1, 2, 3], 3), 2)
    show("subarray_sum_equals_k([1, -1, 0], 0)",
         lambda: subarray_sum_equals_k([1, -1, 0], 0), 3)
    show("subarray_sum_equals_k([3, 4, 7, 2, -3, 1, 4, 2], 7)",
         lambda: subarray_sum_equals_k([3, 4, 7, 2, -3, 1, 4, 2], 7), 4)
    show("subarray_sum_equals_k([1], 0)",
         lambda: subarray_sum_equals_k([1], 0), 0)

    show("two_sum([2, 7, 11, 15], 9)",
         lambda: two_sum([2, 7, 11, 15], 9), [0, 1])
    show("two_sum([3, 2, 4], 6)",
         lambda: two_sum([3, 2, 4], 6), [1, 2])
    show("two_sum([3, 3], 6)",
         lambda: two_sum([3, 3], 6), [0, 1])
