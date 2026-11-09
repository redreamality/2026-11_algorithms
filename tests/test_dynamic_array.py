import pytest

from dsa.dynamic_array import DynamicArray


def make(*values):
    arr = DynamicArray()
    for v in values:
        arr.append(v)
    return arr


def items(arr):
    return [arr[i] for i in range(len(arr))]


def test_starts_empty():
    arr = DynamicArray()
    assert len(arr) == 0
    assert arr.capacity == 1


def test_append_and_get():
    arr = make("a", "b", "c")
    assert len(arr) == 3
    assert items(arr) == ["a", "b", "c"]


def test_capacity_doubles_when_full():
    arr = DynamicArray()
    seen = []
    for i in range(9):
        arr.append(i)
        seen.append(arr.capacity)
    assert seen == [1, 2, 4, 4, 8, 8, 8, 8, 16]


def test_storage_is_fixed_size_block():
    arr = make(*range(5))
    assert len(arr._data) == arr.capacity == 8


def test_set():
    arr = make(1, 2, 3)
    arr[1] = 20
    assert items(arr) == [1, 20, 3]


@pytest.mark.parametrize("i", [3, 100, -1])
def test_index_out_of_range(i):
    arr = make(1, 2, 3)
    with pytest.raises(IndexError):
        arr[i]
    with pytest.raises(IndexError):
        arr[i] = 0


def test_pop():
    arr = make(1, 2, 3)
    assert arr.pop() == 3
    assert arr.pop() == 2
    assert items(arr) == [1]


def test_pop_empty():
    with pytest.raises(IndexError):
        DynamicArray().pop()


def test_insert_middle_front_end():
    arr = make(1, 3)
    arr.insert(1, 2)
    arr.insert(0, 0)
    arr.insert(4, 4)
    assert items(arr) == [0, 1, 2, 3, 4]
    assert arr.capacity == 8


@pytest.mark.parametrize("i", [-1, 3])
def test_insert_out_of_range(i):
    arr = make(1, 2)
    with pytest.raises(IndexError):
        arr.insert(i, 0)


def test_remove_at():
    arr = make(0, 1, 2, 3)
    assert arr.remove_at(1) == 1
    assert items(arr) == [0, 2, 3]
    assert arr.remove_at(2) == 3
    assert items(arr) == [0, 2]


def test_remove_at_out_of_range():
    with pytest.raises(IndexError):
        make(1).remove_at(1)


def test_many_operations_match_builtin_list():
    arr, ref = DynamicArray(), []
    for i in range(200):
        arr.append(i)
        ref.append(i)
        if i % 3 == 0:
            arr.insert(i // 2, -i)
            ref.insert(i // 2, -i)
        if i % 5 == 0:
            assert arr.remove_at(len(ref) // 3) == ref.pop(len(ref) // 3)
        if i % 7 == 0:
            assert arr.pop() == ref.pop()
    assert items(arr) == ref
