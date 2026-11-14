"""第 19 课：动态规划（一）：从递归到记忆化。讲解见 lessons/19-dp-memo.html

实际项目里，记忆化直接用标准库的 @functools.cache / @functools.lru_cache（见 examples/dp_memo_in_practice.py）。
这里先自己手写一个同样用法的装饰器 memoize，搞懂它在背后做了什么；后面的题都用它或用填表来写。

规则：
- memoize 里不要用 functools.cache / lru_cache，缓存自己用 dict 写（functools.wraps 可以用）。
- 每题动手前先写下 DP 三问的答案：① 状态 dp[i] 是什么；② 转移怎么算；③ 初始值是多少。
- fibonacci_memo 用递归 + 你的 memoize；其余函数用填表（自底向上）写。

写完后运行 uv run dsa/dp_memo.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_dp_memo.py。
"""

from collections import Counter
from typing import NamedTuple


class CacheInfo(NamedTuple):
    """和 functools 的 cache_info() 一样的三个字段。"""

    hits: int  # 查缓存命中的次数
    misses: int  # 没命中、真正调用了原函数的次数
    currsize: int  # 缓存里现在存了几条


def memoize(function):
    """装饰器：把 function 的结果按参数缓存起来，同样的参数第二次调用直接返回缓存。

    用法和 @functools.cache 一样：

        @memoize
        def fibonacci(n): ...

        fibonacci(30)
        fibonacci.cache_info()   # CacheInfo(hits=28, misses=31, currsize=31)
        fibonacci.cache_clear()  # 清空缓存，计数也归零

    要求：
    - 缓存的键用 (args, tuple(sorted(kwargs.items())))。参数不可哈希（比如传了 list）时，
      查 dict 会自然抛 TypeError，不用特殊处理——functools.cache 也是这样。
    - 返回的包装函数要带上 cache_info 和 cache_clear 两个属性（函数也是对象，可以直接 wrapper.cache_info = ...）。
    - 用 functools.wraps(function) 保留原函数的 __name__ 和 docstring。
    """
    raise NotImplementedError


def fibonacci_memo(n: int) -> int:
    """第 n 个斐波那契数：fibonacci(0) = 0，fibonacci(1) = 1，fibonacci(n) = fibonacci(n-1) + fibonacci(n-2)。n ≥ 0。

    要求：在函数里定义一个递归的内部函数，用你写的 @memoize 装饰它，再调用。O(n)。
    这样每次调用 fibonacci_memo 都有一份新缓存，不会在两次调用之间悄悄共享状态。
    """
    raise NotImplementedError


def fibonacci_table(n: int) -> int:
    """同 fibonacci_memo，但用填表写，不递归，所以 n = 5000 也不会 RecursionError。O(n) 时间。

    进阶：只留两个变量，额外空间 O(1)。
    """
    raise NotImplementedError


def climb_stairs(n: int) -> int:
    """爬 n 级台阶，每次走 1 级或 2 级，有几种走法？n ≥ 0，约定 climb_stairs(0) = 1。O(n)。"""
    raise NotImplementedError


def min_coins(denominations: list[int], amount: int) -> Counter[int] | None:
    """用面值 denominations（每种不限张数）凑出 amount，张数最少。返回 Counter({面值: 张数})。

    凑不出返回 None；amount = 0 返回空的 Counter()。最少张数的凑法不止一种时，返回哪一种都行。
    和第 18 课的贪心 make_change 对比：面值 [1, 3, 4] 凑 6，这里返回 Counter({3: 2})。

    状态 fewest[a] = 凑出 a 的最少张数；转移 fewest[a] = min(fewest[a - coin] + 1)。
    要知道“用了哪些”，再开一个 last_coin[a] 记下取到最小值时用的是哪个面值，
    最后从 amount 开始沿着 last_coin 往回走：a -= last_coin[a]，一路把面值记进 Counter。
    O(amount × len(denominations))。凑不出先用 math.inf 表示。
    """
    raise NotImplementedError


def unique_paths(rows: int, columns: int, blocked: frozenset[tuple[int, int]] = frozenset()) -> int:
    """rows 行 columns 列的网格，从左上角 (0, 0) 走到右下角，每步只能向右或向下，有几条路？

    blocked 是走不通的格子 (行, 列)。起点或终点被堵住时返回 0。rows, columns ≥ 1。
    状态 paths[row][column] = 走到这一格的路数 = 上面一格 + 左边一格；被堵的格子是 0。O(rows × columns)。
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

    # 端到端场景一：一个很慢的“查汇率”函数，用 memoize 包一层，重复查询不再真正调用。
    def cached_rate_lookup():
        calls = []

        @memoize
        def exchange_rate(currency: str) -> float:
            calls.append(currency)  # 记下真正被调用了几次
            return {"USD": 7.1, "EUR": 7.7}[currency]

        for currency in ["USD", "EUR", "USD", "USD", "EUR"]:
            exchange_rate(currency)
        return calls, exchange_rate.cache_info()

    show("查 5 次汇率，只真正调用 2 次", cached_rate_lookup, (["USD", "EUR"], CacheInfo(hits=3, misses=2, currsize=2)))

    show("fibonacci_memo(80)", lambda: fibonacci_memo(80), 23416728348467685)
    show("fibonacci_table(100)", lambda: fibonacci_table(100), 354224848179261915075)

    # 场景二：面值不标准的游戏代币，凑出指定金额要几枚、分别是哪些。
    show("代币 [1, 3, 4] 凑 6", lambda: min_coins([1, 3, 4], 6), Counter({3: 2}))
    show("代币 [1, 7, 10] 凑 14", lambda: min_coins([1, 7, 10], 14), Counter({7: 2}))
    show("只有 5 和 10，凑不出 7", lambda: min_coins([5, 10], 7), None)

    # 场景三：仓库机器人在 3×4 的货架网格里只能向右或向下走，(1, 1) 处有货架挡着。
    show("机器人有几条路可走", lambda: unique_paths(3, 4, frozenset({(1, 1)})), 4)
