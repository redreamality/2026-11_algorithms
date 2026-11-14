"""第 23 课（选修）：KMP 字符串匹配。讲解见 lessons/23-kmp.html

实际项目里直接用 in、str.find、str.count、re.finditer（见 examples/kmp_in_practice.py）。
这里手写的版本接口和标准库对齐，写完可以直接替换着用，测试也会拿它们和标准库逐个对比：
- find(text, pattern, start=0)   ≈ text.find(pattern, start)，找不到返回 -1
- index(text, pattern, start=0)  ≈ text.index(pattern, start)，找不到抛 ValueError
- find_all(text, pattern)        所有出现位置的生成器，允许重叠（"aaaa" 里找 "aa" 产出 0、1、2）
- count(text, pattern)           不重叠的出现次数 ≈ text.count(pattern)

规则：
- 不要用 str.find / str.index / in / re 之类的现成查找，自己一个字符一个字符地比。
- 空模式和标准库一致：find(text, "") 返回 start（start 超过 len(text) 时返回 -1）；
  find_all(text, "") 产出 0、1、……、len(text)；prefix_function("") 返回 []。
- 下面复杂度里 n 是文本长度，m 是模式长度。

写完后运行 uv run dsa/kmp.py，看端到端的例子；再跑 uv run pytest tests/test_kmp.py。
"""

from collections.abc import Iterator


def naive_find_all(text: str, pattern: str) -> Iterator[int]:
    """暴力匹配：把模式依次放在每个起点上，从头逐个比较，失配就换下一个起点。

    按从小到大产出所有匹配的起点（允许重叠）。最坏 O(n·m)。用来和 KMP 对比。
    """
    raise NotImplementedError


def prefix_function(pattern: str) -> list[int]:
    """前缀函数（前缀表）：table[k] = pattern[:k+1] 的“最长相等真前缀和真后缀”的长度。

    “真”的意思是不能是整个串本身。例：prefix_function("ABABC") == [0, 0, 1, 2, 0]，
    因为 "ABA" 首尾都是 "A"（长 1），"ABAB" 首尾都是 "AB"（长 2）。O(m)。
    """
    raise NotImplementedError


def find_all(text: str, pattern: str, start: int = 0) -> Iterator[int]:
    """KMP：失配时文本指针不回退，模式按前缀表直接跳。

    从 text[start] 开始找，按从小到大产出所有匹配的起点（允许重叠），是生成器。
    结果必须和 naive_find_all 一样。O(n + m)，额外空间 O(m)。
    """
    raise NotImplementedError


def find(text: str, pattern: str, start: int = 0) -> int:
    """第一个匹配的起点，找不到返回 -1，和 text.find(pattern, start) 一样。

    提示：next(find_all(...), -1)。生成器找到第一个就停，不会把整个文本扫完。
    """
    raise NotImplementedError


def index(text: str, pattern: str, start: int = 0) -> int:
    """和 find 一样，但找不到抛 ValueError("substring not found")，和 str.index 一样。"""
    raise NotImplementedError


def count(text: str, pattern: str) -> int:
    """不重叠的出现次数，和 text.count(pattern) 一样："aaaa" 里 "aa" 出现 2 次。

    空模式返回 len(text) + 1（标准库的约定）。
    提示：遍历 find_all，跳过和上一个被计入的匹配重叠的位置。
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

    # 端到端场景：在一段服务日志里定位错误。
    log = "INFO start\nERROR db timeout\nINFO retry\nERROR db timeout\nINFO ok\n"

    show("第一个 ERROR 在哪", lambda: find(log, "ERROR"), log.find("ERROR"))
    show("ERROR 一共几次", lambda: count(log, "ERROR"), 2)
    show("每个 ERROR 所在的行号",
         lambda: [log.count("\n", 0, position) + 1 for position in find_all(log, "ERROR")], [2, 4])
    show("找不到 FATAL 时 find 返回 -1", lambda: find(log, "FATAL"), -1)

    def index_missing():
        try:
            index(log, "FATAL")
        except ValueError as error:
            return str(error)
        return "没有抛异常"

    show("找不到 FATAL 时 index 抛 ValueError", index_missing, "substring not found")
    show("DNA 序列里重叠出现的 ATA", lambda: list(find_all("ATATATA", "ATA")), [0, 2, 4])
