"""第 8 课：归并排序。讲解见 lessons/08-merge-sort.html

实际项目里排序用 sorted()（Timsort 就是归并 + 插入的改良版），合并多个有序序列用 heapq.merge，
见 examples/merge_sort_in_practice.py。这里自己手写，接口和它们一样：
- merge_sort(iterable, *, key=None, reverse=False) 和 sorted() 用法相同，返回新列表，不改输入。
- merge(left, right, *, key=None, reverse=False) 和 heapq.merge 用法相同（只合并两路），返回一个惰性迭代器，
  所以能直接合并两个很大的、已经排好序的文件，而不用先把它们读进内存。

规则：
- 不要用 sorted()、list.sort()、heapq，自己写。
- merge 只能用 iter() / next() 一个一个往前取，不要用下标，也不要用 pop(0)（它要挪动后面全部元素，是 O(n)）。
  这样传进来的是文件、生成器也能工作。
- 稳定：两边 key 相等时先取左边（left）的。reverse=True 时也一样。
- 和 heapq.merge 一样，merge 的 reverse=True 表示两路输入都是从大到小排好的，输出也从大到小。
- merge_sort 对每个元素只调用一次 key：先把每个元素和它的 key 配成一对，排序时比较 key，最后再把元素取出来。

写完后运行 uv run dsa/merge_sort.py，看端到端的例子是否和期望一致；再跑 uv run pytest tests/test_merge_sort.py。
"""

from collections.abc import Callable, Iterable, Iterator


def merge(left: Iterable, right: Iterable, *, key: Callable | None = None, reverse: bool = False) -> Iterator:
    """把两个已经有序的可迭代对象合并成一个有序的迭代器（用 yield 写）。

    相等时 left 的元素排在前面。一共 O(len(left) + len(right))，额外空间 O(1)。
    提示：各拿一个迭代器，手里各“攥着”一个当前元素；某一边取完了，用 yield from 把另一边剩下的全部交出去。
    """
    raise NotImplementedError


def merge_sort(iterable: Iterable, *, key: Callable | None = None, reverse: bool = False) -> list:
    """返回排好序的新列表，不修改输入。稳定（reverse=True 时也稳定）。和 sorted() 一样可以接收任何可迭代对象。

    时间 O(n log n)，额外空间 O(n)。key 对每个元素只调用一次。
    """
    raise NotImplementedError


def count_inversions(items: Iterable, *, key: Callable | None = None) -> int:
    """（进阶）数逆序对：有多少对 i < j 满足 key(items[i]) > key(items[j])。相等不算。

    用途：衡量两个排名有多不一样。把 B 的排名按 A 的顺序列出来，逆序对越多，两份排名越不一致。
    要求 O(n log n)：边归并边数。提示：合并时从右边取走一个元素，左边还没取的那些都比它大，各和它组成一个逆序对。
    """
    raise NotImplementedError


if __name__ == "__main__":
    import io

    def show(title, compute, expected):
        """运行一个例子，打印期望和实际结果。compute 是一个不带参数的函数。"""
        try:
            actual = compute()
        except NotImplementedError:
            print(f"[待实现] {title}\n    期望：{expected!r}")
            return
        verdict = "通过" if actual == expected else "不对"
        print(f"[{verdict}] {title}\n    期望：{expected!r}\n    实际：{actual!r}")

    # 端到端场景一：两台服务器的日志各自按时间排好序，合并成一份时间线。用 StringIO 模拟两个文件。
    server_a = io.StringIO("09:00 a 启动\n09:30 a 登录\n10:15 a 下单\n")
    server_b = io.StringIO("09:10 b 启动\n09:30 b 心跳\n11:00 b 退出\n")
    show("合并两个日志文件（同一时刻 a 在前）",
         lambda: [line.split()[1] + line.split()[0] for line in merge(server_a, server_b, key=lambda line: line[:5])],
         ["a09:00", "b09:10", "a09:30", "b09:30", "a10:15", "b11:00"])

    # 端到端场景二：商品按销量从高到低展示，销量相同保持上架顺序。
    products = [("鼠标", 120), ("键盘", 300), ("耳机", 120), ("显示器", 45), ("U 盘", 300)]
    show("merge_sort(products, key=销量, reverse=True)",
         lambda: [name for name, _ in merge_sort(products, key=lambda product: product[1], reverse=True)],
         ["键盘", "U 盘", "鼠标", "耳机", "显示器"])
    show("merge_sort 不改原列表", lambda: (merge_sort(products), products[0])[1], ("鼠标", 120))

    # 端到端场景三：两位评委给 5 部电影排名，评委 B 的名次按评委 A 的顺序列出来，逆序对越多分歧越大。
    show("两位评委排名的分歧（逆序对个数）", lambda: count_inversions([2, 1, 3, 5, 4]), 2)
