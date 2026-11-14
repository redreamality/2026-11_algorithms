"""第 19 课实战：Python 项目里记忆化真正是怎么写的。

几乎不会手写 memo 字典，直接用标准库：
1. @functools.cache：无上限缓存。适合“参数种类有限”的纯函数，比如递归求解、解析配置。
2. @functools.lru_cache(maxsize=N)：最多存 N 条，满了淘汰最久没用的。适合参数无穷多的场景（查汇率、查用户）。
3. 三个常见坑：
   - 参数必须可哈希：list / dict 要先转成 tuple / frozenset。
   - 递归太深会 RecursionError（默认上限约 1000 层）：先“从小到大预热”，或者干脆改成填表。
   - 只缓存纯函数：结果依赖时间、数据库等外部状态时，缓存会返回过期数据。

运行：uv run examples/dp_memo_in_practice.py
"""

from functools import cache, lru_cache


def split_into_words(text: str, dictionary: frozenset[str]) -> list[str] | None:
    """把没有空格的文本切成词典里的词（比如解析拼在一起的标签、域名）。切不出返回 None。

    状态：best_split(start) = text[start:] 的一种切法。同一个 start 会被反复问到，用 @cache 记住。
    dictionary 用 frozenset 传进来，所以它本身也是可哈希的；内部函数只用一个 int 参数。
    """

    @cache
    def best_split(start: int) -> tuple[str, ...] | None:
        if start == len(text):
            return ()
        for end in range(start + 1, len(text) + 1):
            word = text[start:end]
            if word in dictionary:
                rest = best_split(end)
                if rest is not None:
                    return (word, *rest)
        return None

    result = best_split(0)
    return list(result) if result is not None else None


class RateService:
    """模拟一个很慢的远程汇率接口，记录真正被调用的次数。"""

    def __init__(self) -> None:
        self.remote_calls = 0

    def fetch(self, currency: str) -> float:
        self.remote_calls += 1
        return {"USD": 7.10, "EUR": 7.70, "JPY": 0.047}[currency]


def shipping_cost(weight_in_kilograms: int) -> int:
    """阶梯运费（元）：每次可以按 1 kg 首重 10 元、或 5 kg 包 35 元、或 20 kg 包 120 元打包，求最便宜。

    最便宜的打包方式 = 最后一个包选哪种，再加剩下重量的最便宜价格。递归 + @cache。
    重量很大时递归会太深，所以先从小到大预热一遍缓存，每次只往下递归一两层。
    """
    packages = {1: 10, 5: 35, 20: 120}

    @cache
    def cheapest(weight: int) -> int:
        if weight <= 0:
            return 0
        return min(price + cheapest(weight - size) for size, price in packages.items())

    for warm_up_weight in range(weight_in_kilograms):
        cheapest(warm_up_weight)
    return cheapest(weight_in_kilograms)


def main() -> None:
    dictionary = frozenset({"python", "py", "thon", "data", "science", "sci", "ence"})
    words = split_into_words("pythondatascience", dictionary)
    assert words == ["py", "thon", "data", "sci", "ence"]
    assert split_into_words("pythonx", dictionary) is None
    print("切词：", words)

    service = RateService()
    cached_fetch = lru_cache(maxsize=2)(service.fetch)
    for currency in ["USD", "EUR", "USD", "JPY", "USD", "EUR"]:
        cached_fetch(currency)
    info = cached_fetch.cache_info()
    # maxsize=2：JPY 进来时淘汰了最久没用的 EUR，所以最后一次查 EUR 又要远程调用。
    assert (info.hits, info.misses, info.currsize) == (2, 4, 2)
    assert service.remote_calls == 4
    print("查 6 次汇率，远程调用", service.remote_calls, "次：", info)

    try:
        cache(sum)([1, 2, 3])
    except TypeError as error:
        print("list 参数不能缓存：", error)
    else:
        raise AssertionError("list 应该不可哈希")

    assert shipping_cost(7) == 55  # 5 kg 包 + 两个 1 kg
    assert shipping_cost(25) == 155  # 20 kg 包 + 5 kg 包
    assert shipping_cost(5000) == 30000  # 不预热的话这里会 RecursionError
    print("25 kg 运费：", shipping_cost(25), "元；5000 kg 运费：", shipping_cost(5000), "元")


if __name__ == "__main__":
    main()
