"""第 5 课：递归与分治。讲解见 lessons/05-recursion.html

实际项目里，递归最常用在“形状本身就是递归的数据”上：嵌套的 JSON、目录树、组织架构、评论楼中楼。
标准库已经替你写好的就直接用（os.walk、Path.rglob、math.factorial、pow），见 examples/recursion_in_practice.py。
这里自己手写，练的是“基线条件 + 把问题缩小一点交给自己”。

规则：
- “往深处走”一律用递归，不要自己维护栈或队列。同一层的兄弟节点可以用 for 循环挨个处理。
- 不要用现成的轮子：math.factorial、pow、**、os.walk、Path.rglob、Path.walk。
- 写之前先想两件事：① 基线条件是什么（最小的问题，直接给答案）；
  ② 怎么把问题缩小一点，交给自己去算。
- 异常和标准库一致：参数不合法抛 ValueError（和 math.factorial(-1) 一样）。

写完后运行 uv run dsa/recursion.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_recursion.py。
"""

from collections.abc import Iterator
from pathlib import Path


def factorial(number: int) -> int:
    """number! = 1 × 2 × … × number，约定 0! = 1。number < 0 抛 ValueError。O(n)。

    热身题，讲解页的调用栈动画演示的就是它。
    """
    raise NotImplementedError


def power(base, exponent: int):
    """base 的 exponent 次方（快速幂）。exponent < 0 抛 ValueError。

    要求 O(log n)：base^n = (base^(n//2))²，n 是奇数时再乘一个 base。
    注意 base^(n//2) 只算一次，存到变量里再平方；算两次就退回 O(n) 了。
    """
    raise NotImplementedError


def flatten(nested) -> Iterator:
    """把任意层嵌套的 list / tuple 摊平，按从左到右的顺序逐个 yield 出来。

    字符串、数字、dict 等其他东西都当成一个整体，不往里拆。
    例子：list(flatten([1, [2, [3, [4]]], (5, 6), "ab"])) == [1, 2, 3, 4, 5, 6, "ab"]
    提示：遇到 list / tuple 就 yield from flatten(它)，否则 yield 它本身。O(元素总数)。
    """
    raise NotImplementedError


def flatten_json(document: dict, separator: str = ".") -> dict:
    """把嵌套的 JSON（dict 套 dict / list）摊平成一层，键是从根到叶子的路径。

    - dict 的键直接拼进路径；list 的元素用下标（转成字符串）拼进路径。
    - 叶子是除 dict、list 以外的值。空的 dict / list 也当叶子原样保留，不然信息就丢了。
    - 返回新的 dict，按遍历顺序插入（先深入第一个孩子，再处理下一个兄弟）。

    例子：flatten_json({"user": {"name": "Ann", "tags": ["a", "b"]}, "ok": True})
          == {"user.name": "Ann", "user.tags.0": "a", "user.tags.1": "b", "ok": True}
    用途：把嵌套配置写进只认一层键值的地方（环境变量、CSV 表头、日志字段）。O(节点总数)。
    """
    raise NotImplementedError


def directory_size(path: Path) -> int:
    """目录里所有文件的字节数之和，包括所有子目录。path 是文件时直接返回它的大小。

    用 Path.iterdir() 列出一层，子目录交给递归。符号链接不跟进（算 0），避免绕圈。
    path 不存在时让 FileNotFoundError 自然抛出来，不要吞掉。O(文件和目录总数)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    import tempfile

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    show("factorial(5)", lambda: factorial(5), 120)
    show("power(2, 64)：2 的 64 次方", lambda: power(2, 64), 18446744073709551616)

    # 端到端场景一：一个接口返回了嵌套的订单数据，要写进一张只有一层列名的表。
    order = {
        "id": 1001,
        "customer": {"name": "小红", "address": {"city": "上海", "zip": "200000"}},
        "items": [{"sku": "A1", "count": 2}, {"sku": "B7", "count": 1}],
        "coupons": [],
    }
    show("flatten_json(order)：变成表格的一行", lambda: flatten_json(order), {
        "id": 1001,
        "customer.name": "小红",
        "customer.address.city": "上海",
        "customer.address.zip": "200000",
        "items.0.sku": "A1",
        "items.0.count": 2,
        "items.1.sku": "B7",
        "items.1.count": 1,
        "coupons": [],
    })
    show("flatten_json(order, separator='__')：用作环境变量名",
         lambda: list(flatten_json(order, separator="__"))[:2], ["id", "customer__name"])
    show("flatten：把分组后的标签合成一个列表",
         lambda: list(flatten([["python", ["fastapi", "pydantic"]], ("redis",), "docker"])),
         ["python", "fastapi", "pydantic", "redis", "docker"])

    # 端到端场景二：统计一个项目目录占了多少磁盘空间。
    def project_size():
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "src" / "app").mkdir(parents=True)
            (root / "README.md").write_bytes(b"x" * 100)
            (root / "src" / "main.txt").write_bytes(b"x" * 20)
            (root / "src" / "app" / "views.txt").write_bytes(b"x" * 3)
            return directory_size(root)

    show("directory_size：100 + 20 + 3 字节，分在三层目录里", project_size, 123)
