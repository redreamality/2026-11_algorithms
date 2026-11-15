import inspect
from itertools import count, islice

import pytest

from dsa.python_basics import Book, Shelf, all_titles, group_by_author, parse_price, running_totals, top_sellers

BOOKS = [
    Book("三体", "刘慈欣", 120),
    Book("活着", "余华", 95),
    Book("球状闪电", "刘慈欣", 60),
    Book("兄弟", "余华", 95),
    Book("围城", "钱钟书", 30),
]


def test_group_by_author_keeps_order():
    result = group_by_author(BOOKS)
    assert result == {"刘慈欣": ["三体", "球状闪电"], "余华": ["活着", "兄弟"], "钱钟书": ["围城"]}
    assert list(result) == ["刘慈欣", "余华", "钱钟书"]


def test_group_by_author_empty_and_generator():
    assert group_by_author([]) == {}
    assert group_by_author(book for book in BOOKS[:2]) == {"刘慈欣": ["三体"], "余华": ["活着"]}


@pytest.mark.parametrize(
    "k, expected",
    [
        (1, ["三体"]),
        (3, ["三体", "兄弟", "活着"]),
        (10, ["三体", "兄弟", "活着", "球状闪电", "围城"]),
        (0, []),
        (-1, []),
    ],
)
def test_top_sellers(k, expected):
    assert top_sellers(BOOKS, k) == expected


def test_top_sellers_does_not_modify_input():
    books = list(BOOKS)
    top_sellers(books, 2)
    assert books == BOOKS


@pytest.mark.parametrize("text, expected", [("¥12.50", 12.5), (" ¥0 ", 0.0), ("¥3", 3.0)])
def test_parse_price(text, expected):
    assert parse_price(text) == expected


@pytest.mark.parametrize("text", ["12.50", "$12", "", "¥-1"])
def test_parse_price_rejects(text):
    with pytest.raises(ValueError):
        parse_price(text)


def test_parse_price_chains_original_error():
    with pytest.raises(ValueError) as caught:
        parse_price("¥abc")
    assert isinstance(caught.value.__cause__, ValueError)


def test_running_totals():
    assert list(running_totals([3, 1, 4])) == [3, 4, 8]
    assert list(running_totals([])) == []
    assert inspect.isgeneratorfunction(running_totals)


def test_running_totals_is_lazy():
    assert list(islice(running_totals(count(1)), 4)) == [1, 3, 6, 10]


def test_shelf_basic_protocols():
    shelf = Shelf("小说", ["活着", "兄弟", "活着"])
    assert len(shelf) == 3
    assert shelf[0] == "活着"
    assert shelf[-1] == "活着"
    with pytest.raises(IndexError):
        shelf[3]
    assert list(shelf) == ["活着", "兄弟", "活着"]
    assert "兄弟" in shelf and "围城" not in shelf
    assert list(reversed(shelf)) == ["活着", "兄弟", "活着"]
    assert shelf.index("兄弟") == 1
    assert shelf.count("活着") == 2
    assert not Shelf("空")


def test_shelf_copies_titles():
    titles = ["活着"]
    shelf = Shelf("小说", titles)
    titles.append("兄弟")
    assert len(shelf) == 1


def test_shelf_equality():
    assert Shelf("小说", ["活着"]) == Shelf("小说", ["活着"])
    assert Shelf("小说", ["活着"]) != Shelf("文学", ["活着"])
    assert Shelf("小说", ["活着"]) != Shelf("小说", ["兄弟"])
    assert Shelf("小说", ["活着"]) != ["活着"]
    assert Shelf("小说", ["活着"]).__eq__(["活着"]) is NotImplemented


def test_all_titles():
    shelves = [Shelf("A", ["x"]), Shelf("B", []), Shelf("C", ["y", "z"])]
    assert list(all_titles(*shelves)) == ["x", "y", "z"]
    assert list(all_titles()) == []
    assert list(all_titles(["a"], (title for title in ["b", "c"]))) == ["a", "b", "c"]
    assert inspect.isgeneratorfunction(all_titles)


def test_all_titles_is_lazy():
    assert list(islice(all_titles(["a"], (f"t{number}" for number in count())), 3)) == ["a", "t0", "t1"]
