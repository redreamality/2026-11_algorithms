"""第 33 课：堆与 Top K。讲解见 lessons/33-top-k.html

规则：
- 第 12 课已经手写过堆，这一课可以直接用标准库 heapq：
  heapq.heappush(heap, item)、heapq.heappop(heap)、heap[0]（看堆顶不弹出）、heapq.heapify(list)。
- heapq 只有最小堆。需要最大堆时，存相反数：放进去 -num，取出来再取反。
- 不要用 sorted / list.sort 把全部数据排序来“偷懒”，也不要用 heapq.nlargest / nsmallest，
  这一课练的就是自己维护一个大小为 k 的堆。（统计频率可以用 dict 或 collections.Counter。）
- 文件里的 ListNode、build_linked_list、linked_list_to_list 是工具函数，已经写好，不是练习。
- 自查：uv run dsa/top_k.py ，会打印每道题的「输入、期望、实际」。
"""

import heapq  # noqa: F401  练习里会用到


class ListNode:
    def __init__(self, val, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next


# ---------- 工具函数（已经写好，直接用） ----------

def build_linked_list(values: list) -> ListNode | None:
    """[1, 4, 5] → 1 -> 4 -> 5，返回头节点。空列表返回 None。"""
    dummy_head = ListNode(None)
    tail = dummy_head
    for value in values:
        tail.next = ListNode(value)
        tail = tail.next
    return dummy_head.next


def linked_list_to_list(head: ListNode | None) -> list:
    """1 -> 4 -> 5 → [1, 4, 5]。"""
    values = []
    while head is not None:
        values.append(head.val)
        head = head.next
    return values


# ---------- 练习 ----------

def kth_largest(nums: list[int], k: int) -> int:
    """LeetCode 215 · 数组中的第 K 个最大元素。

    题意：返回 nums 排好序之后从大往小数的第 k 个数（重复的数分别计数）。1 <= k <= len(nums)。
    例子：nums = [3, 2, 1, 5, 6, 4]，k = 2 → 5；nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]，k = 4 → 4。

    思路：维护一个最多放 k 个数的最小堆 min_heap_of_k_largest，它装着“目前见过的最大的 k 个数”。
    每来一个数就放进去；放进去后如果超过 k 个，就把堆顶（这 k + 1 个里最小的）弹出。
    全部处理完，堆顶就是这 k 个最大数里最小的那个，也就是第 k 大。
    目标：时间 O(n log k)，额外空间 O(k)。
    """
    raise NotImplementedError


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """LeetCode 347 · 前 K 个高频元素。

    题意：返回出现次数最多的 k 个数，顺序随意。题目保证答案唯一。
    例子：nums = [1, 1, 1, 2, 2, 3]，k = 2 → [1, 2]。

    思路：先用字典统计每个数出现几次（count_of_number）。
    再像 kth_largest 一样维护一个大小为 k 的最小堆，堆里放 (出现次数, 数)，
    按出现次数比较；超过 k 个就弹出次数最少的。最后堆里剩下的就是答案。
    目标：时间 O(n log k)，额外空间 O(n)（字典）。
    """
    raise NotImplementedError


def merge_k_sorted_lists(lists: list[ListNode | None]) -> ListNode | None:
    """LeetCode 23 · 合并 K 个升序链表。

    题意：lists 里有 k 个各自升序的链表（有的可能是空链表 None），合并成一个升序链表，返回头节点。
    例子：[1->4->5, 1->3->4, 2->6] → 1->1->2->3->4->4->5->6。

    思路：最小堆里同时只放“每个链表当前的第一个节点”，最多 k 个。
    每次弹出最小的那个节点接到结果末尾，再把它的下一个节点（如果有）放进堆。
    注意：堆里放 (节点值, 链表编号, 节点)。值相等时 heapq 会接着比较第二项；
    如果第二项直接是节点，ListNode 之间不能比较大小，会报 TypeError。加一个编号就不会比到节点。
    提示：用一个哑节点 dummy_head 当结果链表的开头，最后返回 dummy_head.next。
    目标：时间 O(N log k)，N 是所有链表的节点总数；额外空间 O(k)。
    """
    raise NotImplementedError


class MedianFinder:
    """LeetCode 295 · 数据流的中位数。

    题意：数一个一个地到来，随时可能被问“目前所有数的中位数是多少”。
    个数为奇数时，中位数是排序后正中间的那个；为偶数时，是中间两个的平均值。
    例子：依次加入 1、2 后中位数是 1.5；再加入 3 后中位数是 2。

    思路：把所有数分成两半，用两个堆存：
    - max_heap_of_smaller_half：较小的一半，大顶堆（heapq 里存相反数），堆顶是这一半的最大值；
    - min_heap_of_larger_half：较大的一半，小顶堆，堆顶是这一半的最小值。
    时刻保持两个条件：① 较小一半的每个数都 <= 较大一半的每个数；
    ② 较小一半的个数等于较大一半，或者正好多 1 个。
    这样中位数只和两个堆顶有关。

    add_number(num) 的一种写法（三步）：
    1. 先把 num 放进较小的一半；
    2. 再把较小一半的最大值弹出，放进较大的一半（保证条件 ①）；
    3. 如果较大的一半比较小的一半多了，把较大一半的最小值弹出，放回较小的一半（保证条件 ②）。
    目标：add_number O(log n)，find_median O(1)。
    """

    def __init__(self) -> None:
        """建两个空堆：self.max_heap_of_smaller_half 和 self.min_heap_of_larger_half。"""
        raise NotImplementedError

    def add_number(self, num: int) -> None:
        """加入一个数。O(log n)。"""
        raise NotImplementedError

    def find_median(self) -> float:
        """返回目前所有数的中位数（float）。至少加入过一个数才会调用。O(1)。"""
        raise NotImplementedError


# ---------- 自查 ----------

def report_case(title: str, input_text: str, expected, compute) -> None:
    try:
        actual = compute()
    except NotImplementedError:
        print(f"[还没实现] {title}  输入：{input_text}  期望：{expected}")
        return
    verdict = "通过" if actual == expected else "不对"
    print(f"[{verdict}] {title}  输入：{input_text}  期望：{expected}  实际：{actual}")


def medians_after_each_add(stream: list[int]) -> list[float]:
    median_finder = MedianFinder()
    medians = []
    for num in stream:
        median_finder.add_number(num)
        medians.append(median_finder.find_median())
    return medians


if __name__ == "__main__":
    for nums, k, expected in [
        ([3, 2, 1, 5, 6, 4], 2, 5), ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, 4), ([1], 1, 1), ([7, 7, 7], 2, 7), ([2, 1], 2, 1),
    ]:
        report_case("kth_largest", f"nums={nums}, k={k}", expected, lambda: kth_largest(nums, k))

    # 顺序随意，所以排好序再比较
    for nums, k, expected in [([1, 1, 1, 2, 2, 3], 2, [1, 2]), ([1], 1, [1]), ([4, 4, 5, 5, 5, 6, 6, 6, 6], 2, [5, 6])]:
        report_case("top_k_frequent", f"nums={nums}, k={k}（结果排序后比较）", expected,
                    lambda: sorted(top_k_frequent(nums, k)))

    for lists, expected in [
        ([[1, 4, 5], [1, 3, 4], [2, 6]], [1, 1, 2, 3, 4, 4, 5, 6]), ([], []), ([[]], []), ([[2], [], [1]], [1, 2]),
    ]:
        report_case("merge_k_sorted_lists", str(lists), expected,
                    lambda: linked_list_to_list(merge_k_sorted_lists([build_linked_list(values) for values in lists])))

    for stream, expected in [
        ([5, 15, 1, 3, 8, 7, 9, 10], [5.0, 10.0, 5.0, 4.0, 5.0, 6.0, 7.0, 7.5]),
        ([1, 2, 3], [1.0, 1.5, 2.0]),
        ([-1, -2, -3], [-1.0, -1.5, -2.0]),
    ]:
        report_case("MedianFinder", f"依次加入 {stream}，每次加入后的中位数", expected,
                    lambda: medians_after_each_add(stream))
