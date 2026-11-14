"""第 28 课：单调栈。讲解见 lessons/28-monotonic-stack.html

规则：
- 每道题都用单调栈做到 O(n)：每个下标最多进栈一次、出栈一次。
  不要写“对每个元素再往右扫一遍”的两层循环，那是 O(n²) 的暴力做法。
- 栈用 Python 的 list：append 是入栈，pop() 是出栈，stack_of_indices[-1] 是看栈顶。
- 栈里存“下标”，不要存“值”：有了下标就能算距离、算宽度，值随时可以用 numbers[index] 取回来。
- 写之前先想清楚两件事：栈里的值从栈底到栈顶是递增还是递减？
  弹出时用 < 还是 <=（有相等元素时两者结果不同）？

自查：在项目目录运行 uv run dsa/monotonic_stack.py，会逐个打印“输入、期望、实际”。
"""


def daily_temperatures(temperatures: list[int]) -> list[int]:
    """LeetCode 739 每日温度。

    temperatures[i] 是第 i 天的气温。对每一天，求“还要再等几天才会遇到更高的气温”。
    如果之后再也没有更高的气温，这一天填 0。

    例子：temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
          返回           [ 1,  1,  4,  2,  1,  1,  0,  0]
    第 2 天是 75 度，往后看 71、69、72 都不比它高，直到第 6 天的 76 度才更高，所以等 6 - 2 = 4 天。

    思路提示：stack_of_indices 里放“还没等到更高气温的那些天”的下标，
    它们的气温从栈底到栈顶是递减的。来了新的一天 i，只要它比栈顶那天更热，
    栈顶那天的答案就是 i - 栈顶下标，弹出；一直弹到栈顶不比它冷为止，再把 i 入栈。

    目标复杂度：时间 O(n)，额外空间 O(n)。
    """
    raise NotImplementedError


def next_greater_element(query_numbers: list[int], numbers: list[int]) -> list[int]:
    """LeetCode 496 下一个更大元素 I。

    numbers 里的数互不相同，query_numbers 里的每个数都在 numbers 中出现过。
    对 query_numbers 里的每个数 x：在 numbers 里找到 x 的位置，从那里往右看，
    第一个比 x 大的数是多少？没有就填 -1。

    例子：query_numbers = [4, 1, 2]，numbers = [1, 3, 4, 2]
          返回 [-1, 3, -1]
    4 在 numbers 里右边只有 2，没有更大的，所以是 -1；1 右边第一个更大的是 3；2 在最右边，是 -1。

    思路提示：先对 numbers 整体跑一遍单调栈，把“每个数 → 它右边第一个更大的数”
    存进字典 value_to_next_greater；再按 query_numbers 逐个查字典。

    目标复杂度：时间 O(len(numbers) + len(query_numbers))，额外空间 O(len(numbers))。
    """
    raise NotImplementedError


def next_greater_element_circular(numbers: list[int]) -> list[int]:
    """LeetCode 503 下一个更大元素 II（循环数组）。

    numbers 首尾相连：最后一个元素的下一个是第一个元素。对每个位置，
    沿着这个环往后找第一个比它大的数；绕一整圈都找不到就填 -1。numbers 里可以有重复的数。

    例子：numbers = [1, 2, 1]
          返回 [2, -1, 2]
    最后那个 1 往后走会绕回开头，先遇到 1（不比它大），再遇到 2，所以答案是 2。

    思路提示：把数组“假装”接成两倍长，下标 i 从 0 走到 2n - 1，真正的位置是 i % n。
    只有第一圈（i < n）才把下标入栈；第二圈只负责给栈里还在等的元素找答案。

    目标复杂度：时间 O(n)，额外空间 O(n)。
    """
    raise NotImplementedError


