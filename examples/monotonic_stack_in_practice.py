"""第 28 课实战：单调栈在真实代码里出现在哪。

标准库里没有现成的单调栈，用 list 的 append / pop 就是栈。它出现在这类“每一项回头（或往前）看第一个更大/更小”的报表里：
1. 股票跨度：今天的价格连续高于（等于）前面多少天 → 往左看第一个更高的价格。
2. 天气日报：每天还要等几天才升温 → 往右看第一个更高的气温。
3. 监控告警：每个指标点之后，多久才再次超过它 → 同上。
暴力是 O(n²)，单调栈每个元素进栈出栈各一次，O(n)；流式数据（来一条处理一条）也能用。

运行：uv run examples/monotonic_stack_in_practice.py
"""


class StockSpanner:
    """场景一：价格一条一条流进来，每来一条，回答“连续多少天价格 <= 今天”（含今天）。"""

    def __init__(self) -> None:
        self._stack: list[tuple[int, int]] = []  # (价格, 它覆盖的天数)；价格从栈底到栈顶递减

    def next(self, price: int) -> int:
        span = 1
        while self._stack and self._stack[-1][0] <= price:
            span += self._stack.pop()[1]  # 比今天低的那些天，连同它们覆盖的天数，都并进来
        self._stack.append((price, span))
        return span


def days_until_warmer(temperatures: list[float]) -> list[int]:
    """场景二：天气日报，每天还要再等几天才有更高的气温；等不到就是 0。"""
    waits = [0] * len(temperatures)
    waiting_days: list[int] = []  # 还没等到升温的日子；对应气温从栈底到栈顶递减
    for today, temperature in enumerate(temperatures):
        while waiting_days and temperatures[waiting_days[-1]] < temperature:
            earlier_day = waiting_days.pop()
            waits[earlier_day] = today - earlier_day
        waiting_days.append(today)
    return waits


def main() -> None:
    spanner = StockSpanner()
    spans = [spanner.next(price) for price in [100, 80, 60, 70, 60, 75, 85]]
    assert spans == [1, 1, 1, 2, 1, 4, 6]
    print("股票跨度：", spans)

    waits = days_until_warmer([18.0, 19.5, 17.0, 16.5, 20.0, 22.0, 21.0])
    assert waits == [1, 3, 2, 1, 1, 0, 0]
    print("还要等几天升温：", waits)


if __name__ == "__main__":
    main()
