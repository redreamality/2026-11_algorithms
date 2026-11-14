"""第 26 课：滑动窗口。讲解见 lessons/26-sliding-window.html

规则：
- 每道题都用滑动窗口做到 O(n)，不要两层循环枚举所有子串或子数组。
- 窗口是一段连续区间 [window_start, window_end]。外层循环让 window_end 每次右移一格，
  把新元素放进窗口；然后用内层 while 循环右移 window_start，把窗口收缩到满足要求为止。
- window_start 和 window_end 都只往右走，不回头，所以每个元素最多进窗口一次、出窗口一次。
- 写完后运行 uv run dsa/sliding_window.py，看每个例子的“期望”和“实际”是否一致。
"""


def longest_substring_without_repeat(text: str) -> int:
    """无重复字符的最长子串（LeetCode 3）。

    返回 text 中不含重复字符的最长子串的长度。子串必须是连续的一段。空字符串返回 0。

    例子：text = "abcabcbb"，返回 3（最长的是 "abc"）。
          text = "pwwkew"，返回 3（最长的是 "wke"；"pwke" 不连续，不算子串）。

    思路提示：用一个集合 characters_in_window 记录窗口里有哪些字符。
    window_end 右移时，如果新字符已经在窗口里，就不断把 window_start 处的字符移出集合、
    window_start 右移，直到没有重复，再把新字符加进去，用当前窗口长度更新答案。

    目标复杂度：时间 O(n)，额外空间 O(字符种类数)。
    """
    raise NotImplementedError


def min_window_substring(source: str, target: str) -> str:
    """最小覆盖子串（LeetCode 76）。

    在 source 里找一个最短的连续子串，使 target 里的每个字符（连重复次数一起算）都包含在这个子串里。
    返回这个子串；找不到返回空字符串 ""。题目保证最短的答案只有一个。

    例子：source = "ADOBECODEBANC"，target = "ABC"，返回 "BANC"。
          source = "a"，target = "aa"，返回 ""（source 里只有一个 a，不够两个）。

    思路提示：
    - need_count：target 里每个字符需要几个（用 dict 统计）。
    - missing_count：窗口里还差几个字符才能覆盖 target，一开始等于 len(target)。
    - window_end 右移，放进一个字符：如果它是还缺的字符（need_count 里该字符的值大于 0），
      missing_count 减 1；不管缺不缺，need_count 里该字符都减 1（变成负数表示窗口里多出来了）。
    - missing_count 变成 0 时，窗口已经覆盖 target。此时尽量右移 window_start 缩小窗口，
      每缩一次先记录答案；移出的字符让 need_count 加 1，加完大于 0 说明又缺了，missing_count 加 1，停止收缩。

    目标复杂度：时间 O(len(source) + len(target))，额外空间 O(字符种类数)。
    """
    raise NotImplementedError


def min_subarray_length(target: int, numbers: list[int]) -> int:
    """长度最小的子数组（LeetCode 209）。

    numbers 里都是正整数。找出和大于等于 target 的最短连续子数组，返回它的长度；
    不存在返回 0。

    例子：target = 7，numbers = [2, 3, 1, 2, 4, 3]，返回 2（子数组 [4, 3] 的和是 7）。

    思路提示：维护窗口的和 window_sum。window_end 右移时把新数加进 window_sum；
    只要 window_sum >= target，就用窗口长度更新答案，然后把 numbers[window_start] 减掉、window_start 右移。
    因为所有数都是正数，窗口变短，和一定变小，所以“收缩到不满足为止”不会错过答案。

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


if __name__ == "__main__":

    def show(title, compute, expected):
        """运行一个例子，打印输入、期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    show('longest_substring_without_repeat("abcabcbb")',
         lambda: longest_substring_without_repeat("abcabcbb"), 3)
    show('longest_substring_without_repeat("bbbbb")',
         lambda: longest_substring_without_repeat("bbbbb"), 1)
    show('longest_substring_without_repeat("pwwkew")',
         lambda: longest_substring_without_repeat("pwwkew"), 3)
    show('longest_substring_without_repeat("")',
         lambda: longest_substring_without_repeat(""), 0)
    show('longest_substring_without_repeat("abba")',
         lambda: longest_substring_without_repeat("abba"), 2)

    show('min_window_substring("ADOBECODEBANC", "ABC")',
         lambda: min_window_substring("ADOBECODEBANC", "ABC"), "BANC")
    show('min_window_substring("a", "a")',
         lambda: min_window_substring("a", "a"), "a")
    show('min_window_substring("a", "aa")',
         lambda: min_window_substring("a", "aa"), "")
    show('min_window_substring("aaflslflsldkalskaaa", "aaa")',
         lambda: min_window_substring("aaflslflsldkalskaaa", "aaa"), "aaa")

    show("min_subarray_length(7, [2, 3, 1, 2, 4, 3])",
         lambda: min_subarray_length(7, [2, 3, 1, 2, 4, 3]), 2)
    show("min_subarray_length(4, [1, 4, 4])",
         lambda: min_subarray_length(4, [1, 4, 4]), 1)
    show("min_subarray_length(11, [1, 1, 1, 1, 1, 1, 1, 1])",
         lambda: min_subarray_length(11, [1, 1, 1, 1, 1, 1, 1, 1]), 0)
    show("min_subarray_length(15, [1, 2, 3, 4, 5])",
         lambda: min_subarray_length(15, [1, 2, 3, 4, 5]), 5)
