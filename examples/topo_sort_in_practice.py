"""第 14 课实战：Python 项目里拓扑排序真正是怎么写的。

标准库 graphlib（Python 3.9+）自带 TopologicalSorter，不用手写：
1. 只要一个合法顺序 → TopologicalSorter(依赖表).static_order()。
2. 要并行执行（CI 构建、并行安装依赖）→ prepare() / get_ready() / done() 循环，
   每轮拿到的都是“依赖全部完成、现在就能开工”的任务。
3. 有环时抛 graphlib.CycleError，e.args[1] 就是环上的节点，可以直接报给用户。

运行：uv run examples/topo_sort_in_practice.py
"""

from graphlib import CycleError, TopologicalSorter

# 步骤 -> 它要等的步骤
BUILD_STEPS = {
    "install": [],
    "codegen": ["install"],
    "lint": ["install"],
    "compile": ["codegen"],
    "test": ["compile"],
    "package": ["compile", "lint"],
    "deploy": ["test", "package"],
}


def install_order(requirements: dict[str, list[str]]) -> list[str]:
    """场景一：包管理器的安装顺序。依赖一定先装。"""
    return list(TopologicalSorter(requirements).static_order())


def run_pipeline(steps: dict[str, list[str]]) -> list[set[str]]:
    """场景二：像 CI 一样分批跑构建步骤。返回每一轮同时可以跑哪些步骤。

    每轮 get_ready() 拿到的都是“依赖全部完成、现在就能开工”的步骤。
    真实项目里会把这一批交给线程池或子进程并行跑；这里为了只演示拓扑排序，直接按顺序标记完成。
    """
    sorter = TopologicalSorter(steps)
    sorter.prepare()  # 这一步就会检查环，有环立刻抛 CycleError
    rounds = []
    while sorter.is_active():
        ready = sorter.get_ready()  # 依赖都完成了的步骤
        rounds.append(set(ready))
        for finished_step in ready:
            sorter.done(finished_step)
    return rounds


def find_cycle(steps: dict[str, list[str]]) -> list[str] | None:
    """场景三：配置写错成了循环依赖，把环找出来报给用户。"""
    try:
        TopologicalSorter(steps).prepare()
    except CycleError as error:
        return error.args[1]  # 环上的节点，首尾相同，比如 ['a', 'b', 'a']
    return None


def main() -> None:
    requirements = {"web-app": ["http-client", "templating"], "http-client": ["urllib-compat"], "templating": []}
    order = install_order(requirements)
    assert order.index("urllib-compat") < order.index("http-client") < order.index("web-app")
    assert order.index("templating") < order.index("web-app")
    print("安装顺序：", " → ".join(order))

    rounds = run_pipeline(BUILD_STEPS)
    assert rounds == [{"install"}, {"codegen", "lint"}, {"compile"}, {"test", "package"}, {"deploy"}]
    print("并行构建的轮次：", [sorted(steps) for steps in rounds])

    assert find_cycle(BUILD_STEPS) is None
    cycle = find_cycle({**BUILD_STEPS, "install": ["deploy"]})
    assert cycle is not None and cycle[0] == cycle[-1] and "install" in cycle
    print("循环依赖：", " → ".join(cycle))


if __name__ == "__main__":
    main()
