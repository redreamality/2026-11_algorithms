"""第 45 课：树形 DP。讲解见 lessons/45-tree-dp.html

实际项目里的树多半是“谁归谁管”的父子关系（组织架构、目录、评论楼中楼），常见需求是
自底向上汇总（目录总大小、团建邀请谁），完整例子见 examples/tree_dp_in_practice.py。

规则：
- 树形 DP 的状态定义在“以 v 为根的子树”上。先处理所有孩子，再用孩子的结果算 v（后序，第 10、31 课）。
- rob_tree 的输入是第 31 课的 TreeNode 二叉树，用递归写即可。
- 其余三个函数的输入是笔试常见的格式：节点编号 0..n-1，再给一个边列表 edges，每条边 (a, b) 没有方向。
  约定以 0 号节点为根。
  测试里有 2 万个节点连成一条链的树，递归会超过 Python 默认的递归深度（约 1000 层），
  所以这三个函数请用循环写：先从根出发 BFS 得到一个“父亲总在孩子前面”的顺序，再倒着处理这个顺序。
- 文件里的 TreeNode、build_tree 和第 31 课的工具函数一样，已经写好，不是练习。
- 变量名用完整的英文单词，例如 adjacency、parent、take_this、skip_this，不要写 res、tmp、cnt。
- 自查：uv run dsa/tree_dp.py；测试：uv run pytest tests/test_tree_dp.py
"""

from collections import deque


class TreeNode:
    def __init__(self, val, left: "TreeNode | None" = None, right: "TreeNode | None" = None) -> None:
        self.val = val
        self.left = left
        self.right = right


# ---------- 工具函数（已经写好，直接用） ----------

def build_tree(values: list) -> TreeNode | None:
    """按 LeetCode 的层序写法建树，例如 [3, 4, 5, 1, 3, None, 1]。

    None 表示这个位置没有节点；没有节点的位置不会再有孩子。
    """
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    waiting_for_children = deque([root])
    index = 1
    while waiting_for_children and index < len(values):
        parent = waiting_for_children.popleft()
        if index < len(values) and values[index] is not None:
            parent.left = TreeNode(values[index])
            waiting_for_children.append(parent.left)
        index += 1
        if index < len(values) and values[index] is not None:
            parent.right = TreeNode(values[index])
            waiting_for_children.append(parent.right)
        index += 1
    return root


# ---------- 练习 ----------


def build_adjacency_list(node_count: int, edges: list[tuple[int, int]]) -> list[list[int]]:
    """把边列表变成邻接表（第 13 课）：adjacency[v] = 和 v 直接相连的所有节点。边没有方向，两头都要记。

    例子：node_count = 4，edges = [(0, 1), (0, 2), (2, 3)]
          返回 [[1, 2], [0], [0, 3], [2]]（每个列表里的顺序按边出现的顺序）。
    目标复杂度：O(n)。
    """
    raise NotImplementedError


def rob_tree(root: TreeNode | None) -> int:
    """打家劫舍 III（LeetCode 337）：房子连成一棵二叉树，有边直接相连的两间（父子）不能同一晚都偷。最多偷多少？

    例子：build_tree([3, 4, 5, 1, 3, None, 1])
                3
              /   \\
             4     5
            / \\     \\
           1   3     1
          偷 4 和 5，得 9，返回 9（偷根 3 再偷三个孙子只有 3 + 1 + 3 + 1 = 8）。空树返回 0。

    思路提示：
      每个节点返回两个数 (take_this, skip_this)：
        take_this = 偷这个节点时，它这棵子树最多偷多少 = node.val + 左孩子的 skip + 右孩子的 skip；
        skip_this = 不偷这个节点时，最多偷多少 = 左孩子两种里大的 + 右孩子两种里大的。
      空树返回 (0, 0)。答案是根的两种里大的。

    目标复杂度：O(n) 时间，O(h) 递归深度。
    """
    raise NotImplementedError


def max_non_adjacent_total(values: list[int], edges: list[tuple[int, int]]) -> int:
    """同一道题，换成笔试的输入格式：节点 v 的价值是 values[v]（都 ≥ 0），edges 是 n - 1 条边。
    有边相连的两个节点不能都选，选出的价值总和最大是多少？（也叫“没有上司的舞会”：直属上下级不能同时来）

    例子：values = [3, 4, 5, 1, 3, 1]，edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
          这就是 rob_tree 例子里那棵树（节点编号按层序），返回 9。空列表返回 0。
          每个节点的孩子可以不止两个。

    思路提示：和 rob_tree 一样，每个节点算 take[v] 和 skip[v]，只是“左右孩子”换成“所有孩子”。
      ① 建邻接表；② 从根 0 出发 BFS，记下每个节点的 parent，得到顺序 order；
      ③ 倒着遍历 order（孩子一定比父亲先处理），邻居里不是 parent 的就是孩子。
    要求：不用递归（2 万个节点的链也要能跑）。目标复杂度：O(n)。
    """
    raise NotImplementedError


def tree_diameter(node_count: int, edges: list[tuple[int, int]]) -> int:
    """树的直径（LeetCode 1245）：树上最远的两个节点之间有几条边？

    例子：node_count = 6，edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
          最长路径 3 → 1 → 0 → 2 → 5，有 4 条边，返回 4。
          node_count 为 0 或 1 时返回 0。

    思路提示（第 31 课二叉树直径的推广）：
      deepest[v] = 从 v 往下走（只走向孩子），最多能走几条边。叶子是 0。
      以 v 为最高点的最长路径 = 最深的两个孩子方向之和：
        每个孩子 child 方向能走 deepest[child] + 1 条边，取最大的两个加起来（只有一个孩子时第二个算 0）。
      所有节点里的最大值就是答案。
    要求：不用递归。目标复杂度：O(n)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def check(function, arguments, expected):
        """跑一个例子，打印「输入、期望、实际」。还没实现的函数会提示一下，不会让脚本中断。"""
        shown_input = ", ".join(repr(argument) for argument in arguments)
        if len(shown_input) > 100:
            shown_input = shown_input[:100] + "……"
        try:
            actual = function(*arguments)
        except NotImplementedError:
            print(f"[未实现] {function.__name__}({shown_input})")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {function.__name__}({shown_input})  期望 {expected!r}，实际 {actual!r}")

    example_edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
    chain_edges = [(index, index + 1) for index in range(19999)]

    check(build_adjacency_list, (4, [(0, 1), (0, 2), (2, 3)]), [[1, 2], [0], [0, 3], [2]])
    check(build_adjacency_list, (1, []), [[]])

    def rob_tree_from_list(values):
        """把层序列表建成树再调用 rob_tree，方便打印。"""
        return rob_tree(build_tree(values))

    check(rob_tree_from_list, ([3, 4, 5, 1, 3, None, 1],), 9)
    check(rob_tree_from_list, ([3, 2, 3, None, 3, None, 1],), 7)
    check(rob_tree_from_list, ([],), 0)

    check(max_non_adjacent_total, ([3, 4, 5, 1, 3, 1], example_edges), 9)
    check(max_non_adjacent_total, ([5, 1, 1, 1, 1], [(0, 1), (0, 2), (0, 3), (0, 4)]), 5)
    check(max_non_adjacent_total, ([1] * 20000, chain_edges), 10000)
    check(max_non_adjacent_total, ([], []), 0)

    check(tree_diameter, (6, example_edges), 4)
    check(tree_diameter, (5, [(0, 1), (0, 2), (0, 3), (0, 4)]), 2)
    check(tree_diameter, (20000, chain_edges), 19999)
    check(tree_diameter, (1, []), 0)
