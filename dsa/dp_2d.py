"""第 38 课：二维 DP 高频题。讲解见 lessons/38-dp-2d.html

实际项目里比较字符串和文本先用标准库 difflib（get_close_matches、unified_diff）；需要严格的编辑距离时
才手写（命令纠错、配置 diff 的完整例子见 examples/dp_2d_in_practice.py）。这里练的是二维表怎么填。

规则：
- 每道题动手前，先用一句完整的中文写下 dp[i][j] 代表什么，再写它从哪几格推过来、
  第 0 行和第 0 列填什么、按什么顺序填（保证用到的格子都已经填好）。
- 用填表（自底向上）写，不要用 functools.cache / lru_cache。
- 变量名用完整的英文单词，例如 paths_to_cell、cheapest_cost_to、edit_distance_table、
  is_palindrome，不要写 res、tmp、s1、s2 这类缩写。下标 i、j 可以用。
- 自查：uv run dsa/dp_2d.py，会对每个函数跑几个例子，打印「输入、期望、实际」。
"""


def unique_paths_with_obstacles(obstacle_grid: list[list[int]]) -> int:
    """不同路径 II（LeetCode 63）：网格里有障碍，从左上角走到右下角有几条路？

    obstacle_grid[i][j] == 1 表示 (i, j) 是障碍，不能走；0 表示空地。每步只能向右或向下。
    起点或终点是障碍时返回 0。

    例子：obstacle_grid = [[0, 0, 0],
                           [0, 1, 0],
                           [0, 0, 0]]
          中间有一块障碍，只剩“先走右边一路”和“先走下边一路”两条，返回 2。

    思路提示（第 19 课 unique_paths 的升级版）：
      paths_to_cell[i][j] = 从起点走到 (i, j) 的路数。
      (i, j) 只能从上面 (i - 1, j) 或左边 (i, j - 1) 走过来，所以等于这两格的路数相加；
      如果 (i, j) 自己是障碍，就是 0。
      注意第 0 行：一旦遇到障碍，它右边的格子全都走不到了（第 0 列同理）。

    目标复杂度：O(m × n) 时间。
    """
    raise NotImplementedError


def min_path_sum(grid: list[list[int]]) -> int:
    """最小路径和（LeetCode 64）：从左上角走到右下角，路过的数字之和最小是多少？

    grid 里都是非负整数，每步只能向右或向下。起点和终点的数字都要算进去。

    例子：grid = [[1, 3, 1],
                  [1, 5, 1],
                  [4, 2, 1]]
          走 1 → 3 → 1 → 1 → 1，和是 7，返回 7。

    思路提示：
      cheapest_cost_to[i][j] = 从起点走到 (i, j)（含两端）的最小数字和。
      cheapest_cost_to[i][j] = grid[i][j] + min(上面那格, 左边那格)。
      第 0 行只能从左边一路走过来，第 0 列只能从上面一路走下来，所以它们是前缀和。

    目标复杂度：O(m × n) 时间。进阶：只留一行，额外空间 O(n)。
    """
    raise NotImplementedError


def edit_distance_table(source: str, target: str) -> list[list[int]]:
    """编辑距离（LeetCode 72）的整张 DP 表。

    一次操作可以：插入一个字符、删除一个字符、替换一个字符。
    返回一张 (len(source) + 1) 行 × (len(target) + 1) 列的表，
    其中 table[i][j] = 把 source 的前 i 个字符变成 target 的前 j 个字符，最少要几次操作。

    例子：source = "ab"，target = "b"，返回
          [[0, 1],     # 第 0 行：""   变成 ""、"b"
           [1, 1],     # 第 1 行："a"  变成 ""、"b"
           [2, 1]]     # 第 2 行："ab" 变成 ""、"b"（删掉 a 就行，1 次）

    思路提示：
      第 0 行：table[0][j] = j（空串变成 j 个字符，只能插入 j 次）。
      第 0 列：table[i][0] = i（i 个字符变成空串，只能删除 i 次）。
      其余格子看两个末尾字符 source[i - 1] 和 target[j - 1]：
        相同：不用操作，table[i][j] = table[i - 1][j - 1]（左上）。
        不同：三选一再 + 1——
          替换：table[i - 1][j - 1] + 1（左上）
          删除 source 的末尾字符：table[i - 1][j] + 1（上）
          在末尾插入 target 的末尾字符：table[i][j - 1] + 1（左）
    按行从上到下、每行从左到右填。

    目标复杂度：O(m × n) 时间和空间。
    """
    raise NotImplementedError


