"""第 31 课：二叉树高频题。讲解见 lessons/31-tree-patterns.html

规则：
- 每道题都用递归写。动手前先回答两个问题：
  ① 这个递归函数“返回什么”？（比如：以这个节点为根的子树有多深）
  ② 空树（None）应该返回什么？
- 需要把左右子树的信息合起来的题（直径、最近公共祖先），在“后序位置”汇总：
  先递归拿到左子树的结果和右子树的结果，再用这两个结果算出当前节点的结果。
- 右视图可以用队列一层一层地遍历（collections.deque），也可以用递归，二选一。
- 只有 invert_tree 会原地修改树，其他函数不要改动传进来的树。
- 文件里的 TreeNode、build_tree、tree_to_list、find_node 是工具函数，已经写好，不是练习。
- 自查：uv run dsa/tree_patterns.py ，会打印每道题的「输入、期望、实际」。
"""

from collections import deque


class TreeNode:
    def __init__(self, val, left: "TreeNode | None" = None, right: "TreeNode | None" = None) -> None:
        self.val = val
        self.left = left
        self.right = right


# ---------- 工具函数（已经写好，直接用） ----------

def build_tree(values: list) -> TreeNode | None:
    """按 LeetCode 的层序写法建树，例如 [3, 9, 20, None, None, 15, 7]。

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


def tree_to_list(root: TreeNode | None) -> list:
    """build_tree 的反过程：按层序列出节点值，空位写 None，末尾多余的 None 去掉。"""
    values = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            values.append(None)
            continue
        values.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while values and values[-1] is None:
        values.pop()
    return values


def find_node(root: TreeNode | None, value) -> TreeNode | None:
    """在树里找值等于 value 的节点（假设值互不相同），找不到返回 None。"""
    if root is None or root.val == value:
        return root
    return find_node(root.left, value) or find_node(root.right, value)


# ---------- 练习 ----------

def max_depth(root: TreeNode | None) -> int:
    """LeetCode 104 · 二叉树的最大深度。

    题意：从根走到最远的叶子，路上一共经过几个节点。空树是 0。
    例子：[3, 9, 20, None, None, 15, 7] 的最大深度是 3（3 → 20 → 15）。

    思路：函数返回“以 root 为根的子树有多深”。
    左子树深 left_depth，右子树深 right_depth，那么整棵树深 1 + max(left_depth, right_depth)。
    目标：时间 O(n)，额外空间 O(h)，h 是树高（调用栈的深度）。
    """
    raise NotImplementedError


def invert_tree(root: TreeNode | None) -> TreeNode | None:
    """LeetCode 226 · 翻转二叉树。

    题意：把每个节点的左孩子和右孩子对调（整棵树照镜子），返回根节点。原地修改。
    例子：[4, 2, 7, 1, 3, 6, 9] 翻转后是 [4, 7, 2, 9, 6, 3, 1]。

    思路：先翻转左子树、翻转右子树，再把 root.left 和 root.right 对调。
    （先对调再分别翻转也可以，但不要对调之后又按“对调前的名字”递归，那会把同一边翻两次。）
    目标：时间 O(n)，额外空间 O(h)。
    """
    raise NotImplementedError


def is_symmetric(root: TreeNode | None) -> bool:
    """LeetCode 101 · 对称二叉树。

    题意：判断这棵树是不是左右镜像对称。空树算对称。
    例子：[1, 2, 2, 3, 4, 4, 3] 对称；[1, 2, 2, None, 3, None, 3] 不对称。

    思路：写一个辅助函数 is_mirror(left_subtree, right_subtree)，判断两棵树是否互为镜像：
    两个都空 → 是；只有一个空 → 不是；值不同 → 不是；
    否则要求“左树的左孩子”和“右树的右孩子”互为镜像，并且“左树的右孩子”和“右树的左孩子”互为镜像。
    目标：时间 O(n)，额外空间 O(h)。
    """
    raise NotImplementedError


def diameter_of_binary_tree(root: TreeNode | None) -> int:
    """LeetCode 543 · 二叉树的直径。

    题意：树里任意两个节点之间最长的路径有几条边。这条路径不一定经过根。空树是 0。
    例子：[1, 2, 3, 4, 5] 的直径是 3（4 → 2 → 1 → 3，或 5 → 2 → 1 → 3）。

    思路：写一个辅助递归函数 depth(node)，返回“以 node 为根的子树有多深”（和 max_depth 一样）。
    在后序位置，拿到 left_depth 和 right_depth 之后，
    “最高点正好是 node 的最长路径”有 left_depth + right_depth 条边，用它更新全局最大值 longest_path。
    递归函数返回的是深度，题目要的直径另外记在 longest_path 里——这是本题的关键。
    目标：时间 O(n)，额外空间 O(h)。
    """
    raise NotImplementedError


def lowest_common_ancestor(root: TreeNode | None, first_node: TreeNode, second_node: TreeNode) -> TreeNode | None:
    """LeetCode 236 · 二叉树的最近公共祖先。

    题意：给两个一定在树里的节点，找出离它们最近的共同祖先（一个节点也算自己的祖先）。
    例子：在 [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4] 里，5 和 1 的最近公共祖先是 3；
    5 和 4 的最近公共祖先是 5（5 是 4 的祖先，也是它自己的祖先）。

    思路：函数返回“在 root 这棵子树里找到的东西”：
    - root 是空，返回 None；root 就是 first_node 或 second_node，直接返回 root。
    - 否则分别在左、右子树里找，得到 found_in_left 和 found_in_right（后序位置）。
      两边都不是 None：两个节点分居两侧，root 就是答案；
      只有一边不是 None：答案在那一边，把它原样往上传。
    目标：时间 O(n)，额外空间 O(h)。
    """
    raise NotImplementedError


def right_side_view(root: TreeNode | None) -> list:
    """LeetCode 199 · 二叉树的右视图。

    题意：站在树的右边往左看，从上到下能看到的节点值，也就是每一层最右边的那个节点。
    例子：[1, 2, 3, None, 5, None, 4] 的右视图是 [1, 3, 4]；
    [1, 2, 3, 4] 的右视图是 [1, 3, 4]（第三层只有 4，它在左边，但从右边也能看到）。

    思路一：层序遍历，每一层取最后一个节点。
    思路二：递归时先走右孩子再走左孩子，并带上当前深度 depth；
    第一次到达某个深度时（len(visible_values) == depth），这个节点就是该层从右边看到的那个。
    目标：时间 O(n)。
    """
    raise NotImplementedError


def is_valid_bst(root: TreeNode | None) -> bool:
    """LeetCode 98 · 验证二叉搜索树。

    题意：判断这棵树是不是二叉搜索树：任何节点左子树里的所有值都严格小于它，
    右子树里的所有值都严格大于它。空树算。
    例子：[2, 1, 3] 是；[5, 4, 6, None, None, 3, 7] 不是——3 在 5 的右子树里却比 5 小，
    虽然 3 < 6 满足“和父亲比”的局部条件。

    思路：辅助函数 check(node, lower_bound, upper_bound)：node 的值必须严格落在这两个界之间。
    往左走，上界变成 node.val；往右走，下界变成 node.val。根的两个界是负无穷和正无穷。
    另一种思路：中序遍历二叉搜索树得到的是严格递增序列。
    目标：时间 O(n)，额外空间 O(h)。
    """
    raise NotImplementedError


# ---------- 自查 ----------

def report_case(title: str, input_text: str, expected, compute) -> None:
    try:
        actual = compute()
    except NotImplementedError:
        print(f"[还没实现] {title}  输入：{input_text}  期望：{expected}")
        return
    verdict = "通过" if actual == expected else "不对"
    print(f"[{verdict}] {title}  输入：{input_text}  期望：{expected}  实际：{actual}")


def value_of(node: TreeNode | None):
    return None if node is None else node.val


if __name__ == "__main__":
    LESSON_TREE = [1, 2, 3, 4, 5, None, None, 6, None, None, 7, 8, None, None, 9]

    for values, expected in [([3, 9, 20, None, None, 15, 7], 3), ([], 0), ([1, None, 2], 2)]:
        report_case("max_depth", str(values), expected, lambda: max_depth(build_tree(values)))

    for values, expected in [([4, 2, 7, 1, 3, 6, 9], [4, 7, 2, 9, 6, 3, 1]), ([2, 1, 3], [2, 3, 1]), ([], [])]:
        report_case("invert_tree", str(values), expected, lambda: tree_to_list(invert_tree(build_tree(values))))

    for values, expected in [([1, 2, 2, 3, 4, 4, 3], True), ([1, 2, 2, None, 3, None, 3], False), ([1], True)]:
        report_case("is_symmetric", str(values), expected, lambda: is_symmetric(build_tree(values)))

    for values, expected in [([1, 2, 3, 4, 5], 3), ([1, 2], 1), (LESSON_TREE, 6)]:
        report_case("diameter_of_binary_tree", str(values), expected,
                    lambda: diameter_of_binary_tree(build_tree(values)))

    LEETCODE_TREE = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]
    for values, first_value, second_value, expected in [
        (LEETCODE_TREE, 5, 1, 3), (LEETCODE_TREE, 5, 4, 5), (LEETCODE_TREE, 7, 8, 3), (LESSON_TREE, 8, 7, 2),
    ]:
        def compute():
            root = build_tree(values)
            return value_of(lowest_common_ancestor(root, find_node(root, first_value), find_node(root, second_value)))
        report_case("lowest_common_ancestor", f"{values}，找 {first_value} 和 {second_value}", expected, compute)

    for values, expected in [([1, 2, 3, None, 5, None, 4], [1, 3, 4]), ([1, 2, 3, 4], [1, 3, 4]), ([], [])]:
        report_case("right_side_view", str(values), expected, lambda: right_side_view(build_tree(values)))

    for values, expected in [
        ([2, 1, 3], True), ([5, 1, 4, None, None, 3, 6], False), ([5, 4, 6, None, None, 3, 7], False), ([2, 2, 2], False),
    ]:
        report_case("is_valid_bst", str(values), expected, lambda: is_valid_bst(build_tree(values)))
