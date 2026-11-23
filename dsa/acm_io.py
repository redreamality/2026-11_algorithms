"""预备课：ACM 模式输入输出。讲解见 lessons/acm-io.html

主线题目（每个函数都是它的一个变体）：给一张无向图，n 个点（编号 1～n）、m 条边，没有自环和重边。
对每张图输出两行：
- 第一行：1～n 号点各自的度数（邻居个数），用一个空格隔开；
- 第二行：平均度数，保留两位小数。

例子：输入
    4 3
    1 2
    2 3
    2 4
输出
    1 3 1 1
    1.50

规则：
- 每个 solve_* 函数的参数 text 是整份 stdin 的内容（一个字符串），返回值是整份 stdout 的内容。
  这样不用真的读键盘就能测。考场上只要再包一层：sys.stdout.write(solve(sys.stdin.read()) + "\n")。
- 多行输出用 "\n" 连起来；末尾有没有换行、行尾有没有空格都算对（测试和大多数判题机一样会忽略）。
- 读数一律用 text.split() 切成 token，再用 iter() + next() 一个个取，不要按行硬拆（solve_named_cities 例外）。
- 命名用完整的英文单词，别用 res、tmp、l/r 这种缩写。

写完后运行 uv run dsa/acm_io.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_acm_io.py。
考场版参考写法在 examples/acm_io_in_practice.py（看之前先自己写一遍）。
"""

from collections.abc import Iterator


def read_graph(node_count: int, tokens: Iterator[str]) -> list[list[int]]:
    """n 已经由调用方读走了（作为 node_count 传进来），从 tokens 接着读 m，再读 m 条边。

    返回邻接表 adjacency：长度 n + 1，下标 0 空着不用，adjacency[u] 是 u 的邻居列表。
    无向图，每条边 u v 要同时记进 adjacency[u] 和 adjacency[v]。
    只能用 next(tokens) 取数；读完这张图后，tokens 要正好停在下一张图的开头。
    """
    raise NotImplementedError


def degree_report(adjacency: list[list[int]]) -> list[str]:
    """一张图的两行输出，返回 [度数那一行, 平均度数那一行]。

    adjacency 是 read_graph 的返回值（下标 0 不算一个点）。
    例子：[[], [2], [1, 3, 4], [2], [2]] 返回 ["1 3 1 1", "1.50"]。
    提示：" ".join(map(str, ...))；f"{x:.2f}"。
    """
    raise NotImplementedError


def solve_single_case(text: str) -> str:
    """单组输入：text 里只有一张图。

    "4 3\\n1 2\\n2 3\\n2 4\\n" 返回 "1 3 1 1\\n1.50"。
    """
    raise NotImplementedError


def solve_test_cases(text: str) -> str:
    """先读 T，再读 T 张图，每张图输出两行，按顺序接在一起（中间不加空行）。

    "2\\n4 3\\n1 2\\n2 3\\n2 4\\n3 1\\n1 3\\n" 返回 "1 3 1 1\\n1.50\\n1 0 1\\n0.67"。
    """
    raise NotImplementedError


def solve_until_eof(text: str) -> str:
    """不告诉有几张图，一直读到输入结束（EOF）。text 可能是空串或只有空白，这时返回 ""。

    "4 3\\n1 2\\n2 3\\n2 4\\n3 1\\n1 3\\n" 返回 "1 3 1 1\\n1.50\\n1 0 1\\n0.67"。
    提示：for 循环遍历 token 迭代器，每一轮取到的就是下一张图的 n。
    """
    raise NotImplementedError


def solve_adjacency_matrix(text: str) -> str:
    """同一道题，但图用邻接矩阵给出：先读 n，再读 n 行、每行 n 个 0 或 1。

    第 i 行第 j 个数是 1，表示 i 号点和 j 号点之间有边（i、j 从 1 数）。矩阵是对称的，对角线全是 0。
    "4\\n0 1 0 0\\n1 0 1 1\\n0 1 0 0\\n0 1 0 0\\n" 返回 "1 3 1 1\\n1.50"。
    提示：先把矩阵读成 n 个长度为 n 的 list（列表推导式里套 next），再转成邻接表交给 degree_report。
    """
    raise NotImplementedError


def solve_named_cities(text: str) -> str:
    """点有名字：第一行 n m；接下来 n 行，第 i 行是 i 号城市的名字（可能含空格，如 New York）；
    再接下来 m 行，每行一条边 u v（用编号）。

    输出 n 行，第 i 行是“城市名 度数”，名字原样输出（去掉首尾空白）。
    "3 2\\nNew York\\nLos Angeles\\nChicago\\n1 2\\n1 3\\n" 返回 "New York 2\\nLos Angeles 1\\nChicago 1"。
    提示：名字里有空格，整份 split() 会把 "New York" 拆成两个 token。这里改成 text.splitlines() 按行读。
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
        verdict = "通过" if actual.rstrip() == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    single_case = "4 3\n1 2\n2 3\n2 4\n"
    second_case = "3 1\n1 3\n"
    show("单组", lambda: solve_single_case(single_case), "1 3 1 1\n1.50")
    show("先读 T 组", lambda: solve_test_cases("2\n" + single_case + second_case), "1 3 1 1\n1.50\n1 0 1\n0.67")
    show("读到 EOF", lambda: solve_until_eof(single_case + second_case), "1 3 1 1\n1.50\n1 0 1\n0.67")
    show("邻接矩阵", lambda: solve_adjacency_matrix("4\n0 1 0 0\n1 0 1 1\n0 1 0 0\n0 1 0 0\n"), "1 3 1 1\n1.50")
    show("城市名带空格", lambda: solve_named_cities("3 2\nNew York\nLos Angeles\nChicago\n1 2\n1 3\n"),
         "New York 2\nLos Angeles 1\nChicago 1")
