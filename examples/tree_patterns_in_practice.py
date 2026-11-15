"""第 31 课实战：Python 项目里“树”真正长什么样、怎么写。

业务里的树很少是 left / right 的二叉树，常见的是：
1. 嵌套的 JSON / dict（评论楼中楼、菜单、目录）：每个节点有一个 children 列表。
   “最大深度”“子树汇总”就是本课的后序递归，只是从两个孩子变成了一个 for 循环。
2. 数据库里一行一个节点，带 parent_id（组织架构、地区、分类）：天然是“指向父亲的指针”。
   最近公共祖先不用递归整棵树：先把一方的所有上级放进集合，再从另一方往上走，第一个碰到的就是。O(深度)。
3. 数据可能很深（用户能无限回复）时，Python 默认递归上限约 1000 层，
   要么用显式栈改成循环，要么在入库时就限制深度。

运行：uv run examples/tree_patterns_in_practice.py
"""

COMMENTS = {
    "id": 1, "text": "这篇文章写得好", "children": [
        {"id": 2, "text": "同意", "children": [
            {"id": 4, "text": "+1", "children": [
                {"id": 7, "text": "楼上说得对", "children": []},
            ]},
        ]},
        {"id": 3, "text": "有个地方不对", "children": [
            {"id": 5, "text": "哪里？", "children": []},
            {"id": 6, "text": "第二段", "children": []},
        ]},
    ],
}


def max_nesting_depth(comment: dict) -> int:
    """楼中楼最多嵌套几层（只有自己算 1 层）。本课“最大深度”的 N 叉版本。

    max 的 default=0：没有孩子时生成器是空的，max 对空序列会抛 ValueError，
    default=0 表示“一个孩子都没有就按 0 算”。
    """
    return 1 + max((max_nesting_depth(child) for child in comment["children"]), default=0)


def max_nesting_depth_iterative(comment: dict) -> int:
    """同一件事用显式栈写，不受递归上限影响。"""
    deepest = 0
    stack = [(comment, 1)]
    while stack:
        current, depth = stack.pop()
        deepest = max(deepest, depth)
        stack.extend((child, depth + 1) for child in current["children"])
    return deepest


def reply_counts(comment: dict, counts: dict[int, int]) -> int:
    """后序汇总：每条评论下面一共有多少条回复（不含自己），写进 counts，返回含自己的总数。"""
    total = 1 + sum(reply_counts(child, counts) for child in comment["children"])
    counts[comment["id"]] = total - 1
    return total


# 组织架构：数据库里一行一个人，manager 就是 parent_id。
MANAGER_OF = {
    "CEO": None,
    "CTO": "CEO", "CFO": "CEO",
    "后端负责人": "CTO", "前端负责人": "CTO", "会计": "CFO",
    "小王": "后端负责人", "小李": "后端负责人", "小张": "前端负责人",
}


def chain_of_command(person: str) -> list[str]:
    """从自己一路往上到 CEO。"""
    chain = []
    while person is not None:
        chain.append(person)
        person = MANAGER_OF[person]
    return chain


def lowest_common_manager(first_person: str, second_person: str) -> str:
    """两个人最近的共同上级（可以是其中一人自己）。有父指针时的最近公共祖先：O(深度)。"""
    ancestors_of_first = set(chain_of_command(first_person))
    for person in chain_of_command(second_person):
        if person in ancestors_of_first:
            return person
    raise ValueError("不在同一棵组织树里")


def main() -> None:
    assert max_nesting_depth(COMMENTS) == 4
    assert max_nesting_depth_iterative(COMMENTS) == 4
    print("评论最多嵌套：", max_nesting_depth(COMMENTS), "层")

    very_deep = {"id": 0, "children": []}
    current = very_deep
    for index in range(1, 5000):  # 有人连着回复了 5000 层
        child = {"id": index, "children": []}
        current["children"].append(child)
        current = child
    assert max_nesting_depth_iterative(very_deep) == 5000  # 递归版在这里会 RecursionError
    print("5000 层的评论用显式栈也能算：", max_nesting_depth_iterative(very_deep))

    counts: dict[int, int] = {}
    reply_counts(COMMENTS, counts)
    assert counts == {7: 0, 4: 1, 2: 2, 5: 0, 6: 0, 3: 2, 1: 6}
    print("每条评论下的回复数：", dict(sorted(counts.items())))

    assert lowest_common_manager("小王", "小李") == "后端负责人"
    assert lowest_common_manager("小王", "小张") == "CTO"
    assert lowest_common_manager("小王", "会计") == "CEO"
    assert lowest_common_manager("小张", "CTO") == "CTO"  # 一方是另一方的上级
    print("小王和小张的共同上级：", lowest_common_manager("小王", "小张"))


if __name__ == "__main__":
    main()
