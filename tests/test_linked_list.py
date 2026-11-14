import random
from collections import deque

import pytest

from dsa.linked_list import LinkedList


def check(linked_list, expected):
    """内容、长度、head、tail 都要对。"""
    assert list(linked_list) == expected
    assert len(linked_list) == len(expected)
    if expected:
        assert linked_list.head.value == expected[0]
        assert linked_list.tail.value == expected[-1]
        assert linked_list.tail.next is None
    else:
        assert linked_list.head is None and linked_list.tail is None


def test_empty():
    check(LinkedList(), [])
    assert not LinkedList()  # 空的时候为假，和 deque 一样


def test_build_from_iterable_and_append():
    linked_list = LinkedList([1, 2])
    linked_list.append(3)
    check(linked_list, [1, 2, 3])
    assert linked_list == [1, 2, 3]
    assert repr(linked_list) == "LinkedList([1, 2, 3])"


def test_appendleft():
    linked_list = LinkedList()
    for value in (3, 2, 1):
        linked_list.appendleft(value)
    check(linked_list, [1, 2, 3])


def test_popleft():
    linked_list = LinkedList([1, 2])
    assert linked_list.popleft() == 1
    check(linked_list, [2])
    assert linked_list.popleft() == 2
    check(linked_list, [])
    with pytest.raises(IndexError):
        linked_list.popleft()


def test_reuse_after_emptied():
    linked_list = LinkedList([1])
    linked_list.popleft()
    linked_list.append(2)
    linked_list.appendleft(1)
    check(linked_list, [1, 2])


def test_contains():
    linked_list = LinkedList([1, 2, 3])
    assert 2 in linked_list
    assert 4 not in linked_list
    assert 1 not in LinkedList()


def test_remove_head_middle_tail():
    linked_list = LinkedList([1, 2, 3, 4])
    linked_list.remove(1)
    check(linked_list, [2, 3, 4])
    linked_list.remove(3)
    check(linked_list, [2, 4])
    linked_list.remove(4)
    check(linked_list, [2])
    linked_list.append(5)  # 删掉尾巴后 tail 必须正确，否则这里会接错地方
    check(linked_list, [2, 5])


def test_remove_only_first_match():
    linked_list = LinkedList([1, 2, 1])
    linked_list.remove(1)
    check(linked_list, [2, 1])


def test_remove_missing_raises_value_error():
    linked_list = LinkedList([1, 2])
    with pytest.raises(ValueError):
        linked_list.remove(9)
    check(linked_list, [1, 2])
    with pytest.raises(ValueError):
        LinkedList().remove(1)


def test_remove_last_node():
    linked_list = LinkedList([1])
    linked_list.remove(1)
    check(linked_list, [])


def test_reverse():
    linked_list = LinkedList([1, 2, 3, 4])
    nodes = [linked_list.head, linked_list.head.next, linked_list.head.next.next, linked_list.tail]
    linked_list.reverse()
    check(linked_list, [4, 3, 2, 1])
    assert linked_list.head is nodes[-1] and linked_list.tail is nodes[0]  # 不新建节点
    linked_list.append(0)
    check(linked_list, [4, 3, 2, 1, 0])


@pytest.mark.parametrize("values", [[], [1]])
def test_reverse_tiny(values):
    linked_list = LinkedList(values)
    linked_list.reverse()
    check(linked_list, values)


def test_random_against_deque():
    rng = random.Random(2)
    linked_list, reference = LinkedList(), deque()
    for step in range(500):
        choice = rng.random()
        if choice < 0.35:
            linked_list.append(step % 20)
            reference.append(step % 20)
        elif choice < 0.6:
            linked_list.appendleft(step % 20)
            reference.appendleft(step % 20)
        elif choice < 0.75 and reference:
            assert linked_list.popleft() == reference.popleft()
        elif choice < 0.95:
            value = rng.randrange(20)
            if value in reference:
                linked_list.remove(value)
                reference.remove(value)
            else:
                with pytest.raises(ValueError):
                    linked_list.remove(value)
        else:
            linked_list.reverse()
            reference.reverse()
    check(linked_list, list(reference))
