"""第 20 课：动态规划（二）：背包与序列。讲解见 lessons/20-dp-knapsack.html

实际项目里：比较文本用标准库 difflib，模糊匹配用 difflib.get_close_matches（见 examples/dp_knapsack_in_practice.py）；
“预算内选一组东西”标准库没有现成的，小规模就自己写背包 DP，规模大了上整数规划求解器。
这里手写的版本都按业务代码的习惯来：返回“选了哪些 / 具体是哪个子序列”，而不只是一个最优值。

规则：
- 用自底向上的表格（list 套 list），不要用 functools.cache 之类的现成记忆化。
- 每道题先想清楚三件事：dp 格子代表什么、它从哪几个格子推出来、第 0 行 / 第 0 列填什么。
- 要返回“具体方案”，就先把整张表填好，再从右下角往回走，看每一格是从哪一格来的。
- 不要用暴力枚举所有子集或子序列（那是指数级的），测试里有稍大一点的数据。

写完后运行 uv run dsa/dp_knapsack.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_dp_knapsack.py。
"""

from collections.abc import Sequence
from typing import NamedTuple


class Item(NamedTuple):
    name: str
    cost: int  # 重量、价格、工时……总之是“占预算”的那个量，非负整数
    value: int  # 收益


def choose_items(items: list[Item], budget: int) -> list[Item]:
    """0-1 背包：每件最多选一次，总 cost 不超过 budget，让总 value 最大。返回选中的物品，保持 items 里的先后顺序。

    最优方案不止一种时，返回哪一种都行（测试只检查总价值和是否超预算）。

    best[i][b] = 只看前 i 件、预算为 b 时的最大总价值。
    第 i 件要么不选（best[i-1][b]），要么选（best[i-1][b - cost] + value，前提是 b >= cost）。
    填完表后从 i = len(items)、b = budget 往回走：best[i][b] != best[i-1][b] 说明第 i 件被选了，b 减去它的 cost。
    O(len(items) × budget) 时间和空间。
    """
    raise NotImplementedError


def longest_common_subsequence(first: Sequence, second: Sequence) -> list:
    """最长公共子序列（不要求连续），返回其中任意一个，以 list 形式。

    first、second 可以是字符串（按字符比），也可以是“文件的行列表”（按行比，这就是 diff 的核心）。
    common[i][j] = first 前 i 个元素和 second 前 j 个元素的 LCS 长度。
    元素相同：左上 + 1；不同：上、左取大。填完从右下角往回走：相同就收下、走左上；否则往值更大的一边走。
    O(len(first) × len(second))。
    """
    raise NotImplementedError


def diff_lines(old: list[str], new: list[str]) -> list[str]:
    """逐行比较两个版本，返回带前缀的行：\"  \" 表示没变，\"- \" 表示删掉的旧行，\"+ \" 表示新加的行。

    要求改动的行数最少，也就是保留的 \"  \" 行恰好是一个最长公共子序列。
    同一处既有删又有加时，先输出 \"- \" 行再输出 \"+ \" 行（和 difflib.ndiff 的习惯一样）。

    例子：old = [\"a\", \"b\", \"c\"]，new = [\"a\", \"c\", \"d\"]，
          返回 [\"  a\", \"- b\", \"  c\", \"+ d\"]。

    提示：和 longest_common_subsequence 用同一张表。这回从左上角往右下角走会更顺：
    把表定义成“后缀”的 LCS，common[i][j] = old[i:] 和 new[j:] 的 LCS 长度，从右下角往左上角填；
    然后从 (0, 0) 出发：两行相同就输出 \"  \" 一起前进；否则哪边的后缀 LCS 更大就往哪边走（删旧行或加新行）。
    O(len(old) × len(new))。
    """
    raise NotImplementedError


def longest_increasing_subsequence(numbers: list[int]) -> list[int]:
    """最长严格递增子序列（不要求连续），返回其中任意一个。空列表返回 []。

    length[i] = 以 numbers[i] 结尾的最长递增子序列长度 = 1 + max(length[j])，其中 j < i 且 numbers[j] < numbers[i]。
    另开一个 previous_index[i] 记下接在谁后面，最后从 length 最大的位置沿着 previous_index 往回走，再反转。
    O(n²)。
    """
    raise NotImplementedError


def edit_distance(first: str, second: str) -> int:
    """（选做）编辑距离：把 first 变成 second 最少要几次插入、删除或替换一个字符。拼写纠错就靠它。

    distance[i][j] 的意思和 LCS 一样。字符相同就抄左上；不同就取 左、上、左上 三者最小值再 + 1。
    第 0 行是 j，第 0 列是 i。O(len(first) × len(second))。
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

    # 端到端场景一：这个迭代只有 10 人天，从候选需求里挑出总收益最大的一组。
    backlog = [
        Item("导出 Excel", 5, 50),
        Item("暗色模式", 4, 30),
        Item("单点登录", 6, 66),
        Item("消息推送", 2, 10),
        Item("搜索提速", 5, 50),
    ]
    show("10 人天能做哪些需求", lambda: [item.name for item in choose_items(backlog, 10)], ["导出 Excel", "搜索提速"])
    # 注意：按“性价比”贪心会先拿单点登录（11/人天），剩 4 人天只能再塞暗色模式，总收益 96 < 100。

    # 场景二：两版配置文件做 diff。
    old_config = ["host=db1", "port=5432", "user=app", "timeout=30"]
    new_config = ["host=db2", "port=5432", "user=app", "timeout=30", "pool=10"]
    show("配置文件 diff", lambda: diff_lines(old_config, new_config),
         ["- host=db1", "+ host=db2", "  port=5432", "  user=app", "  timeout=30", "+ pool=10"])

    show("LCS(\"ABCBDAB\", \"BDCABA\") 的长度", lambda: len(longest_common_subsequence("ABCBDAB", "BDCABA")), 4)

    # 场景三：每天的活跃用户数，找出最长的一段“逐步创新高”的日子（不要求连续）。
    show("最长递增子序列的长度", lambda: len(longest_increasing_subsequence([10, 9, 2, 5, 3, 7, 101, 18])), 4)

    # 场景四：用户把 \"recieve\" 打错了，离正确拼写有多远？
    show("edit_distance(\"recieve\", \"receive\")", lambda: edit_distance("recieve", "receive"), 2)
