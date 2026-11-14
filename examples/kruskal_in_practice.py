"""第 17 课实战：Python 项目里最小生成树真正是怎么写的。

标准库没有 MST，但 Kruskal 就是 sorted + 一个小并查集，十几行：
- 边写成 (u, v, 成本)，节点直接用名字。排序只按成本：sorted(edges, key=itemgetter(2))，
  同成本时不去比较节点，而且保持输入顺序，结果可复现。
- 典型用途：布线、铺管道、修路的最低成本方案；以及“跑到一半就停”的单链接聚类，
  把距离近的东西分到一组（门店划片区、相似文档归类）。
- 稠密图（几乎每两点都有边）上 Prim 常常更快；大规模需求才考虑 networkx / scipy。

运行：uv run examples/kruskal_in_practice.py
"""

from operator import itemgetter


def kruskal(nodes, edges, stop_at_groups: int = 1):
    """按成本从低到高选边，连通块剩 stop_at_groups 个时停。返回 (选中的边, 节点 -> 组根 的函数)。"""
    parent = {node: node for node in nodes}

    def find(node):
        root = parent.setdefault(node, node)
        while parent[root] != root:
            root = parent[root]
        while parent[node] != root:  # 路径压缩
            parent[node], node = root, parent[node]
        return root

    groups = len(parent)
    chosen = []
    for start, end, cost in sorted(edges, key=itemgetter(2)):
        if groups <= stop_at_groups:
            break
        root_start, root_end = find(start), find(end)
        if root_start != root_end:  # 两头不在同一块，连上不会成环
            parent[root_end] = root_start
            chosen.append((start, end, cost))
            groups -= 1
    return chosen, find


def cheapest_cabling(rooms: list[str], routes: list[tuple[str, str, int]]) -> list[tuple[str, str, int]]:
    """场景一：给所有房间拉网线，总长度最短。连不通就报错，不能悄悄少连一个房间。"""
    chosen, _ = kruskal(rooms, routes)
    if len(chosen) != len(rooms) - 1:
        raise ValueError("有房间无论如何都连不上")
    return chosen


def delivery_zones(stores: list[str], distances: list[tuple[str, str, int]], zone_count: int) -> list[list[str]]:
    """场景二：把门店分成 zone_count 个配送片区，近的店分在一起（单链接聚类）。"""
    _, find = kruskal(stores, distances, stop_at_groups=zone_count)
    zones: dict[str, list[str]] = {}
    for store in stores:
        zones.setdefault(find(store), []).append(store)
    return list(zones.values())


def main() -> None:
    rooms = ["机房", "前台", "会议室", "财务室", "研发区"]
    routes = [("机房", "前台", 30), ("机房", "研发区", 12), ("前台", "会议室", 8), ("会议室", "研发区", 15),
              ("财务室", "前台", 9), ("财务室", "机房", 40), ("研发区", "财务室", 25)]
    plan = cheapest_cabling(rooms, routes)
    assert plan == [("前台", "会议室", 8), ("财务室", "前台", 9), ("机房", "研发区", 12), ("会议室", "研发区", 15)]
    print("布线方案：", "；".join(f"{start}—{end} {meters} 米" for start, end, meters in plan),
          f"，共 {sum(meters for _, _, meters in plan)} 米")

    try:
        cheapest_cabling(rooms + ["仓库"], routes)
    except ValueError as error:
        print("加上没有线路的仓库：", error)
    else:
        raise AssertionError("应该报错")

    stores = ["徐汇店", "静安店", "浦东店", "张江店", "黄浦店", "陆家嘴店"]
    kilometers = [("徐汇店", "静安店", 6), ("静安店", "黄浦店", 4), ("浦东店", "张江店", 7),
                  ("陆家嘴店", "浦东店", 5), ("黄浦店", "陆家嘴店", 9), ("徐汇店", "张江店", 25)]
    zones = delivery_zones(stores, kilometers, zone_count=2)
    assert zones == [["徐汇店", "静安店", "黄浦店"], ["浦东店", "张江店", "陆家嘴店"]]
    print("两个配送片区：", zones)


if __name__ == "__main__":
    main()
