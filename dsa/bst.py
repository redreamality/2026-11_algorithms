"""第 11 课：二叉搜索树（BST），做成一个能直接用的有序字典 TreeMap。讲解见 lessons/11-bst.html

实际项目里一般直接用 sortedcontainers.SortedDict（见 examples/bst_in_practice.py）。
这里自己手写一个，接口和 dict 一样：tree[key] = value、tree[key]、del tree[key]、
key in tree、len(tree)、for key in tree，另外加上 dict 做不到的有序查询。

规则：
- 任何节点：左子树里的键都比它小，右子树里的键都比它大。每个方法做完都要保持这一点。
- 键已经存在时，tree[key] = value 只更新值，不新增节点，长度不变。
- 删除有两个孩子的节点时，用“后继”（右子树里最小的键）替换它，再删掉后继原来的节点。
  测试会检查这一点：删掉有两个孩子的根以后，root.key 应该变成后继。
- 同时维护 _size，让 len() 是 O(1)。
- 高度约定和第 10 课一样：空树是 0，只有根是 1。
- 下面的 h 指树高。树平衡时 h ≈ log n，退化成链表时 h = n。

继承 MutableMapping 以后，只要写好 __getitem__、__setitem__、__delitem__、__iter__、__len__，
Python 会自动送你 get、pop、setdefault、update、keys、values、items、in、== 这些方法。

写完后运行 uv run dsa/bst.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_bst.py。
"""

from collections.abc import Iterator, MutableMapping


class Node:
    def __init__(self, key, value, left: "Node | None" = None, right: "Node | None" = None) -> None:
        self.key = key
        self.value = value
        self.left = left
        self.right = right


class TreeMap(MutableMapping):
    def __init__(self, items=()) -> None:
        self.root: Node | None = None
        self._size = 0
        self.update(items)  # MutableMapping 自带的 update，内部会调用 __setitem__

    @classmethod
    def fromkeys(cls, keys, value=None) -> "TreeMap":
        """和 dict.fromkeys 一样：TreeMap.fromkeys([3, 1, 2]) 按这个顺序插入，值都是 None。"""
        return cls((key, value) for key in keys)

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"TreeMap({dict(self.items())!r})"

    def __setitem__(self, key, value) -> None:
        """tree[key] = value。小往左、大往右走到空位挂上新节点；键已存在就只改值。O(h)。"""
        raise NotImplementedError

    def __getitem__(self, key):
        """tree[key]。找不到要抛 KeyError(key)，这样 get、in 才能正常工作。O(h)。"""
        raise NotImplementedError

    def __delitem__(self, key) -> None:
        """del tree[key]。找不到抛 KeyError(key)。O(h)。

        三种情况：没有孩子直接删；一个孩子让孩子顶上来；两个孩子用后继替换。
        提示：写一个递归辅助函数“在这棵子树里删掉 key，返回删完后的新子树根”，最省事。
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        """for key in tree：按中序（从小到大）依次产出键。用 yield 写。O(n)。"""
        raise NotImplementedError

    def min_key(self):
        """最小的键：一路往左走到底。O(h)。空树抛 ValueError。"""
        raise NotImplementedError

    def max_key(self):
        """最大的键：一路往右走到底。O(h)。空树抛 ValueError。"""
        raise NotImplementedError

    def floor_key(self, key):
        """小于等于 key 的最大键；没有就返回 None。key 本身不必在树里。O(h)。

        例子：键是 10、20、30 时，floor_key(25) 是 20，floor_key(20) 是 20，floor_key(5) 是 None。
        提示：从根往下走。当前键 <= key 时它是一个候选，记下来再往右找更大的；否则往左。
        """
        raise NotImplementedError

    def ceiling_key(self, key):
        """大于等于 key 的最小键；没有就返回 None。和 floor_key 左右对称。O(h)。"""
        raise NotImplementedError

    def items_between(self, low, high) -> Iterator[tuple]:
        """按键从小到大产出所有 low <= 键 <= high 的 (键, 值)。用 yield 写。

        不能先遍历整棵树再过滤：当前键 <= low 时，左子树里的键都更小，不用进去；
        当前键 >= high 时，右子树同理。这样复杂度是 O(h + 结果个数)。
        """
        raise NotImplementedError

    def height(self) -> int:
        """树高。空树 0，只有根 1。O(n)。"""
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

    # 端到端场景：一个按价格索引的商品目录，键是价格（分），值是商品名。
    def build_catalog():
        return TreeMap({1999: "鼠标", 8999: "显示器", 4599: "键盘", 29900: "笔记本", 699: "鼠标垫"})

    show("len(catalog)", lambda: len(build_catalog()), 5)
    show("list(catalog)：按价格从低到高", lambda: list(build_catalog()), [699, 1999, 4599, 8999, 29900])
    show("catalog[4599]", lambda: build_catalog()[4599], "键盘")
    show("catalog.get(1234, '没有')", lambda: build_catalog().get(1234, "没有"), "没有")
    show("最便宜 / 最贵", lambda: (build_catalog().min_key(), build_catalog().max_key()), (699, 29900))
    show("预算 50 元（5000 分）能买到的最贵商品",
         lambda: (lambda c: c[c.floor_key(5000)])(build_catalog()), "键盘")
    show("100 元以上最便宜的商品", lambda: (lambda c: c[c.ceiling_key(10000)])(build_catalog()), "笔记本")
    show("20～90 元之间的商品", lambda: list(build_catalog().items_between(2000, 9000)),
         [(4599, "键盘"), (8999, "显示器")])

    def restock():
        catalog = build_catalog()
        catalog[1999] = "无线鼠标"  # 同价换货：只改值
        del catalog[699]  # 下架
        return list(catalog.items())

    show("改值 + 下架之后", restock,
         [(1999, "无线鼠标"), (4599, "键盘"), (8999, "显示器"), (29900, "笔记本")])
