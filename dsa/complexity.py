"""第 0 课：复杂度。讲解见 lessons/00-complexity.html

实际项目里查重一般一行搞定：len(set(items)) != len(items)，或者 collections.Counter
（见 examples/complexity_in_practice.py）。这里同一个问题写三种解法，感受 O(n²)、O(n log n) 和 O(n) 的差别，
最后写一个业务里真正会用的 find_duplicates。

问题：一批数据里有没有重复的？
- 前三个函数接收的 items 可以是数字、字符串，任何能比较相等的值都行。
- 不能修改传进来的 items。

类型标注里的 Hashable 意思是“能放进 set、能当 dict 的键”的值：数字、字符串、元组可以，list 不行。
为什么有这个限制，第 4 课讲哈希表时会讲。

写完后运行 uv run dsa/complexity.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_complexity.py。
"""

from collections.abc import Hashable, Iterable, Sequence


def has_duplicate_slow(items: Sequence) -> bool:
    """两两比较。时间 O(n²)，额外空间 O(1)。"""
    raise NotImplementedError


def has_duplicate_sorted(items: Sequence) -> bool:
    """先排序，再看相邻两个是否相等。时间 O(n log n)。

    注意：不能写 items.sort()，那会改掉调用者的列表；用 sorted(items) 生成一份新的。
    """
    raise NotImplementedError


def has_duplicate_fast(items: Iterable[Hashable]) -> bool:
    """用 set 记住见过的值，一碰到见过的就立刻返回 True。时间 O(n)，额外空间 O(n)。

    items 可以是生成器（只能遍历一次、不知道长度），所以只能用 for 走一遍，不能用 len 或下标。
    """
    raise NotImplementedError


def find_duplicates(items: Iterable[Hashable]) -> list:
    """找出所有出现不止一次的值，每个只列一次，按“第二次出现”的先后排序。O(n)。

    例子：find_duplicates(["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com", "a@x.com"])
          返回 ["a@x.com", "b@x.com"]。
    提示：两个 set，seen 记见过的，reported 记已经报告过的。
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

    # 端到端场景：活动报名表，检查有没有人用同一个邮箱报了两次。
    signups = ["amy@x.com", "bob@x.com", "amy@x.com", "cat@x.com", "bob@x.com", "amy@x.com"]
    for function in (has_duplicate_slow, has_duplicate_sorted, has_duplicate_fast):
        # function.__name__ 是函数的名字字符串。lambda 里写 function=function，是把这一轮的 function
        # 存成 lambda 的默认参数；这里 show 会立刻调用 lambda，不写也行，但养成习惯可以避开
        # “循环里造的 lambda 全都用到最后一个值”的坑。
        show(f"{function.__name__}(报名表)", lambda function=function: function(signups), True)
    show("has_duplicate_fast(生成器：小写化后的邮箱)",
         lambda: has_duplicate_fast(email.lower() for email in ["A@x.com", "a@x.com"]), True)
    show("find_duplicates(报名表)", lambda: find_duplicates(signups), ["amy@x.com", "bob@x.com"])
    show("find_duplicates(没有重复)", lambda: find_duplicates(["d@x.com", "e@x.com"]), [])
    show("报名表没被改动", lambda: (has_duplicate_sorted(signups), signups)[1],
         ["amy@x.com", "bob@x.com", "amy@x.com", "cat@x.com", "bob@x.com", "amy@x.com"])
