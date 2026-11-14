"""第 5 课实战：Python 项目里“递归”真正是怎么用的。

业务代码里很少手写阶乘、快速幂，标准库都有。真正要自己写递归的，是“形状本身就是递归的数据”：
1. 遍历目录树 → 标准库 Path.rglob / os.walk，不用自己递归。
2. 嵌套 JSON / 配置 / 组织架构 → 自己写一个小递归函数，几行就够。
3. 重复子问题 → functools.cache 记忆化，一行把指数级降成线性。
4. 数据可能很深（用户上传的 JSON）→ 递归有约 1000 层的上限，改用显式栈，或先检查深度。

运行：uv run examples/recursion_in_practice.py
"""

import json
import math
import sys
import tempfile
from functools import cache
from pathlib import Path


def total_size(root: Path, pattern: str = "*") -> int:
    """场景一：目录占用空间。rglob 自己会递归进子目录，我们只管加起来。"""
    return sum(path.stat().st_size for path in root.rglob(pattern) if path.is_file())


def find_values(document, wanted_key: str) -> list:
    """场景二：在任意嵌套的 JSON 里收集某个键的所有值（例如所有 "email"）。"""
    found = []
    if isinstance(document, dict):
        for key, child in document.items():
            if key == wanted_key:
                found.append(child)
            found.extend(find_values(child, wanted_key))
    elif isinstance(document, list):
        for child in document:
            found.extend(find_values(child, wanted_key))
    return found


def headcount(department: dict) -> int:
    """场景二：组织架构树，统计一个部门（含所有下级部门）的人数。"""
    return len(department.get("members", [])) + sum(headcount(child) for child in department.get("children", []))


@cache
def ways_to_climb(steps: int) -> int:
    """场景三：每次走 1 或 2 级台阶，有几种走法。没有 @cache 时 steps=80 要算到天荒地老。"""
    if steps <= 1:
        return 1
    return ways_to_climb(steps - 1) + ways_to_climb(steps - 2)


def depth_iterative(document) -> int:
    """场景四：数据可能很深时，用显式栈代替递归，不受 sys.getrecursionlimit() 限制。"""
    deepest = 0
    stack = [(document, 1)]
    while stack:
        node, depth = stack.pop()
        if isinstance(node, (dict, list)):
            deepest = max(deepest, depth)
            children = node.values() if isinstance(node, dict) else node
            stack.extend((child, depth + 1) for child in children)
    return deepest


def main() -> None:
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        (root / "src" / "app").mkdir(parents=True)
        (root / "README.md").write_bytes(b"x" * 100)
        (root / "src" / "main.txt").write_bytes(b"x" * 20)
        (root / "src" / "app" / "views.txt").write_bytes(b"x" * 3)
        assert total_size(root) == 123
        assert total_size(root, "*.txt") == 23
        print("项目目录总大小：", total_size(root), "字节")

    response = json.loads("""
    {"team": "后端", "lead": {"name": "小红", "email": "red@example.com"},
     "members": [{"name": "小明", "email": "ming@example.com"},
                 {"name": "小刚", "contact": {"email": "gang@example.com"}}]}
    """)
    emails = find_values(response, "email")
    assert emails == ["red@example.com", "ming@example.com", "gang@example.com"]
    print("接口里所有邮箱：", emails)

    company = {"members": ["CEO"], "children": [
        {"members": ["甲", "乙"], "children": [{"members": ["丙"]}]},
        {"members": ["丁"]},
    ]}
    assert headcount(company) == 5
    print("全公司人数：", headcount(company))

    assert ways_to_climb(80) == 37889062373143906
    print("80 级台阶的走法：", ways_to_climb(80))

    assert math.factorial(20) == 2432902008176640000  # 阶乘、幂直接用标准库
    assert pow(2, 64) == 18446744073709551616

    very_deep: list = []
    for _ in range(sys.getrecursionlimit() * 2):  # 比递归上限还深
        very_deep = [very_deep]
    assert depth_iterative(very_deep) == sys.getrecursionlimit() * 2 + 1
    print("比递归上限还深的嵌套，用显式栈照样能算：", depth_iterative(very_deep), "层")


if __name__ == "__main__":
    main()
