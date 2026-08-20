from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from books.models import Book


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def book_payload() -> dict:
    return {
        "title": "El Quijote",
        "author": "Miguel de Cervantes",
        "isbn": "978-84-376-0494-7",
        "cost_usd": "15.99",
        "stock_quantity": 25,
        "category": "Literatura Clasica",
        "supplier_country": "ES",
    }


@pytest.fixture
def book(db) -> Book:
    return Book.objects.create(
        title="El Quijote",
        author="Miguel de Cervantes",
        isbn="9788437604947",
        cost_usd=Decimal("15.99"),
        stock_quantity=25,
        category="Literatura Clasica",
        supplier_country="ES",
    )


@pytest.fixture(autouse=True)
def clear_rate_cache():
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()
