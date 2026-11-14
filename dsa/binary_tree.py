"""第 10 课：二叉树与递归遍历。讲解见 lessons/10-binary-tree.html

实际项目里很少自己定义二叉树，但“递归走一棵树”天天在用：JSON 嵌套结构、ast 语法树、目录树。
见 examples/binary_tree_in_practice.py。这里手写的版本按 Python 的习惯来：

规则：
- 空树用 None 表示。每个函数都要能处理 root 是 None 的情况。
- 遍历函数是生成器（用 yield / yield from），调用方想要 list 就写 list(preorder(root))。
  这样遍历一棵大树时不用先把结果全堆进内存，找到想要的就可以提前 break。
- preorder / inorder / postorder 用递归写；level_order 用队列（collections.deque）。
- 高度约定：空树是 0，只有根节点是 1。
- 序列化有两种格式，都要能来回转换：
  - 层序列表（LeetCode 的写法）：build_from_list / to_list。
  - 嵌套 dict（可以直接 json.dumps 存盘或通过接口传输）：to_dict / from_dict。

写完后运行 uv run dsa/binary_tree.py，看端到端的例子；再跑 uv run pytest tests/test_binary_tree.py。
"""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class TreeNode:
    """dataclass 自动生成 __init__、__repr__ 和 __eq__：两棵树结构和值都一样时 == 为 True。"""

    val: object
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None


def preorder(root: TreeNode | None) -> Iterator:
    """前序：根 → 左 → 右，依次 yield 节点的值。O(n)。"""
    raise NotImplementedError


def inorder(root: TreeNode | None) -> Iterator:
    """中序：左 → 根 → 右。O(n)。"""
    raise NotImplementedError


def postorder(root: TreeNode | None) -> Iterator:
    """后序：左 → 右 → 根。O(n)。"""
    raise NotImplementedError


def level_order(root: TreeNode | None) -> Iterator[list]:
    """层序：每次 yield 一整层的值（一个 list），从上到下、每层从左到右。O(n)。

    例：讲解页那棵树依次产出 [1]、[2, 3]、[4, 5, 6]。
    提示：用 deque。每一轮先记下当前队列长度 level_size，只出队这么多个，它们就是同一层。
    """
    raise NotImplementedError


def height(root: TreeNode | None) -> int:
    """树的高度（层数）。空树 0，只有根 1。O(n)。"""
    raise NotImplementedError


def count_nodes(root: TreeNode | None) -> int:
    """节点总数。O(n)。"""
    raise NotImplementedError


def build_from_list(values: list) -> TreeNode | None:
    """按层序列表建树，None 表示这个位置没有节点。O(n)。

    和 LeetCode 的写法一样：None 位置没有孩子，后面的值按顺序分给下一个真实节点。
    例：[1, 2, 3, None, 4] 建出
          1
         / \\
        2   3
         \\
          4
    空列表或第一个值是 None，返回 None。
    """
    raise NotImplementedError


def to_list(root: TreeNode | None) -> list:
    """build_from_list 的反方向：把树写成层序列表，末尾多余的 None 去掉。O(n)。

    例：上面那棵树写回 [1, 2, 3, None, 4]。空树返回 []。
    要求 build_from_list(to_list(tree)) == tree。
    """
    raise NotImplementedError


def to_dict(root: TreeNode | None) -> dict | None:
    """转成嵌套 dict：{"val": 1, "left": {...} 或 None, "right": {...} 或 None}。空树返回 None。O(n)。

    结果只含 dict、list、数字、字符串和 None，可以直接 json.dumps。
    """
    raise NotImplementedError


def from_dict(data: dict | None) -> TreeNode | None:
    """to_dict 的反方向。要求 from_dict(to_dict(tree)) == tree。O(n)。"""
    raise NotImplementedError


if __name__ == "__main__":
    import json

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景：一个公司的汇报关系，接口用层序列表传过来，处理完再存成 JSON。
    def org_chart():
        return build_from_list(["CEO", "CTO", "CFO", "后端", "前端", None, "会计"])

    show("前序：从上往下列出所有人", lambda: list(preorder(org_chart())),
         ["CEO", "CTO", "后端", "前端", "CFO", "会计"])
    show("后序：先列下属再列领导（解散部门时的顺序）", lambda: list(postorder(org_chart())),
         ["后端", "前端", "CTO", "会计", "CFO", "CEO"])
    show("按层分组：每一级有谁", lambda: list(level_order(org_chart())),
         [["CEO"], ["CTO", "CFO"], ["后端", "前端", "会计"]])
    show("一共几级、几个人", lambda: (height(org_chart()), count_nodes(org_chart())), (3, 6))
    show("找到第一个“前端”就停：生成器可以提前 break",
         lambda: next(name for name in preorder(org_chart()) if name.startswith("前")), "前端")
    show("写回层序列表", lambda: to_list(org_chart()), ["CEO", "CTO", "CFO", "后端", "前端", None, "会计"])
    show("存成 JSON 再读回来，树不变",
         lambda: from_dict(json.loads(json.dumps(to_dict(org_chart()), ensure_ascii=False))) == org_chart(), True)
