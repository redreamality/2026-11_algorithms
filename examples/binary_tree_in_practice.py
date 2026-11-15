"""第 10 课实战：Python 项目里“走一棵树”真正是怎么写的。

业务代码几乎不会自己定义 TreeNode，但树形数据到处都是，处理它们用的正是递归遍历：
1. JSON / 配置文件的嵌套结构 → 递归生成器，把所有叶子拍平成 "a.b.c" 这样的路径。
2. 源代码 → 标准库 ast 把代码解析成语法树，ast.walk 是层序（BFS），NodeVisitor 是前序（DFS）。
3. 目录树 → os.walk / pathlib.Path.rglob 已经替你写好了遍历。

运行：uv run examples/binary_tree_in_practice.py
"""

import ast
from collections.abc import Iterator


def flatten(config, prefix: str = "") -> Iterator[tuple[str, object]]:
    """场景一：把嵌套配置拍平，方便和环境变量、命令行参数比对。

    这就是前序遍历：dict 和 list 是“有孩子的节点”，其余值是叶子。
    """
    if isinstance(config, dict):
        children = config.items()
    elif isinstance(config, list):
        children = enumerate(config)
    else:
        yield prefix, config
        return
    for key, child in children:
        yield from flatten(child, f"{prefix}.{key}" if prefix else str(key))


def max_depth(config) -> int:
    """嵌套有几层：和二叉树的 height 是同一个递归，只是孩子不止两个。"""
    # max(生成器, default=0)：序列为空时返回 0（比如叶子没有孩子），而不是报错
    if isinstance(config, dict):
        return 1 + max((max_depth(child) for child in config.values()), default=0)
    if isinstance(config, list):
        return 1 + max((max_depth(child) for child in config), default=0)
    return 0


class CallCollector(ast.NodeVisitor):
    """场景二：静态检查一段代码，列出每个函数里调用了哪些函数。

    NodeVisitor 按前序走语法树：先 visit 当前节点，generic_visit 再去走孩子。
    """

    def __init__(self) -> None:
        self.calls_by_function: dict[str, list[str]] = {}
        self._current_function: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        outer_function = self._current_function
        self._current_function = node.name
        self.calls_by_function[node.name] = []
        self.generic_visit(node)  # 往下走孩子
        self._current_function = outer_function  # 回溯：离开这个函数

    def visit_Call(self, node: ast.Call) -> None:
        if self._current_function is not None and isinstance(node.func, ast.Name):
            self.calls_by_function[self._current_function].append(node.func.id)
        self.generic_visit(node)


SOURCE = '''
def load(path):
    text = read(path)
    return parse(text)

def main():
    data = load("app.toml")
    print(validate(data))
'''


def main() -> None:
    config = {
        "database": {"host": "localhost", "port": 5432, "replicas": ["db-1", "db-2"]},
        "debug": False,
    }
    flat = dict(flatten(config))
    assert flat == {
        "database.host": "localhost",
        "database.port": 5432,
        "database.replicas.0": "db-1",
        "database.replicas.1": "db-2",
        "debug": False,
    }
    assert max_depth(config) == 3
    print("拍平后的配置：", flat)

    tree = ast.parse(SOURCE)  # 把源代码字符串解析成语法树；ast 是标准库，用法见本文件开头的说明
    collector = CallCollector()
    collector.visit(tree)
    assert collector.calls_by_function == {"load": ["read", "parse"], "main": ["load", "print", "validate"]}
    print("每个函数调用了谁：", collector.calls_by_function)

    # ast.walk 是层序遍历：先看到外层的函数定义，再看到里面的调用
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert function_names == ["load", "main"]
    print("ast.walk 找到的函数：", function_names)


if __name__ == "__main__":
    main()
