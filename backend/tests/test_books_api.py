import pytest

from books.models import Book

pytestmark = pytest.mark.django_db


def test_creates_a_book_and_normalizes_its_isbn(api, book_payload):
    response = api.post("/books", book_payload, format="json")

    assert response.status_code == 201
    assert response.data["isbn"] == "9788437604947"
    # El precio de venta solo lo fija el cálculo de precio.
    assert response.data["selling_price_local"] is None


def test_rejects_a_duplicate_isbn_written_with_other_separators(api, book_payload):
    api.post("/books", book_payload, format="json")

    response = api.post("/books", {**book_payload, "isbn": "9788437604947"}, format="json")

    assert response.status_code == 400
    assert "isbn" in response.data["error"]["details"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("isbn", "123"),
        ("cost_usd", "0"),
        ("cost_usd", "-1.00"),
        ("stock_quantity", -1),
        ("supplier_country", "ESP"),
    ],
)
def test_rejects_values_that_break_a_business_rule(api, book_payload, field, value):
    response = api.post("/books", {**book_payload, field: value}, format="json")

    assert response.status_code == 400
    assert field in response.data["error"]["details"]


def test_selling_price_cannot_be_set_through_the_crud_endpoints(api, book_payload):
    response = api.post("/books", {**book_payload, "selling_price_local": "99.99"}, format="json")

    assert response.status_code == 201
    assert response.data["selling_price_local"] is None


def test_returns_404_for_an_unknown_book(api):
    response = api.get("/books/999999")

    assert response.status_code == 404
    assert response.data["error"]["code"] == 404


def test_updates_and_deletes_a_book(api, book, book_payload):
    updated = api.put(f"/books/{book.id}", {**book_payload, "stock_quantity": 99}, format="json")
    assert updated.status_code == 200
    assert updated.data["stock_quantity"] == 99

    assert api.delete(f"/books/{book.id}").status_code == 204
    assert not Book.objects.filter(pk=book.id).exists()


def test_listing_is_unpaginated_unless_a_page_is_requested(api, book):
    assert isinstance(api.get("/books").data, list)

    paginated = api.get("/books?page=1&page_size=1").data
    assert paginated["count"] == 1
    assert len(paginated["results"]) == 1


def test_searches_by_category(api, book):
    assert len(api.get("/books/search?category=literatura").data) == 1
    assert len(api.get("/books/search?category=Poesia").data) == 0
    assert api.get("/books/search").status_code == 400


def test_low_stock_uses_an_inclusive_threshold(api, book):
    book.stock_quantity = 10
    book.save()

    assert len(api.get("/books/low-stock?threshold=10").data) == 1
    assert len(api.get("/books/low-stock?threshold=9").data) == 0
    assert api.get("/books/low-stock?threshold=abc").status_code == 400
