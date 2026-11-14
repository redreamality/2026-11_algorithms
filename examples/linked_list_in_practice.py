"""第 2 课实战：Python 项目里“链表”真正是怎么用的。

业务代码里几乎没人手写链表节点。需要链表的那些特性时，按场景选：
1. 两端都要快速增删（任务队列、工单队列、BFS）→ collections.deque。两端进出 O(1)。
2. 只保留最近 N 条（最近浏览、滑动日志）→ deque(maxlen=N)，满了自动从另一头挤掉。
3. 要“按 key 找到再挪到最前 / 最后”（LRU 缓存）→ collections.OrderedDict 的 move_to_end，
   它底层就是哈希表 + 双向链表（第 30 课会自己实现一个）。

运行：uv run examples/linked_list_in_practice.py
"""

from collections import OrderedDict, deque


class TicketQueue:
    """客服工单队列：普通工单排队尾，加急工单插队头，客服从队头取。"""

    def __init__(self) -> None:
        self._tickets: deque[str] = deque()

    def submit(self, ticket: str, urgent: bool = False) -> None:
        if urgent:
            self._tickets.appendleft(ticket)  # O(1)；list.insert(0, x) 是 O(n)
        else:
            self._tickets.append(ticket)

    def take(self) -> str | None:
        return self._tickets.popleft() if self._tickets else None  # O(1)；list.pop(0) 是 O(n)

    def withdraw(self, ticket: str) -> bool:
        """用户撤回工单：中间删除要先找到它，O(n)。deque.remove 找不到抛 ValueError。"""
        try:
            self._tickets.remove(ticket)
        except ValueError:
            return False
        return True

    def pending(self) -> list[str]:
        return list(self._tickets)


class RecentlyOpenedFiles:
    """编辑器的“最近打开的文件”：再次打开的文件挪到最前，最多记 limit 个。"""

    def __init__(self, limit: int) -> None:
        self._files: OrderedDict[str, None] = OrderedDict()
        self._limit = limit

    def open(self, path: str) -> None:
        self._files[path] = None
        self._files.move_to_end(path, last=False)  # 挪到最前，O(1)
        if len(self._files) > self._limit:
            self._files.popitem(last=True)  # 挤掉最旧的，O(1)

    def listing(self) -> list[str]:
        return list(self._files)


def main() -> None:
    queue = TicketQueue()
    for ticket in ["退款-101", "咨询-102", "投诉-103"]:
        queue.submit(ticket)
    queue.submit("加急-999", urgent=True)
    assert queue.take() == "加急-999"
    assert queue.withdraw("咨询-102") is True
    assert queue.withdraw("不存在-000") is False
    assert queue.pending() == ["退款-101", "投诉-103"]
    print("待处理工单：", queue.pending())

    recent_logs: deque[str] = deque(maxlen=3)
    for line in ["启动", "连接数据库", "收到请求", "返回 200"]:
        recent_logs.append(line)
    assert list(recent_logs) == ["连接数据库", "收到请求", "返回 200"]
    print("最近 3 条日志：", list(recent_logs))

    recent_files = RecentlyOpenedFiles(limit=3)
    for path in ["a.py", "b.py", "c.py", "a.py", "d.py"]:
        recent_files.open(path)
    assert recent_files.listing() == ["d.py", "a.py", "c.py"]
    print("最近打开：", recent_files.listing())


if __name__ == "__main__":
    main()
