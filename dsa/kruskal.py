"""第 17 课：最小生成树（Kruskal）。讲解见 lessons/17-kruskal.html

实际项目里就是 sorted + 一个小并查集，十几行（见 examples/kruskal_in_practice.py）。

规则：
- 无向带权图。nodes 是所有节点（任何可哈希的东西）；edges 是 (u, v, weight) 的可迭代对象。
  边的端点不在 nodes 里时，也当作图里的点。
- 边按权从小到大考察：两头不在同一个连通块就选中，否则会成环、跳过。
  排序只按权排：sorted(edges, key=lambda edge: edge[2])。不要直接 sorted(edges)，
  权相同时会去比较节点，节点没法比大小就抛 TypeError；而且 sorted 是稳定的，同权的边保持输入顺序。
- 判断“是否同一块”用并查集。请在本文件里自己写一个小的（dict parent + find + union，十来行），
  不要 import dsa.union_find，这样第 15 课没写完也不影响这课。
- 可能有重边、自环；不要改动传进来的 edges。E 是边数。

写完后运行 uv run dsa/kruskal.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_kruskal.py。
"""

from collections.abc import Hashable, Iterable

Edge = tuple[Hashable, Hashable, float]


def minimum_spanning_tree(nodes: Iterable[Hashable], edges: Iterable[Edge]) -> list[Edge]:
    """返回最小生成树选中的边，按被选中的先后排列（也就是按权从小到大），每条边原样返回。

    一共“节点数 - 1”条，总权用 sum(weight for _, _, weight in tree) 算。
    没有节点或只有一个节点时返回 []。图不连通（选不够）时抛 ValueError。
    选够了就提前停，不用把剩下的边看完。O(E log E)。
    """
    raise NotImplementedError


def cluster(nodes: Iterable[Hashable], edges: Iterable[Edge], cluster_count: int) -> list[set]:
    """把节点分成 cluster_count 组，让“组和组之间最近的距离”尽量大（单链接聚类）。

    做法就是 Kruskal 跑到一半：从全部节点各自成组开始，按权从小到大合并，
    剩下 cluster_count 组时停下。边的权在这里是“距离”，越小越该在同一组。
    返回每组一个 set，顺序按每组里最先出现在 nodes 中的节点排。
    cluster_count 小于 1 或大于节点数时抛 ValueError；边不够、合并不到这么少组时也抛 ValueError。
    O(E log E)。
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

    # 端到端场景：一栋楼里给 5 个房间拉网线，边是能布线的路径和成本（米）。
    ROOMS = ["机房", "前台", "会议室", "财务室", "研发区"]
    CABLE_ROUTES = [("机房", "前台", 30), ("机房", "研发区", 12), ("前台", "会议室", 8),
                    ("会议室", "研发区", 15), ("财务室", "前台", 9), ("财务室", "机房", 40),
                    ("研发区", "财务室", 25)]

    show("最省的布线方案", lambda: minimum_spanning_tree(ROOMS, CABLE_ROUTES),
         [("前台", "会议室", 8), ("财务室", "前台", 9), ("机房", "研发区", 12), ("会议室", "研发区", 15)])
    show("一共要多少米网线", lambda: sum(meters for _, _, meters in minimum_spanning_tree(ROOMS, CABLE_ROUTES)), 44)
    def without_finance_routes():
        try:
            minimum_spanning_tree(ROOMS, [route for route in CABLE_ROUTES if "财务室" not in route])
        except ValueError:
            return "抛出 ValueError"
        return "没报错"

    show("财务室的线路都走不通：连不起来", without_finance_routes, "抛出 ValueError")
    show("把房间分成两个片区（片区之间离得最远）", lambda: cluster(ROOMS, CABLE_ROUTES, 2),
         [{"机房", "研发区"}, {"前台", "会议室", "财务室"}])
