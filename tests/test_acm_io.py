"""预备课：ACM 模式输入输出。

前半部分测 dsa/acm_io.py 的骨架（没写之前会报 NotImplementedError，这是正常的）。
后半部分用 subprocess 起一个真进程，把输入从 stdin 喂给考场版脚本 examples/acm_io_in_practice.py，
检查它打印到 stdout 的内容——判题机就是这么测你的程序的。
"""

import subprocess
import sys
from pathlib import Path

import pytest

from dsa.acm_io import (
    degree_report,
    read_graph,
    solve_adjacency_matrix,
    solve_named_cities,
    solve_single_case,
    solve_test_cases,
    solve_until_eof,
)

ROOT = Path(__file__).resolve().parent.parent

SINGLE_CASE = "4 3\n1 2\n2 3\n2 4\n"
SECOND_CASE = "3 1\n1 3\n"
BOTH_OUTPUTS = ["1 3 1 1", "1.50", "1 0 1", "0.67"]


def judged(output: str) -> list[str]:
    """像判题机一样比较：忽略末尾的空行和每行行尾的空格。"""
    return [line.rstrip() for line in output.rstrip().splitlines()]


def test_read_graph_builds_adjacency_and_stops_at_next_case():
    tokens = iter("3 2 1 2 2 3 99".split())
    adjacency = read_graph(int(next(tokens)), tokens)
    assert adjacency == [[], [2], [1, 3], [2]]
    assert next(tokens) == "99"  # 正好停在下一张图的开头，没有多取也没有少取


def test_read_graph_without_edges():
    assert read_graph(2, iter(["0"])) == [[], [], []]


def test_degree_report():
    assert degree_report([[], [2], [1, 3, 4], [2], [2]]) == ["1 3 1 1", "1.50"]
    assert degree_report([[], [2], [1], []]) == ["1 1 0", "0.67"]


def test_single_case():
    assert judged(solve_single_case(SINGLE_CASE)) == ["1 3 1 1", "1.50"]


def test_single_case_ignores_line_layout():
    """换行和多余空格放在哪都不影响：split() 不区分空格和换行。"""
    assert judged(solve_single_case("  4 3 1 2\n\n2 3   2 4")) == ["1 3 1 1", "1.50"]


def test_single_case_without_edges():
    assert judged(solve_single_case("3 0\n")) == ["0 0 0", "0.00"]


def test_test_cases():
    assert judged(solve_test_cases("2\n" + SINGLE_CASE + SECOND_CASE)) == BOTH_OUTPUTS
    assert judged(solve_test_cases("1\n" + SECOND_CASE)) == ["1 0 1", "0.67"]


def test_until_eof():
    assert judged(solve_until_eof(SINGLE_CASE + SECOND_CASE)) == BOTH_OUTPUTS
    assert judged(solve_until_eof(SINGLE_CASE)) == ["1 3 1 1", "1.50"]


def test_until_eof_empty_input():
    assert solve_until_eof("").strip() == ""
    assert solve_until_eof("\n  \n").strip() == ""


def test_adjacency_matrix():
    matrix = "4\n0 1 0 0\n1 0 1 1\n0 1 0 0\n0 1 0 0\n"
    assert judged(solve_adjacency_matrix(matrix)) == ["1 3 1 1", "1.50"]
    assert judged(solve_adjacency_matrix("1\n0\n")) == ["0", "0.00"]


def test_named_cities_keep_spaces_in_names():
    text = "3 2\nNew York\nLos Angeles\nChicago\n1 2\n1 3\n"
    assert judged(solve_named_cities(text)) == ["New York 2", "Los Angeles 1", "Chicago 1"]


def test_named_cities_strip_outer_whitespace():
    text = "2 1\n  Hang Zhou  \nShang Hai\r\n1 2\n"
    assert judged(solve_named_cities(text)) == ["Hang Zhou 1", "Shang Hai 1"]


@pytest.mark.parametrize(
    "stdin, expected",
    [
        (SINGLE_CASE, ["1 3 1 1", "1.50"]),
        (SINGLE_CASE + SECOND_CASE, BOTH_OUTPUTS),
        ("5 0", ["0 0 0 0 0", "0.00"]),
    ],
    ids=["single", "until-eof", "no-edges"],
)
def test_reference_script_through_stdin(stdin: str, expected: list[str]):
    """端到端：起一个新进程，把 stdin 管道接到考场版脚本上，读它的 stdout。"""
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples" / "acm_io_in_practice.py"), "--stdin"],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""  # 调试信息不能混进输出，也别留在 stderr 里
    assert judged(result.stdout) == expected
