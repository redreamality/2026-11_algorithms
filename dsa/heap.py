"""第 12 课：堆与优先队列。讲解见 lessons/12-heap.html

实际项目里直接用标准库 heapq（见 examples/heap_in_practice.py）。这里手写的是一个能直接用在
任务调度里的 PriorityQueue，外加 heapq 里最常用的两个函数 nsmallest 和 merge 的自己的版本。

规则：
- 用一个普通 list 存完全二叉树：父亲 (i-1)//2，左孩子 2i+1，右孩子 2i+2。
- 最小堆：每个父亲都 <= 它的孩子，所以最小值在下标 0。
- 不要 import heapq，也不要用 sorted / list.sort。
- 先写两个辅助函数 _sift_up(heap, index) 和 _sift_down(heap, index)，下面所有东西都复用它们。
- 最容易出错的地方是：下沉时没选较小的孩子、只有左孩子、只剩一个元素时 pop。

PriorityQueue 里存的不是元素本身，而是三元组 (优先级, 序号, 元素)：
- 优先级 = key(元素)，没给 key 就是元素自己。
- 序号每 push 一次加一。优先级相同时比序号，所以同优先级先进先出，
  而且永远比不到第三项：元素本身（比如 dict）不能比大小也没关系。
这正是 heapq 官方文档推荐的写法。

写完后运行 uv run dsa/heap.py，看端到端的例子；再跑 uv run pytest tests/test_heap.py。
"""

from collections.abc import Callable, Iterable, Iterator
from itertools import count


def _sift_up(heap: list, index: int) -> None:
    """heap[index] 比父亲小就和父亲交换，一直往上，直到不比父亲小或到了根。O(log n)。"""
    raise NotImplementedError


def _sift_down(heap: list, index: int) -> None:
    """heap[index] 和较小的孩子比，比它大就交换，一直往下，直到没孩子或不比孩子大。O(log n)。"""
    raise NotImplementedError


def heapify(items: list) -> None:
    """原地把 items 变成最小堆：从 len(items)//2 - 1 往前逐个下沉。O(n)。返回 None，和 heapq.heapify 一样。"""
    raise NotImplementedError


class PriorityQueue:
    """谁的优先级最小谁先出；优先级相同时先进先出。

    queue = PriorityQueue(key=lambda task: task["priority"])
    queue.push({"name": "发邮件", "priority": 2})
    queue.pop()  # 取出优先级最小的任务
    """

    def __init__(self, items: Iterable = (), key: Callable | None = None) -> None:
        self._key = key if key is not None else (lambda item: item)
        self._sequence = count()  # 0, 1, 2, ……每次 next() 拿下一个序号
        self._entries: list[tuple] = [(self._key(item), next(self._sequence), item) for item in items]
        heapify(self._entries)  # 一次性建堆是 O(n)，比逐个 push 的 O(n log n) 快

    def __len__(self) -> int:
        return len(self._entries)

    def __bool__(self) -> bool:
        """while queue: ... 这种写法靠它。"""
        return bool(self._entries)

    def __repr__(self) -> str:
        return f"PriorityQueue({[item for _, _, item in self._entries]!r})"

    def push(self, item) -> None:
        """把 (优先级, 序号, item) 放到末尾，再上浮。O(log n)。"""
        raise NotImplementedError

    def pop(self):
        """删除并返回优先级最小的 item（不是三元组）。末尾挪到堆顶，再下沉。O(log n)。

        空队列抛 IndexError("pop from an empty priority queue")。
        """
        raise NotImplementedError

    def peek(self):
        """返回优先级最小的 item 但不删除。O(1)。空队列抛 IndexError。"""
        raise NotImplementedError


def nsmallest(n: int, iterable: Iterable, key: Callable | None = None) -> list:
    """最小的 n 个，从小到大返回，和 heapq.nsmallest 一样。n <= 0 返回 []。

    不许把全部数据排序：维护一个大小为 n 的堆，存“目前最小的 n 个”。
    堆顶要是这 n 个里最大的那个，才能快速判断新来的值要不要换进去，
    所以存相反数把最小堆当最大堆用：堆里放 (-key(x), -位置, x)，这要求 key 返回数字。
    key 相同时位置靠后的先被换出去，所以 key 相同的保持原来的先后顺序。
    最后把堆里剩下的逐个 pop 出来（从大到小），再反过来就是答案。
    时间 O(len(iterable) · log n)，额外空间 O(n)。
    """
    raise NotImplementedError


def merge(*iterables: Iterable) -> Iterator:
    """把几个各自已经排好序的序列合并成一个有序的生成器，和 heapq.merge 一样。

    堆里只放每个序列“当前的第一个”，弹出一个就从同一个序列补一个进来。
    输入可以是很大的文件或生成器，不能先全部读进内存。
    时间 O(总个数 · log k)，k 是序列个数；额外空间 O(k)。值相等时，排在前面的序列先出。
    """
    raise NotImplementedError


if __name__ == "__main__":

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景：客服工单系统。数字越小越紧急，同样紧急就先来先处理。
    def handle_tickets():
        queue = PriorityQueue(key=lambda ticket: ticket["urgency"])
        queue.push({"id": "T1", "urgency": 3})
        queue.push({"id": "T2", "urgency": 1})
        queue.push({"id": "T3", "urgency": 3})
        queue.push({"id": "T4", "urgency": 2})
        handled = []
        while queue:
            handled.append(queue.pop()["id"])
        return handled

    show("工单处理顺序（T1、T3 同样紧急，先来的 T1 先处理）", handle_tickets, ["T2", "T4", "T1", "T3"])
    show("下一个要处理的（只看不取）",
         lambda: PriorityQueue([5, 1, 4]).peek(), 1)
    show("响应最快的 2 个接口",
         lambda: nsmallest(2, [("/login", 120), ("/search", 45), ("/pay", 300), ("/home", 80)],
                           key=lambda pair: pair[1]),
         [("/search", 45), ("/home", 80)])
    show("合并两台服务器各自按时间排好的日志",
         lambda: list(merge([(1, "a 启动"), (5, "a 报错")], [(2, "b 启动"), (3, "b 请求")])),
         [(1, "a 启动"), (2, "b 启动"), (3, "b 请求"), (5, "a 报错")])
