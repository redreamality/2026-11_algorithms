"""第 9 课：快速排序。讲解见 lessons/09-quick-sort.html

实际项目里排序用 sorted() / list.sort()；“第 k 小 / 中位数 / 前几名”用 statistics.median；前几名用 sorted(...)[:k] 先排再切，
见 examples/quick_sort_in_practice.py。这里自己手写：
- quick_sort(items, *, key=None, reverse=False)：用法和 list.sort 一样，原地排序、返回 None（但不稳定）。
- select(iterable, k, *, key=None)：第 k 小的元素，不排序整个数组，平均 O(n)。拿来算中位数、P95 延迟。

规则：
- 不要用 sorted()、list.sort()、heapq、statistics，自己写。
- partition 用 Lomuto 写法：基准取 items[high]，boundary 标出“小于区”的右边界，scan 从左往右扫。
  只在 items 里交换元素，不新建列表；递归时传下标 low、high，不要切片。
- quick_sort 每次分区前随机挑一个元素和 items[high] 交换，避免有序输入退化成 O(n²)。
- 和 list.sort 一样，key 对每个元素只调用一次。做法：先建一个 (key, 原下标) 的列表，对它原地快排
  （原下标各不相同，所以永远不会去比较元素本身），排完再按原下标把元素重新排回 items。
- select 不修改传进来的数据：先 list(iterable) 复制一份，在副本上分区。
- 签名里的裸 `*`（如 *, key=None, reverse=False）：它后面的参数只能按关键字传（key=...），不能按位置传。

写完后运行 uv run dsa/quick_sort.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_quick_sort.py。
"""

from collections.abc import Callable, Iterable


def partition(items: list, low: int, high: int) -> int:
    """以 items[high] 为基准，原地分区 items[low..high]（两端都包含），返回基准最终的下标 pivot_index。

    分完之后：items[low..pivot_index-1] 都 <= 基准，items[pivot_index+1..high] 都 >= 基准。
    low..high 以外的元素不能动。O(high - low)。
    """
    raise NotImplementedError


def quick_sort(items: list, *, key: Callable | None = None, reverse: bool = False) -> None:
    """原地把 items 排好，返回 None。不稳定。reverse=True 时从大到小。

    用随机基准：平均 O(n log n)，最坏 O(n²)（几乎碰不到；大量相同元素时 Lomuto 仍会变慢，本课不要求处理）。
    额外空间：递归栈 O(log n)；给了 key 时还要 O(n) 存 (key, 原下标)。
    """
    raise NotImplementedError


def select(iterable: Iterable, k: int, *, key: Callable | None = None):
    """返回第 k 小的元素（k 从 0 开始，即 sorted(iterable, key=key)[k]）。不修改输入。

    k 不在 0..n-1 范围内时抛 IndexError，和 sorted(...)[k] 越界一样（但这里负数也算越界）。
    思路：分区后基准落在 pivot_index。等于 k 就找到了；k 更小只去左边找，否则只去右边找。
    平均 O(n)：每次只往一边走。也用随机基准。
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

    # 端到端场景一：接口 20 次请求的耗时（毫秒），看中位数和 P95。
    latencies = [120, 85, 90, 3000, 95, 110, 88, 92, 101, 99, 87, 105, 93, 97, 89, 115, 91, 94, 96, 1500]
    show("耗时中位数（偏低的那个）：select(latencies, (20 - 1) // 2)",
         lambda: select(latencies, (len(latencies) - 1) // 2), 95)
    show("P95 耗时：第 ceil(0.95 × 20) - 1 = 18 小的", lambda: select(latencies, 18), 1500)
    show("select 不改输入", lambda: (select(latencies, 0), latencies[:3])[1], [120, 85, 90])

    # 端到端场景二：最便宜的商品，不用把整个列表排一遍。
    products = [("显示器", 899), ("鼠标", 59), ("键盘", 199), ("耳机", 59.5)]
    show("第 0 便宜的商品", lambda: select(products, 0, key=lambda product: product[1]), ("鼠标", 59))

    # 端到端场景三：排行榜按分数从高到低，就地排序。
    def leaderboard():
        players = [("小红", 88), ("小明", 95), ("小刚", 72), ("小李", 99)]
        quick_sort(players, key=lambda player: player[1], reverse=True)
        return [name for name, _ in players]

    show("quick_sort(players, key=分数, reverse=True)", leaderboard, ["小李", "小明", "小红", "小刚"])