def largest_rectangle_area(heights: list[int]) -> int:
    """LeetCode 84 柱状图中最大的矩形。

    heights[i] 是第 i 根柱子的高度，每根柱子宽 1，柱子紧挨着排成一排。
    在柱状图里能画出的最大矩形面积是多少？矩形必须完全落在柱子内部。

    例子：heights = [2, 1, 5, 6, 2, 3]，返回 10。
    下标 2、3 的两根柱子（高 5 和 6）合起来，高取较矮的 5，宽 2，面积 5 × 2 = 10。

    思路提示：用 stack_of_indices 维护一个高度从栈底到栈顶递增的栈。
    第 i 根柱子比栈顶柱子矮时，弹出栈顶下标 top_index：
    - 它的右边界就是 i（右边第一根比它矮的柱子）；
    - 弹完后新的栈顶就是它的左边界（左边第一根比它矮的柱子），栈空了左边界就是 -1；
    - 以 heights[top_index] 为高的最大矩形，宽度 = i - 左边界 - 1。
    在 heights 末尾补一根高度为 0 的柱子，能保证最后所有柱子都被弹出来结算。

    目标复杂度：时间 O(n)，额外空间 O(n)。空列表返回 0。
    """
    raise NotImplementedError


def trap_rain_water(heights: list[int]) -> int:
    """LeetCode 42 接雨水。

    heights[i] 是第 i 根柱子的高度，宽度都是 1。下雨之后，柱子之间的凹槽里能存多少格水？

    例子：heights = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]，返回 6。

    思路提示（单调栈，按“横着的一层一层”来算水）：
    stack_of_indices 里柱子高度从栈底到栈顶递减。来了第 i 根柱子，只要它比栈顶高：
    - 弹出栈顶，记作 bottom_index，它是凹槽的底；
    - 如果栈空了，左边没有墙，存不住水，跳出循环；
    - 否则新的栈顶 left_index 是左墙，第 i 根柱子是右墙。
      这一层水的高度 = min(heights[left_index], heights[i]) - heights[bottom_index]，
      宽度 = i - left_index - 1，水量加上 高度 × 宽度。
    最后把 i 入栈。

    目标复杂度：时间 O(n)，额外空间 O(n)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def check(function, arguments, expected):
        try:
            actual = function(*arguments)
        except NotImplementedError:
            actual = "还没实现"
        verdict = "[对]" if actual == expected else "[错]"
        shown_arguments = ", ".join(repr(argument) for argument in arguments)
        print(f"{verdict} {function.__name__}({shown_arguments})")
        print(f"    期望：{expected!r}")
        print(f"    实际：{actual!r}")

    check(daily_temperatures, ([73, 74, 75, 71, 69, 72, 76, 73],), [1, 1, 4, 2, 1, 1, 0, 0])
    check(daily_temperatures, ([30, 40, 50, 60],), [1, 1, 1, 0])
    check(daily_temperatures, ([30, 60, 90],), [1, 1, 0])
    check(daily_temperatures, ([50, 50, 50],), [0, 0, 0])
    check(daily_temperatures, ([],), [])

    check(next_greater_element, ([4, 1, 2], [1, 3, 4, 2]), [-1, 3, -1])
    check(next_greater_element, ([2, 4], [1, 2, 3, 4]), [3, -1])

    check(next_greater_element_circular, ([1, 2, 1],), [2, -1, 2])
    check(next_greater_element_circular, ([1, 2, 3, 4, 3],), [2, 3, 4, -1, 4])
    check(next_greater_element_circular, ([5, 5, 5],), [-1, -1, -1])

    check(largest_rectangle_area, ([2, 1, 5, 6, 2, 3],), 10)
    check(largest_rectangle_area, ([2, 4],), 4)
    check(largest_rectangle_area, ([3, 3, 3],), 9)
    check(largest_rectangle_area, ([1, 2, 3, 4, 5],), 9)
    check(largest_rectangle_area, ([],), 0)

    check(trap_rain_water, ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), 6)
    check(trap_rain_water, ([4, 2, 0, 3, 2, 5],), 9)
    check(trap_rain_water, ([1, 2, 3],), 0)
    check(trap_rain_water, ([],), 0)
