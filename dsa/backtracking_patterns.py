"""第 36 课：回溯高频题。讲解见 lessons/36-backtracking-patterns.html

实际项目里，能用 itertools.product / combinations / permutations 就直接用；约束多、需要剪枝时才手写回溯
（测试矩阵、挑评审人、排班的完整例子见 examples/backtracking_patterns_in_practice.py）。
这里练的是手写回溯的基本功。

规则：
- 都用回溯写：选择 → 递归 → 撤销（第 21 课的模板）。不要用 itertools。
- 用一个 path 列表记录当前这条路选了什么；收集答案时存副本 path[:]（字符串用 "".join(path)）。
- 能提前判断“这条路走不通”就立刻 return 或 continue（剪枝），别等走到底再检查。
- 返回列表的函数，结果之间的顺序随意（运行本文件时会先排序再比较）；但每个结果内部的顺序要按各题的说明。
- 写完后运行 uv run dsa/backtracking_patterns.py，看每个例子的“期望”和“实际”是否一致。
"""


def subsets_with_duplicates(nums: list[int]) -> list[list[int]]:
    """nums 里可能有重复数字，返回所有不重复的子集（包括空集）。（LeetCode 90. 子集 II）

    每个子集内部从小到大排列；[1, 2] 和 [2, 1] 算同一个，只能出现一次。

    例子：[1, 2, 2] → [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]
    （如果把两个 2 当成不同的数，[1, 2] 和 [2] 会各出现两次。）

    思路：先排序，让相同的数挨在一起。用第 21 课“从 start 往后挑一个数”的写法：
        for i in range(start, len(sorted_nums)):
            if i > start and sorted_nums[i] == sorted_nums[i - 1]:
                continue      # 同一层里，相同的数只试第一个
            ...
    “同一层”指同一次递归调用里的这个 for 循环。i == start 时不跳过，所以 [2, 2] 仍然能选出来。

    目标复杂度：时间 O(n · 2^n)，递归深度 O(n)。
    """
    raise NotImplementedError


def unique_permutations(nums: list[int]) -> list[list[int]]:
    """nums 里可能有重复数字，返回所有不重复的全排列。（LeetCode 47. 全排列 II）

    例子：[1, 1, 2] → [[1, 1, 2], [1, 2, 1], [2, 1, 1]]

    思路：先排序，用 used 布尔列表记录哪些下标已经放进 path。每一层从头到尾挑一个没用过的下标 i，
    并加一条去重规则：
        if i > 0 and sorted_nums[i] == sorted_nums[i - 1] and not used[i - 1]:
            continue
    意思是：相同的几个数，必须按下标从小到大的顺序被选用。前一个相同的数还没用，就不许先用后一个，
    这样“两个 1 交换位置”这种只是换了顺序的重复排列就不会出现。

    目标复杂度：时间 O(n · n!)，递归深度 O(n)。
    """
    raise NotImplementedError


DIGIT_TO_LETTERS = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
}


def letter_combinations(digits: str) -> list[str]:
    """手机九宫格键盘上，每个数字对应几个字母（见 DIGIT_TO_LETTERS）。digits 只包含 2～9，
    返回这串数字能拼出的所有字母组合。digits 为空字符串时返回空列表 []。（LeetCode 17. 电话号码的字母组合）

    例子："23" → ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]

    思路：第 index 层决定第 index 个数字用哪个字母，从 DIGIT_TO_LETTERS[digits[index]] 里挑一个放进 path；
    index 走到 len(digits) 时，"".join(path) 就是一个答案。

    目标复杂度：时间 O(len(digits) · 4^len(digits))（每位最多 4 个字母），递归深度 O(len(digits))。
    """
    raise NotImplementedError


def generate_parentheses(pair_count: int) -> list[str]:
    """生成所有由 pair_count 对括号组成的合法括号串。（LeetCode 22. 括号生成）

    例子：3 → ["((()))", "(()())", "(())()", "()(())", "()()()"]；0 → [""]

    思路：一个字符一个字符地往后加，用 open_count 和 close_count 记录已经放了几个 "(" 和几个 ")"。
    - open_count < pair_count 时，可以放 "("；
    - close_count < open_count 时，才可以放 ")"（右括号不能比左括号多，否则一定不合法）。
    两条规则保证生成的每个串都合法，不需要最后再检查。

    目标复杂度：答案的个数是卡特兰数，约 4^n / n^1.5，时间和答案总长度同阶；递归深度 O(pair_count)。
    """
    raise NotImplementedError


