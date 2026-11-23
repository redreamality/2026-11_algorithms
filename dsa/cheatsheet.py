"""附录：选择题速查。讲解见 lessons/choice-cheatsheet.html

笔试选择题里那些“要在纸上手算”的题，把手算步骤写成代码，用来核对自己的答案。
实际项目里怎么用见 examples/cheatsheet_in_practice.py。

规则：
- 出栈序列：元素按 push_order 的顺序依次进栈，中途可以随时出栈；pop_order 是出栈的顺序。
  两个序列里的元素各不相同。
- 二叉树还原：所有节点的值各不相同，输入一定是同一棵树的两种遍历，不用检查非法输入。
  前序 = 根左右，中序 = 左根右，后序 = 左右根（第 10 课）。只返回遍历结果的列表，不用建 TreeNode。
- 不要改动传进来的列表。

写完后运行 uv run dsa/cheatsheet.py，看例子是否和期望一致；再跑 uv run pytest tests/test_cheatsheet.py。
"""


def is_valid_pop_sequence(push_order: list, pop_order: list) -> bool:
    """按 push_order 依次进栈（随时可以出栈），能不能得到 pop_order 这个出栈序列？

    例：push_order = [1, 2, 3, 4, 5]
        [4, 5, 3, 2, 1] → True；[4, 3, 5, 1, 2] → False（弹完 4 3 5 后栈里是 1 2，2 压在上面，1 出不来）。
    两个列表长度不同、或者元素不一样，直接返回 False。
    做法：用一个 list 当栈模拟。对 pop_order 里每个要弹的数，栈顶不是它就继续进栈，直到进完；
    进完了栈顶还不是它，就不合法。O(n)。
    """
    raise NotImplementedError


def count_pop_sequences(n: int) -> int:
    """n 个元素依次进栈，一共有几种不同的出栈序列？答案是第 n 个卡特兰数。

    C(n) = (2n)! / ((n + 1)! × n!)，也就是 comb(2n, n) // (n + 1)。
    n = 0 → 1，n = 3 → 5，n = 4 → 14。可以用 math.comb。
    """
    raise NotImplementedError


def postorder_from_preorder_inorder(preorder: list, inorder: list) -> list:
    """由前序和中序还原二叉树，返回它的后序。

    例（第 10 课的那棵树）：preorder = [1, 2, 4, 5, 3, 6]，inorder = [4, 2, 5, 1, 3, 6] → [4, 5, 2, 6, 3, 1]。
    做法：前序第一个是根；在中序里找到根，左边是左子树，右边是右子树；
    左子树有几个节点，就从前序里根后面切几个给左子树，剩下的给右子树；两边递归，最后按“左、右、根”拼起来。
    先用一个 dict 记下每个值在中序里的下标，整体 O(n)。
    """
    raise NotImplementedError


def preorder_from_postorder_inorder(postorder: list, inorder: list) -> list:
    """由后序和中序还原二叉树，返回它的前序。

    例：postorder = [4, 5, 2, 6, 3, 1]，inorder = [4, 2, 5, 1, 3, 6] → [1, 2, 4, 5, 3, 6]。
    和上一个函数对称：后序的最后一个是根。O(n)。
    """
    raise NotImplementedError


def complete_tree_shape(n: int) -> tuple[int, int]:
    """n 个节点（n >= 1）的完全二叉树，返回 (层数, 叶子数)。根在第 1 层。

    层数 = floor(log2 n) + 1，也就是 n.bit_length()；叶子数 = n - n // 2（上取整的 n / 2）。
    例：n = 6 → (3, 3)；n = 1000 → (10, 500)。O(1)。
    """
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

    show("1 2 3 4 5 进栈，能得到 4 5 3 2 1 吗", lambda: is_valid_pop_sequence([1, 2, 3, 4, 5], [4, 5, 3, 2, 1]), True)
    show("1 2 3 4 5 进栈，能得到 4 3 5 1 2 吗", lambda: is_valid_pop_sequence([1, 2, 3, 4, 5], [4, 3, 5, 1, 2]), False)
    show("a b c 进栈，能得到 c a b 吗", lambda: is_valid_pop_sequence(list("abc"), list("cab")), False)
    show("4 个元素进栈，出栈序列有几种", lambda: count_pop_sequences(4), 14)
    show("前序 + 中序 → 后序", lambda: postorder_from_preorder_inorder([1, 2, 4, 5, 3, 6], [4, 2, 5, 1, 3, 6]),
         [4, 5, 2, 6, 3, 1])
    show("后序 + 中序 → 前序", lambda: preorder_from_postorder_inorder([4, 5, 2, 6, 3, 1], [4, 2, 5, 1, 3, 6]),
         [1, 2, 4, 5, 3, 6])
    show("1000 个节点的完全二叉树：几层、几个叶子", lambda: complete_tree_shape(1000), (10, 500))
