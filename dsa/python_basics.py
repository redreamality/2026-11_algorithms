"""预备课：Python 基础。讲解见 lessons/python-basics.html

场景：一家小书店的后台。每个练习对应讲解页的一两个小节，括号里是小节号。
真实脚本里这些写法怎么配合，见 examples/python_basics_in_practice.py。

规则：
- 不能修改传进来的参数（list、Shelf 都不能改）。
- 命名用完整的英文单词，别用 res、tmp、l/r 这种缩写。
- 每个函数的 docstring 写清了要求；不确定的行为，看 tests/test_python_basics.py。

写完后运行 uv run dsa/python_basics.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_python_basics.py。
"""

from collections.abc import Iterable, Iterator, Sequence
from typing import NamedTuple


class Book(NamedTuple):
    title: str
    author: str
    sold: int


def group_by_author(books: Iterable[Book]) -> dict[str, list[str]]:
    """作者 → 他写的书名列表。作者按第一次出现的顺序，书名按原来的顺序。（第 7 节）

    用 setdefault 写，一行把书名放进对应作者的列表。
    """
    raise NotImplementedError


def top_sellers(books: Iterable[Book], k: int) -> list[str]:
    """销量最高的 k 本书的书名。销量降序；销量相同按书名升序。（第 6 节）

    k 比书的数量还大时，返回全部；k <= 0 返回空列表。
    提示：sorted 的 key 返回一个元组，数字取负号就能让这一项降序。
    """
    raise NotImplementedError


def parse_price(text: str) -> float:
    """把 "¥12.50" 这样的价格文本解析成 12.5。前后的空格要忽略。（第 8 节）

    - 不是以 ¥ 开头：抛 ValueError。
    - ¥ 后面不是数字（例如 "¥abc"）：抛 ValueError，并用 raise ... from 挂上 float() 原来抛的异常。
    - 价格是负数：抛 ValueError。
    """
    raise NotImplementedError


def running_totals(daily_sales: Iterable[float]) -> Iterator[float]:
    """逐天产出“到这一天为止的累计销售额”。用 yield 写成生成器。（第 13 节）

    running_totals([3, 1, 4]) 依次产出 3、4、8。
    必须是懒的：daily_sales 可能是一个无穷的生成器，调用者要几个就算几个。
    """
    raise NotImplementedError


class Shelf(Sequence):
    """一个只读书架，按顺序放着书名。（第 11、12 节）

    继承 Sequence 后，你只要写 __getitem__ 和 __len__，
    in、for、reversed、index、count 都会自动能用。另外写 __eq__：
    - 两个 Shelf 名字相同、书名列表也相同，才相等。
    - 和不是 Shelf 的东西比较时，返回 NotImplemented（注意不是抛 NotImplementedError）。
    """

    def __init__(self, name: str, titles: Iterable[str] = ()) -> None:
        self.name = name
        self._titles = list(titles)  # 拷一份，外面再改原来的 list 也不影响书架

    def __repr__(self) -> str:
        return f"Shelf({self.name!r}, {self._titles!r})"

    def __getitem__(self, index):
        """shelf[index]。越界抛 IndexError（直接交给内部的 list 就行）。"""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        raise NotImplementedError


def all_titles(*shelves: Iterable[str]) -> Iterator[str]:
    """把几个书架上的书名按顺序接起来，逐个产出。用 yield from 写。（第 14 节）

    all_titles(Shelf("A", ["x"]), Shelf("B", ["y", "z"])) 依次产出 x、y、z。
    书架也可以是任何能 for 的东西，比如 list 或生成器。
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

    def raised(compute):
        """运行 compute，返回抛出的异常类型名；没抛异常就返回 "没抛异常"。"""
        try:
            compute()
        except NotImplementedError:
            raise
        except Exception as error:
            return type(error).__name__
        return "没抛异常"

    # 端到端场景：书店月底盘点。
    books = [
        Book("三体", "刘慈欣", 120),
        Book("活着", "余华", 95),
        Book("球状闪电", "刘慈欣", 60),
        Book("兄弟", "余华", 95),
        Book("围城", "钱钟书", 30),
    ]
    show("按作者分组", lambda: group_by_author(books),
         {"刘慈欣": ["三体", "球状闪电"], "余华": ["活着", "兄弟"], "钱钟书": ["围城"]})
    show("销量前 3（同销量按书名排）", lambda: top_sellers(books, 3), ["三体", "兄弟", "活着"])
    show("parse_price(' ¥12.50 ')", lambda: parse_price(" ¥12.50 "), 12.5)
    show("parse_price('12.50') 缺少 ¥", lambda: raised(lambda: parse_price("12.50")), "ValueError")
    show("一周的累计销售额", lambda: list(running_totals([300, 0, 150.5, 49.5])), [300, 300, 450.5, 500.0])

    fiction = Shelf("小说", ["活着", "兄弟"])
    science = Shelf("科幻", ["三体", "球状闪电"])
    show("len(fiction)", lambda: len(fiction), 2)
    show("fiction[-1]", lambda: fiction[-1], "兄弟")
    show("'活着' in fiction（Sequence 白送的）", lambda: "活着" in fiction, True)
    show("list(reversed(science))", lambda: list(reversed(science)), ["球状闪电", "三体"])
    show("两个内容一样的书架相等", lambda: fiction == Shelf("小说", ["活着", "兄弟"]), True)
    show("所有书架上的书名", lambda: list(all_titles(fiction, science)), ["活着", "兄弟", "三体", "球状闪电"])
