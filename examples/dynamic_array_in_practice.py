"""第 1 课实战：Python 的 list 就是动态数组，日常怎么用才不踩坑。

按场景选：
1. 末尾追加、按下标读写 → list。append 均摊 O(1)，下标 O(1)。
2. 要在头部频繁增删（任务队列、最近 N 条记录）→ collections.deque。list.insert(0, x) / pop(0) 是 O(n)。
3. 先攒一批再一起处理 → 往 list 里 append，最后 "".join 或批量写入；不要在循环里 s += 拼字符串。

运行：uv run examples/dynamic_array_in_practice.py
"""

import sys
from collections import deque


def batches(rows: list, batch_size: int) -> list[list]:
    """把一批行按 batch_size 切成若干批，常用于“每 500 条写一次数据库”。切片是 O(k) 的拷贝。"""
    return [rows[start:start + batch_size] for start in range(0, len(rows), batch_size)]


def build_csv(rows: list[tuple[str, int]]) -> str:
    """先把每行 append 进 list，最后 join 一次：整体 O(总长度)。"""
    lines = ["name,score"]
    for name, score in rows:
        lines.append(f"{name},{score}")
    return "\n".join(lines)


def count_capacity_changes(count: int) -> int:
    """连续 append count 次，list 底层内存一共换了几次。sys.getsizeof 能看到预留空间的大小。"""
    numbers, changes, last_size = [], 0, sys.getsizeof([])
    for number in range(count):
        numbers.append(number)
        size = sys.getsizeof(numbers)
        if size != last_size:
            changes, last_size = changes + 1, size
    return changes


def main() -> None:
    rows = [(f"student{number}", 60 + number % 40) for number in range(1, 1201)]
    groups = batches(rows, 500)
    assert [len(group) for group in groups] == [500, 500, 200]
    print("每批条数：", [len(group) for group in groups])

    csv_text = build_csv(rows[:3])
    assert csv_text == "name,score\nstudent1,61\nstudent2,62\nstudent3,63"
    print(csv_text.replace("\n", " | "))

    changes = count_capacity_changes(10_000)
    assert changes < 100  # 按比例扩容，一万次 append 只搬几十次家
    print(f"append 10000 次，list 底层只扩容了 {changes} 次")

    # 头部频繁进出：用 deque，不用 list
    recent_pages: deque[str] = deque(maxlen=3)  # 只保留最近 3 条，满了自动从另一头挤掉
    for page in ["首页", "搜索", "商品", "购物车", "结算"]:
        recent_pages.append(page)
    assert list(recent_pages) == ["商品", "购物车", "结算"]
    print("最近访问：", list(recent_pages))


if __name__ == "__main__":
    main()
