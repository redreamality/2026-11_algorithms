"""第 27 课实战：前缀和与哈希计数在真实代码里出现在哪。

1. 累计值（累计销售额、余额曲线）→ 标准库 itertools.accumulate，一行算出前缀和。
2. 报表里反复查“第 a 天到第 b 天的总和”→ 先算好前缀和（前面补一个 0），每次查询只做一次减法。
3. 按权重随机抽样（抽奖、灰度发布按比例分流）→ 权重的前缀和 + bisect 二分，O(log n) 一次。
   标准库 random.choices(population, weights=...) 内部就是这么做的。
4. 计数 → collections.Counter，就是本课的“哈希计数”。

运行：uv run examples/prefix_sum_in_practice.py
"""

import random
from bisect import bisect_right
from collections import Counter
from itertools import accumulate


class SalesReport:
    """场景一：每日销售额固定下来以后，反复查任意日期区间的总额。"""

    def __init__(self, daily_sales: list[int]) -> None:
        self._prefix_sum = list(accumulate(daily_sales, initial=0))  # 比原数组多一格，开头是 0

    def total(self, first_day: int, last_day: int) -> int:
        """第 first_day 天到第 last_day 天（两端都包含，从 0 开始数）的总额。O(1)。"""
        return self._prefix_sum[last_day + 1] - self._prefix_sum[first_day]


class WeightedPicker:
    """场景二：按权重抽样。灰度发布时 90% 流量走旧版、10% 走新版，就是权重 [90, 10]。"""

    def __init__(self, choices: list[str], weights: list[int]) -> None:
        self._choices = choices
        self._cumulative_weights = list(accumulate(weights))  # [90, 100]
        self._total_weight = self._cumulative_weights[-1]

    def pick(self, rng: random.Random) -> str:
        ticket = rng.random() * self._total_weight  # 落在 [0, 总权重) 里的一个点
        return self._choices[bisect_right(self._cumulative_weights, ticket)]  # 落在哪一段


def main() -> None:
    daily_sales = [120, 80, 200, 150, 90, 300, 60]
    report = SalesReport(daily_sales)
    assert report.total(0, 6) == sum(daily_sales)
    assert report.total(2, 4) == 200 + 150 + 90
    assert report.total(5, 5) == 300
    print("第 2～4 天销售额：", report.total(2, 4))

    balances = list(accumulate([100, -30, 50, -80]))
    assert balances == [100, 70, 120, 40]
    print("每笔交易后的余额：", balances)

    picker = WeightedPicker(["旧版", "新版"], [90, 10])
    # random.Random(27)：造一个独立的随机数生成器，27 是种子（作用和预备课讲的 random.seed(27) 一样）。
    # rng.random() 返回 [0, 1) 之间的小数。用独立的生成器比直接用 random 模块函数更可控。
    rng = random.Random(27)
    counts = Counter(picker.pick(rng) for _ in range(10_000))
    assert 8800 < counts["旧版"] < 9200
    print("1 万次分流：", dict(counts))

    words = "the cat and the hat and the bat".split()
    assert Counter(words).most_common(2) == [("the", 3), ("and", 2)]
    print("出现最多的两个词：", Counter(words).most_common(2))


if __name__ == "__main__":
    main()
