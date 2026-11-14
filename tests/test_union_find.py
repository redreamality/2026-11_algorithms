import pytest

from dsa.union_find import UnionFind


def test_starts_all_alone():
    uf = UnionFind(range(5))
    assert uf.set_count == 5
    assert len(uf) == 5
    for element in range(5):
        assert uf.find(element) == element
        assert uf.size_of(element) == 1


def test_empty():
    uf = UnionFind()
    assert uf.set_count == 0
    assert len(uf) == 0
    assert uf.groups() == []


def test_any_hashable_elements():
    uf = UnionFind()
    uf.union("ann@example.com", "ann@work.example.com")
    uf.union((0, 0), (0, 1))
    assert uf.connected("ann@work.example.com", "ann@example.com")
    assert not uf.connected("ann@example.com", (0, 0))
    assert uf.set_count == 2


def test_add_is_idempotent():
    uf = UnionFind()
    uf.add("a")
    uf.union("a", "b")
    uf.add("a")
    assert uf.set_count == 1
    assert uf.size_of("b") == 2


def test_union_adds_unknown_elements():
    uf = UnionFind()
    assert uf.union("x", "y")
    assert "x" in uf and "y" in uf and "z" not in uf
    assert len(uf) == 2


def test_unknown_element_raises_key_error():
    uf = UnionFind(["a"])
    with pytest.raises(KeyError):
        uf.find("nobody")
    with pytest.raises(KeyError):
        uf.size_of("nobody")
    assert not uf.connected("a", "nobody")
    assert "nobody" not in uf  # connected 不应该偷偷把它加进来


def test_union_returns_whether_merged():
    uf = UnionFind(range(4))
    assert uf.union(0, 1)
    assert not uf.union(1, 0)
    assert not uf.union(2, 2)


def test_count_drops_only_on_real_merge():
    uf = UnionFind(range(5))
    uf.union(0, 1)
    uf.union(1, 2)
    assert uf.set_count == 3
    uf.union(0, 2)
    assert uf.set_count == 3


def test_connected_is_transitive():
    uf = UnionFind(range(6))
    uf.union(0, 1)
    uf.union(1, 2)
    uf.union(3, 4)
    assert uf.connected(0, 2)
    assert uf.connected(3, 4)
    assert not uf.connected(2, 3)
    assert not uf.connected(5, 0)
    assert uf.connected(5, 5)


def test_size_of():
    uf = UnionFind(range(6))
    uf.union(0, 1)
    uf.union(1, 2)
    uf.union(3, 4)
    assert [uf.size_of(element) for element in range(6)] == [3, 3, 3, 2, 2, 1]
    uf.union(4, 0)
    assert uf.size_of(3) == 5


def test_small_tree_goes_under_big_tree():
    uf = UnionFind(range(4))
    uf.union(0, 1)
    uf.union(0, 2)
    big_root = uf.find(0)
    uf.union(3, 0)  # 3 是单个元素，挂到大树下面，大树的根不变
    assert uf.find(3) == big_root
    assert uf.parent[3] == big_root


def test_tie_keeps_root_of_a():
    uf = UnionFind(["a", "b"])
    uf.union("a", "b")
    assert uf.parent == {"a": "a", "b": "a"}


def test_path_compression():
    uf = UnionFind(range(5))
    uf.parent = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3}  # 手动搭一条链：4 → 3 → 2 → 1 → 0
    assert uf.find(4) == 0
    assert uf.parent == {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # 沿途每个节点都直接指向根


def test_find_on_long_chain_does_not_recurse():
    length = 200_000
    uf = UnionFind(range(length))
    uf.parent = {element: max(element - 1, 0) for element in range(length)}  # 手搭一条超长链
    assert uf.find(length - 1) == 0


def test_groups():
    uf = UnionFind(["d", "a", "b", "c", "e"])
    uf.union("a", "c")
    uf.union("e", "b")
    assert uf.groups() == [{"d"}, {"a", "c"}, {"b", "e"}]


def test_long_chain_of_unions_is_fast():
    n = 200_000
    uf = UnionFind()
    for element in range(n - 1):
        uf.union(element, element + 1)
    assert uf.set_count == 1
    assert uf.connected(0, n - 1)
    assert uf.size_of(n // 2) == n
