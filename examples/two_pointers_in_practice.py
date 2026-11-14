"""第 25 课实战：双指针在真实代码里出现在哪。

业务代码里很少写“对撞指针找两数之和”，但这两类需求天天有：
1. 合并两份已经排好序的数据（两个按时间排序的日志、两页按价格排序的结果）→ 标准库 heapq.merge，
   内部就是“每份数据一个指针，每次取较小的那个往前走”，O(n + m)，还不用把数据全读进内存。
   两份数据要“对齐”（找出两边都有的、只有一边有的）时，才需要手写双指针。
2. 原地去掉不要的元素（快慢指针）→ Python 里一般直接写列表推导式生成新列表，
   保持顺序的去重用 dict.fromkeys。只有数据大到不能复制一份时，才原地用快慢指针。

运行：uv run examples/two_pointers_in_practice.py
"""

import heapq


def merge_logs(server_a: list[tuple[int, str]], server_b: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """场景一：两台服务器的日志各自按时间戳排好序，合成一份按时间排序的日志。"""
    return list(heapq.merge(server_a, server_b))


def reconcile(ledger_ids: list[int], bank_ids: list[int]) -> tuple[list[int], list[int], list[int]]:
    """场景二：对账。两份流水号都从小到大排好序，找出两边都有的、只在账本里的、只在银行里的。

    heapq.merge 只会合并，不会对齐，这里手写同向双指针：哪边小就说明它在另一边找不到，记下来往前走。
    时间 O(n + m)。用 set 也能做，但结果要再排序，而且要额外存一份。
    """
    matched, ledger_only, bank_only = [], [], []
    ledger_index = bank_index = 0
    while ledger_index < len(ledger_ids) and bank_index < len(bank_ids):
        ledger_id, bank_id = ledger_ids[ledger_index], bank_ids[bank_index]
        if ledger_id == bank_id:
            matched.append(ledger_id)
            ledger_index += 1
            bank_index += 1
        elif ledger_id < bank_id:
            ledger_only.append(ledger_id)
            ledger_index += 1
        else:
            bank_only.append(bank_id)
            bank_index += 1
    ledger_only.extend(ledger_ids[ledger_index:])
    bank_only.extend(bank_ids[bank_index:])
    return matched, ledger_only, bank_only


def compact_readings(readings: list[float | None]) -> None:
    """场景三：传感器读数里有 None（丢包），原地删掉，保持顺序。

    快慢指针：fast 扫描每个读数，slow 指向下一个有效读数该放的位置，最后截掉尾巴。
    数据不大时直接写 readings[:] = [value for value in readings if value is not None] 更清楚。
    """
    slow = 0
    for fast in range(len(readings)):
        if readings[fast] is not None:
            readings[slow] = readings[fast]
            slow += 1
    del readings[slow:]


def main() -> None:
    server_a = [(100, "a: 登录"), (105, "a: 下单"), (120, "a: 退出")]
    server_b = [(101, "b: 登录"), (130, "b: 支付")]
    merged = merge_logs(server_a, server_b)
    assert [timestamp for timestamp, _ in merged] == [100, 101, 105, 120, 130]
    print("合并后的日志：", [message for _, message in merged])

    matched, ledger_only, bank_only = reconcile([1001, 1002, 1004, 1007], [1001, 1003, 1004, 1008])
    assert matched == [1001, 1004]
    assert ledger_only == [1002, 1007]
    assert bank_only == [1003, 1008]
    print("对上的：", matched, "账本多出：", ledger_only, "银行多出：", bank_only)

    readings = [20.5, None, 21.0, None, None, 22.3]
    compact_readings(readings)
    assert readings == [20.5, 21.0, 22.3]
    print("去掉丢包后的读数：", readings)

    tags = ["python", "sql", "python", "go", "sql"]
    unique_tags = list(dict.fromkeys(tags))  # 保持第一次出现的顺序去重，不需要手写双指针
    assert unique_tags == ["python", "sql", "go"]
    print("去重后的标签：", unique_tags)


if __name__ == "__main__":
    main()
