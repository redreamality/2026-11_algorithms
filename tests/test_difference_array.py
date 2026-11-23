import random

import pytest

from dsa.difference_array import (
    DifferenceArray,
    add_to_submatrices,
    car_pooling,
    corp_flight_bookings,
)

NUMBERS = [3, 1, 4, 1, 5, 9, 2, 6]  # 第 41、42 课共用的主线例子


def test_difference_of_running_example():
    difference_array = DifferenceArray(NUMBERS)
    assert difference_array.difference == [3, -2, 3, -3, 4, 4, -7, 4, 0]
    assert len(difference_array) == 8
    assert difference_array.to_list() == NUMBERS


def test_add_marks_only_two_cells():
    difference_array = DifferenceArray(NUMBERS)
    difference_array.add(2, 5, 2)
    assert difference_array.difference == [3, -2, 5, -3, 4, 4, -9, 4, 0]
    difference_array.add(4, 7, 3)
    assert difference_array.difference == [3, -2, 5, -3, 7, 4, -9, 4, -3]  # right + 1 == n 落在多出来的那格
    assert difference_array.to_list() == [3, 1, 6, 3, 10, 14, 5, 9]


def test_to_list_does_not_consume_marks():
    difference_array = DifferenceArray([0, 0, 0])
    difference_array.add(0, 2, 1)
    assert difference_array.to_list() == [1, 1, 1]
    assert difference_array.to_list() == [1, 1, 1]
    difference_array.add(1, 1, 5)
    assert difference_array.to_list() == [1, 6, 1]


def test_does_not_modify_input():
    numbers = [1, 2, 3]
    difference_array = DifferenceArray(numbers)
    difference_array.add(0, 2, 10)
    assert numbers == [1, 2, 3]


def test_single_element_and_empty():
    difference_array = DifferenceArray([7])
    difference_array.add(0, 0, -7)
    assert difference_array.to_list() == [0]
    assert DifferenceArray([]).to_list() == []
    assert len(DifferenceArray([])) == 0


@pytest.mark.parametrize("left, right", [(-1, 2), (0, 8), (5, 3), (8, 8)])
def test_bad_range_raises_index_error(left, right):
    difference_array = DifferenceArray(NUMBERS)
    with pytest.raises(IndexError):
        difference_array.add(left, right, 1)


def test_matches_brute_force():
    rng = random.Random(41)
    for _ in range(200):
        numbers = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        expected = list(numbers)
        difference_array = DifferenceArray(numbers)
        for _ in range(rng.randint(0, 10)):
            left = rng.randrange(len(numbers))
            right = rng.randrange(left, len(numbers))
            delta = rng.randint(-5, 5)
            difference_array.add(left, right, delta)
            for index in range(left, right + 1):
                expected[index] += delta
        assert difference_array.to_list() == expected


def test_many_adds_are_fast():
    size = 200_000
    difference_array = DifferenceArray([0] * size)
    for left in range(size):
        difference_array.add(left, size - 1, 1)  # 暴力做法要 O(n²)
    result = difference_array.to_list()
    assert result[0] == 1 and result[-1] == size


def test_corp_flight_bookings():
    assert corp_flight_bookings([[1, 2, 10], [2, 3, 20], [2, 5, 25]], 5) == [10, 55, 45, 25, 25]
    assert corp_flight_bookings([[1, 2, 10], [2, 2, 15]], 2) == [10, 25]
    assert corp_flight_bookings([], 3) == [0, 0, 0]
    assert corp_flight_bookings([[3, 3, 4]], 3) == [0, 0, 4]


def test_car_pooling():
    trips = [[2, 1, 5], [3, 3, 7]]
    assert car_pooling(trips, 4) is False
    assert car_pooling(trips, 5) is True
    assert car_pooling([[2, 1, 5], [3, 5, 7]], 3) is True  # 在 5 下车的人不占 5 的座位
    assert car_pooling([[3, 2, 7], [3, 7, 9], [8, 3, 9]], 11) is True
    assert car_pooling([[9, 0, 1000]], 8) is False


def test_add_to_submatrices():
    assert add_to_submatrices(3, 3, [[1, 1, 2, 2, 1], [0, 0, 1, 1, 1]]) == [[1, 1, 0], [1, 2, 1], [0, 1, 1]]
    assert add_to_submatrices(2, 3, []) == [[0, 0, 0], [0, 0, 0]]
    assert add_to_submatrices(2, 2, [[0, 0, 1, 1, 5], [1, 1, 1, 1, -5]]) == [[5, 5], [5, 0]]


def test_add_to_submatrices_matches_brute_force():
    rng = random.Random(42)
    for _ in range(50):
        row_count, column_count = rng.randint(1, 6), rng.randint(1, 6)
        expected = [[0] * column_count for _ in range(row_count)]
        additions = []
        for _ in range(rng.randint(0, 8)):
            top = rng.randrange(row_count)
            bottom = rng.randrange(top, row_count)
            left = rng.randrange(column_count)
            right = rng.randrange(left, column_count)
            delta = rng.randint(-3, 3)
            additions.append([top, left, bottom, right, delta])
            for row in range(top, bottom + 1):
                for column in range(left, right + 1):
                    expected[row][column] += delta
        assert add_to_submatrices(row_count, column_count, additions) == expected
