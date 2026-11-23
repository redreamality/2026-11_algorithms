"""第 43 课：区间 DP。讲解见 lessons/43-interval-dp.html

实际项目里常用 functools.cache 写递归 best(i, j)，再倒推出具体方案（合并相邻文件的顺序、
矩阵连乘加括号、把字符串补成回文，完整例子见 examples/interval_dp_in_practice.py）。
这里按笔试要求用填表写，练的是“按区间长度从小到大”的遍历顺序。

规则：
- 每道题动手前，先在纸上写下四步法的答案（第 37 课）：
  ① 状态：dp[i][j] 代表区间 i..j（两端都含）的什么；
  ② 转移：区间 i..j 由哪些更短的区间算出来（通常是枚举分割点 k，或者去掉一端）；
  ③ 初始值：长度为 1 的区间是多少；
  ④ 遍历顺序：外层循环区间长度 length 从 2 到 n，内层循环左端点 i，右端点 j = i + length - 1。
- 用填表（自底向上）写，不要用 functools.cache / lru_cache。
- 变量名用完整的英文单词，例如 merge_cost、split_point、range_total，不要写 res、tmp、cnt。
- 自查：uv run dsa/interval_dp.py；测试：uv run pytest tests/test_interval_dp.py
"""


def merge_stones_min_cost(piles: list[int]) -> int:
    """石子合并：一排石子堆，每次只能把相邻的两堆合成一堆，代价是新堆的石子数。
    合到只剩一堆，最少总代价是多少？

    例子：piles = [3, 4, 2, 4]
          先合 3 + 4 = 7（代价 7），再合 2 + 4 = 6（代价 6），最后 7 + 6 = 13（代价 13），
          总代价 26，这是最少的，返回 26。
          贪心地“每次合最小的相邻两堆”会先合 4 + 2，总代价 28，不对。
          空列表或只有一堆时，不用合，返回 0。

    思路提示：
      状态：merge_cost[i][j] = 把第 i 堆到第 j 堆（两端都含）合成一堆的最少代价。
      最后一次合并一定是“左边一块 i..k”和“右边一块 k+1..j”合起来，代价是 i..j 的石子总数。
      转移：merge_cost[i][j] = min(merge_cost[i][k] + merge_cost[k + 1][j]，k 从 i 到 j - 1)
                                + (第 i 堆到第 j 堆的石子总数)
      区间总数用前缀和（第 27 课）O(1) 算出来。
      初始值：merge_cost[i][i] = 0（一堆不用合）。

    目标复杂度：O(n³) 时间，O(n²) 空间。
    """
    raise NotImplementedError


def merge_plan(piles: list[int]) -> int | tuple:
    """（选做）返回代价最少的合并方案，用嵌套的二元组表示“谁和谁合”。

    例子：piles = [3, 4, 2, 4]，返回 ((3, 4), (2, 4))：
          先各自合成 (3, 4) 和 (2, 4)，最后两块合在一起。
          只有一堆时返回那一堆本身，例如 [5] 返回 5。保证 piles 非空。
    最优方案不止一种时，返回任意一种都算对（测试只检查顺序没变、总代价最少）。

    思路提示：先像 merge_stones_min_cost 那样把表填满，同时记下每个区间最好的分割点
    best_split[i][j]；再从整个区间 0..n-1 开始，按分割点递归拆开。
    """
    raise NotImplementedError


def longest_palindromic_subsequence(text: str) -> int:
    """最长回文子序列（LeetCode 516）：从 text 里按原顺序挑出一些字符（可以不连续），
    组成正读反读都一样的串，最长有多长？

    例子：text = "bbbab"，挑出 "bbbb"，返回 4。
          text = "cbbd"，挑出 "bb"，返回 2。空串返回 0。

    思路提示：
      状态：longest[i][j] = text[i..j]（两端都含）里最长回文子序列的长度。
      看两端字符：
        text[i] == text[j]：两端可以配成一对放在最外层，longest[i][j] = longest[i + 1][j - 1] + 2；
        不相等：两端至少有一个用不上，longest[i][j] = max(longest[i + 1][j], longest[i][j - 1])。
      初始值：longest[i][i] = 1。注意长度为 2 时 i + 1 > j - 1，中间是空串，算 0。

    目标复杂度：O(n²) 时间和空间。
    """
    raise NotImplementedError


def min_insertions_to_palindrome(text: str) -> int:
    """让字符串成为回文串的最少插入次数（LeetCode 1312）：每次可以在任意位置插入一个字符。

    例子："mbadm" 插入 2 个字符变成 "mbdadbm"，返回 2。"zzazz" 已经是回文，返回 0。

    思路提示：最长回文子序列里的字符不用动，剩下的每个字符都要在对称位置补一个。
    所以答案 = len(text) - longest_palindromic_subsequence(text)。
    """
    raise NotImplementedError


def max_coins_bursting_balloons(numbers: list[int]) -> int:
    """（选做）戳气球（LeetCode 312）：一排气球，戳破第 i 个能得到 左邻 × 自己 × 右邻 枚硬币，
    左右邻是“还没戳破的”相邻气球，越界时当成 1。全部戳破，最多拿多少硬币？

    例子：numbers = [3, 1, 5, 8]，按 1、5、3、8 的顺序戳：
          3×1×5 + 3×5×8 + 1×3×8 + 1×8×1 = 15 + 120 + 24 + 8 = 167，返回 167。空列表返回 0。

    思路提示（和石子合并反过来想）：
      在两端各补一个 1：padded = [1, *numbers, 1]。
      状态：coins[left][right] = 只戳 left 和 right 之间（不含两端）的气球，最多拿多少。
      枚举这一段里“最后一个被戳破”的气球 last：它被戳时，左右邻正好是 padded[left] 和 padded[right]，
      coins[left][right] = max(coins[left][last] + padded[left] * padded[last] * padded[right] + coins[last][right])
      按 right - left 从小到大填。

    目标复杂度：O(n³) 时间。
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

    check(merge_stones_min_cost, ([3, 4, 2, 4],), 26)
    check(merge_stones_min_cost, ([2, 2, 1, 2],), 14)
    check(merge_stones_min_cost, ([5, 7],), 12)
    check(merge_stones_min_cost, ([5],), 0)
    check(merge_stones_min_cost, ([],), 0)

    check(merge_plan, ([3, 4, 2, 4],), ((3, 4), (2, 4)))
    check(merge_plan, ([5],), 5)

    check(longest_palindromic_subsequence, ("bbbab",), 4)
    check(longest_palindromic_subsequence, ("cbbd",), 2)
    check(longest_palindromic_subsequence, ("character",), 5)
    check(longest_palindromic_subsequence, ("",), 0)

    check(min_insertions_to_palindrome, ("mbadm",), 2)
    check(min_insertions_to_palindrome, ("zzazz",), 0)
    check(min_insertions_to_palindrome, ("leetcode",), 5)

    check(max_coins_bursting_balloons, ([3, 1, 5, 8],), 167)
    check(max_coins_bursting_balloons, ([1, 5],), 10)
    check(max_coins_bursting_balloons, ([],), 0)
