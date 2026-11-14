import random
import re
from collections.abc import Iterator

import pytest

from dsa.kmp import count, find, find_all, index, naive_find_all, prefix_function

FIND_ALLS = [naive_find_all, find_all]


def overlapping_positions(text, pattern):
    """标准库对照：用正则的前瞻 (?=...) 找出所有可重叠的位置。"""
    return [match.start() for match in re.finditer(f"(?={re.escape(pattern)})", text)]


@pytest.mark.parametrize(
    "pattern, expected",
    [
        ("A", [0]),
        ("ABABC", [0, 0, 1, 2, 0]),
        ("AAAA", [0, 1, 2, 3]),
        ("ABCDABD", [0, 0, 0, 0, 1, 2, 0]),
        ("AABAAAB", [0, 1, 0, 1, 2, 2, 3]),
        ("", []),
    ],
)
def test_prefix_function(pattern, expected):
    assert prefix_function(pattern) == expected


@pytest.mark.parametrize("search", FIND_ALLS)
def test_find_all_basic(search):
    result = search("ABABABCABABC", "ABABC")
    assert isinstance(result, Iterator)  # 生成器，不是 list
    assert list(result) == [2, 7]
    assert list(search("hello world", "o")) == [4, 7]


@pytest.mark.parametrize("search", FIND_ALLS)
def test_find_all_overlapping(search):
    assert list(search("aaaa", "aa")) == [0, 1, 2]
    assert list(search("abababa", "aba")) == [0, 2, 4]


@pytest.mark.parametrize("search", FIND_ALLS)
def test_find_all_edges(search):
    assert list(search("abc", "d")) == []
    assert list(search("ab", "abc")) == []  # 模式比文本长
    assert list(search("abc", "abc")) == [0]
    assert list(search("", "a")) == []
    assert list(search("abc", "")) == [0, 1, 2, 3]  # 空模式在每个位置都匹配，和 re 一样
    assert list(search("", "")) == [0]


def test_find_all_start():
    assert list(find_all("abcabcabc", "abc", 1)) == [3, 6]
    assert list(find_all("abcabc", "abc", 99)) == []


def test_find_like_str_find():
    text = "hello world, hello python"
    for pattern in ["hello", "o", "python", "java", "", "d, h"]:
        for start in [0, 1, 7, 13, len(text), len(text) + 1]:
            assert find(text, pattern, start) == text.find(pattern, start), (pattern, start)


def test_find_stops_at_first_match():
    """find 用的是生成器：找到第一个就停，不会把后面的文本也读一遍。"""

    class CountingText(str):
        reads = 0

        def __getitem__(self, position):
            CountingText.reads += 1
            return str.__getitem__(self, position)

        def __iter__(self):
            for character in str.__iter__(self):
                CountingText.reads += 1
                yield character

    text = CountingText("ab" + "x" * 10_000)
    assert find(text, "ab") == 0
    assert CountingText.reads < 100


def test_index_like_str_index():
    assert index("banana", "nan") == 2
    assert index("banana", "a", 2) == 3
    with pytest.raises(ValueError, match="substring not found"):
        index("banana", "xyz")


@pytest.mark.parametrize(
    "text, pattern",
    [("aaaa", "aa"), ("abababa", "aba"), ("abc", "d"), ("abc", ""), ("", ""), ("banana", "a"), ("aaaaa", "aa")],
)
def test_count_like_str_count(text, pattern):
    assert count(text, pattern) == text.count(pattern)


def test_random_against_standard_library():
    rng = random.Random(23)
    for _ in range(300):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 30)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        expected = overlapping_positions(text, pattern)
        assert list(find_all(text, pattern)) == expected, (text, pattern)
        assert list(naive_find_all(text, pattern)) == expected, (text, pattern)
        assert find(text, pattern) == text.find(pattern)
        assert count(text, pattern) == text.count(pattern)
