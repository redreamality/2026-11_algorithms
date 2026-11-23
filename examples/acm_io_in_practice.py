"""预备课实战：ACM 模式的输入输出。讲解见 lessons/acm-io.html

笔试（牛客、各家公司的在线笔试）大多是 ACM 模式：程序自己从标准输入（stdin）读数据，
把答案打印到标准输出（stdout），判题机逐行比对。这个脚本就是一份考场能直接交的程序。

主线题目（整课都用它）：给一张无向图，n 个点（编号 1～n）、m 条边。
输出两行：第一行是 1～n 号点各自的度数（邻居个数），用空格隔开；第二行是平均度数，保留两位小数。

输入可能有三种组织方式，这里都写了：
- 单组：直接给一张图。
- 先给 T，再给 T 张图。
- 不告诉有几张图，一直读到输入结束（EOF）。

两种运行方式：
- uv run examples/acm_io_in_practice.py            跑自带的 assert，并用管道把输入喂给自己（演示本地怎么测）。
- uv run examples/acm_io_in_practice.py --stdin < input.txt
                                                   考场模式：从 stdin 读到 EOF，打印答案。
"""

import io
import subprocess
import sys
from collections.abc import Iterator


def read_graph(node_count: int, tokens: Iterator[str]) -> list[list[int]]:
    """n 已经由调用方读走了；这里接着从 token 迭代器里读 m 和 m 条边。
    返回邻接表，点从 1 开始编号，所以开 n + 1 格，下标 0 空着不用。"""
    edge_count = int(next(tokens))
    adjacency: list[list[int]] = [[] for _ in range(node_count + 1)]
    for _ in range(edge_count):
        u = int(next(tokens))
        v = int(next(tokens))
        adjacency[u].append(v)  # 无向图：两头都要记
        adjacency[v].append(u)
    return adjacency


def degree_report(adjacency: list[list[int]]) -> list[str]:
    """一张图的两行输出：各点度数、平均度数（两位小数）。"""
    degrees = [len(neighbors) for neighbors in adjacency[1:]]
    average = sum(degrees) / len(degrees)
    return [" ".join(map(str, degrees)), f"{average:.2f}"]


def solve(text: str) -> str:
    """考场版本：读到 EOF，有几张图就输出几组。单组输入也是它的特例。"""
    tokens = iter(text.split())
    output_lines: list[str] = []
    # for 每轮从迭代器里取一个 token，就是这张图的 n；取不到（EOF）循环自己结束。
    # 循环体里的 read_graph 接着从同一个迭代器往后取，所以下一轮拿到的正好是下一张图的 n。
    for node_count_token in tokens:
        adjacency = read_graph(int(node_count_token), tokens)
        output_lines.extend(degree_report(adjacency))
    return "\n".join(output_lines)


def main_from_stdin() -> None:
    """真正交上去的入口：一次读完 stdin，一次写完 stdout。"""
    sys.stdout.write(solve(sys.stdin.read()) + "\n")


SINGLE_CASE = """4 3
1 2
2 3
2 4
"""

TWO_CASES_UNTIL_EOF = SINGLE_CASE + """3 1
1 3
"""


def main() -> None:
    # 1. 直接调用 solve：输入和输出都是字符串，最好测。
    assert solve(SINGLE_CASE) == "1 3 1 1\n1.50"
    assert solve(TWO_CASES_UNTIL_EOF) == "1 3 1 1\n1.50\n1 0 1\n0.67"
    assert solve("2 0") == "0 0\n0.00"  # 没有边
    assert solve("3 2 1 2 2 3") == "1 2 1\n1.33"  # 换行随便放，split() 都不在乎
    print("单组：", solve(SINGLE_CASE).splitlines())

    # 2. 用 io.StringIO 假装成 stdin：本地调试时不用每次手敲输入。
    real_stdin, real_stdout = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = io.StringIO(TWO_CASES_UNTIL_EOF), io.StringIO()
    try:
        main_from_stdin()
        captured = sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = real_stdin, real_stdout
    assert captured == "1 3 1 1\n1.50\n1 0 1\n0.67\n"
    print("StringIO 模拟 stdin：", captured.splitlines())

    # 3. 真的起一个新进程，用管道把输入喂给它的 stdin——和判题机做的事一样。
    result = subprocess.run(
        [sys.executable, __file__, "--stdin"],
        input=TWO_CASES_UNTIL_EOF,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == ["1 3 1 1", "1.50", "1 0 1", "0.67"]
    print("管道喂给子进程：", result.stdout.splitlines())


if __name__ == "__main__":
    if "--stdin" in sys.argv:
        main_from_stdin()
    else:
        main()
