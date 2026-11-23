"""第 41 课：差分数组。讲解见 lessons/41-difference-array.html

规则：
- 差分数组比原数组多一格：difference[0] = numbers[0]，difference[i] = numbers[i] - numbers[i - 1]，
  最后多出来的 difference[n] 一开始是 0，只用来接住 right + 1 == n 时的那个“减回去”的标记，不用特判。
- 给下标 left 到 right（两端都包含）整体加 delta：只改两格，difference[left] += delta，difference[right + 1] -= delta。
- 还原：对 difference 做一遍前缀和（第 27 课），前 n 项就是改完以后的数组。
- 不要用 itertools.accumulate，自己写循环累加。
- 写完后运行 uv run pytest tests/test_difference_array.py。
"""


class DifferenceArray:
    """支持“区间整体加”的数组：先攒很多次 add，最后一次性 to_list() 拿结果。

    例子：numbers = [3, 1, 4, 1, 5, 9, 2, 6]
          add(2, 5, 2)  # 下标 2～5 都加 2
          add(4, 7, 3)  # 下标 4～7 都加 3
          to_list() 返回 [3, 1, 6, 3, 10, 14, 5, 9]
          这时 difference == [3, -2, 5, -3, 7, 4, -9, 4, -3]

    要求：
    - self.difference 是长度 len(numbers) + 1 的 list，含义见文件顶部规则。
    - add 的 left、right 是下标，两端都包含；0 <= left <= right < len(self) 之外的情况抛 IndexError。
    - to_list() 不修改 self.difference，可以反复调用，也可以调用之后继续 add。
    - len(差分数组对象) 返回原数组长度 n（不是 n + 1）。

    目标复杂度：构造 O(n)，每次 add O(1)，to_list O(n)。
    """

    def __init__(self, numbers: list[int]):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def add(self, left: int, right: int, delta: int) -> None:
        raise NotImplementedError

    def to_list(self) -> list[int]:
        raise NotImplementedError


def corp_flight_bookings(bookings: list[list[int]], flight_count: int) -> list[int]:
    """航班预订统计（LeetCode 1109）。

    航班编号从 1 到 flight_count。bookings[i] = [first, last, seats] 表示
    第 first 到第 last 个航班（两端都包含）每个都预订了 seats 个座位。
    返回长度为 flight_count 的列表，第 i 项是第 i + 1 个航班的总预订数。

    例子：bookings = [[1, 2, 10], [2, 3, 20], [2, 5, 25]]，flight_count = 5
          返回 [10, 55, 45, 25, 25]

    注意编号从 1 开始，换成下标要减 1。

    目标复杂度：时间 O(flight_count + len(bookings))。
    """
    raise NotImplementedError


def car_pooling(trips: list[list[int]], capacity: int) -> bool:
    """拼车（LeetCode 1094）。

    车只往一个方向开，trips[i] = [passengers, start, end] 表示有 passengers 个人
    在位置 start 上车、在位置 end 下车（到 end 时已经下车，不占座）。
    车上最多坐 capacity 人，能接完所有乘客就返回 True。位置都是 0～1000 的整数。

    例子：trips = [[2, 1, 5], [3, 3, 7]]，capacity = 4，返回 False（位置 3～4 车上有 5 人）。
          同样的 trips，capacity = 5，返回 True。

    思路提示：每一单就是“位置 start 到 end - 1 都加 passengers”，
    还原后看最大值有没有超过 capacity。

    目标复杂度：时间 O(len(trips) + 最大位置)。
    """
    raise NotImplementedError


def add_to_submatrices(row_count: int, column_count: int, additions: list[list[int]]) -> list[list[int]]:
    """（选做）二维差分：子矩阵整体加。

    从一个 row_count × column_count 的全 0 矩阵开始。additions[i] = [top, left, bottom, right, delta]
    表示把第 top～bottom 行、第 left～right 列（都包含）这一块全部加 delta。返回最终矩阵。

    例子：row_count = 3，column_count = 3，additions = [[1, 1, 2, 2, 1], [0, 0, 1, 1, 1]]
          返回 [[1, 1, 0],
                [1, 2, 1],
                [0, 1, 1]]

    思路提示：二维差分数组 (row_count + 1) × (column_count + 1)，一次子矩阵加只改四个角：
    [top][left] += delta，[top][right + 1] -= delta，[bottom + 1][left] -= delta，
    [bottom + 1][right + 1] += delta；最后做一遍二维前缀和还原。

    目标复杂度：时间 O(row_count × column_count + len(additions))。
    """
    raise NotImplementedError
