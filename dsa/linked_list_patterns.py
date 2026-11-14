"""第 29 课：链表高频技巧。讲解见 lessons/29-linked-list-patterns.html

规则：
- 只改节点的 next 指针，不要把链表倒进 Python list 里处理完再建一条新链表
  （那样空间是 O(n)，也练不到指针操作）。每道题的额外空间都应该是 O(1)。
- 改指针之前，先想清楚“改完之后，谁会因此找不到”，需要的话先用一个变量记住它。
- 头节点可能被删掉或换掉的题，先在 head 前面放一个哑节点：dummy_node = ListNode(0, head)，
  最后返回 dummy_node.next。
- 下面的 ListNode、build_linked_list、linked_list_to_list、build_linked_list_with_cycle
  是写好的小工具，不是练习，直接用就行。

自查：在项目目录运行 uv run dsa/linked_list_patterns.py，会逐个打印“输入、期望、实际”。
"""


class ListNode:
    def __init__(self, value, next: "ListNode | None" = None) -> None:
        self.value = value
        self.next = next

    def __repr__(self) -> str:
        return f"ListNode({self.value!r})"


# ---------- 写好的小工具（不是练习） ----------

def build_linked_list(values: list) -> ListNode | None:
    """把 [1, 2, 3] 变成链表 1 → 2 → 3，返回头节点；空列表返回 None。"""
    dummy_node = ListNode(None)
    tail_node = dummy_node
    for value in values:
        tail_node.next = ListNode(value)
        tail_node = tail_node.next
    return dummy_node.next


def linked_list_to_list(head: ListNode | None, max_length: int = 10_000) -> list:
    """把链表 1 → 2 → 3 变回 [1, 2, 3]。

    如果走了 max_length 步还没走到 None，说明链表可能有环，抛 ValueError，免得死循环。
    """
    values = []
    current_node = head
    while current_node is not None:
        if len(values) >= max_length:
            raise ValueError("链表太长，可能有环")
        values.append(current_node.value)
        current_node = current_node.next
    return values


def build_linked_list_with_cycle(values: list, cycle_entry_index: int) -> ListNode | None:
    """建一条可能带环的链表：最后一个节点的 next 指回下标为 cycle_entry_index 的节点。

    cycle_entry_index 为 -1 表示没有环。例如 values = [1, 2, 3, 4]、cycle_entry_index = 1，
    得到 1 → 2 → 3 → 4 → 2 → 3 → 4 → ……（入环点是值为 2 的节点）。
    """
    head = build_linked_list(values)
    if head is None or cycle_entry_index < 0:
        return head
    entry_node = None
    current_node = head
    index = 0
    while True:
        if index == cycle_entry_index:
            entry_node = current_node
        if current_node.next is None:
            break
        current_node = current_node.next
        index += 1
    current_node.next = entry_node
    return head


# ---------- 练习 ----------

def reverse_list(head: ListNode | None) -> ListNode | None:
    """LeetCode 206 反转链表。原地反转，返回新的头节点。

    例子：1 → 2 → 3 → 4 → 5  变成  5 → 4 → 3 → 2 → 1。空链表返回 None。

    思路提示：用三个变量 previous_node、current_node、next_node。
    开始时 previous_node = None，current_node = head。每一轮：
    先用 next_node 记住 current_node.next，再让 current_node.next = previous_node（掉头），
    最后 previous_node 和 current_node 都往前挪一个。current_node 变成 None 时，
    previous_node 就是新的头。

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


def merge_two_sorted_lists(first_head: ListNode | None, second_head: ListNode | None) -> ListNode | None:
    """LeetCode 21 合并两个有序链表。

    两条链表都已经从小到大排好序，把它们合并成一条从小到大的链表并返回头节点。
    直接复用原来的节点（改 next 指针），不要新建值节点。

    例子：1 → 2 → 4 和 1 → 3 → 4  合并成  1 → 1 → 2 → 3 → 4 → 4。

    思路提示：建一个哑节点 dummy_node，再用 tail_node 指向“结果链表的最后一个节点”。
    每次比较两条链表当前的头，把较小的那个接到 tail_node 后面，tail_node 和被取走的那条链表各前进一步。
    有一条走完了，就把另一条剩下的部分整个接上。返回 dummy_node.next。

    目标复杂度：时间 O(m + n)，额外空间 O(1)。
    """
    raise NotImplementedError


def middle_node(head: ListNode | None) -> ListNode | None:
    """LeetCode 876 链表的中间结点。

    返回中间那个节点。节点数是偶数时有两个中间节点，返回第二个。

    例子：1 → 2 → 3 → 4 → 5 返回值为 3 的节点；1 → 2 → 3 → 4 → 5 → 6 返回值为 4 的节点。

    思路提示：快慢指针。slow 每次走 1 步，fast 每次走 2 步，都从 head 出发。
    循环条件是 fast is not None and fast.next is not None。fast 走到头时，slow 正好在中间。

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


