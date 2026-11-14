"""第 24 课（选修）：AVL 树，做成一个不管按什么顺序插入都不会退化的有序字典。讲解见 lessons/24-balanced-tree.html

实际项目里用 sortedcontainers.SortedDict（见 examples/avl_in_practice.py），它不是平衡树，
但给的保证一样：增删查约 O(log n)、按键有序遍历。这里手写的 AVLTreeMap 用法和第 11 课的 TreeMap、
和 dict 都一样：tree[key] = value、tree[key]、del tree[key]、key in tree、len(tree)、for key in tree。
区别是它在插入时自动旋转，按 1、2、3…… 的顺序插入也能保持 h = O(log n)。

规则：
- 它首先是一棵 BST：左子树的键都比节点小，右子树的键都比节点大。
  键已经存在时，tree[key] = value 只更新值，不新增节点，长度不变。
- 每个节点记着自己的 height：叶子是 1，空树（None）是 0。用下面的 height() 取，别自己判空。
- 平衡因子 bf = 左高 - 右高，每个节点都要在 -1、0、1 之内。插入后沿路往回检查，超出就旋转：
    LL：右旋；RR：左旋；LR：先左旋左孩子再右旋；RL：先右旋右孩子再左旋。
- 旋转函数返回新的子树根，并且负责更新相关节点的 height（先下面的，后上面的）。
- 同时维护 _size，让 len() 是 O(1)。

写完后运行 uv run dsa/avl.py，看端到端的例子；再跑 uv run pytest tests/test_avl.py。
"""

from collections.abc import Iterator, MutableMapping


class AVLNode:
    def __init__(self, key, value=None) -> None:
        self.key = key
        self.value = value
        self.left: "AVLNode | None" = None
        self.right: "AVLNode | None" = None
        self.height = 1


def height(node: AVLNode | None) -> int:
    """节点的高度，None 是 0。"""
    return node.height if node else 0


def update_height(node: AVLNode) -> None:
    """按两个孩子的高度重新算 node.height。孩子的高度必须已经是对的。"""
    node.height = 1 + max(height(node.left), height(node.right))


def rotate_right(top: AVLNode) -> AVLNode:
    """右旋：top 的左孩子升上来当根，top 变成它的右孩子，它原来的右子树挂到 top 的左边。

    更新两个节点的 height（先 top，再新根），返回新根。O(1)。
    """
    raise NotImplementedError


def rotate_left(top: AVLNode) -> AVLNode:
    """左旋：和 rotate_right 对称。更新 height，返回新的子树根。O(1)。"""
    raise NotImplementedError


def rebalance(node: AVLNode) -> AVLNode:
    """先更新 node 的 height，再看平衡因子，需要就做四种旋转之一。返回这棵子树新的根。O(1)。

    判断方法：bf = +2 时看左孩子的 bf，>= 0 是 LL（一次右旋），< 0 是 LR（两次旋转）。-2 对称。
    """
    raise NotImplementedError


class AVLTreeMap(MutableMapping):
    def __init__(self, items=()) -> None:
        self.root: AVLNode | None = None
        self._size = 0
        self.update(items)  # MutableMapping 自带的 update，内部会调用 __setitem__

    @classmethod
    def fromkeys(cls, keys, value=None) -> "AVLTreeMap":
        """和 dict.fromkeys 一样：按这个顺序插入，值都是 value。"""
        return cls((key, value) for key in keys)

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"AVLTreeMap({dict(self.items())!r})"

    def __setitem__(self, key, value) -> None:
        """tree[key] = value。插入后沿路 rebalance，保持平衡。键已存在就只改值。O(log n)。

        提示：写一个递归的 _insert(node, key, value)，返回插入（并旋转）后的新子树根，
        调用方写 node.left = self._insert(node.left, key, value)，父亲的指针就自动改好了。
        """
        raise NotImplementedError

    def __getitem__(self, key):
        """tree[key]。找不到抛 KeyError(key)。O(log n)。"""
        raise NotImplementedError

    def __delitem__(self, key) -> None:
        """（选做）del tree[key]。找不到抛 KeyError(key)。O(log n)。

        和第 11 课一样分三种情况（两个孩子时用后继替换），只是回来的路上每个节点都要 rebalance。
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator:
        """for key in tree：按中序（从小到大）依次产出键。用 yield 写。O(n)。"""
        raise NotImplementedError

    def height(self) -> int:
        """整棵树的高度，空树 0。O(1)（直接读根的 height）。"""
        raise NotImplementedError

    def is_balanced(self) -> bool:
        """每个节点的 |左高 - 右高| <= 1 吗？

        要按真实结构重新算高度，不能只信节点里存的 height。O(n)。
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

    # 端到端场景：订单号是自增的，按顺序写入一个“订单号 -> 金额”的索引。
    # 普通 BST 会退化成 1 万层的链表；AVL 始终只有十几层。
    def build_orders():
        return AVLTreeMap((order_id, order_id % 97) for order_id in range(1, 10_001))

    show("1 万个自增订单号，树有几层（不超过 1.44 log2 n ≈ 19）",
         lambda: build_orders().height() <= 19, True)
    show("每个节点都平衡", lambda: build_orders().is_balanced(), True)
    show("查订单 4242 的金额", lambda: build_orders()[4242], 4242 % 97)
    show("最早的三个订单号", lambda: list(build_orders())[:3], [1, 2, 3])

    def cancel_orders():
        orders = build_orders()
        for order_id in range(1, 5001):
            del orders[order_id]  # 选做：删掉前一半
        return len(orders), orders.is_balanced(), next(iter(orders))

    show("（选做）取消前 5000 个订单后：剩几个、是否平衡、最早的订单号", cancel_orders, (5000, True, 5001))
