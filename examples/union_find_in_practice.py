"""第 15 课实战：Python 项目里并查集真正是怎么写的。

标准库没有并查集，但它只有二十来行，实际项目里就是复制一个小类进来：
- parent 用 dict，元素直接用业务里的东西（邮箱、设备 ID、(行, 列)），不用先编号。
- 适合“只合并、不拆分，反复问是不是一伙”的场景：账号合并、去重聚类、网络连通性、
  图里有没有环（Kruskal 判环就用它，见第 17 课）。
- 需要拆分，或者要知道“怎么连上的”，就不适合，改用图的 BFS（第 13 课）。

运行：uv run examples/union_find_in_practice.py
"""


class DisjointSet:
    """最常见的写法：dict + 路径压缩 + 按大小合并。"""

    def __init__(self) -> None:
        self.parent: dict = {}
        self.size: dict = {}

    def find(self, element):
        self.parent.setdefault(element, element)  # 第一次见到就自成一组
        self.size.setdefault(element, 1)
        root = element
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[element] != root:  # 路径压缩
            self.parent[element], element = root, self.parent[element]
        return root

    def union(self, a, b) -> bool:
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return False
        if self.size[root_a] < self.size[root_b]:  # 小树挂到大树下
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        return True

    def groups(self) -> list[set]:
        by_root: dict = {}
        for element in self.parent:
            by_root.setdefault(self.find(element), set()).add(element)
        return list(by_root.values())


def merge_accounts(signups: list[tuple[str, list[str]]]) -> list[tuple[str, list[str]]]:
    """场景一：账号合并（LeetCode 721 的业务原型）。

    每条注册记录是 (姓名, 邮箱列表)。只要两条记录有一个邮箱相同，就是同一个人。
    返回 [(姓名, 排好序的全部邮箱), ...]。
    """
    emails = DisjointSet()
    owner = {}
    for name, addresses in signups:
        for address in addresses:
            owner[address] = name
            emails.union(addresses[0], address)
    return sorted((owner[next(iter(group))], sorted(group)) for group in emails.groups())


def has_redundant_cable(cables: list[tuple[str, str]]) -> tuple[str, str] | None:
    """场景二：机房布线，找出第一根“多余”的网线：它两头的设备早已连通，接上会形成环路。"""
    network = DisjointSet()
    for left, right in cables:
        if not network.union(left, right):
            return (left, right)
    return None


def main() -> None:
    signups = [
        ("Ann", ["ann@work.example.com", "ann@home.example.com"]),
        ("Bob", ["bob@example.com"]),
        ("Ann", ["ann@home.example.com", "ann.lee@example.com"]),
        ("Bob", ["bobby@example.com", "bob@example.com"]),
        ("Dan", ["dan@example.com"]),
    ]
    accounts = merge_accounts(signups)
    assert accounts == [
        ("Ann", ["ann.lee@example.com", "ann@home.example.com", "ann@work.example.com"]),
        ("Bob", ["bob@example.com", "bobby@example.com"]),
        ("Dan", ["dan@example.com"]),
    ]
    for name, addresses in accounts:
        print(f"{name}：{', '.join(addresses)}")

    cables = [("router", "switch-a"), ("switch-a", "server-1"), ("router", "switch-b"),
              ("switch-b", "server-2"), ("server-1", "router")]
    assert has_redundant_cable(cables) == ("server-1", "router")
    assert has_redundant_cable(cables[:-1]) is None
    print("多余的网线：", " — ".join(has_redundant_cable(cables)))


if __name__ == "__main__":
    main()
