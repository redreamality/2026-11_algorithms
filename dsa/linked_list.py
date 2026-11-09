"""第 2 课：单链表。讲解见 lessons/02-linked-list.html

规则：
- 只能通过 Node 的 next 指针串起数据，不要在内部偷偷用 list 存元素。
- 同时维护 head（头）和 tail（尾），让 push_back 也是 O(1)。
- 每个改动链表的方法写完后，都检查一下 head、tail、size 是否还对。
  最容易出错的地方是：链表变空、只剩一个节点、删掉的正好是尾巴。
"""


class Node:
    def __init__(self, value, next: "Node | None" = None) -> None:
        self.value = value
        self.next = next


class LinkedList:
    def __init__(self) -> None:
        self.head: Node | None = None
        self.tail: Node | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        """从头到尾依次产出每个值。O(n)。"""
        raise NotImplementedError

    def push_front(self, value) -> None:
        """在头部插入。O(1)。"""
        raise NotImplementedError

    def push_back(self, value) -> None:
        """在尾部插入。O(1)。"""
        raise NotImplementedError

    def pop_front(self):
        """删除并返回头部的值。O(1)。空链表抛 IndexError。"""
        raise NotImplementedError

    def find(self, value) -> bool:
        """是否包含 value。O(n)。"""
        raise NotImplementedError

    def remove(self, value) -> bool:
        """删除第一个等于 value 的节点，删到了返回 True。O(n)。"""
        raise NotImplementedError

    def reverse(self) -> None:
        """原地反转：不新建节点，只改 next 指针。O(n)。"""
        raise NotImplementedError
