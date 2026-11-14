"""第 34 课：区间问题。讲解见 lessons/34-intervals.html

规则：
- 区间用两个元素的列表 [start, end] 表示，start <= end。
- merge_intervals 和 insert_interval 里的区间是闭区间：[1, 3] 和 [3, 5] 在 3 处相接，算重叠，要合并。
- min_removals_to_avoid_overlap 和 min_meeting_rooms 里，端点相接不算重叠：
  [1, 2] 和 [2, 3] 可以共存，一场会议在 10 点结束、另一场 10 点开始，可以用同一间会议室。
- 不要修改传进来的列表，需要排序时用 sorted(...) 拿一份新的。
- 写完后运行 uv run dsa/intervals.py，看每个例子的“期望”和“实际”是否一致。
"""


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """合并所有重叠的区间，返回按起点从小到大排好的结果。（LeetCode 56. 合并区间）

    例子：[[1, 3], [2, 6], [8, 10], [15, 18]] → [[1, 6], [8, 10], [15, 18]]
    （[1, 3] 和 [2, 6] 重叠，合成 [1, 6]）。空列表返回空列表。

    思路：按起点排序后，能和某个区间重叠的区间一定紧挨着它。
    从左往右扫，用 merged_intervals 存结果，只需要看最后一段 merged_intervals[-1]：
    - 当前区间的起点 <= 最后一段的终点：重叠，把最后一段的终点更新成两者终点的较大值；
    - 否则：接不上，当前区间作为新的一段追加到末尾。

    目标复杂度：时间 O(n log n)（排序），额外空间 O(n)（结果）。
    """
    raise NotImplementedError


def insert_interval(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    """intervals 已经按起点排好序且互不重叠。插入 new_interval，必要时合并，返回新的列表。（LeetCode 57. 插入区间）

    例子：intervals = [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]]，new_interval = [4, 8]
         → [[1, 2], [3, 10], [12, 16]]（[3, 5]、[6, 7]、[8, 10] 都和 [4, 8] 重叠，合成 [3, 10]）。

    思路：输入已经有序，不需要重新排序，一趟扫描分三段处理：
    1. 终点 < new_interval 起点的区间，完全在左边，原样放进结果；
    2. 起点 <= new_interval 终点的区间，和它重叠，把它们并进 new_interval
       （起点取较小值，终点取较大值），扫完这一段后把 new_interval 放进结果；
    3. 剩下的区间完全在右边，原样放进结果。

    目标复杂度：时间 O(n)，额外空间 O(n)（结果）。
    """
    raise NotImplementedError


def min_removals_to_avoid_overlap(intervals: list[list[int]]) -> int:
    """最少删掉几个区间，能让剩下的区间两两不重叠。端点相接不算重叠。（LeetCode 435. 无重叠区间）

    例子：[[1, 2], [2, 3], [3, 4], [1, 3]] → 1（删掉 [1, 3]，剩下三个首尾相接，不算重叠）。

    思路：“最少删几个”等于“总数减去最多能留几个”。“最多留几个互不重叠的区间”就是第 18 课的活动选择：
    按终点排序，用 current_end 记录上一个留下的区间的终点；当前区间的起点 >= current_end 就留下它，
    并把 current_end 更新成它的终点，否则删掉它。

    目标复杂度：时间 O(n log n)，额外空间 O(1)（不算排序用的空间）。
    """
    raise NotImplementedError


def min_meeting_rooms(meetings: list[list[int]]) -> int:
    """每个会议是 [start, end]，最少要几间会议室才能把所有会议都安排下。（LeetCode 253. 会议室 II）

    一场会议在 end 时刻结束，另一场在同一时刻开始，可以接着用同一间会议室。

    例子：[[0, 30], [5, 10], [15, 20]] → 2（[0, 30] 占一间；[5, 10] 和 [15, 20] 先后用另一间）。

    思路（任选一种）：
    - 最小堆：按开始时间排序，堆里放“正在使用的会议室各自什么时候空出来”（结束时间）。
      每来一场会议，如果堆顶的结束时间 <= 这场会议的开始时间，说明那间会议室已经空了，先弹出它；
      再把这场会议的结束时间放进堆。过程中堆的最大大小就是答案。
    - 两个有序列表：start_times 和 end_times 各自排序，用两个下标同时往后走。
      遇到开始事件 rooms_in_use 加一，遇到结束事件减一；时间相同时先处理结束事件。答案是 rooms_in_use 的最大值。

    目标复杂度：时间 O(n log n)，额外空间 O(n)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def show(function, arguments, expected):
        """调用 function(*arguments)，打印输入、期望和实际结果。"""
        shown_input = ", ".join(repr(argument) for argument in arguments)
        try:
            actual = function(*arguments)
            verdict = "通过" if actual == expected else "不对"
        except NotImplementedError:
            actual, verdict = "（还没写）", "未完成"
        print(f"[{verdict}] {function.__name__}({shown_input})")
        print(f"        期望：{expected!r}")
        print(f"        实际：{actual!r}")

    show(merge_intervals, ([[1, 3], [2, 6], [8, 10], [15, 18]],), [[1, 6], [8, 10], [15, 18]])
    show(merge_intervals, ([[1, 4], [4, 5]],), [[1, 5]])
    show(merge_intervals, ([[8, 10], [1, 4], [2, 3], [5, 7]],), [[1, 4], [5, 7], [8, 10]])
    show(merge_intervals, ([],), [])

    show(insert_interval, ([[1, 3], [6, 9]], [2, 5]), [[1, 5], [6, 9]])
    show(insert_interval, ([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]), [[1, 2], [3, 10], [12, 16]])
    show(insert_interval, ([], [5, 7]), [[5, 7]])
    show(insert_interval, ([[1, 5]], [6, 8]), [[1, 5], [6, 8]])

    show(min_removals_to_avoid_overlap, ([[1, 2], [2, 3], [3, 4], [1, 3]],), 1)
    show(min_removals_to_avoid_overlap, ([[1, 2], [1, 2], [1, 2]],), 2)
    show(min_removals_to_avoid_overlap, ([[1, 2], [2, 3]],), 0)
    show(min_removals_to_avoid_overlap, ([[1, 100], [11, 22], [1, 11], [2, 12]],), 2)

    show(min_meeting_rooms, ([[0, 30], [5, 10], [15, 20]],), 2)
    show(min_meeting_rooms, ([[7, 10], [2, 4]],), 1)
    show(min_meeting_rooms, ([[1, 5], [5, 10], [10, 15]],), 1)
    show(min_meeting_rooms, ([[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]],), 4)
    show(min_meeting_rooms, ([],), 0)
