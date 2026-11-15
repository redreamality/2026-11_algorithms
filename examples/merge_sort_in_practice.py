"""第 8 课实战：Python 项目里“归并”真正是怎么用的。

排序本身直接用 sorted()，它的 Timsort 就是归并排序的改良版。归并的思想真正要自己用的地方是“合并有序数据”：
1. 多个已经有序的序列（各服务器的日志、各分片的查询结果）→ heapq.merge，惰性、不用全读进内存。
   用法：把任意多个已排好序的序列传给它（可加 key=、reverse=True），它按序逐个产出。内部用堆实现（第 12 课讲），这里只当现成工具用。
2. 数据大到内存放不下 → 外部排序：切块，每块用 sorted 排好写到临时文件，再 heapq.merge 合起来。
3. 只是把两个小列表合并后排序 → sorted(a + b) 最省事，Timsort 能识别出两段有序区，接近 O(n)。

运行：uv run examples/merge_sort_in_practice.py
"""

import heapq
import io
import itertools
import random
import tempfile
from pathlib import Path


def merged_timeline(*log_files) -> list[str]:
    """场景一：几台服务器的日志各自按时间有序，合成一份时间线。每行开头 5 个字符是时间。"""
    return [line.rstrip("\n") for line in heapq.merge(*log_files, key=lambda line: line[:5])]


def external_sort(numbers, chunk_size: int, work_folder: Path) -> list[int]:
    """场景二：外部排序。假装内存一次只放得下 chunk_size 个数。"""
    chunk_files = []
    iterator = iter(numbers)
    chunk_number = 0
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if not chunk:
            break
        path = work_folder / f"chunk_{chunk_number}.txt"
        path.write_text("".join(f"{value}\n" for value in sorted(chunk)), encoding="utf-8")
        chunk_files.append(path)
        chunk_number += 1
    handles = [path.open(encoding="utf-8") for path in chunk_files]
    try:
        return [int(line) for line in heapq.merge(*handles, key=int)]  # 每个文件同时只读一行
    finally:
        for handle in handles:
            handle.close()


def main() -> None:
    server_a = io.StringIO("09:00 a 启动\n09:30 a 登录\n10:15 a 下单\n")
    server_b = io.StringIO("09:10 b 启动\n09:30 b 心跳\n11:00 b 退出\n")
    timeline = merged_timeline(server_a, server_b)
    assert [line[:7] for line in timeline] == ["09:00 a", "09:10 b", "09:30 a", "09:30 b", "10:15 a", "11:00 b"]
    print("合并后的时间线：")
    for line in timeline:
        print("   ", line)

    random.seed(8)  # 固定随机种子，每次运行生成同一批数
    numbers = [random.randint(0, 10_000) for _ in range(1_000)]
    with tempfile.TemporaryDirectory() as folder:
        result = external_sort(numbers, chunk_size=128, work_folder=Path(folder))
        chunk_count = len(list(Path(folder).glob("chunk_*.txt")))
    assert result == sorted(numbers)
    print(f"外部排序：1000 个数切成 {chunk_count} 块，归并后前 5 个是 {result[:5]}")

    page_one, page_two = [3, 8, 15], [1, 9, 20]
    assert sorted(page_one + page_two) == [1, 3, 8, 9, 15, 20]
    assert list(heapq.merge([9, 5], [8, 2], reverse=True)) == [9, 8, 5, 2]  # 两路都从大到小时加 reverse=True
    print("两个小列表直接 sorted(a + b)：", sorted(page_one + page_two))


if __name__ == "__main__":
    main()
