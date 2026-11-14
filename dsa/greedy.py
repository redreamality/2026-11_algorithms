"""第 18 课：贪心。讲解见 lessons/18-greedy.html

实际项目里，贪心几乎都是“sorted(..., key=...) + 一次遍历”，不需要任何库（见 examples/greedy_in_practice.py）。
这里的函数都按业务代码的习惯写：返回“选了哪些”，而不只是一个数字；不改动传进来的数据。

规则：
- 每个函数都是“排个序（或按某个顺序扫一遍），每步取当前最好”的写法，不要写成 DP 或暴力枚举。
- 区间用 (start, end) 表示，保证 start <= end。
- 不要改动传进来的列表：要排序就用 sorted() 得到新列表。

写完后运行 uv run dsa/greedy.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_greedy.py。
"""

from collections import Counter


def select_activities(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """选出尽量多的互不重叠的活动，按结束时间从早到晚返回选中的那些。

    活动是左闭右开的 [start, end)：一个在 5 结束、另一个在 5 开始，不算重叠。
    最优解可能不止一种，这里约定用“按结束时间排序，能选就选”得到的那一组；
    结束时间相同时，按 sorted 的稳定性保留原来的先后顺序。

    例子：[(1, 4), (3, 5), (5, 7)] 返回 [(1, 4), (5, 7)]。
    提示：sorted(intervals, key=lambda interval: interval[1])，记住上一个选中活动的结束时间。O(n log n)。
    """
    raise NotImplementedError


def make_change(denominations: list[int], amount: int) -> Counter[int] | None:
    """贪心找零：每次拿不超过剩余金额的最大面值。返回 Counter({面值: 张数})。

    amount 为 0 返回空的 Counter()；凑不出来返回 None。
    注意：这是“贪心的答案”，不一定张数最少。人民币 [1, 5, 10, 20, 50, 100] 这种标准币制是对的；
    面值 [1, 3, 4] 凑 6 会得到 Counter({4: 1, 1: 2})，而最优是两个 3（要用第 19 课的 DP）。

    提示：面值从大到小排序，每种面值一次用 divmod 算出能拿几张，不要一张一张地减。
    O(k log k)，k 是面值种数。
    """
    raise NotImplementedError


def can_reach_end(max_steps: list[int]) -> bool:
    """跳跃游戏：站在下标 0，max_steps[i] 是在 i 处最多能往前跳几格，能否到达最后一个下标。

    提示：从左往右扫，维护“目前最远能到哪”（farthest_reachable）；
    走到某个下标时它已经超过了 farthest_reachable，就说明到不了。O(n)。空列表不会出现。
    """
    raise NotImplementedError


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """合并所有重叠的区间，按起点从小到大返回 tuple 的列表。

    这里区间是闭区间 [start, end]，首尾相接也要合并：(1, 3) 和 (3, 5) 合成 (1, 5)。
    提示：按起点排序，能接上就延长最后一段（最后一段的终点取两者较大值）。O(n log n)。
    """
    raise NotImplementedError


if __name__ == "__main__":

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景一：一间会议室，一天收到这些预约（单位：点钟），尽量多排几场。
    bookings = [(9, 12), (9, 10), (10, 11), (11, 13), (13, 14), (12, 15)]
    show("会议室最多能排哪几场", lambda: select_activities(bookings), [(9, 10), (10, 11), (11, 13), (13, 14)])

    # 场景二：收银台找零（单位：元）。
    rmb = [100, 50, 20, 10, 5, 1]
    show("找零 188 元", lambda: make_change(rmb, 188), Counter({100: 1, 50: 1, 20: 1, 10: 1, 5: 1, 1: 3}))
    show("面值 [1, 3, 4] 找零 6：贪心不是最优", lambda: make_change([1, 3, 4], 6), Counter({4: 1, 1: 2}))
    show("只有 5 元和 10 元，找不开 3 元", lambda: make_change([5, 10], 3), None)

    # 场景三：日历上把一个人所有忙碌的时间段合并，好算出空闲时间。
    busy = [(14, 16), (9, 10), (9, 11), (11, 12), (15, 17)]
    show("合并忙碌时段", lambda: merge_intervals(busy), [(9, 12), (14, 17)])

    show("can_reach_end([2, 3, 1, 1, 4])", lambda: can_reach_end([2, 3, 1, 1, 4]), True)
    show("can_reach_end([3, 2, 1, 0, 4])", lambda: can_reach_end([3, 2, 1, 0, 4]), False)
