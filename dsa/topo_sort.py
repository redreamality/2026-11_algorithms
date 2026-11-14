"""第 14 课：拓扑排序。讲解见 lessons/14-topological-sort.html

实际项目里直接用标准库 graphlib.TopologicalSorter（见 examples/topo_sort_in_practice.py）。
这里自己手写，输入格式和它一样：

    dependencies = {"app": ["lib", "config"], "lib": ["utils"]}   # 节点 -> 它依赖的节点（先做的）

规则：
- 节点可以是任何可哈希的东西。只出现在依赖里、自己不是键的节点（上例的 utils、config）也算图里的点。
- 用 Kahn 算法：入度为 0 的点入队，出队一个就把它指出去的边“划掉”。队列用 collections.deque。
  这里“入度”就是“还有几个依赖没做完”。
- 答案往往不止一个，返回任意一个合法顺序都行。
- 有环（包括自己依赖自己）时抛 graphlib.CycleError，和标准库一样。它是 ValueError 的子类。
- 重复的依赖只算一次。不要改动传进来的 dependencies。
- n 是节点数，m 是依赖关系（边）的条数。

写完后运行 uv run dsa/topo_sort.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_topo_sort.py。
"""

from collections.abc import Hashable, Iterable, Mapping
from graphlib import CycleError

__all__ = ["CycleError", "has_cycle", "parallel_batches", "topological_order"]


def topological_order(dependencies: Mapping[Hashable, Iterable[Hashable]]) -> list:
    """返回所有节点的一个顺序：每个节点都排在它依赖的所有节点后面。

    有环抛 CycleError。O(n + m)。
    提示：先建“反向”邻接表 dependents[被依赖的] = [依赖它的, ...]，再数每个点还差几个依赖。
    """
    raise NotImplementedError


def parallel_batches(dependencies: Mapping[Hashable, Iterable[Hashable]]) -> list[set]:
    """把节点分成若干批：同一批里的节点互不依赖，可以同时做；每一批只依赖前面的批。

    第一批是没有任何依赖的节点；把它们全部做完后，新变成“没有依赖”的节点是第二批，依此类推。
    这正是 CI 里并行构建、包管理器并行安装的做法。空输入返回 []。有环抛 CycleError。O(n + m)。
    提示：Kahn 算法不用一个一个出队，而是一次把当前所有入度为 0 的点拿走，作为一批。
    """
    raise NotImplementedError


def has_cycle(dependencies: Mapping[Hashable, Iterable[Hashable]]) -> bool:
    """依赖关系里是否有环。O(n + m)。提示：借用 topological_order，捕获 CycleError。"""
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

    # 端到端场景：一个项目的构建步骤，键是步骤，值是它要等的步骤。
    BUILD_STEPS = {
        "install": [],
        "codegen": ["install"],
        "lint": ["install"],
        "compile": ["codegen"],
        "test": ["compile"],
        "package": ["compile", "lint"],
        "deploy": ["test", "package"],
    }

    def respects_dependencies(order):
        position = {step: index for index, step in enumerate(order)}
        return all(position[before] < position[step] for step, befores in BUILD_STEPS.items() for before in befores)

    show("构建顺序合法（每步都在它等的步骤之后）", lambda: respects_dependencies(topological_order(BUILD_STEPS)), True)
    show("deploy 一定最后", lambda: topological_order(BUILD_STEPS)[-1], "deploy")
    show("可以并行的批次", lambda: parallel_batches(BUILD_STEPS),
         [{"install"}, {"codegen", "lint"}, {"compile"}, {"test", "package"}, {"deploy"}])
    show("没有循环依赖", lambda: has_cycle(BUILD_STEPS), False)
    show("install 反过来依赖 deploy：成环", lambda: has_cycle({**BUILD_STEPS, "install": ["deploy"]}), True)
