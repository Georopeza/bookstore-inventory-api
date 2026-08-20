import pytest

from books.domain.exceptions import InvalidISBNError
from books.domain.value_objects import ISBN


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("978-84-376-0494-7", "9788437604947"),
        ("9788437604947", "9788437604947"),
        ("0 306 40615 2", "0306406152"),
        ("030640615x", "030640615X"),
    ],
)
def test_parses_and_normalizes_valid_isbn(raw, expected):
    assert ISBN.parse(raw).value == expected


@pytest.mark.parametrize(
    "raw", ["123", "97884376049477", "abcdefghij", "", None, "97884376049X7"]
)
def test_rejects_malformed_isbn(raw):
    with pytest.raises(InvalidISBNError):
        ISBN.parse(raw)


def test_same_isbn_written_differently_is_the_same_value():
    assert ISBN.parse("978-84-376-0494-7") == ISBN.parse("9788437604947")
