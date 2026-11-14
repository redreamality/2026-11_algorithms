import json
import sys

import pytest

from dsa.recursion import directory_size, factorial, flatten, flatten_json, power


def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    with pytest.raises(ValueError):
        factorial(-1)


@pytest.mark.parametrize("base, exponent", [(2, 0), (2, 1), (2, 10), (3, 7), (5, 13), (1.5, 4)])
def test_power(base, exponent):
    assert power(base, exponent) == base**exponent


def test_power_is_log_n():
    # O(n) 的递归要 10 万层，早就 RecursionError 了；O(log n) 只要 17 层左右。
    assert power(1, 100_000) == 1
    assert power(2, 1000) == 2**1000


def test_power_negative_exponent():
    with pytest.raises(ValueError):
        power(2, -1)


def test_flatten_is_lazy_generator():
    result = flatten([1, [2]])
    assert iter(result) is result  # 用 yield 写的生成器，不是一次性建好的 list
    assert list(result) == [1, 2]


def test_flatten():
    assert list(flatten([])) == []
    assert list(flatten([1, [2, [3, [4]]], (5, 6), "ab"])) == [1, 2, 3, 4, 5, 6, "ab"]
    assert list(flatten([[], [[]], [[], [7]]])) == [7]
    assert list(flatten([{"a": 1}, [None]])) == [{"a": 1}, None]  # dict 当整体


def test_flatten_deep_but_within_limit():
    nested = [0]
    for value in range(1, 200):
        nested = [nested, value]
    assert list(flatten(nested)) == list(range(200))


def test_flatten_json():
    document = {"user": {"name": "Ann", "tags": ["a", "b"]}, "ok": True}
    assert flatten_json(document) == {"user.name": "Ann", "user.tags.0": "a", "user.tags.1": "b", "ok": True}


def test_flatten_json_order_and_separator():
    document = {"b": {"y": 1, "x": 2}, "a": [[3, 4]]}
    assert list(flatten_json(document, separator="/").items()) == [
        ("b/y", 1), ("b/x", 2), ("a/0/0", 3), ("a/0/1", 4)
    ]


def test_flatten_json_keeps_empty_containers_and_falsy_leaves():
    document = {"empty_dict": {}, "empty_list": [], "zero": 0, "none": None, "blank": ""}
    assert flatten_json(document) == document
    assert flatten_json({}) == {}


def test_flatten_json_does_not_modify_input():
    document = {"a": {"b": [1, {"c": 2}]}}
    snapshot = json.dumps(document)
    flatten_json(document)
    assert json.dumps(document) == snapshot


def test_directory_size(tmp_path):
    (tmp_path / "a" / "b" / "c").mkdir(parents=True)
    (tmp_path / "empty").mkdir()
    (tmp_path / "top.bin").write_bytes(b"x" * 10)
    (tmp_path / "a" / "one.bin").write_bytes(b"x" * 200)
    (tmp_path / "a" / "b" / "c" / "deep.bin").write_bytes(b"x" * 3000)
    assert directory_size(tmp_path) == 3210
    assert directory_size(tmp_path / "a") == 3200
    assert directory_size(tmp_path / "empty") == 0
    assert directory_size(tmp_path / "top.bin") == 10


def test_directory_size_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        directory_size(tmp_path / "nope")


def test_recursion_limit_untouched():
    assert sys.getrecursionlimit() >= 1000
