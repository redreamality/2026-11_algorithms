"""第 9 课实战：Python 项目里“快排 / 快速选择”对应的东西真正怎么写。

Python 的 sorted() 是 Timsort，不是快排；但快排的“分区”思想解决的问题，标准库都有现成的：
1. 排序 → sorted() / list.sort()。
2. 中位数、分位数（P95 延迟）→ statistics.median / statistics.quantiles。
3. 前 k 名、后 k 名（k 远小于 n）→ heapq.nlargest / nsmallest，O(n log k)。
4. 只要第 k 小的一个值、数据量大 → 自己写 quickselect，平均 O(n)；或者装 numpy 用 numpy.partition。

运行：uv run examples/quick_sort_in_practice.py
"""

import heapq
import statistics


def latency_report(latencies_ms: list[float]) -> dict[str, float]:
    """场景一：接口耗时报告。median 抗极端值，P95 看“大多数用户最慢会遇到多慢”。"""
    percentiles = statistics.quantiles(latencies_ms, n=100, method="inclusive")  # 99 个切分点
    return {
        "mean": round(statistics.fmean(latencies_ms), 1),
        "median": statistics.median(latencies_ms),
        "p95": round(percentiles[94], 1),
    }


def top_sellers(sales: dict[str, int], count: int) -> list[str]:
    """场景二：销量前几名。只要前 count 个时，nlargest 比整个排序省。"""
    return heapq.nlargest(count, sales, key=sales.__getitem__)


def main() -> None:
    latencies = [120, 85, 90, 3000, 95, 110, 88, 92, 101, 99, 87, 105, 93, 97, 89, 115, 91, 94, 96, 1500]
    report = latency_report(latencies)
    assert report["median"] == 95.5
    assert report["mean"] > 300  # 两个极端值把平均数拉得很高，所以看中位数
    assert report["p95"] == 1575.0
    print("耗时报告：", report)

    sales = {"鼠标": 520, "键盘": 310, "耳机": 880, "显示器": 95, "U 盘": 610}
    assert top_sellers(sales, 3) == ["耳机", "U 盘", "鼠标"]
    print("销量前三：", top_sellers(sales, 3))

    cheapest_two = heapq.nsmallest(2, [("显示器", 899), ("鼠标", 59), ("键盘", 199)], key=lambda item: item[1])
    assert [name for name, _ in cheapest_two] == ["鼠标", "键盘"]
    print("最便宜的两个：", cheapest_two)

    players = [("小红", 88), ("小明", 95), ("小刚", 72)]
    players.sort(key=lambda player: player[1], reverse=True)
    assert players[0][0] == "小明"
    print("排行榜：", players)


if __name__ == "__main__":
    main()