def word_exists(board: list[list[str]], word: str) -> bool:
    """board 是字母网格，判断 word 能否由相邻格子（上下左右）里的字母依次连成，同一个格子不能用两次。
    （LeetCode 79. 单词搜索）

    例子：board =
        ["A", "B", "C", "E"]
        ["S", "F", "C", "S"]
        ["A", "D", "E", "E"]
    word = "ABCCED" → True；"SEE" → True；"ABCB" → False（B 用了两次）。

    思路：以每个格子为起点试一次。backtrack(row, col, index) 表示“从 (row, col) 开始匹配 word[index:]”：
    - 出界，或 board[row][col] != word[index]：返回 False；
    - index 是最后一个字母：返回 True；
    - 否则临时把 board[row][col] 改成 "#"（标记“这条路上已经用过”），往四个方向递归，
      递归回来后改回原来的字母（撤销），这样别的路径还能用这个格子。

    目标复杂度：时间 O(row_count · col_count · 3^len(word))（除了来的方向，每步最多 3 个方向可走）；
    额外空间 O(len(word))（递归深度）。
    """
    raise NotImplementedError


def palindrome_partitions(text: str) -> list[list[str]]:
    """把 text 切成若干段，要求每一段都是回文串（正着读和反着读一样），返回所有切法。（LeetCode 131. 分割回文串）

    每种切法内部按原来的先后顺序排列。

    例子："aab" → [["a", "a", "b"], ["aa", "b"]]

    思路：backtrack(start) 决定“从下标 start 开始的这一段切到哪里”：枚举 end 从 start 到 len(text) - 1，
    如果 text[start:end + 1] 是回文串，就把它放进 path，递归 backtrack(end + 1)，回来后撤销；
    不是回文串就跳过（剪枝）。start 走到 len(text) 时，path 就是一种切法。
    判断回文可以写一个辅助函数，用两个下标从两头往中间比。

    目标复杂度：最坏（全是同一个字母）有 2^(n-1) 种切法，时间 O(n · 2^n)；递归深度 O(n)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def show(function, arguments, expected, ignore_order=False):
        """调用 function(*arguments)，打印输入、期望和实际结果。ignore_order 为 True 时，比较前先把结果排序。"""
        shown_input = ", ".join(repr(argument) for argument in arguments)
        try:
            actual = function(*arguments)
            comparable_actual = sorted(actual) if ignore_order else actual
            comparable_expected = sorted(expected) if ignore_order else expected
            verdict = "通过" if comparable_actual == comparable_expected else "不对"
        except NotImplementedError:
            actual, verdict = "（还没写）", "未完成"
        print(f"[{verdict}] {function.__name__}({shown_input})")
        print(f"        期望：{expected!r}")
        print(f"        实际：{actual!r}")

    show(subsets_with_duplicates, ([1, 2, 2],), [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]], ignore_order=True)
    show(subsets_with_duplicates, ([0],), [[], [0]], ignore_order=True)
    show(subsets_with_duplicates, ([4, 4, 4, 1, 4],),
         [[], [1], [1, 4], [1, 4, 4], [1, 4, 4, 4], [1, 4, 4, 4, 4], [4], [4, 4], [4, 4, 4], [4, 4, 4, 4]],
         ignore_order=True)

    show(unique_permutations, ([1, 1, 2],), [[1, 1, 2], [1, 2, 1], [2, 1, 1]], ignore_order=True)
    show(unique_permutations, ([1, 2, 3],),
         [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]], ignore_order=True)
    show(unique_permutations, ([2, 2, 2],), [[2, 2, 2]], ignore_order=True)

    show(letter_combinations, ("23",), ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"], ignore_order=True)
    show(letter_combinations, ("",), [], ignore_order=True)
    show(letter_combinations, ("7",), ["p", "q", "r", "s"], ignore_order=True)

    show(generate_parentheses, (3,), ["((()))", "(()())", "(())()", "()(())", "()()()"], ignore_order=True)
    show(generate_parentheses, (1,), ["()"], ignore_order=True)
    show(generate_parentheses, (0,), [""], ignore_order=True)

    example_board = [
        ["A", "B", "C", "E"],
        ["S", "F", "C", "S"],
        ["A", "D", "E", "E"],
    ]
    show(word_exists, (example_board, "ABCCED"), True)
    show(word_exists, (example_board, "SEE"), True)
    show(word_exists, (example_board, "ABCB"), False)
    show(word_exists, ([["A"]], "A"), True)

    show(palindrome_partitions, ("aab",), [["a", "a", "b"], ["aa", "b"]], ignore_order=True)
    show(palindrome_partitions, ("a",), [["a"]], ignore_order=True)
    show(palindrome_partitions, ("aba",), [["a", "b", "a"], ["aba"]], ignore_order=True)