def edit_distance(source: str, target: str) -> int:
    """把 source 变成 target 最少要几次插入、删除或替换。

    例子：source = "horse"，target = "ros"，返回 3：
          horse → rorse（把 h 换成 r）→ rose（删掉 r）→ ros（删掉 e）。

    提示：就是 edit_distance_table 的右下角。
    """
    raise NotImplementedError


def min_deletions_to_make_equal(first_word: str, second_word: str) -> int:
    """（选做）两个字符串的删除操作（LeetCode 583）。

    每次可以从任意一个字符串里删掉一个字符，最少删几次能让两个字符串相同？

    例子：first_word = "sea"，second_word = "eat"
          从 "sea" 删 s 得 "ea"，从 "eat" 删 t 得 "ea"，共 2 次，返回 2。

    思路提示：最后留下来的，正好是两者的一个公共子序列；留得越长删得越少。
    所以答案 = len(first_word) + len(second_word) - 2 × 最长公共子序列长度。
    最长公共子序列的表第 20 课已经写过（dsa/dp_knapsack.py 的 lcs_length），这里再写一遍。

    目标复杂度：O(m × n) 时间。
    """
    raise NotImplementedError


def longest_palindromic_substring(text: str) -> str:
    """最长回文子串（LeetCode 5）：text 里最长的、连续的、正读反读一样的一段。

    长度相同的有好几段时，返回最靠左的那一段。空串返回 ""。

    例子：text = "babad"，"bab" 和 "aba" 都是长度 3 的回文，"bab" 更靠左，返回 "bab"。
          text = "cbbd"，返回 "bb"。

    思路提示：
      is_palindrome[i][j] = text[i..j]（含两端）是不是回文。
      一段是回文，当且仅当：两端字符相同，并且去掉两端后中间那段也是回文。
        is_palindrome[i][j] = text[i] == text[j] and (j - i < 2 or is_palindrome[i + 1][j - 1])
      遍历顺序：is_palindrome[i][j] 要用到更短的 is_palindrome[i + 1][j - 1]，
      所以按“子串长度”从 1 到 n 一圈圈地填；同一长度里，起点 i 从左往右。

    目标复杂度：O(n²) 时间。进阶：中心扩展法，O(n²) 时间、O(1) 空间。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def check(function, arguments, expected):
        """跑一个例子，打印「输入、期望、实际」。还没实现的函数会提示一下，不会让脚本中断。"""
        shown_input = ", ".join(repr(argument) for argument in arguments)
        try:
            actual = function(*arguments)
        except NotImplementedError:
            print(f"[未实现] {function.__name__}({shown_input})")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {function.__name__}({shown_input})  期望 {expected!r}，实际 {actual!r}")

    check(unique_paths_with_obstacles, ([[0, 0, 0], [0, 1, 0], [0, 0, 0]],), 2)
    check(unique_paths_with_obstacles, ([[0, 1], [0, 0]],), 1)
    check(unique_paths_with_obstacles, ([[0, 0], [1, 1], [0, 0]],), 0)
    check(unique_paths_with_obstacles, ([[1]],), 0)
    check(unique_paths_with_obstacles, ([[0]],), 1)

    check(min_path_sum, ([[1, 3, 1], [1, 5, 1], [4, 2, 1]],), 7)
    check(min_path_sum, ([[1, 2, 3], [4, 5, 6]],), 12)
    check(min_path_sum, ([[5]],), 5)

    check(edit_distance_table, ("ab", "b"), [[0, 1], [1, 1], [2, 1]])
    check(edit_distance_table, ("", "ab"), [[0, 1, 2]])
    check(edit_distance_table, ("cat", "cut"), [[0, 1, 2, 3], [1, 0, 1, 2], [2, 1, 1, 2], [3, 2, 2, 1]])

    check(edit_distance, ("horse", "ros"), 3)
    check(edit_distance, ("intention", "execution"), 5)
    check(edit_distance, ("", "abc"), 3)
    check(edit_distance, ("same", "same"), 0)

    check(min_deletions_to_make_equal, ("sea", "eat"), 2)
    check(min_deletions_to_make_equal, ("leetcode", "etco"), 4)
    check(min_deletions_to_make_equal, ("abc", "xyz"), 6)

    check(longest_palindromic_substring, ("babad",), "bab")
    check(longest_palindromic_substring, ("cbbd",), "bb")
    check(longest_palindromic_substring, ("forgeeksskeegfor",), "geeksskeeg")
    check(longest_palindromic_substring, ("a",), "a")
    check(longest_palindromic_substring, ("",), "")
