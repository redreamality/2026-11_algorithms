import random
from collections.abc import Iterator

import pytest

from dsa.trie import Trie


def test_empty():
    trie = Trie()
    assert len(trie) == 0
    assert "a" not in trie
    assert "" not in trie
    assert list(trie) == []
    assert not trie.has_prefix("")
    assert trie.complete("a") == []
    with pytest.raises(KeyError):
        del trie["a"]


def test_add_and_contains():
    trie = Trie(["car", "cat", "dog"])
    assert "car" in trie and "cat" in trie and "dog" in trie
    assert "cow" not in trie
    assert 42 not in trie  # 不是字符串也不报错
    assert len(trie) == 3


def test_prefix_is_not_a_word():
    trie = Trie(["car"])
    assert "ca" not in trie  # 走得到，但 count 是 0
    assert "cars" not in trie  # 走到半路就没路了


def test_word_inside_another_word():
    trie = Trie(["car", "ca"])
    assert "ca" in trie and "car" in trie
    assert list(trie) == ["ca", "car"]


def test_has_prefix():
    trie = Trie(["car", "dog"])
    assert trie.has_prefix("c")
    assert trie.has_prefix("car")
    assert not trie.has_prefix("cart")
    assert not trie.has_prefix("x")
    assert trie.has_prefix("")


def test_shares_prefix_nodes():
    trie = Trie(["car", "cat"])
    assert list(trie.root.children) == ["c"]  # 公共前缀 "ca" 只存一份
    assert set(trie.root.children["c"].children["a"].children) == {"r", "t"}


def test_add_counts_and_len():
    trie = Trie()
    trie.add("go")
    trie.add("go")
    trie.add("go", times=3)
    assert len(trie) == 1  # 不同单词只算一个
    assert trie.count("go") == 5
    assert trie.count("g") == 0
    assert trie.count("missing") == 0


def test_starts_with_is_sorted_generator():
    trie = Trie(["tea", "ten", "to", "inn", "ted", "te"])
    result = trie.starts_with("te")
    assert isinstance(result, Iterator)
    assert list(result) == ["te", "tea", "ted", "ten"]
    assert list(trie.starts_with("t")) == ["te", "tea", "ted", "ten", "to"]
    assert list(trie) == ["inn", "te", "tea", "ted", "ten", "to"]


def test_starts_with_missing():
    trie = Trie(["apple"])
    assert list(trie.starts_with("b")) == []
    assert list(trie.starts_with("apples")) == []


def test_complete_by_count_then_alphabet():
    trie = Trie()
    for word, times in [("python", 50), ("pytest", 30), ("pydantic", 30), ("pandas", 40), ("py", 5)]:
        trie.add(word, times)
    assert trie.complete("py", 3) == ["python", "pydantic", "pytest"]
    assert trie.complete("p", 2) == ["python", "pandas"]
    assert trie.complete("py") == ["python", "pydantic", "pytest", "py"]  # 默认最多 5 个
    assert trie.complete("z") == []
    assert trie.complete("py", 0) == []


def test_delete():
    trie = Trie(["car", "cat"])
    del trie["car"]
    assert "car" not in trie and "cat" in trie
    assert list(trie.starts_with("ca")) == ["cat"]
    assert len(trie) == 1


def test_delete_missing_or_prefix():
    trie = Trie(["car"])
    with pytest.raises(KeyError):
        del trie["ca"]  # 只是前缀，不是单词
    with pytest.raises(KeyError):
        del trie["dog"]
    assert "car" in trie and len(trie) == 1


def test_delete_keeps_longer_word():
    trie = Trie(["ca", "car"])
    del trie["ca"]
    assert "ca" not in trie and "car" in trie
    assert trie.has_prefix("ca")


def test_delete_prunes_dead_branch():
    trie = Trie(["car", "dog"])
    trie.add("car", 7)
    del trie["car"]  # 不管 count 多少都整个删掉
    assert trie.count("car") == 0
    assert not trie.has_prefix("c")
    assert "c" not in trie.root.children  # 不再通向任何单词的节点被剪掉


def test_random_against_counter():
    rng = random.Random(22)
    trie, reference = Trie(), {}
    for _ in range(800):
        word = "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
        if rng.random() < 0.7:
            times = rng.randint(1, 3)
            trie.add(word, times)
            reference[word] = reference.get(word, 0) + times
        elif word in reference:
            del trie[word]
            del reference[word]
        else:
            with pytest.raises(KeyError):
                del trie[word]
        prefix = word[: rng.randint(0, len(word))]
        matching = sorted(w for w in reference if w.startswith(prefix))
        assert list(trie.starts_with(prefix)) == matching
        assert trie.has_prefix(prefix) == bool(matching)
        assert trie.complete(prefix, 3) == sorted(matching, key=lambda w: (-reference[w], w))[:3]
    assert len(trie) == len(reference)
    assert list(trie) == sorted(reference)
