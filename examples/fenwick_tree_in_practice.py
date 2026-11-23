"""第 42 课实战：树状数组在真实代码里出现在哪。

标准库里没有树状数组。实际项目里遇到“数组会改、还要反复查前缀和 / 区间和”，
通常就地写一个二十行的小类（下面的 FenwickTree），或者在“只关心排名”的场景里改用
sortedcontainers.SortedList（预备课讲过）。

1. 每日销售额会被事后修正（退款、补录），报表又要随时查任意日期区间的合计。
   第 27 课的前缀和改一个数要 O(n)，树状数组改和查都是 O(log n)。
2. 实时排名：分数是 0～100 的整数，玩家不停提交分数，随时查“比我高的有几个人”。
   以“分数”为下标，树状数组里记“每个分数有几个人”。
3. 逆序对计数：树状数组写法和 SortedList 写法对比，结果一样。

运行：uv run examples/fenwick_tree_in_practice.py
"""

from sortedcontainers import SortedList


class FenwickTree:
    """对外下标从 0 开始，内部 tree 从 1 开始编号。"""

    def __init__(self, size: int) -> None:
        self._tree = [0] * (size + 1)

    def add(self, index: int, delta: int) -> None:
        position = index + 1
        while position < len(self._tree):
            self._tree[position] += delta
            position += position & -position  # 往上跳：加上 lowbit

    def prefix_sum(self, count: int) -> int:
        """前 count 个数的和。"""
        total = 0
        while count > 0:
            total += self._tree[count]
            count -= count & -count  # 往下跳：减去 lowbit
        return total

    def range_sum(self, left: int, right: int) -> int:
        return self.prefix_sum(right + 1) - self.prefix_sum(left)


class SalesLedger:
    """场景一：每日销售额，可以事后修正某一天，随时查区间合计。"""

    def __init__(self, daily_sales: list[int]) -> None:
        self._daily_sales = list(daily_sales)
        self._tree = FenwickTree(len(daily_sales))
        for day, amount in enumerate(daily_sales):
            self._tree.add(day, amount)

    def correct(self, day: int, new_amount: int) -> None:
        self._tree.add(day, new_amount - self._daily_sales[day])  # 只加上“差了多少”
        self._daily_sales[day] = new_amount

    def total(self, first_day: int, last_day: int) -> int:
        return self._tree.range_sum(first_day, last_day)


class Leaderboard:
    """场景二：分数是 0～max_score 的整数。查“比 score 高的有几个人”。"""

    def __init__(self, max_score: int) -> None:
        self._max_score = max_score
        self._player_count_by_score = FenwickTree(max_score + 1)  # 下标就是分数
        self._player_count = 0

    def submit(self, score: int) -> None:
        self._player_count_by_score.add(score, 1)
        self._player_count += 1

    def higher_than(self, score: int) -> int:
        return self._player_count - self._player_count_by_score.prefix_sum(score + 1)  # 总人数 - 分数 <= score 的人数


def count_inversions_with_fenwick(numbers: list[int]) -> int:
    rank_of = {value: rank for rank, value in enumerate(sorted(set(numbers)))}  # 离散化
    seen = FenwickTree(len(rank_of))
    inversion_count = 0
    for seen_count, number in enumerate(numbers):
        inversion_count += seen_count - seen.prefix_sum(rank_of[number] + 1)  # 前面比它大的个数
        seen.add(rank_of[number], 1)
    return inversion_count


def count_inversions_with_sorted_list(numbers: list[int]) -> int:
    seen = SortedList()
    inversion_count = 0
    for number in numbers:
        inversion_count += len(seen) - seen.bisect_right(number)  # 前面比它大的个数
        seen.add(number)
    return inversion_count


def main() -> None:
    ledger = SalesLedger([3, 1, 4, 1, 5, 9, 2, 6])  # 和讲解页的主线例子同一个数组
    assert ledger.total(0, 6) == 25
    ledger.correct(4, 8)  # 第 4 天补录了 3
    assert ledger.total(0, 6) == 28
    assert ledger.total(2, 5) == 22
    print("修正后第 2～5 天的销售额：", ledger.total(2, 5))

    board = Leaderboard(max_score=100)
    for score in [88, 95, 70, 95, 60]:
        board.submit(score)
    assert board.higher_than(88) == 2
    assert board.higher_than(95) == 0
    board.submit(99)
    assert board.higher_than(88) == 3
    print("比 88 分高的人数：", board.higher_than(88))

    numbers = [3, 1, 4, 1, 5, 9, 2, 6]
    assert count_inversions_with_fenwick(numbers) == count_inversions_with_sorted_list(numbers) == 8
    big = list(range(20_000, 0, -1))
    assert count_inversions_with_fenwick(big) == count_inversions_with_sorted_list(big) == 20_000 * 19_999 // 2
    print("逆序对个数：", count_inversions_with_fenwick(numbers))


if __name__ == "__main__":
    main()
