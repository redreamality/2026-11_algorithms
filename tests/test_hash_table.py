import random

import pytest

from dsa.hash_table import HashMap


class Same:
    """哈希值永远相同的 key：用来故意制造冲突。"""

    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return isinstance(other, Same) and self.name == other.name


def test_empty():
    table = HashMap()
    assert len(table) == 0
    assert "a" not in table
    assert list(table) == []
    assert not table


def test_set_and_get():
    table = HashMap()
    table["a"] = 1
    table["b"] = 2
    assert table["a"] == 1
    assert table["b"] == 2
    assert len(table) == 2


def test_build_from_dict_and_compare():
    table = HashMap({"a": 1, "b": 2})
    assert table == {"a": 1, "b": 2}
    assert sorted(table) == ["a", "b"]
    assert sorted(table.items()) == [("a", 1), ("b", 2)]
    assert repr(HashMap({"x": 1})) == "HashMap({'x': 1})"


def test_set_overwrites():
    table = HashMap()
    table["a"] = 1
    table["a"] = 9
    assert table["a"] == 9
    assert len(table) == 1


def test_missing_key_raises_key_error():
    table = HashMap({"a": 1})
    with pytest.raises(KeyError):
        table["nope"]
    with pytest.raises(KeyError):
        del table["nope"]
    assert len(table) == 1


def test_methods_inherited_from_mutable_mapping():
    table = HashMap({3: "x"})
    assert 3 in table and 4 not in table
    assert table.get(4) is None and table.get(4, "?") == "?"
    assert table.setdefault(4, "y") == "y"
    assert table.pop(3) == "x"
    assert table == {4: "y"}


def test_delete():
    table = HashMap({"a": 1, "b": 2})
    del table["a"]
    assert "a" not in table
    assert table["b"] == 2
    assert len(table) == 1


def test_index_in_range():
    table = HashMap(capacity=8)
    for key in ["a", 7, -3, (1, 2)]:
        assert 0 <= table._index(key) < 8
    assert table._index(10) == 10 % 8


def test_collisions_share_a_bucket():
    table = HashMap()
    keys = [Same(name) for name in "xyz"]
    for key, value in zip(keys, [1, 2, 3]):
        table[key] = value
    assert [table[key] for key in keys] == [1, 2, 3]
    assert len(table._buckets[table._index(keys[0])]) == 3  # 三个都挂在同一个桶里
    del table[keys[1]]
    assert table[keys[0]] == 1 and table[keys[2]] == 3
    assert keys[1] not in table


def test_resize_when_load_factor_exceeded():
    table = HashMap(capacity=8)
    for number in range(6):  # 6 / 8 = 0.75，还没超过
        table[number] = number
    assert table.capacity == 8
    table[6] = 6  # 7 / 8 > 0.75，翻倍
    assert table.capacity == 16
    table[6] = 60  # 覆盖不算新 key，不会再扩
    assert table.capacity == 16


def test_rehash_keeps_everything_findable():
    table = HashMap(capacity=8)
    for number in range(100):
        table[f"k{number}"] = number
    assert len(table) == 100
    assert table.capacity == 256
    assert all(table[f"k{number}"] == number for number in range(100))
    for index, bucket in enumerate(table._buckets):  # 每个 key 都在它现在该在的桶里
        assert all(table._index(key) == index for key, _ in bucket)


def test_random_against_dict():
    rng = random.Random(4)
    table, reference = HashMap(), {}
    for step in range(1000):
        key = rng.randrange(80)
        if rng.random() < 0.6:
            table[key] = reference[key] = step
        elif key in reference:
            del table[key]
            del reference[key]
        else:
            with pytest.raises(KeyError):
                del table[key]
        assert (key in table) == (key in reference)
        assert len(table) == len(reference)
    assert dict(table.items()) == reference
