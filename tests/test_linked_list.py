import pytest

from dsa.linked_list import LinkedList


def make(*values):
    lst = LinkedList()
    for v in values:
        lst.push_back(v)
    return lst


def check(lst, expected):
    """内容、长度、head、tail 都要对。"""
    assert list(lst) == expected
    assert len(lst) == len(expected)
    if expected:
        assert lst.head.value == expected[0]
        assert lst.tail.value == expected[-1]
        assert lst.tail.next is None
    else:
        assert lst.head is None and lst.tail is None


def test_empty():
    check(LinkedList(), [])


def test_push_back():
    check(make(1, 2, 3), [1, 2, 3])


def test_push_front():
    lst = LinkedList()
    lst.push_front(3)
    lst.push_front(2)
    lst.push_front(1)
    check(lst, [1, 2, 3])


def test_pop_front():
    lst = make(1, 2)
    assert lst.pop_front() == 1
    check(lst, [2])
    assert lst.pop_front() == 2
    check(lst, [])


def test_pop_front_empty():
    with pytest.raises(IndexError):
        LinkedList().pop_front()


def test_reuse_after_emptied():
    lst = make(1)
    lst.pop_front()
    lst.push_back(2)
    lst.push_front(1)
    check(lst, [1, 2])


def test_find():
    lst = make(1, 2, 3)
    assert lst.find(2)
    assert not lst.find(4)
    assert not LinkedList().find(1)


def test_remove_head_middle_tail():
    lst = make(1, 2, 3, 4)
    assert lst.remove(1)
    check(lst, [2, 3, 4])
    assert lst.remove(3)
    check(lst, [2, 4])
    assert lst.remove(4)
    check(lst, [2])
    lst.push_back(5)  # 删掉尾巴后 tail 必须正确，否则这里会接错地方
    check(lst, [2, 5])


def test_remove_only_first_match():
    lst = make(1, 2, 1)
    assert lst.remove(1)
    check(lst, [2, 1])


def test_remove_missing():
    lst = make(1, 2)
    assert not lst.remove(9)
    check(lst, [1, 2])
    assert not LinkedList().remove(1)


def test_remove_last_node():
    lst = make(1)
    assert lst.remove(1)
    check(lst, [])


def test_reverse():
    lst = make(1, 2, 3, 4)
    nodes = [lst.head, lst.head.next, lst.head.next.next, lst.tail]
    lst.reverse()
    check(lst, [4, 3, 2, 1])
    assert lst.head is nodes[-1] and lst.tail is nodes[0]  # 不新建节点
    lst.push_back(0)
    check(lst, [4, 3, 2, 1, 0])


@pytest.mark.parametrize("values", [[], [1]])
def test_reverse_tiny(values):
    lst = make(*values)
    lst.reverse()
    check(lst, values)
