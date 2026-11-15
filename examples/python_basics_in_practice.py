"""预备课实战：预备课里的写法在一个真实小脚本里怎么配合。

任务：读一段订单文本（每行“日期,顾客,书名,价格”），跳过格式错的行并记下原因，
然后统计：每本书卖了几本、每位顾客买了哪些书、销售额最高的顾客、逐日累计销售额。

用到的写法：dataclass、生成器、try/except 与 raise ... from、Counter、defaultdict、
sorted 的 key=、f-string、解包、itertools.accumulate。

运行：uv run examples/python_basics_in_practice.py
"""

from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import accumulate

ORDERS_TEXT = """\
2026-11-01,Ann,三体,59.00
2026-11-01,Bob,活着,35.50
2026-11-02,Ann,活着,35.50
2026-11-02,Cid,三体,abc
2026-11-03,Bob,三体,59.00
这一行格式不对
2026-11-03,Ann,围城,28.00
"""


@dataclass
class Order:
    day: str
    customer: str
    title: str
    price: float


def parse_order(line: str) -> Order:
    """把一行文本解析成 Order。格式错就抛 ValueError，说清是哪一行、错在哪。"""
    parts = line.split(",")
    if len(parts) != 4:
        raise ValueError(f"应该有 4 列，实际 {len(parts)} 列：{line!r}")
    day, customer, title, price_text = parts  # 解包
    try:
        price = float(price_text)
    except ValueError as error:
        raise ValueError(f"价格不是数字：{line!r}") from error
    return Order(day, customer, title, price)


def read_orders(lines: Iterable[str], errors: list[str]) -> Iterator[Order]:
    """生成器：逐行产出解析好的订单；坏行不中断，把原因记进 errors。"""
    for line_number, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            yield parse_order(line)
        except ValueError as error:
            errors.append(f"第 {line_number} 行：{error}")


def main() -> None:
    errors: list[str] = []
    orders = list(read_orders(ORDERS_TEXT.splitlines(), errors))  # 要遍历多次，先存成 list
    assert len(orders) == 5
    assert len(errors) == 2 and "价格不是数字" in errors[0] and "应该有 4 列" in errors[1]

    copies_sold = Counter(order.title for order in orders)
    assert copies_sold.most_common(1) == [("三体", 2)]

    books_by_customer = defaultdict(list)
    for order in orders:
        books_by_customer[order.customer].append(order.title)
    assert dict(books_by_customer) == {"Ann": ["三体", "活着", "围城"], "Bob": ["活着", "三体"]}

    spent = Counter()
    for order in orders:
        spent[order.customer] += order.price
    ranking = sorted(spent.items(), key=lambda item: (-item[1], item[0]))
    assert ranking == [("Ann", 122.5), ("Bob", 94.5)]

    sales_by_day = defaultdict(float)
    for order in orders:
        sales_by_day[order.day] += order.price
    days = sorted(sales_by_day)
    totals = list(accumulate(sales_by_day[day] for day in days))
    assert totals == [94.5, 130.0, 217.0]

    print("跳过的行：")
    for message in errors:
        print(f"  {message}")
    print("销量：", dict(copies_sold))
    for customer, amount in ranking:
        print(f"{customer:<4} 消费 ¥{amount:>7.2f}，买了 {'、'.join(books_by_customer[customer])}")
    for day, total in zip(days, totals):
        print(f"{day} 累计 ¥{total:.2f}")


if __name__ == "__main__":
    main()
