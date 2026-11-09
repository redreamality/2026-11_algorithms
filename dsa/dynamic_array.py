"""第 1 课：动态数组。讲解见 lessons/01-dynamic-array.html

Python 的 list 本身就是动态数组。这里我们自己造一个，看清楚它是怎么“变长”的。

规则：
- self._data 是一块“定长”的内存，只能用下标读写，长度永远等于 capacity。
  不要对它调用 append / insert / pop，否则就等于借用了 list 本身的扩容。
- 满了就扩容为原来的 2 倍：新建一块 [None] * (2 * capacity)，把旧元素逐个搬过去。
- 下标只支持 0 <= i < len(self)，越界抛 IndexError。
"""


class DynamicArray:
    def __init__(self) -> None:
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, i: int):
        """O(1)"""
        raise NotImplementedError

    def __setitem__(self, i: int, value) -> None:
        """O(1)"""
        raise NotImplementedError

    def append(self, value) -> None:
        """在末尾追加。均摊 O(1)。满了先调用 self._resize(2 * capacity)。"""
        raise NotImplementedError

    def pop(self):
        """删除并返回最后一个元素。O(1)。空数组抛 IndexError。"""
        raise NotImplementedError

    def insert(self, i: int, value) -> None:
        """在下标 i 处插入，后面的元素整体右移。O(n)。

        允许 0 <= i <= len(self)，i == len(self) 等同于 append；其他越界抛 IndexError。
        """
        raise NotImplementedError

    def remove_at(self, i: int):
        """删除并返回下标 i 处的元素，后面的元素整体左移。O(n)。"""
        raise NotImplementedError

    def _resize(self, new_capacity: int) -> None:
        """换一块大小为 new_capacity 的新内存，把旧元素搬过去。O(n)。"""
        raise NotImplementedError
