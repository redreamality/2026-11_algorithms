"""第 26 课实战：滑动窗口在真实代码里出现在哪。

最常见的是“按时间滑动的窗口”，几乎都用标准库 collections.deque：
1. 限流：每个用户最近 60 秒最多请求 N 次 → deque 存请求时间，右边进新请求，左边弹掉过期的。
2. 移动平均、最近 N 条记录 → deque(maxlen=N)，满了以后自动从左边挤掉最旧的，固定大小的窗口一行搞定。
3. 一次性批量统计（每 k 天的滚动和）→ 维护窗口和：进一个加、出一个减，不要每次 sum 整个窗口。

每个元素只进窗口一次、出窗口一次，所以都是 O(n)；deque 两端进出都是 O(1)，list.pop(0) 是 O(n)。

运行：uv run examples/sliding_window_in_practice.py
"""

from collections import deque


class RateLimiter:
    """场景一：滑动时间窗口限流。任意 window_seconds 秒内，同一个用户最多 max_requests 次。"""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._request_times: dict[str, deque[float]] = {}

    def allow(self, user_id: str, now: float) -> bool:
        request_times = self._request_times.setdefault(user_id, deque())
        while request_times and request_times[0] <= now - self.window_seconds:
            request_times.popleft()  # 收缩：过期的请求移出窗口
        if len(request_times) >= self.max_requests:
            return False
        request_times.append(now)  # 扩张：新请求放进窗口
        return True


def moving_average(values: list[float], window_size: int) -> list[float]:
    """场景二：最近 window_size 个读数的平均值，每来一个读数输出一次（不满时按已有的算）。"""
    window: deque[float] = deque(maxlen=window_size)
    window_sum = 0.0
    averages = []
    for value in values:
        if len(window) == window_size:
            window_sum -= window[0]  # 马上要被 maxlen 挤出去的那个
        window.append(value)
        window_sum += value
        averages.append(window_sum / len(window))
    return averages


def rolling_sums(daily_sales: list[int], days: int) -> list[int]:
    """场景三：报表里的“近 days 天销售额”，每一天出一个数（从第 days 天开始）。"""
    window_sum = sum(daily_sales[:days])
    sums = [window_sum]
    for window_end in range(days, len(daily_sales)):
        window_sum += daily_sales[window_end] - daily_sales[window_end - days]
        sums.append(window_sum)
    return sums


def main() -> None:
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    decisions = [limiter.allow("alice", now) for now in [0, 10, 20, 30, 60, 61, 70]]
    # 30 秒：窗口里已有 0、10、20，超限（被拒的请求不进窗口）。
    # 60 秒：0 秒那次过期，放行。61 秒：窗口里是 10、20、60，又满了。70 秒：10 秒那次过期，放行。
    assert decisions == [True, True, True, False, True, False, True]
    assert limiter.allow("bob", 30)  # 每个用户各算各的
    print("alice 的请求是否放行：", decisions)

    averages = moving_average([10, 20, 30, 40, 50], window_size=3)
    assert averages == [10.0, 15.0, 20.0, 30.0, 40.0]
    print("最近 3 个读数的平均：", averages)

    sums = rolling_sums([5, 3, 8, 1, 4, 7, 2], days=3)
    assert sums == [16, 12, 13, 12, 13]
    print("近 3 天销售额：", sums)

    recent_errors = deque(maxlen=3)
    for message in ["超时", "连接失败", "超时", "磁盘满"]:
        recent_errors.append(message)
    assert list(recent_errors) == ["连接失败", "超时", "磁盘满"]
    print("最近 3 条错误：", list(recent_errors))


if __name__ == "__main__":
    main()
