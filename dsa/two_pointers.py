"""第 25 课：双指针。讲解见 lessons/25-two-pointers.html

规则：
- 每道题都用双指针做到目标复杂度，不要用两层循环暴力枚举。
- 对撞指针：left 从最左边出发，right 从最右边出发，每一步根据比较结果只移动其中一个，直到两者相遇。
- 快慢指针：两个指针从同一头出发、同方向走。fast 负责往前扫描每个元素，
  slow 指向“下一个该放有效元素的位置”。
- 下标一律从 0 开始（LeetCode 第 167 题要求返回从 1 开始的下标，这里改成了从 0 开始）。
- 写完后运行 uv run dsa/two_pointers.py，看每个例子的“期望”和“实际”是否一致。
"""


def two_sum_sorted(numbers: list[int], target: int) -> list[int]:
    """两数之和 II（LeetCode 167）。

    numbers 已经从小到大排好序。找出两个不同位置的数，使它们的和等于 target，
    返回这两个下标 [first_index, second_index]，first_index < second_index。
    题目保证恰好有一个答案。

    例子：numbers = [2, 7, 11, 15]，target = 9，返回 [0, 1]，因为 2 + 7 = 9。

    思路提示：left = 0，right = len(numbers) - 1。
    两数之和比 target 小，说明需要更大的数，就把 left 右移；
    比 target 大，就把 right 左移；相等就找到了。

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


def max_water_area(heights: list[int]) -> int:
    """盛最多水的容器（LeetCode 11）。

    heights[i] 是第 i 根竖线的高度，相邻竖线的间距是 1。
    任选两根竖线和 x 轴组成一个容器，它能装的水量是
    min(heights[left], heights[right]) * (right - left)。返回最大水量。
    竖线少于两根时返回 0。

    例子：heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]，返回 49
    （选下标 1 和 8 两根竖线，高度取较矮的 7，宽度 7，面积 49）。

    思路提示：left 和 right 从两头出发，每一步算一次面积并更新最大值，
    然后移动较矮的那一根。较矮的那一根已经和距离最远的搭档算过面积了，
    它再和中间任何一根搭配，宽度更小、高度不会超过它自己，面积不可能更大，所以可以放心丢掉。

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


def three_sum(numbers: list[int]) -> list[list[int]]:
    """三数之和（LeetCode 15）。

    找出所有和为 0 的三元组 [first, second, third]，三个数来自三个不同的位置。
    每个三元组内部从小到大排列，结果里不能有重复的三元组。
    结果列表的先后顺序随意（运行检查时会先排序再比较）。

    例子：numbers = [-1, 0, 1, 2, -1, -4]，返回 [[-1, -1, 2], [-1, 0, 1]]。

    思路提示：先排序。用 first_index 从左到右固定第一个数，
    在它右边的区间里用对撞指针找两个数，使它们的和等于 -numbers[first_index]。
    去重：固定的第一个数和上一轮相同就跳过；找到一组答案后，
    left 和 right 都要跳过和刚才相同的值。

    目标复杂度：时间 O(n²)，除结果以外的额外空间 O(1)（排序本身的开销不算）。
    """
    raise NotImplementedError


def move_zeroes(numbers: list[int]) -> None:
    """移动零（LeetCode 283）。

    原地修改 numbers：把所有 0 移到末尾，非零元素保持原来的先后顺序。不返回任何东西。

    例子：numbers = [0, 1, 0, 3, 12]，调用后 numbers 变成 [1, 3, 12, 0, 0]。

    思路提示：快慢指针。fast 从头扫到尾；slow 指向“下一个非零数该放的位置”。
    fast 遇到非零数，就和 slow 位置的数交换，然后 slow 右移一格。

    目标复杂度：时间 O(n)，额外空间 O(1)。
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

    show("two_sum_sorted([2, 7, 11, 15], 9)",
         lambda: two_sum_sorted([2, 7, 11, 15], 9), [0, 1])
    show("two_sum_sorted([2, 3, 4], 6)",
         lambda: two_sum_sorted([2, 3, 4], 6), [0, 2])
    show("two_sum_sorted([-1, 0], -1)",
         lambda: two_sum_sorted([-1, 0], -1), [0, 1])

    show("max_water_area([1, 8, 6, 2, 5, 4, 8, 3, 7])",
         lambda: max_water_area([1, 8, 6, 2, 5, 4, 8, 3, 7]), 49)
    show("max_water_area([1, 1])",
         lambda: max_water_area([1, 1]), 1)
    show("max_water_area([4, 3, 2, 1, 4])",
         lambda: max_water_area([4, 3, 2, 1, 4]), 16)
    show("max_water_area([5])",
         lambda: max_water_area([5]), 0)

    show("three_sum([-1, 0, 1, 2, -1, -4])",
         lambda: sorted(three_sum([-1, 0, 1, 2, -1, -4])), [[-1, -1, 2], [-1, 0, 1]])
    show("three_sum([0, 1, 1])",
         lambda: sorted(three_sum([0, 1, 1])), [])
    show("three_sum([0, 0, 0, 0])",
         lambda: sorted(three_sum([0, 0, 0, 0])), [[0, 0, 0]])
    show("three_sum([-2, 0, 1, 1, 2])",
         lambda: sorted(three_sum([-2, 0, 1, 1, 2])), [[-2, 0, 2], [-2, 1, 1]])

    def move_zeroes_result(numbers):
        """调用 move_zeroes 后返回被修改过的列表，方便打印。"""
        move_zeroes(numbers)
        return numbers

    show("move_zeroes([0, 1, 0, 3, 12])",
         lambda: move_zeroes_result([0, 1, 0, 3, 12]), [1, 3, 12, 0, 0])
    show("move_zeroes([0])",
         lambda: move_zeroes_result([0]), [0])
    show("move_zeroes([4, 0, 5, 0, 0, 6])",
         lambda: move_zeroes_result([4, 0, 5, 0, 0, 6]), [4, 5, 6, 0, 0, 0])
