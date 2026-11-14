"""第 37 课：一维 DP 高频题。讲解见 lessons/37-dp-1d.html

实际项目里常用 functools.cache 写递归，再倒推出具体方案（会员卡购买、不相邻广告位、话题标签分词，
完整例子见 examples/dp_1d_in_practice.py）。这里按面试要求用填表写，练的是状态和转移。

规则：
- 每道题动手前，先在纸上写下四步法的答案：
  ① 定义状态：dp[i] 代表什么（写成一句完整的中文）；
  ② 写转移：dp[i] 由哪几个更小的状态算出来；
  ③ 定初始值：最小的几个状态是多少；
  ④ 定遍历顺序：先算哪个、后算哪个，保证用到的状态都已经算好。
- 用填表（自底向上）写，不要用 functools.cache / lru_cache。
- 变量名用完整的英文单词，例如 best_amount_up_to、ways_to_make、can_build_prefix，
  不要写 res、tmp、cnt 这类缩写。DP 表叫 dp 可以，但要在注释里写清 dp[i] 的含义。
- 自查：uv run dsa/dp_1d.py，会对每个函数跑几个例子，打印「输入、期望、实际」。
"""


def rob_houses(house_values: list[int]) -> int:
    """打家劫舍（LeetCode 198）。

    一排房子，house_values[i] 是第 i 间房子里的钱（都 ≥ 0）。
    相邻的两间不能在同一晚都偷（会触发警报）。问最多能偷到多少钱。

    例子：house_values = [2, 7, 9, 3, 1]
          偷第 0、2、4 间：2 + 9 + 1 = 12，这是最多的，返回 12。
          空列表返回 0。

    思路提示：
      状态：best_amount_up_to[i] = 只考虑前 i + 1 间房子（下标 0..i）时，最多能偷多少。
      看第 i 间：不偷它，答案就是 best_amount_up_to[i - 1]；
                 偷它，第 i - 1 间就不能偷，答案是 best_amount_up_to[i - 2] + house_values[i]。
      两者取大。

    目标复杂度：O(n) 时间。进阶：只留两个变量，额外空间 O(1)。
    """
    raise NotImplementedError


def rob_houses_in_circle(house_values: list[int]) -> int:
    """（选做）打家劫舍 II（LeetCode 213）：房子围成一圈，第一间和最后一间也算相邻。

    例子：house_values = [2, 3, 2]，第 0 间和第 2 间相邻，不能同时偷，最多偷 3。
          只有一间房子时，直接偷它。空列表返回 0。

    思路提示：首尾不能同时偷，所以拆成两种情况——“不考虑最后一间”和“不考虑第一间”，
    各自是一个普通的打家劫舍，答案取两者中大的。

    目标复杂度：O(n) 时间。
    """
    raise NotImplementedError


def count_coin_combinations(coins: list[int], amount: int) -> int:
    """零钱兑换 II（LeetCode 518）：用面值 coins（每种不限个数）凑出 amount，有多少种组合？

    组合不看顺序：1 + 2 + 2 和 2 + 1 + 2 算同一种。
    amount = 0 时返回 1（一枚都不拿，也算一种凑法）。

    例子：coins = [1, 2, 5]，amount = 5，有 4 种：
          5 / 2 + 2 + 1 / 2 + 1 + 1 + 1 / 1 + 1 + 1 + 1 + 1，返回 4。

    思路提示：
      状态：ways_to_make[a] = 凑出金额 a 的组合数。初始值 ways_to_make[0] = 1。
      遍历顺序是关键：外层循环面值，内层循环金额。
        for coin in coins:
            for a in range(coin, amount + 1):
                ways_to_make[a] += ways_to_make[a - coin]
      想一想：如果把两层循环反过来，数出来的会是什么？（讲解页里有答案）

    目标复杂度：O(len(coins) × amount) 时间，O(amount) 空间。
    """
    raise NotImplementedError


