"""第 0 课实战：复杂度在日常 Python 代码里长什么样。

真实项目里很少有人专门“写算法”，复杂度问题通常藏在一行看着无害的代码里：
1. 在循环里写 x in some_list —— 每次都是 O(n)，整体变成 O(n²)。换成 set，整体 O(n)。
2. 查重、去重、计数 —— 用 set、dict.fromkeys、collections.Counter，一遍搞定。
3. 拿不准哪个快 —— 用标准库 timeit 量一下，而不是猜。

运行：uv run examples/complexity_in_practice.py
"""

from collections import Counter
from timeit import timeit


def new_customers_slow(today: list[str], known: list[str]) -> list[str]:
    """今天下单的人里，哪些是新客户。known 是 list，每次 in 都要从头扫：O(n × m)。"""
    return [customer for customer in today if customer not in known]


def new_customers_fast(today: list[str], known: list[str]) -> list[str]:
    """先把 known 转成 set（O(m) 一次），之后每次 in 平均 O(1)：整体 O(n + m)。结果和慢版一样。"""
    known_set = set(known)
    return [customer for customer in today if customer not in known_set]


def main() -> None:
    # 查重：一行
    signups = ["amy@x.com", "bob@x.com", "amy@x.com", "cat@x.com"]
    assert len(set(signups)) != len(signups)

    # 去重但保留原来的顺序：dict 记住插入顺序，O(n)
    assert list(dict.fromkeys(signups)) == ["amy@x.com", "bob@x.com", "cat@x.com"]

    # 计数：哪个邮箱重复了几次
    counts = Counter(signups)
    assert [email for email, times in counts.items() if times > 1] == ["amy@x.com"]
    print("重复报名：", {email: times for email, times in counts.items() if times > 1})

    # 循环里的 in：list 和 set 结果一样，速度差几个数量级
    known = [f"user{number}" for number in range(5000)]
    today = [f"user{number}" for number in range(4500, 5500)]
    assert new_customers_slow(today, known) == new_customers_fast(today, known)
    assert len(new_customers_fast(today, known)) == 500

    slow_seconds = timeit(lambda: new_customers_slow(today, known), number=3)
    fast_seconds = timeit(lambda: new_customers_fast(today, known), number=3)
    # 计时受机器负载影响，这里只打印，不做断言
    print(f"新客户 500 个；list 版 {slow_seconds:.3f} 秒，set 版 {fast_seconds:.4f} 秒")


if __name__ == "__main__":
    main()
