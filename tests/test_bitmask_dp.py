import random
import time
from itertools import permutations

from dsa.bitmask_dp import min_assignment_cost, shortest_round_trip, shortest_round_trip_route

CITY_DISTANCE = [[0, 2, 9, 10], [2, 0, 6, 4], [9, 6, 0, 3], [10, 4, 3, 0]]


# ---------- 暴力对照：枚举所有排列 ----------

def brute_assignment(cost) -> int:
    n = len(cost)
    return min(sum(cost[worker][task] for worker, task in enumerate(order)) for order in permutations(range(n)))


def route_length(distance, route) -> int:
    return sum(distance[here][there] for here, there in zip(route, route[1:]))


def brute_round_trip(distance) -> int:
    n = len(distance)
    if n <= 1:
        return 0
    return min(route_length(distance, [0, *middle, 0]) for middle in permutations(range(1, n)))


def random_matrix(generator, n, symmetric=False):
    matrix = [[0 if row == column else generator.randint(1, 20) for column in range(n)] for row in range(n)]
    if symmetric:
        for row in range(n):
            for column in range(row):
                matrix[row][column] = matrix[column][row]
    return matrix


# ---------- 分配任务 ----------

def test_assignment_example():
    assert min_assignment_cost([[9, 2, 7], [6, 4, 3], [5, 8, 1]]) == 9  # 贪心会得到 10


def test_assignment_small():
    assert min_assignment_cost([]) == 0
    assert min_assignment_cost([[4]]) == 4
    assert min_assignment_cost([[1, 100], [1, 100]]) == 101


def test_assignment_random_against_brute_force():
    generator = random.Random(44)
    for _ in range(40):
        n = generator.randint(1, 7)
        cost = [[generator.randint(0, 30) for _ in range(n)] for _ in range(n)]
        assert min_assignment_cost(cost) == brute_assignment(cost), cost


def test_assignment_n16_is_fast():
    generator = random.Random(16)
    cost = [[generator.randint(1, 99) for _ in range(16)] for _ in range(16)]
    started = time.perf_counter()
    min_assignment_cost(cost)  # O(2^n × n) ≈ 100 万次；暴力 16! 跑不完
    assert time.perf_counter() - started < 10


# ---------- 旅行商 ----------

def test_round_trip_example():
    assert shortest_round_trip(CITY_DISTANCE) == 18


def test_round_trip_small():
    assert shortest_round_trip([[0]]) == 0
    assert shortest_round_trip([[0, 5], [5, 0]]) == 10
    assert shortest_round_trip([[0, 1, 9], [9, 0, 1], [1, 9, 0]]) == 3  # 不对称：只有 0→1→2→0 便宜


def test_round_trip_random_against_brute_force():
    generator = random.Random(4444)
    for _ in range(40):
        n = generator.randint(1, 7)
        distance = random_matrix(generator, n, symmetric=generator.random() < 0.5)
        assert shortest_round_trip(distance) == brute_round_trip(distance), distance


def test_round_trip_n12_is_fast():
    generator = random.Random(12)
    distance = random_matrix(generator, 12, symmetric=True)
    started = time.perf_counter()
    shortest_round_trip(distance)  # O(2^n × n²) ≈ 59 万次；暴力 11! ≈ 4000 万条路线
    assert time.perf_counter() - started < 10


# ---------- 路线 ----------

def check_route(distance, route):
    n = len(distance)
    assert route[0] == 0 and route[-1] == 0
    assert sorted(route[:-1]) == list(range(n))  # 每个点正好一次
    assert route_length(distance, route) == brute_round_trip(distance)


def test_route_example():
    assert shortest_round_trip_route(CITY_DISTANCE) in ([0, 1, 3, 2, 0], [0, 2, 3, 1, 0])
    assert shortest_round_trip_route([[0]]) == [0, 0]


def test_route_random():
    generator = random.Random(44444)
    for _ in range(30):
        n = generator.randint(2, 7)
        distance = random_matrix(generator, n, symmetric=generator.random() < 0.5)
        check_route(distance, shortest_round_trip_route(distance))
