"""第 15 课：并查集。讲解见 lessons/15-union-find.html

标准库没有并查集，但它很短，实际项目里就是自己写一个小类（见 examples/union_find_in_practice.py）。
这里写一个能直接用的版本：元素可以是任何可哈希的东西（邮箱、用户 ID、(行, 列)），不用先编号成 0..n-1。

规则：
- self.parent 是 dict：parent[x] 是 x 的父节点，根的 parent 是它自己。
  整个结构是一片森林，每棵树是一个集合，树根就是集合的“代表”。测试会直接检查 self.parent。
- 元素第一次出现在 union 里时自动加进来（自成一个集合）；add 也可以显式加。
  find / size_of 碰到从没加过的元素，抛 KeyError(x)，和 dict 一样。
- find 要做路径压缩：找到根以后，把沿途经过的每个节点都直接指向根。
  要用循环写，不要递归：一条 20 万长的链递归会超过 Python 的递归深度。
- union 要按大小合并：小树的根挂到大树的根下面，一样大时让 a 的根当新根。
  两条优化都做了，每次操作近似 O(1)。
- len(uf) 是元素个数，uf.set_count 是集合个数，x in uf 判断元素是否加进来过。

写完后运行 uv run dsa/union_find.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_union_find.py。
"""

from collections.abc import Hashable, Iterable


class UnionFind:
    def __init__(self, elements: Iterable[Hashable] = ()) -> None:
        self.parent: dict = {}   # 元素 -> 父节点
        self._size: dict = {}    # 只有根上的值有意义：这棵树有几个元素
        self.set_count = 0       # 集合数
        for element in elements:
            self.add(element)

    def __len__(self) -> int:
        return len(self.parent)

    def __contains__(self, element) -> bool:
        return element in self.parent

    def add(self, element) -> None:
        """把 element 加进来，自成一个集合；已经有了就什么都不做。O(1)。"""
        raise NotImplementedError

    def find(self, element):
        """返回 element 所在集合的根，顺带做路径压缩。没加过抛 KeyError。近似 O(1)。"""
        raise NotImplementedError

    def union(self, a, b) -> bool:
        """合并 a、b 所在的集合，没加过的先 add。真的合并了返回 True，本来就在一起返回 False。近似 O(1)。"""
        raise NotImplementedError

    def connected(self, a, b) -> bool:
        """a、b 是否在同一个集合。任意一个没加过就返回 False（不抛异常）。近似 O(1)。"""
        raise NotImplementedError

    def size_of(self, element) -> int:
        """element 所在集合有几个元素。没加过抛 KeyError。近似 O(1)。"""
        raise NotImplementedError

    def groups(self) -> list[set]:
        """所有集合，每个是一个 set。顺序：按每组里最早被 add 的元素排。O(n)。

        提示：dict 记住了插入顺序。遍历 self.parent，按 find 的结果把元素分到 {根: set} 里。
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

    # 端到端场景：几条注册记录用了重叠的邮箱，同一个人的记录要合并成一个账号。
    SIGNUPS = [
        ["ann@work.example.com", "ann@home.example.com"],
        ["bob@example.com"],
        ["ann@home.example.com", "ann.lee@example.com"],
        ["bobby@example.com", "bob@example.com"],
        ["dan@example.com"],
    ]

    def merge_accounts():
        emails = UnionFind()
        for addresses in SIGNUPS:
            emails.add(addresses[0])
            for address in addresses[1:]:
                emails.union(addresses[0], address)  # 同一条记录里的邮箱属于同一个人
        return emails

    show("一共有几个人", lambda: merge_accounts().set_count, 3)
    show("ann@work.example.com 和 ann.lee@example.com 是同一个人",
         lambda: merge_accounts().connected("ann@work.example.com", "ann.lee@example.com"), True)
    show("bob 和 dan 不是同一个人", lambda: merge_accounts().connected("bob@example.com", "dan@example.com"), False)
    show("ann 名下有几个邮箱", lambda: merge_accounts().size_of("ann@home.example.com"), 3)
    show("合并后的账号", lambda: merge_accounts().groups(),
         [{"ann@work.example.com", "ann@home.example.com", "ann.lee@example.com"}, {"bob@example.com", "bobby@example.com"}, {"dan@example.com"}])
