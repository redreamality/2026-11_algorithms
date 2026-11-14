"""第 16 课：最短路径（Dijkstra）。讲解见 lessons/16-dijkstra.html

实际项目里就是 dict 存图 + 标准库 heapq，二三十行写完（见 examples/dijkstra_in_practice.py）。
这里写一个能直接用的版本。

规则：
- graph 是 dict 套 dict：{站点: {邻站: 耗时, ...}}，表示一条单向边。无向图两个方向各存一条。
  节点可以是任何可哈希的东西。所有权重都 >= 0，碰到负权抛 ValueError。
- 有的点只出现在别人的邻居里、自己不是 graph 的键，当作它没有出边（用 graph.get(node, {})）。
- 用 heapq 做最小堆。堆里放 (距离, 序号, 节点)：序号是一个一直递增的计数器（itertools.count()），
  距离相同时按序号比，不会去比较节点本身（节点可能是没法比大小的东西）。
- heapq 改不了堆里已有的元素：距离变短就再 push 一条新记录，取出来时发现比已确定的距离旧，就跳过。
- 走不到的点不出现在结果里（调用方用 distances.get(node, math.inf)），不往 dict 里塞 inf。
- 不要改动传进来的 graph。V 是节点数，E 是边数。

写完后运行 uv run dsa/dijkstra.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_dijkstra.py。
"""

from collections.abc import Hashable, Iterator, Mapping

Graph = Mapping[Hashable, Mapping[Hashable, float]]


def walk_by_distance(graph: Graph, source) -> Iterator[tuple[Hashable, float]]:
    """从 source 出发，按最短距离从近到远 yield (节点, 最短距离)，每个能到的节点恰好一次。

    第一个产出的是 (source, 0)。这是一个生成器：调用方拿够了就可以停，后面的图不再计算，
    比如“30 分钟内能到的站”用 itertools.takewhile 就行。
    O((V + E) log V)。
    """
    raise NotImplementedError


def shortest_paths(graph: Graph, source) -> tuple[dict, dict]:
    """一次算出 source 到所有能到的点的最短距离，返回 (distances, previous)。

    distances[node] 是最短距离（source 是 0）；previous[node] 是最短路上 node 的前一个点（source 没有这一项）。
    顺着 previous 从任意终点倒着走，就能复原到 source 的路径。O((V + E) log V)。
    """
    raise NotImplementedError


def shortest_path(graph: Graph, source, target) -> tuple[float, list] | None:
    """source 到 target 的 (最短距离, 路径 [source, ..., target])；走不到返回 None。

    source == target 返回 (0, [source])。最短路不止一条时返回任意一条。
    target 从堆里取出的那一刻就可以返回，不用把整张图算完。O((V + E) log V)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    from itertools import takewhile

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景：一小段地铁线网，权重是两站之间的分钟数（双向）。
    def subway():
        segments = [("人民广场", "南京西路", 2), ("南京西路", "静安寺", 2), ("人民广场", "陆家嘴", 6),
                    ("陆家嘴", "世纪大道", 3), ("静安寺", "世纪大道", 14), ("人民广场", "世纪大道", 11)]
        network: dict[str, dict[str, int]] = {}
        for start, end, minutes in segments:
            network.setdefault(start, {})[end] = minutes
            network.setdefault(end, {})[start] = minutes
        return network

    show("静安寺到世纪大道最快怎么走", lambda: shortest_path(subway(), "静安寺", "世纪大道"),
         (13, ["静安寺", "南京西路", "人民广场", "陆家嘴", "世纪大道"]))
    show("人民广场到各站的分钟数", lambda: shortest_paths(subway(), "人民广场")[0],
         {"人民广场": 0, "南京西路": 2, "静安寺": 4, "陆家嘴": 6, "世纪大道": 9})
    show("从人民广场出发 5 分钟内能到的站（按远近）",
         lambda: [station for station, minutes in takewhile(lambda item: item[1] <= 5,
                                                            walk_by_distance(subway(), "人民广场"))],
         ["人民广场", "南京西路", "静安寺"])
    show("不在线网里的站", lambda: shortest_path(subway(), "人民广场", "虹桥机场"), None)