def has_cycle(head: ListNode | None) -> bool:
    """LeetCode 141 环形链表。判断链表里有没有环。

    例子：1 → 2 → 3 → 4 → (回到 2) 有环，返回 True；1 → 2 → 3 → None 没有环，返回 False。

    思路提示：快慢指针。slow 每次走 1 步，fast 每次走 2 步。
    有环的话，两个指针最后都会进到环里绕圈，fast 每一步都比 slow 多走 1 步，迟早追上（相遇）；
    没有环的话，fast 会先走到 None。

    目标复杂度：时间 O(n)，额外空间 O(1)。不要用集合记录走过的节点（那是 O(n) 空间）。
    """
    raise NotImplementedError


def find_cycle_entry(head: ListNode | None) -> ListNode | None:
    """LeetCode 142 环形链表 II。返回链表开始入环的第一个节点；没有环返回 None。

    例子：1 → 2 → 3 → 4 → 5 → 6 → (回到 3)，返回值为 3 的节点。

    思路提示：分两个阶段。
    第一阶段和 has_cycle 一样，找到 slow 和 fast 的相遇点 meeting_node（没相遇就是无环）。
    第二阶段：一个指针从 head 出发，另一个从 meeting_node 出发，都每次走 1 步，
    它们相遇的那个节点就是入环点。讲解页里有为什么成立的推导。

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    """LeetCode 19 删除链表的倒数第 N 个结点。返回删除后的头节点。保证 1 <= n <= 链表长度。

    例子：1 → 2 → 3 → 4 → 5，n = 2，删掉 4，得到 1 → 2 → 3 → 5。
          1 → 2，n = 2，删掉的是头节点，得到 2。

    思路提示：在 head 前面放哑节点 dummy_node，ahead 和 behind 都从 dummy_node 出发。
    ahead 先走 n 步，然后两个一起走，直到 ahead.next 是 None。
    这时 behind 停在“倒数第 n 个节点的前一个”，执行 behind.next = behind.next.next 即可。
    最后返回 dummy_node.next（不能返回 head，因为 head 可能刚被删掉）。

    目标复杂度：只遍历一遍，时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


def is_palindrome(head: ListNode | None) -> bool:
    """LeetCode 234 回文链表（综合题：找中点 + 反转）。

    从前往后读和从后往前读一样，就是回文。空链表和只有一个节点的链表都算回文。

    例子：1 → 2 → 2 → 1 返回 True；1 → 2 → 3 返回 False。

    思路提示：用快慢指针找到中点，把后半段反转，然后一个指针从 head、一个从反转后的后半段头部出发，
    逐个比较值。（做完后可以把后半段再反转回去，恢复原链表，这是好习惯。）

    目标复杂度：时间 O(n)，额外空间 O(1)。
    """
    raise NotImplementedError


if __name__ == "__main__":
    def check(description, compute, expected):
        try:
            actual = compute()
        except NotImplementedError:
            actual = "还没实现"
        verdict = "[对]" if actual == expected else "[错]"
        print(f"{verdict} {description}")
        print(f"    期望：{expected!r}")
        print(f"    实际：{actual!r}")

    def value_or_none(node):
        return None if node is None else node.value

    for values in ([1, 2, 3, 4, 5], [1, 2], [7], []):
        check(f"reverse_list({values})",
              lambda: linked_list_to_list(reverse_list(build_linked_list(values))), values[::-1])

    for first_values, second_values, expected in (
        ([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]),
        ([], [0], [0]),
        ([], [], []),
        ([5, 6], [1, 2, 3], [1, 2, 3, 5, 6]),
    ):
        check(f"merge_two_sorted_lists({first_values}, {second_values})",
              lambda: linked_list_to_list(merge_two_sorted_lists(
                  build_linked_list(first_values), build_linked_list(second_values))), expected)

    for values, expected in (([1, 2, 3, 4, 5], 3), ([1, 2, 3, 4, 5, 6], 4), ([1], 1)):
        check(f"middle_node({values}) 的值",
              lambda: value_or_none(middle_node(build_linked_list(values))), expected)

    for values, entry_index, expected in (
        ([3, 2, 0, -4], 1, True), ([1, 2], 0, True), ([1], -1, False), ([1, 2, 3], -1, False), ([], -1, False),
    ):
        check(f"has_cycle({values}，尾巴指回下标 {entry_index})",
              lambda: has_cycle(build_linked_list_with_cycle(values, entry_index)), expected)

    for values, entry_index, expected in (
        ([1, 2, 3, 4, 5, 6], 2, 3), ([3, 2, 0, -4], 1, 2), ([1, 2], 0, 1), ([1], 0, 1), ([1, 2, 3], -1, None),
    ):
        check(f"find_cycle_entry({values}，尾巴指回下标 {entry_index}) 的值",
              lambda: value_or_none(find_cycle_entry(build_linked_list_with_cycle(values, entry_index))), expected)

    for values, n, expected in (
        ([1, 2, 3, 4, 5], 2, [1, 2, 3, 5]), ([1, 2], 2, [2]), ([1, 2], 1, [1]), ([1], 1, []),
    ):
        check(f"remove_nth_from_end({values}, n={n})",
              lambda: linked_list_to_list(remove_nth_from_end(build_linked_list(values), n)), expected)

    for values, expected in (([1, 2, 2, 1], True), ([1, 2, 3, 2, 1], True), ([1, 2, 3], False), ([1, 2], False), ([], True)):
        check(f"is_palindrome({values})", lambda: is_palindrome(build_linked_list(values)), expected)
