import itertools
import types
from itertools import islice

import pytest

from dsa.backtracking import combination_sum, n_queens, permutations, solve_sudoku, subsets


def normalized(results):
    """排序后比较，不依赖生成顺序。"""
    return sorted(results)


# ---------- 全排列 ----------

def test_permutations_is_a_generator_of_tuples():
    result = permutations([1, 2, 3])
    assert isinstance(result, types.GeneratorType)
    assert all(isinstance(permutation, tuple) for permutation in result)


def test_permutations_same_order_as_itertools():
    for items in ([1, 2, 3], "abcd", [3, 1, 2], [1, 1, 2]):
        assert list(permutations(items)) == list(itertools.permutations(items))


def test_permutations_edges():
    assert list(permutations([])) == [()]
    assert list(permutations([7])) == [(7,)]


def test_permutations_count_and_not_corrupted_by_undo():
    result = list(permutations([1, 2, 3, 4, 5]))
    assert len(result) == 120
    assert len(set(result)) == 120


def test_permutations_is_lazy():
    # 20! ≈ 2.4×10^18 个排列，先建好整个列表再返回是不可能跑完的
    assert next(permutations(range(20))) == tuple(range(20))
    assert list(islice(permutations(range(20)), 2))[1] == (*range(18), 19, 18)


# ---------- 子集 ----------

def test_subsets():
    assert normalized(subsets([1, 2, 3])) == normalized(
        [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    )


def test_subsets_keep_original_order():
    for subset in subsets(["c", "a", "b"]):
        assert list(subset) == [item for item in ["c", "a", "b"] if item in subset]


def test_subsets_edges_and_laziness():
    assert list(subsets([])) == [()]
    assert sum(1 for _ in subsets(range(10))) == 1024
    first_three = list(islice(subsets(range(40)), 3))  # 2^40 个，只取前 3 个
    assert len(first_three) == 3


# ---------- 组合总和 ----------

def test_combination_sum():
    assert normalized(combination_sum([2, 3, 6, 7], 7)) == [(2, 2, 3), (7,)]
    assert normalized(combination_sum([2, 3, 5], 8)) == [(2, 2, 2, 2), (2, 3, 3), (3, 5)]


def test_combination_sum_unsorted_input_not_mutated():
    candidates = [5, 3, 2]
    assert normalized(combination_sum(candidates, 8)) == [(2, 2, 2, 2), (2, 3, 3), (3, 5)]
    assert candidates == [5, 3, 2]


def test_combination_sum_none_and_zero():
    assert list(combination_sum([2], 1)) == []
    assert list(combination_sum([2, 3], 0)) == [()]


def test_combination_sum_against_brute_force():
    candidates, target = [3, 4, 7, 9], 20
    expected = {
        combination
        for size in range(target // min(candidates) + 1)
        for combination in itertools.combinations_with_replacement(candidates, size)
        if sum(combination) == target
    }
    result = list(combination_sum(candidates, target))
    assert len(result) == len(set(result))
    assert set(result) == expected


# ---------- N 皇后 ----------

@pytest.mark.parametrize("n, count", [(0, 1), (1, 1), (2, 0), (3, 0), (4, 2), (5, 10), (6, 4), (8, 92)])
def test_n_queens_count(n, count):
    assert sum(1 for _ in n_queens(n)) == count


def test_n_queens_first_solution_and_order():
    assert next(n_queens(4)) == (1, 3, 0, 2)
    assert list(n_queens(4)) == [(1, 3, 0, 2), (2, 0, 3, 1)]
    assert next(n_queens(8)) == (0, 4, 7, 5, 2, 6, 1, 3)


def test_n_queens_solutions_are_valid():
    for solution in n_queens(6):
        assert sorted(solution) == list(range(6))
        assert len({row - column for row, column in enumerate(solution)}) == 6
        assert len({row + column for row, column in enumerate(solution)}) == 6


# ---------- 数独（选做） ----------

PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def is_valid_solution(puzzle, solution) -> bool:
    digits = set(range(1, 10))
    rows = all(set(row) == digits for row in solution)
    columns = all({solution[row][column] for row in range(9)} == digits for column in range(9))
    boxes = all(
        {solution[row][column] for row in range(top, top + 3) for column in range(left, left + 3)} == digits
        for top in (0, 3, 6)
        for left in (0, 3, 6)
    )
    keeps_givens = all(
        puzzle[row][column] in (0, solution[row][column]) for row in range(9) for column in range(9)
    )
    return rows and columns and boxes and keeps_givens


def test_solve_sudoku():
    original = [row[:] for row in PUZZLE]
    solution = solve_sudoku(PUZZLE)
    assert is_valid_solution(PUZZLE, solution)
    assert solution[0] == [5, 3, 4, 6, 7, 8, 9, 1, 2]
    assert PUZZLE == original  # 不改动传进来的棋盘


def test_solve_sudoku_unsolvable():
    # 已给的数本身不冲突，但左上角只能填 9，而同一列下面已经有 9 了
    broken = [[0] * 9 for _ in range(9)]
    broken[0] = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    broken[1][0] = 9
    assert solve_sudoku(broken) is None
