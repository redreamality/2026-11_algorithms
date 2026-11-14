"""第 37 课实战：一维 DP 在业务代码里长什么样。

真实代码里很少写“dp 数组”这个词，常见的是两种写法：
1. 递归 + functools.cache：把“我想求的东西”直接写成递归函数，cache 自动记住算过的结果。
   写起来最像题意，适合状态数不大（几千以内，递归深度受 Python 默认 1000 层限制）。
2. 一个列表从前往后填：状态多、或者要避免递归太深时用。

而且业务里往往不只要“最优值”，还要“具体怎么选”，所以要记下每一步的选择，最后倒推出方案。

运行：uv run examples/dp_1d_in_practice.py
"""

from functools import cache


def cheapest_pass_plan(travel_days: list[int], prices: dict[int, int]) -> tuple[int, list[tuple[int, int]]]:
    """场景一：最省钱的会员购买方案（LeetCode 983 的业务版）。

    travel_days 是一年里要用的日子（从小到大），prices 是 {有效天数: 价格}，例如 {1: 7, 7: 30, 30: 99}。
    返回 (最少花多少钱, 购买计划)。购买计划是 [(从哪天开始买, 买几天的卡), ...]。

    用 functools.cache：cost_from(index) = 从第 index 个出行日起，覆盖后面所有出行日的最少花费。
    """

    def first_uncovered(index: int, duration: int) -> int:
        covered_until = travel_days[index] + duration  # 这一天起不再覆盖
        while index < len(travel_days) and travel_days[index] < covered_until:
            index += 1
        return index

    @cache
    def cost_from(index: int) -> int:
        if index == len(travel_days):
            return 0
        return min(price + cost_from(first_uncovered(index, duration)) for duration, price in prices.items())

    plan = []
    index = 0
    while index < len(travel_days):  # 倒推方案：每一步选“让总花费等于最优值”的那张卡
        for duration, price in prices.items():
            next_index = first_uncovered(index, duration)
            if price + cost_from(next_index) == cost_from(index):
                plan.append((travel_days[index], duration))
                index = next_index
                break
    return cost_from(0), plan


def pick_non_adjacent_slots(revenues: list[int]) -> tuple[int, list[int]]:
    """场景二：广告位不能相邻投放（打家劫舍的业务版），选哪些位置收入最高？

    返回 (最高收入, 选中的下标)。用列表从前往后填：
    best_up_to[i] = 只看前 i 个位置时的最高收入；第 i - 1 个位置要么不选，要么选（那就不能选第 i - 2 个）。
    """
    best_up_to = [0] * (len(revenues) + 1)
    for i in range(1, len(revenues) + 1):
        skip_this = best_up_to[i - 1]
        take_this = revenues[i - 1] + (best_up_to[i - 2] if i >= 2 else 0)
        best_up_to[i] = max(skip_this, take_this)

    chosen = []
    i = len(revenues)
    while i >= 1:  # 从后往前倒推：最优值没变说明这个位置没选
        if best_up_to[i] == best_up_to[i - 1]:
            i -= 1
        else:
            chosen.append(i - 1)
            i -= 2
    return best_up_to[-1], chosen[::-1]


def split_into_words(text: str, vocabulary: set[str]) -> list[str] | None:
    """场景三：把没有空格的字符串切成词（话题标签、域名分词）。切不开返回 None。

    就是单词拆分（LeetCode 139），只是要返回切法而不只是 True/False。
    split_starting_at(start) = text[start:] 的一种切法；cache 保证每个起点只算一次。
    """
    longest_word = max(map(len, vocabulary), default=0)

    @cache
    def split_starting_at(start: int) -> tuple[str, ...] | None:
        if start == len(text):
            return ()
        for end in range(min(len(text), start + longest_word), start, -1):  # 优先试长词
            word = text[start:end]
            if word in vocabulary:
                rest = split_starting_at(end)
                if rest is not None:
                    return (word, *rest)
        return None

    words = split_starting_at(0)
    return list(words) if words is not None else None


def main() -> None:
    days = [1, 4, 6, 7, 8, 20]
    total, plan = cheapest_pass_plan(days, {1: 2, 7: 7, 30: 15})
    assert total == 11
    assert plan == [(1, 1), (4, 7), (20, 1)]
    print("出行日", days, "最少花", total, "元，计划：", plan)

    many_days = list(range(1, 29))
    total, plan = cheapest_pass_plan(many_days, {1: 2, 7: 7, 30: 15})
    assert (total, plan) == (15, [(1, 30)])
    print("连续出行 28 天：买一张 30 天卡，", total, "元")

    revenue, slots = pick_non_adjacent_slots([5, 1, 1, 5, 3, 9])
    assert (revenue, slots) == (19, [0, 3, 5])
    print("不相邻广告位：选", slots, "收入", revenue)
    assert pick_non_adjacent_slots([]) == (0, [])

    vocabulary = {"python", "py", "thon", "data", "science", "sci", "ence"}
    assert split_into_words("pythondatascience", vocabulary) == ["python", "data", "science"]
    assert split_into_words("pythonx", vocabulary) is None
    print("话题标签分词：", split_into_words("pythondatascience", vocabulary))


if __name__ == "__main__":
    main()