def longest_increasing_length_fast(numbers: list[int]) -> int:
    """最长严格递增子序列的长度（LeetCode 300），要求 O(n log n)。

    子序列：按原来的顺序挑出一些数，可以不连续。
    例子：numbers = [10, 9, 2, 5, 3, 7, 101, 18]
          最长递增子序列之一是 [2, 3, 7, 18]，返回 4。空列表返回 0。

    第 20 课的 O(n²) 写法是：dp[i] = 以 numbers[i] 结尾的最长长度，往前扫所有 j。
    这里要换一个状态：
      smallest_tail[k] = 在所有“长度为 k + 1 的递增子序列”里，结尾最小可以是多少。
      这个列表一定是严格递增的，所以可以二分。
    对每个新数 number：
      - 它比 smallest_tail 里所有数都大：接在最长的后面，append 到末尾；
      - 否则：找到第一个 ≥ number 的位置，把那里的数换成 number（结尾变小了，以后更好接）。
    最后 smallest_tail 的长度就是答案。

    二分可以自己写，也可以用 bisect.bisect_left。
    目标复杂度：O(n log n) 时间。
    """
    raise NotImplementedError


def can_break_into_words(text: str, dictionary_words: list[str]) -> bool:
    """单词拆分（LeetCode 139）：text 能不能切成若干段，每一段都在 dictionary_words 里？

    词典里的词可以重复使用。
    例子：text = "applepenapple"，dictionary_words = ["apple", "pen"]
          可以切成 "apple" + "pen" + "apple"，返回 True。
          text = "catsandog"，dictionary_words = ["cats", "dog", "sand", "and", "cat"]，返回 False。

    思路提示：
      状态：can_build_prefix[i] = text 的前 i 个字符（text[:i]）能不能被切好。
      初始值：can_build_prefix[0] = True（空串不用切）。
      转移：can_build_prefix[i] 为 True，当且仅当存在某个 j < i，
            使得 can_build_prefix[j] 为 True，并且 text[j:i] 在词典里。
      先把 dictionary_words 转成 set，查一个词是 O(1)。

    目标复杂度：O(n² × 切片长度) 以内即可；进阶：j 只往回看“最长单词长度”那么远。
    """
    raise NotImplementedError


def max_subarray_sum(numbers: list[int]) -> int:
    """最大子数组和（LeetCode 53）：找一段连续的、非空的子数组，使它的和最大，返回这个和。

    例子：numbers = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
          连续的一段 [4, -1, 2, 1] 和最大，返回 6。
          全是负数时，答案是最大的那个负数，例如 [-3, -1, -2] 返回 -1。
    保证 numbers 至少有一个数。

    思路提示：
      状态：best_sum_ending_here[i] = 必须以 numbers[i] 结尾的子数组里，最大的和。
      转移：要么接在前面那段后面，要么从 numbers[i] 自己重新开始：
            best_sum_ending_here[i] = max(best_sum_ending_here[i - 1] + numbers[i], numbers[i])
      答案是所有 best_sum_ending_here[i] 里最大的，不一定是最后一个。

    目标复杂度：O(n) 时间，O(1) 额外空间。
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

    check(rob_houses, ([1, 2, 3, 1],), 4)
    check(rob_houses, ([2, 7, 9, 3, 1],), 12)
    check(rob_houses, ([2, 1, 1, 2],), 4)
    check(rob_houses, ([5],), 5)
    check(rob_houses, ([],), 0)

    check(rob_houses_in_circle, ([2, 3, 2],), 3)
    check(rob_houses_in_circle, ([1, 2, 3, 1],), 4)
    check(rob_houses_in_circle, ([1, 2, 3],), 3)
    check(rob_houses_in_circle, ([5],), 5)

    check(count_coin_combinations, ([1, 2, 5], 5), 4)
    check(count_coin_combinations, ([2], 3), 0)
    check(count_coin_combinations, ([10], 10), 1)
    check(count_coin_combinations, ([1, 2, 5], 0), 1)

    check(longest_increasing_length_fast, ([10, 9, 2, 5, 3, 7, 101, 18],), 4)
    check(longest_increasing_length_fast, ([0, 1, 0, 3, 2, 3],), 4)
    check(longest_increasing_length_fast, ([7, 7, 7, 7],), 1)
    check(longest_increasing_length_fast, ([],), 0)

    check(can_break_into_words, ("leetcode", ["leet", "code"]), True)
    check(can_break_into_words, ("applepenapple", ["apple", "pen"]), True)
    check(can_break_into_words, ("catsandog", ["cats", "dog", "sand", "and", "cat"]), False)
    check(can_break_into_words, ("", ["a"]), True)

    check(max_subarray_sum, ([-2, 1, -3, 4, -1, 2, 1, -5, 4],), 6)
    check(max_subarray_sum, ([-3, -1, -2],), -1)
    check(max_subarray_sum, ([5, 4, -1, 7, 8],), 23)
    check(max_subarray_sum, ([1],), 1)
