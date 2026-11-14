import heapq
import itertools
import random

import pytest

from dsa.heap import PriorityQueue, heapify, merge, nsmallest


def is_heap(items):
    """每个父亲都 <= 它的孩子。"""
    return all(items[(index - 1) // 2] <= items[index] for index in range(1, len(items)))


def drain(queue):
    result = []
    while queue:
        result.append(queue.pop())
    return result


def test_empty():
    queue = PriorityQueue()
    assert len(queue) == 0
    assert not queue
    with pytest.raises(IndexError):
        queue.pop()
    with pytest.raises(IndexError):
        queue.peek()


def test_push_peek():
    queue = PriorityQueue()
    for value in [5, 3, 8]:
        queue.push(value)
    assert queue.peek() == 3
    assert len(queue) == 3  # peek 不删除
    assert queue


def test_pop_in_order():
    queue = PriorityQueue()
    for value in [5, 3, 8, 1, 9, 2]:
        queue.push(value)
    assert drain(queue) == [1, 2, 3, 5, 8, 9]
    assert len(queue) == 0


def test_build_from_items():
    queue = PriorityQueue([9, 4, 7, 1, 8, 2])
    assert len(queue) == 6
    assert drain(queue) == [1, 2, 4, 7, 8, 9]


def test_pop_last_one_then_reuse():
    queue = PriorityQueue()
    queue.push(7)
    assert queue.pop() == 7
    assert not queue
    queue.push(4)
    assert queue.peek() == 4


def test_key_and_fifo_for_equal_priority():
    queue = PriorityQueue(key=lambda task: task["priority"])
    for name, priority in [("a", 2), ("b", 1), ("c", 2), ("d", 1), ("e", 2)]:
        queue.push({"name": name, "priority": priority})  # dict 本身不能比大小
    assert [task["name"] for task in drain(queue)] == ["b", "d", "a", "c", "e"]


def test_items_need_not_be_comparable():
    class Job:
        def __init__(self, cost):
            self.cost = cost

    jobs = [Job(3), Job(1), Job(3), Job(2)]
    queue = PriorityQueue(jobs, key=lambda job: job.cost)
    assert drain(queue) == [jobs[1], jobs[3], jobs[0], jobs[2]]


def test_internal_array_is_heap():
    queue = PriorityQueue()
    for value in [9, 4, 7, 1, 8, 2, 6, 3, 5]:
        queue.push(value)
        assert is_heap(queue._entries)
    queue.pop()
    assert is_heap(queue._entries)


def test_random_against_heapq():
    rng = random.Random(12)
    queue, model = PriorityQueue(), []
    for _ in range(500):
        if model and rng.random() < 0.4:
            assert queue.pop() == heapq.heappop(model)
        else:
            value = rng.randint(-50, 50)
            queue.push(value)
            heapq.heappush(model, value)
        assert len(queue) == len(model)


def test_heapify_in_place():
    items = [9, 4, 7, 1, 8, 2, 6, 3, 5]
    before = sorted(items)
    assert heapify(items) is None
    assert is_heap(items)
    assert sorted(items) == before
    assert items[0] == 1


@pytest.mark.parametrize("items", [[], [1], [2, 1], [3, 3, 3]])
def test_heapify_tiny(items):
    expected = sorted(items)
    heapify(items)
    assert is_heap(items) and sorted(items) == expected


def test_heapify_random():
    rng = random.Random(7)
    for size in range(30):
        items = [rng.randint(0, 20) for _ in range(size)]
        heapify(items)
        assert is_heap(items)


def test_nsmallest():
    assert nsmallest(3, [5, 1, 9, 3, 7]) == [1, 3, 5]
    assert nsmallest(10, [2, 1]) == [1, 2]
    assert nsmallest(0, [2, 1]) == []
    assert nsmallest(2, []) == []
    assert nsmallest(2, iter([4, 2, 3])) == [2, 3]  # 只能遍历一次的输入也行


def test_nsmallest_with_key_is_stable():
    pairs = [("a", 2), ("b", 1), ("c", 2), ("d", 1), ("e", 2)]
    assert nsmallest(3, pairs, key=lambda pair: pair[1]) == [("b", 1), ("d", 1), ("a", 2)]


def test_nsmallest_random_against_heapq():
    rng = random.Random(33)
    for _ in range(200):
        values = [rng.randint(0, 30) for _ in range(rng.randint(0, 40))]
        size = rng.randint(0, 10)
        assert nsmallest(size, values) == heapq.nsmallest(size, values)
        pairs = [(index, value) for index, value in enumerate(values)]
        key = lambda pair: pair[1]  # noqa: E731
        assert nsmallest(size, pairs, key=key) == heapq.nsmallest(size, pairs, key=key)


def test_merge():
    assert list(merge([1, 4, 7], [2, 5], [3, 6, 8])) == [1, 2, 3, 4, 5, 6, 7, 8]
    assert list(merge()) == []
    assert list(merge([], [1], [])) == [1]


def test_merge_equal_values_keep_input_order():
    first = [(1, "first")]
    second = [(1, "second")]
    merged = list(merge([1, 1], [1]))
    assert merged == [1, 1, 1]
    keyed = list(merge([(1, "a"), (2, "a")], [(1, "b")]))
    assert keyed == [(1, "a"), (1, "b"), (2, "a")]
    assert list(merge(first, second)) == [(1, "first"), (1, "second")]


def test_merge_is_lazy():
    """输入是无限生成器也能工作：说明 merge 没有先把输入全读进来。"""
    evens = itertools.count(0, 2)
    odds = itertools.count(1, 2)
    assert list(itertools.islice(merge(evens, odds), 6)) == [0, 1, 2, 3, 4, 5]


def test_merge_random_against_heapq():
    rng = random.Random(5)
    for _ in range(100):
        inputs = [sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 8))) for _ in range(rng.randint(0, 5))]
        assert list(merge(*inputs)) == list(heapq.merge(*inputs))
