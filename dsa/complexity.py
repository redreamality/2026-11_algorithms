"""第 0 课：复杂度。讲解见 lessons/00-complexity.html

同一个问题写三种解法，感受 O(n²)、O(n log n) 和 O(n) 的差别。
问题：列表里有没有重复的数？
"""


def has_duplicate_slow(nums: list[int]) -> bool:
    """两两比较。时间 O(n²)，额外空间 O(1)。"""
    raise NotImplementedError


def has_duplicate_sorted(nums: list[int]) -> bool:
    """先排序，再看相邻两个是否相等。时间 O(n log n)。

    注意：不能修改传进来的 nums。
    """
    raise NotImplementedError


def has_duplicate_fast(nums: list[int]) -> bool:
    """用 set 记住见过的数。时间 O(n)，额外空间 O(n)。"""
    raise NotImplementedError
