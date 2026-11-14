"""第 1 课：动态数组。讲解见 lessons/01-dynamic-array.html

Python 的 list 本身就是动态数组，实际项目里直接用 list（见 examples/dynamic_array_in_practice.py）。
这里自己造一个用法和 list 一样的 DynamicArray，看清楚它是怎么“变长”的：
arr = DynamicArray([1, 2]); arr.append(3); arr[0]; arr[-1] = 9; del arr[0]; len(arr); for x in arr; 3 in arr。

规则：
- self._data 是一块“定长”的内存，只能用下标读写，长度永远等于 capacity。
  不要对它调用 append / insert / pop，否则就等于借用了 list 本身的扩容。
- 满了就扩容为原来的 2 倍：新建一块 [None] * (2 * capacity)，把旧元素逐个搬过去。
- 下标和 list 一样支持负数：-1 是最后一个。合法范围是 -len(self) <= index < len(self)，越界抛 IndexError。
  只支持整数下标，不用支持切片。

继承 MutableSequence 以后，只要写好 __getitem__、__setitem__、__delitem__、__len__、insert，
Python 会自动送你 append、pop、remove、extend、index、count、reverse、in、for 循环这些方法。
比如继承来的 append(value) 就是 self.insert(len(self), value)，pop() 就是先取 self[-1] 再 del self[-1]。

写完后运行 uv run dsa/dynamic_array.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_dynamic_array.py。
"""

from collections.abc import MutableSequence


class DynamicArray(MutableSequence):
    def __init__(self, items=()) -> None:
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity
        self.extend(items)  # MutableSequence 自带的 extend，内部会逐个调用 append

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"DynamicArray({list(self)!r})"

    def __eq__(self, other) -> bool:
        """和 list 一样按内容比较：DynamicArray([1, 2]) == [1, 2] 为 True。"""
        if not isinstance(other, (DynamicArray, list)):
            return NotImplemented
        return list(self) == list(other)

    def _check_index(self, index: int) -> int:
        """把可能为负的下标换成 0 <= index < len(self) 的正下标；越界抛 IndexError。O(1)。

        例子：长度为 3 时，_check_index(-1) 返回 2，_check_index(3) 抛 IndexError。
        """
        raise NotImplementedError

    def __getitem__(self, index: int):
        """arr[index]。O(1)。"""
        raise NotImplementedError

    def __setitem__(self, index: int, value) -> None:
        """arr[index] = value。O(1)。"""
        raise NotImplementedError

    def __delitem__(self, index: int) -> None:
        """del arr[index]：后面的元素整体左移一格。O(n)。"""
        raise NotImplementedError

    def insert(self, index: int, value) -> None:
        """在 index 处插入，后面的元素整体右移。满了先调用 self._resize(2 * capacity)。O(n)。

        和 list.insert 一样不会抛异常：index 为负就从末尾数；比 len 大就插到末尾，比 -len 小就插到开头。
        所以 insert(len(self), value) 就是 append，在末尾插入不用挪元素，均摊 O(1)。
        """
        raise NotImplementedError

    def _resize(self, new_capacity: int) -> None:
        """换一块大小为 new_capacity 的新内存，把旧元素搬过去。O(n)。"""
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

    # 端到端场景：音乐播放列表。
    def build_playlist():
        return DynamicArray(["晴天", "稻香", "七里香"])

    show("len(playlist)", lambda: len(build_playlist()), 3)
    show("playlist[-1]：最后一首", lambda: build_playlist()[-1], "七里香")
    show("'稻香' in playlist", lambda: "稻香" in build_playlist(), True)
    show("playlist.index('七里香')", lambda: build_playlist().index("七里香"), 2)

    def edit_playlist():
        playlist = build_playlist()
        playlist.append("夜曲")  # 加到末尾
        playlist.insert(0, "开场白")  # 插到最前
        playlist[1] = "晴天（live）"  # 换版本
        playlist.remove("稻香")  # 按值删掉
        last = playlist.pop()  # 删掉最后一首并拿到它
        return list(playlist), last

    show("增、改、删之后", edit_playlist, (["开场白", "晴天（live）", "七里香"], "夜曲"))

    def capacities():
        playlist, seen = DynamicArray(), []
        for number in range(9):
            playlist.append(number)
            seen.append(playlist.capacity)
        return seen

    show("连续 append 9 次，capacity 的变化", capacities, [1, 2, 4, 4, 8, 8, 8, 8, 16])
