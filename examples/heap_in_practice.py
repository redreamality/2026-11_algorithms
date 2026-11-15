"""第 12 课实战：Python 项目里“优先队列”真正是怎么写的。

几乎没人手写堆，按场景选：
1. 单线程里的优先队列 → 标准库 heapq，堆就是一个普通 list。存 (优先级, 序号, 任务)，
   序号保证同优先级先进先出，也保证永远不会去比较任务本身。
2. 最大 / 最小的 k 个 → heapq.nlargest / nsmallest，O(n log k)，不用全排序。
3. 合并多个已排序的大文件 → heapq.merge，惰性生成，内存只占 O(文件数)。
4. 多线程生产者 / 消费者 → queue.PriorityQueue（加了锁，可以阻塞等待）。

运行：uv run examples/heap_in_practice.py
"""

import heapq
from datetime import datetime, timedelta
from itertools import count


class Scheduler:
    """场景一：定时任务调度。最早到期的任务先执行，同一时刻到期的按提交顺序执行。"""

    def __init__(self) -> None:
        self._heap: list[tuple[datetime, int, str]] = []
        self._sequence = count()

    def schedule(self, run_at: datetime, task_name: str) -> None:
        heapq.heappush(self._heap, (run_at, next(self._sequence), task_name))

    def run_due(self, now: datetime) -> list[str]:
        """把所有到期（run_at <= now）的任务按顺序取出来执行。堆顶就是最早的，看一眼 O(1)。"""
        executed = []
        while self._heap and self._heap[0][0] <= now:
            _, _, task_name = heapq.heappop(self._heap)
            executed.append(task_name)
        return executed


def slowest_requests(log_lines: list[str], limit: int) -> list[tuple[str, int]]:
    """场景二：从访问日志里找最慢的几个请求。nlargest 内部维护一个大小为 limit 的堆。"""
    requests = []
    for line in log_lines:
        path, milliseconds = line.split()
        requests.append((path, int(milliseconds)))
    return heapq.nlargest(limit, requests, key=lambda request: request[1])


def main() -> None:
    # datetime(年, 月, 日, 时, 分) 是一个时间点，timedelta(minutes=30) 是一段时长，相加得到另一个时间点
    start = datetime(2026, 11, 10, 9, 0)
    scheduler = Scheduler()
    scheduler.schedule(start + timedelta(minutes=30), "生成日报")
    scheduler.schedule(start + timedelta(minutes=5), "清理缓存")
    scheduler.schedule(start + timedelta(minutes=5), "同步库存")  # 和清理缓存同时到期
    scheduler.schedule(start + timedelta(hours=2), "备份数据库")
    first_batch = scheduler.run_due(start + timedelta(minutes=10))
    assert first_batch == ["清理缓存", "同步库存"]
    second_batch = scheduler.run_due(start + timedelta(hours=1))
    assert second_batch == ["生成日报"]
    print("9:10 执行：", first_batch, "；10:00 执行：", second_batch)

    log = ["/home 80", "/pay 300", "/search 45", "/login 120", "/export 950"]
    slowest = slowest_requests(log, 2)
    assert slowest == [("/export", 950), ("/pay", 300)]
    print("最慢的两个请求：", slowest)

    server_a = [(1, "a 启动"), (5, "a 报错")]
    server_b = [(2, "b 启动"), (3, "b 请求")]
    merged = list(heapq.merge(server_a, server_b))
    assert [message for _, message in merged] == ["a 启动", "b 启动", "b 请求", "a 报错"]
    print("合并后的日志：", merged)


if __name__ == "__main__":
    main()
