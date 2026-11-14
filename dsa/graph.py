"""第 13 课：图的表示、BFS、DFS。讲解见 lessons/13-graph-traversal.html

实际项目里，图就是一个 dict：键是节点，值是邻居 list。节点可以是任何可哈希的东西，
用户名、URL、(行, 列) 坐标都行，不必编号成 0..n-1。见 examples/graph_in_practice.py。

规则：
- 邻接表：{"ann": ["bob", "cat"], "bob": ["ann"], "cat": ["ann"]}。
- 邻居按边加入的顺序排列，遍历时也按这个顺序看邻居，这样访问顺序是唯一确定的。
- 某个节点不是 graph 的键时，当作它没有邻居（用 graph.get(node, ())），不要抛 KeyError。
- bfs、dfs 是生成器：用 yield 一个个产出节点。调用方可以边走边停，
  比如 next(node for node in bfs(graph, start) if 满足条件)，找到就不再往下走。
- BFS 用 collections.deque 当队列（不要用 list.pop(0)，那是 O(n)）。
- 每个节点只能访问一次：用一个 set 记下已经见过的节点。
  BFS 要在“入队时”就标记，不然同一个节点会被重复入队。
- 不要改动传进来的 graph。V 是节点数，E 是边数。

写完后运行 uv run dsa/graph.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_graph.py。
"""

from collections.abc import Hashable, Iterable, Iterator


def build_graph(edges: Iterable[tuple[Hashable, Hashable]], directed: bool = False) -> dict[Hashable, list]:
    """由边列表 [(u, v), ...] 建邻接表。

    无向图：u 的邻居里加 v，v 的邻居里也加 u。
    有向图：只在 u 的邻居里加 v，但 v 也要作为键出现（邻居可以是空 list）。
    提示：dict.setdefault(node, []) 或 collections.defaultdict(list)。最后返回普通 dict。
    O(V + E)。
    """
    raise NotImplementedError


def bfs(graph: dict, start) -> Iterator:
    """从 start 出发做广度优先遍历，按访问顺序 yield 节点（第一个就是 start）。O(V + E)。"""
    raise NotImplementedError


def dfs(graph: dict, start) -> Iterator:
    """从 start 出发做深度优先遍历，按访问顺序 yield 节点。O(V + E)。

    顺序要和递归写法一致：先访问自己，再按顺序对每个没见过的邻居递归。
    要求用显式栈写，不用递归：测试里有一条 5 万个节点的链，递归会超过 Python 的递归深度。
    提示：栈里放“邻居迭代器”，栈顶的迭代器取下一个没见过的邻居；取完了就出栈（回头）。
    """
    raise NotImplementedError


def shortest_path(graph: dict, start, goal) -> list | None:
    """无权图里 start 到 goal 边数最少的一条路径，返回节点列表 [start, ..., goal]。

    start == goal 返回 [start]；到不了返回 None。
    提示：BFS 时用 dict 记 came_from[邻居] = 从哪个节点过来的，找到 goal 后倒着走回 start 再反转。
    O(V + E)。
    """
    raise NotImplementedError


def connected_components(graph: dict) -> list[set]:
    """无向图的所有连通块，每块是一个 set。孤立的节点也算一块。

    块的顺序：按每块里“最先出现在 graph 的键里的那个节点”排。空图返回 []。O(V + E)。
    提示：对每个还没见过的键调用一次 bfs。
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

    # 端到端场景：一个小社交网络，边表示“互相关注”。
    FRIENDSHIPS = [("ann", "bob"), ("ann", "cat"), ("bob", "dan"), ("cat", "dan"), ("dan", "eve"),
                   ("fay", "gus")]

    def network():
        return build_graph(FRIENDSHIPS)

    show("ann 的好友", lambda: network()["ann"], ["bob", "cat"])
    show("从 ann 出发，按远近列出能联系到的人（BFS）", lambda: list(bfs(network(), "ann")),
         ["ann", "bob", "cat", "dan", "eve"])
    show("ann 到 eve 的最短引荐链", lambda: shortest_path(network(), "ann", "eve"), ["ann", "bob", "dan", "eve"])
    show("ann 和 gus 之间没有关系链", lambda: shortest_path(network(), "ann", "gus"), None)
    show("离 ann 最近的、名字以 d 开头的人（找到就停）",
         lambda: next(person for person in bfs(network(), "ann") if person.startswith("d")), "dan")
    show("朋友圈（连通块）", lambda: connected_components(network()),
         [{"ann", "bob", "cat", "dan", "eve"}, {"fay", "gus"}])
    show("DFS 顺序", lambda: list(dfs(network(), "ann")), ["ann", "bob", "dan", "cat", "eve"])
