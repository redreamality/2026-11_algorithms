"""第 42 课：树状数组（Fenwick Tree）。讲解见 lessons/42-fenwick-tree.html

规则：
- 对外的下标和 Python 一样从 0 开始；内部的 self.tree 从 1 开始编号，tree[0] 不用。
  对外下标 index 对应内部位置 index + 1。
- lowbit(position) = position & -position：只留下 position 二进制里最低位的那个 1（第 39 课）。
- tree[position] 存的是 numbers 里内部位置 position - lowbit(position) + 1 到 position 这一段的和。
- 单点加：从 position 出发，position += lowbit(position)，一路往上更新，直到超过 n。
- 前缀和：从 position 出发，position -= lowbit(position)，一路往下累加，直到 0。
- prefix_sum(count) 的含义和第 27 课的 prefix_sum[count] 一样：前 count 个数的和，prefix_sum(0) == 0。
- 不要在 prefix_sum 里循环 count 次；循环次数必须是 O(log n)。
- 写完后运行 uv run pytest tests/test_fenwick_tree.py。
"""


def lowbit(position: int) -> int:
    """返回 position 二进制里最低位的 1 所代表的数。position >= 1。

    例子：lowbit(6) == 2（6 = 0b110），lowbit(8) == 8，lowbit(7) == 1。
    """
    raise NotImplementedError


class FenwickTree:
    """支持“单点加”和“前缀和查询”的数组，两种操作都是 O(log n)。

    例子：tree = FenwickTree([3, 1, 4, 1, 5, 9, 2, 6])
          tree.tree == [0, 3, 4, 4, 9, 5, 14, 2, 31]
          tree.prefix_sum(7) == 25           # 3 + 1 + 4 + 1 + 5 + 9 + 2
          tree.add(4, 3)                     # numbers[4] 从 5 变成 8
          tree.tree == [0, 3, 4, 4, 9, 8, 17, 2, 34]
          tree.prefix_sum(7) == 28
          tree.range_sum(2, 5) == 22         # 4 + 1 + 8 + 9
          tree[4] == 8
          tree[4] = 5                        # 改回 5，等价于 add(4, 5 - 8)

    要求：
    - self.tree 是长度 n + 1 的 list，tree[0] 固定为 0。
    - 下标越界（index < 0 或 index >= n；count < 0 或 count > n）抛 IndexError。
    - range_sum(left, right) 两端都包含；left > right 时返回 0。

    目标复杂度：构造 O(n log n)（逐个 add 即可；选做 O(n)），add、prefix_sum、range_sum、
    __getitem__、__setitem__ 都是 O(log n)，额外空间 O(n)。
    """

    def __init__(self, numbers: list[int]):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def add(self, index: int, delta: int) -> None:
        raise NotImplementedError

    def prefix_sum(self, count: int) -> int:
        raise NotImplementedError

    def range_sum(self, left: int, right: int) -> int:
        raise NotImplementedError

    def __getitem__(self, index: int) -> int:
        raise NotImplementedError

    def __setitem__(self, index: int, value: int) -> None:
        raise NotImplementedError


class RangeAddPointQuery:
    """区间加、单点查：把第 41 课的差分数组放进树状数组里。

    例子：numbers = [3, 1, 4, 1, 5, 9, 2, 6]
          values = RangeAddPointQuery(numbers)
          values.add(2, 5, 2)
          values[5] == 11
          values.add(4, 7, 3)
          values[5] == 14
          list(values) == [3, 1, 6, 3, 10, 14, 5, 9]   # 和第 41 课 to_list() 的结果一样

    思路提示：内部用一棵 FenwickTree 存差分数组（长度 n + 1）。区间加就是差分的两次单点加，
    numbers[index] 就是差分数组前 index + 1 项的和。

    要求：add 的区间不合法（0 <= left <= right < n 之外）或 index 越界时抛 IndexError。
    支持 len() 和 for 遍历（实现 __len__ 和 __getitem__，越界抛 IndexError，for 就能用）。

    目标复杂度：add 和 __getitem__ 都是 O(log n)。
    """

    def __init__(self, numbers: list[int]):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def add(self, left: int, right: int, delta: int) -> None:
        raise NotImplementedError

    def __getitem__(self, index: int) -> int:
        raise NotImplementedError


def count_inversions(numbers: list[int]) -> int:
    """逆序对计数：有多少对下标 i < j 满足 numbers[i] > numbers[j]。

    例子：count_inversions([3, 1, 4, 1, 5, 9, 2, 6]) == 8
          count_inversions([1, 2, 3]) == 0
          count_inversions([3, 2, 1]) == 3
          相等的两个数不算逆序对。

    思路提示：
    1. 离散化：numbers 的值可能很大或为负数，先把每个值换成它在 sorted(set(numbers)) 里的排名（从 0 开始）。
    2. 从左到右走，用一棵 FenwickTree 记“每个排名已经出现过几次”。走到 numbers[j] 时，
       前面比它大的个数 = 已经走过的个数 - 前面排名 <= 它的个数。
    3. 再把它的排名记进树里。

    目标复杂度：时间 O(n log n)，额外空间 O(n)。
    """
    raise NotImplementedError
