import copy

import pytest

from dsa.topo_sort import CycleError, has_cycle, parallel_batches, topological_order


def check(dependencies):
    """拓扑序往往不唯一，所以不比对答案，只检查：每个节点恰好出现一次，且都排在它的依赖后面。"""
    order = topological_order(dependencies)
    nodes = set(dependencies) | {before for befores in dependencies.values() for before in befores}
    assert sorted(order, key=repr) == sorted(nodes, key=repr)
    position = {node: index for index, node in enumerate(order)}
    for node, befores in dependencies.items():
        for before in befores:
            assert position[before] < position[node], f"{before} 应该在 {node} 前面：{order}"
    return order


# 课程表（和讲解页动画一样）：课 -> 它的先修课
COURSES = {
    "微积分": [],
    "编程入门": [],
    "数据结构": ["微积分", "编程入门"],
    "数据库": ["编程入门"],
    "算法": ["数据结构"],
    "毕设": ["数据库", "算法"],
}


def test_empty():
    assert topological_order({}) == []
    assert parallel_batches({}) == []


def test_single_node():
    assert topological_order({"a": []}) == ["a"]


def test_no_dependencies_any_order():
    check({"a": [], "b": [], "c": []})


def test_chain_is_unique():
    assert topological_order({"d": ["c"], "b": ["a"], "c": ["b"]}) == ["a", "b", "c", "d"]


def test_courses():
    assert check(COURSES)[-1] == "毕设"


def test_nodes_only_in_dependencies_are_included():
    order = check({"app": ["lib", "config"], "lib": ["utils"]})
    assert set(order) == {"app", "lib", "config", "utils"}


def test_any_hashable_nodes_and_iterables():
    check({(1, 2): ((0, 0),), 3: {(1, 2)}})


def test_duplicate_dependencies():
    check({"b": ["a", "a"], "c": ["b"]})


def test_parallel_batches():
    assert parallel_batches(COURSES) == [{"微积分", "编程入门"}, {"数据结构", "数据库"}, {"算法"}, {"毕设"}]
    assert parallel_batches({"a": [], "b": []}) == [{"a", "b"}]


def test_cycle_raises_cycle_error():
    cyclic = {**COURSES, "编程入门": ["毕设"]}
    with pytest.raises(CycleError):
        topological_order(cyclic)
    with pytest.raises(CycleError):
        parallel_batches(cyclic)


def test_cycle_error_is_the_stdlib_one():
    import graphlib

    assert CycleError is graphlib.CycleError
    with pytest.raises(ValueError):  # CycleError 是 ValueError 的子类，调用方可以按 ValueError 捕获
        topological_order({"a": ["b"], "b": ["a"]})


def test_self_dependency_raises():
    with pytest.raises(CycleError):
        topological_order({"a": [], "b": ["a", "b"]})


def test_has_cycle():
    assert not has_cycle(COURSES)
    assert has_cycle({**COURSES, "编程入门": ["毕设"]})
    assert has_cycle({"a": ["b"], "b": ["a"]})
    assert not has_cycle({})


def test_input_not_modified():
    dependencies = copy.deepcopy(COURSES)
    topological_order(dependencies)
    parallel_batches(dependencies)
    assert dependencies == COURSES


def test_matches_graphlib_on_large_random_dag():
    import graphlib
    import random

    rng = random.Random(14)
    dependencies = {node: rng.sample(range(node), k=min(node, 3)) for node in range(2000)}
    check(dependencies)
    sorter = graphlib.TopologicalSorter(dependencies)
    sorter.prepare()
    expected_batches = []
    while sorter.is_active():
        ready = sorter.get_ready()
        expected_batches.append(set(ready))
        sorter.done(*ready)
    assert parallel_batches(dependencies) == expected_batches
