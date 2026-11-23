"""第 45 课实战：树形 DP 在业务代码里长什么样。

业务里的树通常不是 left / right，而是“每个人有一个上级”“每个目录有一个父目录”这样的父子表，
或者是“哪两台机器之间连了网线”这样的边列表。套路都一样：
1. 先整理出每个节点的孩子（或邻接表）；
2. 得到一个“父亲总在孩子前面”的顺序（从根 BFS），倒着处理，孩子的结果就都先算好了；
3. 每个节点只用自己孩子的结果算自己的结果。
用循环而不是递归：组织架构、目录可能很深，递归会撞上 Python 默认约 1000 层的递归上限。

运行：uv run examples/tree_dp_in_practice.py
"""

from collections import deque


def children_first_order(root: str, children: dict[str, list[str]]) -> list[str]:
    """从根 BFS，返回“父亲总在孩子前面”的顺序。倒过来用，就是“孩子总在父亲前面”。"""
    order = [root]
    for node in order:  # 一边遍历一边往后追加，效果和队列 BFS 一样
        order.extend(children.get(node, []))
    return order


def folder_sizes(parent_of: dict[str, str | None], own_size: dict[str, int]) -> dict[str, int]:
    """场景一：每个目录自己的文件有多大（own_size），算出每个目录连同子目录的总大小。

    parent_of[目录] = 父目录，根目录的父目录是 None。这是最简单的树形 DP：total[v] = own_size[v] + 所有孩子的 total。
    """
    children: dict[str, list[str]] = {}
    root = None
    for folder, parent in parent_of.items():
        if parent is None:
            root = folder
        else:
            children.setdefault(parent, []).append(folder)

    total = {}
    for folder in reversed(children_first_order(root, children)):
        total[folder] = own_size[folder] + sum(total[child] for child in children.get(folder, []))
    return total


def plan_team_party(manager_of: dict[str, str | None], happiness: dict[str, int]) -> tuple[int, list[str]]:
    """场景二：团建邀请（“没有上司的舞会”），直属上下级不能同时来，来的人开心值总和最大是多少？邀请谁？

    take[v] = 邀请 v 时，v 这一支（v 和他所有下属）的最大开心值；skip[v] = 不邀请 v 时的最大值。
    """
    children: dict[str, list[str]] = {}
    boss = None
    for person, manager in manager_of.items():
        if manager is None:
            boss = person
        else:
            children.setdefault(manager, []).append(person)

    order = children_first_order(boss, children)
    take, skip = {}, {}
    for person in reversed(order):
        team = children.get(person, [])
        take[person] = happiness[person] + sum(skip[member] for member in team)
        skip[person] = sum(max(take[member], skip[member]) for member in team)

    # 倒推邀请名单：从上往下，上级来了下属就不能来；上级没来，下属按自己哪种更好决定
    invited = []
    comes = {boss: take[boss] >= skip[boss]}
    for person in order:
        if comes[person]:
            invited.append(person)
        for member in children.get(person, []):
            comes[member] = not comes[person] and take[member] >= skip[member]
    return max(take[boss], skip[boss]), invited


def farthest_machines(links: list[tuple[str, str]]) -> list[str]:
    """场景三：机房里的机器用网线连成一棵树，哪两台机器之间隔的网线最多？返回这条路径。

    只要长度时用本课的树形 DP；要具体路径时，业务里更常见的是“两次 BFS”：
    从任意一台出发找到最远的 A，再从 A 出发找到最远的 B，A 到 B 就是直径（边权都是 1 或非负时成立）。
    """
    neighbors: dict[str, list[str]] = {}
    for first, second in links:
        neighbors.setdefault(first, []).append(second)
        neighbors.setdefault(second, []).append(first)

    def farthest_from(start: str) -> tuple[str, dict[str, str | None]]:
        came_from: dict[str, str | None] = {start: None}
        queue = deque([start])
        last = start
        while queue:
            last = queue.popleft()  # BFS 按距离从近到远出队，最后一个出队的就是最远的
            for neighbor in neighbors[last]:
                if neighbor not in came_from:
                    came_from[neighbor] = last
                    queue.append(neighbor)
        return last, came_from

    one_end, _ = farthest_from(links[0][0])
    other_end, came_from = farthest_from(one_end)
    path = [other_end]
    while came_from[path[-1]] is not None:
        path.append(came_from[path[-1]])
    return path


def main() -> None:
    parent_of = {"/": None, "/home": "/", "/home/alice": "/home", "/home/bob": "/home", "/var": "/", "/var/log": "/var"}
    own_size = {"/": 1, "/home": 2, "/home/alice": 30, "/home/bob": 12, "/var": 3, "/var/log": 40}
    sizes = folder_sizes(parent_of, own_size)
    assert sizes["/home"] == 44 and sizes["/var"] == 43 and sizes["/"] == 88
    print("目录总大小（MB）：", sizes)

    # 和讲解页同一棵树：老板 3 分，两个经理 4 分、5 分，下面三个组员 1、3、1 分
    manager_of = {"老板": None, "经理甲": "老板", "经理乙": "老板", "组员一": "经理甲", "组员二": "经理甲", "组员三": "经理乙"}
    happiness = {"老板": 3, "经理甲": 4, "经理乙": 5, "组员一": 1, "组员二": 3, "组员三": 1}
    total, invited = plan_team_party(manager_of, happiness)
    assert (total, invited) == (9, ["经理甲", "经理乙"])
    print("团建邀请：", invited, "开心值", total)

    # 一万层的汇报链也不会撞上递归上限
    long_chain = {f"员工{index}": (f"员工{index - 1}" if index else None) for index in range(10000)}
    total, invited = plan_team_party(long_chain, dict.fromkeys(long_chain, 1))
    assert total == 5000 and len(invited) == 5000

    links = [("交换机", "服务器A"), ("交换机", "服务器B"), ("服务器A", "数据库1"), ("服务器A", "数据库2"), ("服务器B", "备份机")]
    path = farthest_machines(links)
    assert len(path) - 1 == 4 and {path[0], path[-1]} in ({"数据库1", "备份机"}, {"数据库2", "备份机"})
    print("隔得最远的两台机器：", " - ".join(path), "，", len(path) - 1, "根网线")


if __name__ == "__main__":
    main()
