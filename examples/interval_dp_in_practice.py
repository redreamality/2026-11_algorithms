"""第 43 课实战：区间 DP 在业务代码里长什么样。

区间 DP 的标志是“只能动相邻的东西，最后一步把左右两块拼起来”。真实代码里常见三种：
1. 合并相邻分片（日志分段、视频切片、LSM 树的相邻文件）：每次合并要把合出来的整块重写一遍。
2. 矩阵连乘加括号：A×B×C 先算哪两个，乘法次数可以差几十倍。numpy 的 numpy.linalg.multi_dot
   内部就是这个区间 DP（本课程不装 numpy，这里手写）。
3. 把字符串补成回文：最长回文子序列不用动，其余字符在对称位置补一个。

业务里一般用 functools.cache 写递归 best(i, j)：区间数只有 n² 个，n 到几百都没问题。
要的往往不只是最优值，还有“怎么拼”，所以每个函数都会倒推出方案。

运行：uv run examples/interval_dp_in_practice.py
"""

from functools import cache
from itertools import accumulate


def plan_segment_merges(segment_sizes: list[int]) -> tuple[int, str]:
    """场景一：把相邻的日志分段合并成一个文件，每次只能合相邻两段，代价是合出来那段的大小（要重写的 MB 数）。

    返回 (最少总共重写多少 MB, 合并方案)，方案用括号写，例如 "((300 400) (200 400))"。
    rewrite_cost(i, j) = 把第 i 段到第 j 段合成一个文件的最少代价；最后一次合并把 i..k 和 k+1..j 拼起来。
    """
    prefix_total = list(accumulate(segment_sizes, initial=0))  # prefix_total[j + 1] - prefix_total[i] = 第 i..j 段总大小

    @cache
    def rewrite_cost(i: int, j: int) -> int:
        if i == j:
            return 0
        range_total = prefix_total[j + 1] - prefix_total[i]
        return min(rewrite_cost(i, k) + rewrite_cost(k + 1, j) for k in range(i, j)) + range_total

    def describe(i: int, j: int) -> str:
        if i == j:
            return str(segment_sizes[i])
        range_total = prefix_total[j + 1] - prefix_total[i]
        for k in range(i, j):  # 倒推：哪个分割点让代价等于最优值，就是这样拆的
            if rewrite_cost(i, k) + rewrite_cost(k + 1, j) + range_total == rewrite_cost(i, j):
                return f"({describe(i, k)} {describe(k + 1, j)})"
        raise AssertionError("不可能走到这里")

    last = len(segment_sizes) - 1
    return rewrite_cost(0, last), describe(0, last)


def plan_matrix_chain(shapes: list[tuple[int, int]]) -> tuple[int, str]:
    """场景二：一串矩阵相乘，怎么加括号，乘法次数最少？

    shapes[i] = 第 i 个矩阵的 (行数, 列数)，相邻两个的列数和行数要对得上。
    (p × q) 乘 (q × r) 要做 p·q·r 次乘法，结果是 p × r。
    multiply_cost(i, j) = 算出第 i 个到第 j 个矩阵连乘结果的最少乘法次数。
    最后一次乘法把 i..k 的结果（rows_i × columns_k）和 k+1..j 的结果（rows_{k+1} × columns_j）乘起来。
    """
    names = [chr(ord("A") + index) for index in range(len(shapes))]

    @cache
    def multiply_cost(i: int, j: int) -> int:
        if i == j:
            return 0
        return min(
            multiply_cost(i, k) + multiply_cost(k + 1, j) + shapes[i][0] * shapes[k][1] * shapes[j][1]
            for k in range(i, j)
        )

    def describe(i: int, j: int) -> str:
        if i == j:
            return names[i]
        for k in range(i, j):
            last_step = shapes[i][0] * shapes[k][1] * shapes[j][1]
            if multiply_cost(i, k) + multiply_cost(k + 1, j) + last_step == multiply_cost(i, j):
                return f"({describe(i, k)}{describe(k + 1, j)})"
        raise AssertionError("不可能走到这里")

    last = len(shapes) - 1
    return multiply_cost(0, last), describe(0, last)


def shortest_palindrome_by_insertion(text: str) -> str:
    """场景三：最少插入几个字符，把 text 变成回文串？返回插入后的结果（不止一种时返回其中一种）。

    best(i, j) = 把 text[i..j] 补成回文后的最短结果。
    两端相同：两端留着，中间递归；两端不同：在一边补上另一端的字符，挑结果更短的那种。
    结果长度 = len(text) + 最少插入次数 = 2 × len(text) - 最长回文子序列长度。
    """

    @cache
    def best(i: int, j: int) -> str:
        if i > j:
            return ""
        if i == j:
            return text[i]
        if text[i] == text[j]:
            return text[i] + best(i + 1, j - 1) + text[j]
        keep_left = text[i] + best(i + 1, j) + text[i]    # 在右边补一个 text[i]
        keep_right = text[j] + best(i, j - 1) + text[j]   # 在左边补一个 text[j]
        return min(keep_left, keep_right, key=len)

    return best(0, len(text) - 1)


def main() -> None:
    total, plan = plan_segment_merges([300, 400, 200, 400])
    assert (total, plan) == (2600, "((300 400) (200 400))")
    print("合并日志分段：最少重写", total, "MB，方案", plan)
    greedy_like = plan_segment_merges([200, 200, 100, 200])
    assert greedy_like == (1400, "((200 200) (100 200))")  # 先合最小的 100+200 反而多花 100

    operations, order = plan_matrix_chain([(10, 30), (30, 5), (5, 60)])
    assert (operations, order) == (4500, "((AB)C)")  # 另一种 (A(BC)) 要 27000 次
    print("矩阵连乘：", order, "乘法", operations, "次")
    operations, order = plan_matrix_chain([(40, 20), (20, 30), (30, 10), (10, 30)])
    assert (operations, order) == (26000, "((A(BC))D)")
    print("矩阵连乘：", order, "乘法", operations, "次")

    for text, expected in [("mbadm", "mbdadbm"), ("race", "ecarace"), ("level", "level")]:
        result = shortest_palindrome_by_insertion(text)
        assert result == result[::-1] and len(result) == len(expected), (text, result)
        print("补成回文：", text, "→", result)


if __name__ == "__main__":
    main()
