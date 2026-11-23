"""附录实战：选择题里的手算套路，在真实代码里长什么样。

1. 出栈序列：一条死胡同停车道，车按到达顺序开进去，只能从入口倒出来。
   问调度员给的出车顺序能不能做到——就是“模拟栈”。
2. 前序 + 中序还原树：把树存成两个列表（比如写进 JSON），读回来再还原；
   还原后按后序输出，就是“删除目录时先删里面的、再删自己”的顺序。
3. 堆的下标关系：heapq 的 list 就是数组里的完全二叉树，parent = (i - 1) // 2，用它检查堆性质。
4. 稳定排序：sorted 是稳定的，先按次要关键字排、再按主要关键字排，就得到“主要相同时按次要”。

运行：uv run examples/cheatsheet_in_practice.py
"""

import heapq


# ---------- 1. 死胡同停车道 ----------

def can_dispatch(arrivals: list[str], departures: list[str]) -> bool:
    """车按 arrivals 的顺序开进死胡同（随时可以倒出来），能按 departures 的顺序出车吗？"""
    if sorted(arrivals) != sorted(departures):
        return False
    lane: list[str] = []          # 死胡同就是一个栈：最后开进去的最先出来
    next_arrival = 0
    for car in departures:
        while (not lane or lane[-1] != car) and next_arrival < len(arrivals):
            lane.append(arrivals[next_arrival])
            next_arrival += 1
        if lane[-1] != car:       # 车都进来了，要的车却被堵在里面
            return False
        lane.pop()
    return True


# ---------- 2. 前序 + 中序 还原目录树 ----------

def rebuild(preorder: list[str], inorder: list[str]) -> dict | None:
    """还原成 {"name": ..., "left": ..., "right": ...} 的嵌套 dict（二叉树）。"""
    position = {name: index for index, name in enumerate(inorder)}

    def build(pre_start: int, in_start: int, size: int) -> dict | None:
        if size == 0:
            return None
        root = preorder[pre_start]                     # 前序第一个是根
        left_size = position[root] - in_start          # 中序里根左边有几个，左子树就有几个
        return {"name": root,
                "left": build(pre_start + 1, in_start, left_size),
                "right": build(pre_start + 1 + left_size, position[root] + 1, size - left_size - 1)}

    return build(0, 0, len(preorder))


def deletion_order(node: dict | None):
    """后序：先删两个孩子，再删自己。"""
    if node is None:
        return
    yield from deletion_order(node["left"])
    yield from deletion_order(node["right"])
    yield node["name"]


# ---------- 3. 堆的下标关系 ----------

def is_min_heap(values: list[int]) -> bool:
    return all(values[(index - 1) // 2] <= values[index] for index in range(1, len(values)))


def main() -> None:
    cars = ["沪A1", "沪A2", "沪A3", "沪A4", "沪A5"]
    assert can_dispatch(cars, ["沪A4", "沪A5", "沪A3", "沪A2", "沪A1"])
    assert not can_dispatch(cars, ["沪A4", "沪A3", "沪A5", "沪A1", "沪A2"])   # 沪A1 被 沪A2 堵在里面
    print("出车顺序 4 5 3 2 1 可以，4 3 5 1 2 不行")

    preorder = ["根目录", "文档", "照片", "简历", "代码", "笔记"]
    inorder = ["照片", "文档", "简历", "根目录", "代码", "笔记"]
    tree = rebuild(preorder, inorder)
    assert tree is not None and tree["name"] == "根目录" and tree["left"]["name"] == "文档"
    order = list(deletion_order(tree))
    assert order == ["照片", "简历", "文档", "笔记", "代码", "根目录"]
    print("删除顺序（后序）：", " → ".join(order))

    numbers = [9, 4, 7, 1, 8, 2, 6]
    heapq.heapify(numbers)
    assert is_min_heap(numbers) and numbers[0] == 1
    assert not is_min_heap([3, 1, 2])
    for index in range(1, len(numbers)):
        parent = (index - 1) // 2
        assert index in (2 * parent + 1, 2 * parent + 2)     # 父子下标关系互相对得上
    print("heapify 之后：", numbers, "，下标 i 的父亲是 (i - 1) // 2")

    students = [("小刚", 90), ("小红", 95), ("小明", 90), ("小丽", 95)]
    by_name = sorted(students, key=lambda student: student[0])
    by_score_then_name = sorted(by_name, key=lambda student: -student[1])    # 稳定：同分的保持按名字的顺序
    assert by_score_then_name == sorted(students, key=lambda student: (-student[1], student[0]))
    print("先按名字、再按分数稳定排序：", [name for name, _ in by_score_then_name])


if __name__ == "__main__":
    main()
