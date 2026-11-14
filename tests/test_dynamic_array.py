import random

import pytest

from dsa.dynamic_array import DynamicArray


def test_starts_empty():
    array = DynamicArray()
    assert len(array) == 0
    assert array.capacity == 1
    assert list(array) == []
    assert not array  # 空的时候为假，和 list 一样


def test_build_from_iterable_and_index():
    array = DynamicArray("abc")
    assert len(array) == 3
    assert [array[0], array[1], array[2]] == ["a", "b", "c"]
    assert array == ["a", "b", "c"]


def test_negative_index_like_list():
    array = DynamicArray([10, 20, 30])
    assert array[-1] == 30
    assert array[-3] == 10
    array[-2] = 25
    assert array == [10, 25, 30]


def test_capacity_doubles_when_full():
    array = DynamicArray()
    seen = []
    for number in range(9):
        array.append(number)
        seen.append(array.capacity)
    assert seen == [1, 2, 4, 4, 8, 8, 8, 8, 16]


def test_storage_is_fixed_size_block():
    array = DynamicArray(range(5))
    assert len(array._data) == array.capacity == 8


@pytest.mark.parametrize("index", [3, 100, -4])
def test_index_out_of_range(index):
    array = DynamicArray([1, 2, 3])
    with pytest.raises(IndexError):
        array[index]
    with pytest.raises(IndexError):
        array[index] = 0
    with pytest.raises(IndexError):
        del array[index]


def test_pop():
    array = DynamicArray([1, 2, 3])
    assert array.pop() == 3
    assert array.pop(0) == 1
    assert array == [2]
    array.pop()
    with pytest.raises(IndexError):
        array.pop()


def test_insert_middle_front_end():
    array = DynamicArray([1, 3])
    array.insert(1, 2)
    array.insert(0, 0)
    array.insert(4, 4)
    assert array == [0, 1, 2, 3, 4]
    assert array.capacity == 8


def test_insert_clamps_like_list():
    array, reference = DynamicArray([1, 2, 3]), [1, 2, 3]
    for index, value in [(100, "end"), (-100, "start"), (-1, "before last")]:
        array.insert(index, value)
        reference.insert(index, value)
    assert array == reference


def test_delete_shifts_left():
    array = DynamicArray([0, 1, 2, 3])
    del array[1]
    assert array == [0, 2, 3]
    del array[-1]
    assert array == [0, 2]


def test_methods_inherited_from_mutable_sequence():
    array = DynamicArray(["a", "b", "c", "b"])
    assert "c" in array and "z" not in array
    assert array.index("b") == 1
    assert array.count("b") == 2
    array.remove("b")  # 删第一个
    assert array == ["a", "c", "b"]
    with pytest.raises(ValueError):
        array.remove("z")
    array.extend(["d", "e"])
    array.reverse()
    assert array == ["e", "d", "b", "c", "a"]
    assert repr(DynamicArray([1])) == "DynamicArray([1])"


def test_many_operations_match_builtin_list():
    rng = random.Random(1)
    array, reference = DynamicArray(), []
    for step in range(500):
        choice = rng.random()
        if choice < 0.5:
            array.append(step)
            reference.append(step)
        elif choice < 0.7:
            index = rng.randint(-len(reference) - 2, len(reference) + 2)
            array.insert(index, -step)
            reference.insert(index, -step)
        elif reference:
            index = rng.randrange(-len(reference), len(reference))
            if choice < 0.85:
                assert array.pop(index) == reference.pop(index)
            else:
                array[index] = step
                reference[index] = step
        assert len(array) == len(reference)
    assert list(array) == reference
    assert len(array._data) == array.capacity
