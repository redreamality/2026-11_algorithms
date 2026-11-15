"""第 33 课实战：Python 项目里“Top K / 合并有序流”真正是怎么写的。

业务代码里很少自己维护大小为 k 的堆，标准库已经包好了：
1. 出现次数最多的 k 个 → collections.Counter(...).most_common(k)
2. 按某个字段最大 / 最小的 k 个 → heapq.nlargest(k, items, key=...) / heapq.nsmallest
   内部就是本课的“大小为 k 的堆”，时间 O(n log k)，可以直接吃一个生成器，不用把数据全部装进内存。
3. 多个各自有序的文件 / 分片合并成一个有序流 → heapq.merge(*iterables, key=...)
   内部就是“合并 K 个有序链表”的堆，懒惰地一条一条产出。
4. k 接近 n、或者要全部排好序 → 直接 sorted(...)[:k] 更快更清楚。

运行：uv run examples/top_k_in_practice.py
"""

import heapq
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)  # frozen=True：建好后字段不能再改，当不可变的记录用（@dataclass 的一个开关）
class Request:
    timestamp: int  # 秒
    path: str
    latency_ms: int


# 两台服务器各自的访问日志，每份都已经按时间排好序。
SERVER_A_LOG = [
    Request(100, "/api/orders", 120),
    Request(103, "/api/users", 35),
    Request(107, "/api/orders", 980),
    Request(110, "/health", 2),
    Request(115, "/api/search", 450),
]
SERVER_B_LOG = [
    Request(101, "/api/orders", 140),
    Request(104, "/api/search", 1300),
    Request(108, "/api/orders", 95),
    Request(112, "/api/users", 40),
]


def merged_timeline(*logs: list[Request]) -> list[Request]:
    """把几份按时间排好序的日志合并成一条时间线。heapq.merge 不会把所有日志拼起来再排序。"""
    return list(heapq.merge(*logs, key=lambda request: request.timestamp))


def busiest_paths(requests: list[Request], k: int) -> list[tuple[str, int]]:
    """访问次数最多的 k 个接口：(路径, 次数)，次数从多到少。"""
    return Counter(request.path for request in requests).most_common(k)


def slowest_requests(requests: list[Request], k: int) -> list[Request]:
    """最慢的 k 个请求，从慢到快。"""
    return heapq.nlargest(k, requests, key=lambda request: request.latency_ms)


def main() -> None:
    timeline = merged_timeline(SERVER_A_LOG, SERVER_B_LOG)
    assert [request.timestamp for request in timeline] == [100, 101, 103, 104, 107, 108, 110, 112, 115]
    print("合并后的时间线：", [request.timestamp for request in timeline])

    top_paths = busiest_paths(timeline, 2)
    assert top_paths == [("/api/orders", 4), ("/api/users", 2)]  # 次数相同时，先出现的排前面
    print("访问最多的 2 个接口：", top_paths)

    slowest = slowest_requests(timeline, 3)
    assert [request.latency_ms for request in slowest] == [1300, 980, 450]
    print("最慢的 3 个请求：", [(request.path, request.latency_ms) for request in slowest])

    fastest = heapq.nsmallest(2, timeline, key=lambda request: request.latency_ms)
    assert [request.path for request in fastest] == ["/health", "/api/users"]
    print("最快的 2 个请求：", [(request.path, request.latency_ms) for request in fastest])


if __name__ == "__main__":
    main()
