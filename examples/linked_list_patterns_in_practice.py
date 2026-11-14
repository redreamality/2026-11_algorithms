"""第 29 课实战：Python 业务代码里几乎不手写链表，那链表技巧用在哪？

1. 存一串数据 → list；两头都要进出（队列、撤销栈、最近 N 条）→ collections.deque。不要手写 ListNode。
2. “按 next 指针走”的结构其实到处都有，只是不叫链表：
   - 数据库里的上级关系（员工 → 经理 → 总监）、分类的 parent_id；
   - 重定向链（短链接 → 中间跳转 → 最终地址）；
   - 一个 dict：key → 下一个 key。
   这时“判断有没有环”就是真需求：配置错了会让重定向或上级链无限循环。
   用快慢指针判环只要 O(1) 额外空间；数据不大时用 set 记走过的节点更直白。
3. 反转、合并有序序列 → reversed(items)、heapq.merge，不手写。

运行：uv run examples/linked_list_patterns_in_practice.py
"""

import heapq
from collections import deque


def follow_redirects(redirects: dict[str, str], start: str) -> list[str]:
    """场景一：短链接跳转，一路跟着走到底，返回走过的路径。发现环就抛 ValueError。

    用 set 记走过的地址：最直白，额外空间 O(路径长度)。
    """
    path, seen = [start], {start}
    while path[-1] in redirects:
        next_url = redirects[path[-1]]
        if next_url in seen:
            raise ValueError(f"重定向成环：{' → '.join(path + [next_url])}")
        path.append(next_url)
        seen.add(next_url)
    return path


def reporting_chain_has_cycle(manager_of: dict[str, str], employee: str) -> bool:
    """场景二：员工 → 经理 → …… 的上级链有没有环。数据可能很大，用快慢指针，额外空间 O(1)。"""
    slow = fast = employee
    while fast in manager_of and manager_of[fast] in manager_of:
        slow = manager_of[slow]  # 走一步
        fast = manager_of[manager_of[fast]]  # 走两步
        if slow == fast:
            return True
    return False


def main() -> None:
    redirects = {"s.cn/a": "s.cn/b", "s.cn/b": "example.com/final"}
    assert follow_redirects(redirects, "s.cn/a") == ["s.cn/a", "s.cn/b", "example.com/final"]
    print("跳转路径：", " → ".join(follow_redirects(redirects, "s.cn/a")))

    broken = {"x": "y", "y": "z", "z": "x"}
    try:
        follow_redirects(broken, "x")
        raise AssertionError("应该发现环")
    except ValueError as error:
        print(error)

    manager_of = {"小王": "老李", "老李": "张总", "张总": "董事长"}
    assert not reporting_chain_has_cycle(manager_of, "小王")
    manager_of["董事长"] = "老李"  # 录错数据：董事长的上级成了老李
    assert reporting_chain_has_cycle(manager_of, "小王")
    print("上级链录错以后能发现环：", reporting_chain_has_cycle(manager_of, "小王"))

    undo_history = deque(maxlen=3)  # 撤销栈：只留最近 3 步，两头进出 O(1)
    for action in ["输入 a", "输入 b", "删除", "粘贴"]:
        undo_history.append(action)
    assert undo_history.pop() == "粘贴"
    assert list(undo_history) == ["输入 b", "删除"]
    print("撤销一步后的历史：", list(undo_history))

    assert list(reversed([1, 2, 3])) == [3, 2, 1]
    assert list(heapq.merge([1, 4, 9], [2, 3, 10])) == [1, 2, 3, 4, 9, 10]
    print("反转、合并有序序列都用标准库：", list(heapq.merge([1, 4, 9], [2, 3, 10])))


if __name__ == "__main__":
    main()
