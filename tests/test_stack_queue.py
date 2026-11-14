import random
from collections import deque

import pytest

from dsa.stack_queue import CircularQueue, Stack


# ---------- 栈 ----------

def test_stack_empty():
    stack = Stack()
    assert len(stack) == 0
    assert not stack  # 空栈为假，和 list 一样
    assert list(stack) == []


def test_stack_lifo():
    stack = Stack()
    for value in [1, 2, 3]:
        stack.push(value)
    assert len(stack) == 3 and stack
    assert [stack.pop(), stack.pop(), stack.pop()] == [3, 2, 1]
    assert not stack


def test_stack_build_and_iterate_from_top():
    stack = Stack([1, 2, 3])  # 3 最后压入，在栈顶
    assert list(stack) == [3, 2, 1]
    assert len(stack) == 3  # 遍历不弹出
    assert repr(stack) == "Stack([1, 2, 3])"


def test_stack_peek_does_not_remove():
    stack = Stack([1, 2])
    assert stack.peek() == 2
    assert len(stack) == 2


def test_stack_empty_raises():
    stack = Stack()
    with pytest.raises(IndexError):
        stack.pop()
    with pytest.raises(IndexError):
        stack.peek()


# ---------- 环形队列 ----------

def drain(queue):
    out = []
    while queue:
        out.append(queue.popleft())
    return out


def test_queue_fifo():
    queue = CircularQueue()
    for value in [1, 2, 3]:
        queue.append(value)
    assert len(queue) == 3
    assert queue.peek() == 1
    assert len(queue) == 3
    assert drain(queue) == [1, 2, 3]
    assert not queue


def test_queue_build_and_iterate():
    queue = CircularQueue("abc")
    assert list(queue) == ["a", "b", "c"]
    assert len(queue) == 3  # 遍历不取出
    assert repr(queue) == "CircularQueue(['a', 'b', 'c'])"


def test_queue_empty_raises():
    queue = CircularQueue()
    with pytest.raises(IndexError):
        queue.popleft()
    with pytest.raises(IndexError):
        queue.peek()


def test_queue_wraps_around_without_growing():
    queue = CircularQueue(capacity=4)
    for value in [1, 2, 3]:
        queue.append(value)
    queue.popleft()
    queue.popleft()
    for value in [4, 5, 6]:  # 5、6 要回绕到下标 0、1
        queue.append(value)
    assert queue.capacity == 4
    assert list(queue) == [3, 4, 5, 6]  # 遍历也要按队列顺序，不是按下标顺序
    assert queue._data[:2] == [5, 6]
    assert drain(queue) == [3, 4, 5, 6]


def test_queue_grows_when_full():
    queue = CircularQueue(capacity=4)
    for value in range(5):
        queue.append(value)
    assert queue.capacity == 8
    assert drain(queue) == [0, 1, 2, 3, 4]


def test_queue_grows_after_wraparound_keeps_order():
    queue = CircularQueue(capacity=4)
    for value in [1, 2, 3, 4]:
        queue.append(value)
    queue.popleft()
    queue.popleft()
    for value in [5, 6, 7]:  # 先回绕填满，再扩容：搬家要按队列顺序，不是按下标顺序
        queue.append(value)
    assert queue.capacity == 8
    assert queue._head == 0
    assert queue.peek() == 3
    assert drain(queue) == [3, 4, 5, 6, 7]


def test_queue_reuse_after_emptied():
    queue = CircularQueue(capacity=2)
    for _ in range(5):  # 反复进出，head 绕好几圈
        queue.append("a")
        queue.append("b")
        assert drain(queue) == ["a", "b"]
    assert queue.capacity == 2


def test_queue_random_against_deque():
    rng = random.Random(3)
    queue, reference = CircularQueue(capacity=1), deque()
    for step in range(500):
        if reference and rng.random() < 0.4:
            assert queue.popleft() == reference.popleft()
        else:
            queue.append(step)
            reference.append(step)
        assert len(queue) == len(reference)
        if reference:
            assert queue.peek() == reference[0]
    assert list(queue) == list(reference)
    assert drain(queue) == list(reference)
