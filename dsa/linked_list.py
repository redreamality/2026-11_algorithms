"""第 2 课：单链表。讲解见 lessons/02-linked-list.html

实际项目里要“两端快速增删”直接用 collections.deque（见 examples/linked_list_in_practice.py）。
这里自己造一个单链表，方法名和 deque 一样，写完就能直接替换着用：
tasks = LinkedList(["a", "b"]); tasks.append("c"); tasks.appendleft("urgent"); tasks.popleft();
len(tasks)、for task in tasks、"b" in tasks、tasks.remove("b")、tasks.reverse()。

规则：
- 只能通过 Node 的 next 指针串起数据，不要在内部偷偷用 list 存元素。
- 同时维护 head（头）和 tail（尾），让 append 也是 O(1)。
- 异常和 deque / list 一致：空链表 popleft 抛 IndexError；remove 一个不存在的值抛 ValueError。
- 每个改动链表的方法写完后，都检查一下 head、tail、size 是否还对。
  最容易出错的地方是：链表变空、只剩一个节点、删掉的正好是尾巴。

写完后运行 uv run dsa/linked_list.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_linked_list.py。
"""

from collections.abc import Iterator


class Node:
    def __init__(self, value, next: "Node | None" = None) -> None:
        self.value = value
        self.next = next


class LinkedList:
    def __init__(self, items=()) -> None:
        self.head: Node | None = None
        self.tail: Node | None = None
        self._size = 0
        for item in items:
            self.append(item)

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"LinkedList({list(self)!r})"

    def __eq__(self, other) -> bool:
        """按内容比较：LinkedList([1, 2]) == [1, 2] 为 True。"""
        if not isinstance(other, (LinkedList, list)):
            return NotImplemented
        return list(self) == list(other)

    def __iter__(self) -> Iterator:
        """for value in linked_list：从头到尾依次产出每个值。用 yield 写。O(n)。"""
        raise NotImplementedError

    def __contains__(self, value) -> bool:
        """value in linked_list：从头往后找。O(n)。"""
        raise NotImplementedError

    def appendleft(self, value) -> None:
        """在头部插入。O(1)。"""
        raise NotImplementedError

    def append(self, value) -> None:
        """在尾部插入。靠 tail 做到 O(1)。"""
        raise NotImplementedError

    def popleft(self):
        """删除并返回头部的值。O(1)。空链表抛 IndexError。"""
        raise NotImplementedError

    def remove(self, value) -> None:
        """删除第一个等于 value 的节点。O(n)。找不到抛 ValueError，和 list.remove 一样。

        提示：在 head 前面放一个哨兵节点 dummy，删头节点和删中间节点就是同一种写法。
        """
        raise NotImplementedError

    def reverse(self) -> None:
        """原地反转：不新建节点，只改 next 指针，最后 head 和 tail 互换。O(n)。"""
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

    # 端到端场景：客服工单队列。普通工单排到队尾，加急工单插到队头，客服从队头取。
    def build_tickets():
        return LinkedList(["退款-101", "咨询-102", "投诉-103"])

    show("len(tickets)", lambda: len(build_tickets()), 3)
    show("'咨询-102' in tickets", lambda: "咨询-102" in build_tickets(), True)

    def handle_tickets():
        tickets = build_tickets()
        tickets.append("咨询-104")  # 新工单排队尾
        tickets.appendleft("加急-999")  # 加急插队头
        first = tickets.popleft()  # 客服接走第一个
        tickets.remove("咨询-102")  # 用户撤回了这个工单
        return first, list(tickets)

    show("加急、接单、撤回之后", handle_tickets, ("加急-999", ["退款-101", "投诉-103", "咨询-104"]))

    def withdraw_missing():
        try:
            build_tickets().remove("不存在-000")
        except ValueError:
            return "ValueError"
        return "没抛异常"

    show("撤回一个不存在的工单", withdraw_missing, "ValueError")

    def newest_first():
        tickets = build_tickets()
        tickets.reverse()
        return list(tickets)

    show("reverse()：最新的排最前", newest_first, ["投诉-103", "咨询-102", "退款-101"])
