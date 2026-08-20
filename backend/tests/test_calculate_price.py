from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest
import requests

from books.application.ports import (
    FALLBACK_RATE,
    LIVE_RATE,
    BookRepository,
    BookSnapshot,
    ExchangeRateProvider,
    RateQuote,
)
from books.application.use_cases.calculate_selling_price import CalculateSellingPrice
from books.domain.exceptions import BookNotFoundError, ExchangeRateUnavailableError
from books.infrastructure.exchange_rate.fallback_provider import StaticFallbackRateProvider
from books.infrastructure.exchange_rate.http_provider import ExchangeRateApiProvider
from books.infrastructure.exchange_rate.resilient import ResilientRateProvider


class FakeRateProvider(ExchangeRateProvider):
    def __init__(self, rate: Decimal, source: str = LIVE_RATE) -> None:
        self._rate = rate
        self._source = source

    def get_rate(self, base: str, target: str) -> RateQuote:
        return RateQuote(base, target, self._rate, self._source, datetime.now(timezone.utc))


class UnavailableRateProvider(ExchangeRateProvider):
    def get_rate(self, base: str, target: str) -> RateQuote:
        raise ExchangeRateUnavailableError("provider is down")


class InMemoryBookRepository(BookRepository):
    def __init__(self, books: dict[int, Decimal]) -> None:
        self._books = books
        self.saved_prices: dict[int, Decimal] = {}

    def get_by_id(self, book_id: int) -> BookSnapshot | None:
        cost = self._books.get(book_id)
        return None if cost is None else BookSnapshot(book_id, cost)

    def update_selling_price(self, book_id: int, price: Decimal) -> None:
        self.saved_prices[book_id] = price


def build_use_case(repo: InMemoryBookRepository, rates: ExchangeRateProvider):
    return CalculateSellingPrice(repo, rates, Decimal("40"), "USD")


def test_reproduces_the_figures_documented_in_the_contract():
    """15.99 USD a una tasa de 0.85 con 40% de margen da 13.59 y 19.03."""
    repo = InMemoryBookRepository({1: Decimal("15.99")})

    result = build_use_case(repo, FakeRateProvider(Decimal("0.85"))).execute(1, "EUR")

    assert result.cost_local == Decimal("13.59")
    assert result.selling_price_local == Decimal("19.03")
    assert result.currency == "EUR"
    assert result.rate_source == LIVE_RATE


def test_applies_the_margin_over_the_converted_cost_not_over_usd():
    repo = InMemoryBookRepository({1: Decimal("100.00")})

    result = build_use_case(repo, FakeRateProvider(Decimal("2"))).execute(1, "EUR")

    # Convertir y luego marcar: 100 -> 200 -> 280. Marcar antes daría 140 -> 280
    # con esta tasa, pero cost_local debe seguir siendo el costo sin margen.
    assert result.cost_local == Decimal("200.00")
    assert result.selling_price_local == Decimal("280.00")


def test_rounds_half_up_as_commercial_convention_requires():
    repo = InMemoryBookRepository({1: Decimal("10.005")})

    result = build_use_case(repo, FakeRateProvider(Decimal("1"))).execute(1, "EUR")

    assert result.cost_local == Decimal("10.01")


def test_persists_the_calculated_price():
    repo = InMemoryBookRepository({1: Decimal("15.99")})

    build_use_case(repo, FakeRateProvider(Decimal("0.85"))).execute(1, "EUR")

    assert repo.saved_prices == {1: Decimal("19.03")}


def test_raises_when_the_book_does_not_exist():
    repo = InMemoryBookRepository({})

    with pytest.raises(BookNotFoundError):
        build_use_case(repo, FakeRateProvider(Decimal("0.85"))).execute(404, "EUR")


def test_resilient_provider_falls_back_when_the_primary_fails():
    provider = ResilientRateProvider(
        primary=UnavailableRateProvider(),
        fallback=StaticFallbackRateProvider({"EUR": Decimal("0.85")}),
    )

    quote = provider.get_rate("USD", "EUR")

    assert quote.rate == Decimal("0.85")
    assert quote.source == FALLBACK_RATE


def test_resilient_provider_propagates_when_no_fallback_is_configured():
    provider = ResilientRateProvider(
        primary=UnavailableRateProvider(),
        fallback=StaticFallbackRateProvider({"EUR": Decimal("0.85")}),
    )

    with pytest.raises(ExchangeRateUnavailableError):
        provider.get_rate("USD", "JPY")


def test_http_provider_reports_the_provider_as_unavailable_on_network_error():
    provider = ExchangeRateApiProvider("https://example.invalid", timeout=1, cache_seconds=60)

    with patch("requests.get", side_effect=requests.ConnectionError("down")):
        with pytest.raises(ExchangeRateUnavailableError):
            provider.get_rate("USD", "EUR")


def test_http_provider_caches_the_rate_table():
    provider = ExchangeRateApiProvider("https://example.test", timeout=1, cache_seconds=60)
    payload = {"rates": {"EUR": 0.85}}

    with patch("requests.get") as get:
        get.return_value.json.return_value = payload
        get.return_value.raise_for_status.return_value = None

        provider.get_rate("USD", "EUR")
        provider.get_rate("USD", "EUR")

        assert get.call_count == 1


@pytest.mark.django_db
def test_endpoint_returns_the_price_and_stores_it(api, book):
    with patch("requests.get") as get:
        get.return_value.json.return_value = {"rates": {"EUR": 0.85}}
        get.return_value.raise_for_status.return_value = None

        response = api.post(f"/books/{book.id}/calculate-price", {}, format="json")

    assert response.status_code == 200
    assert response.data["selling_price_local"] == Decimal("19.03")
    assert response.data["rate_source"] == LIVE_RATE

    book.refresh_from_db()
    assert book.selling_price_local == Decimal("19.03")


@pytest.mark.django_db
def test_endpoint_still_prices_the_book_when_the_provider_is_down(api, book):
    with patch("requests.get", side_effect=requests.ConnectionError("down")):
        response = api.post(f"/books/{book.id}/calculate-price", {}, format="json")

    assert response.status_code == 200
    assert response.data["rate_source"] == FALLBACK_RATE


@pytest.mark.django_db
def test_endpoint_returns_503_when_no_rate_can_be_obtained(api, book):
    with patch("requests.get", side_effect=requests.ConnectionError("down")):
        response = api.post(
            f"/books/{book.id}/calculate-price", {"currency": "JPY"}, format="json"
        )

    assert response.status_code == 503
    assert response.data["error"]["code"] == 503


@pytest.mark.django_db
def test_endpoint_returns_404_for_an_unknown_book(api, db):
    assert api.post("/books/999999/calculate-price", {}, format="json").status_code == 404


@pytest.mark.django_db
def test_endpoint_rejects_a_malformed_currency(api, book):
    response = api.post(f"/books/{book.id}/calculate-price", {"currency": "EURO"}, format="json")

    assert response.status_code == 400


@pytest.mark.django_db
def test_endpoint_honours_the_currency_given_in_the_request(api, book):
    with patch("requests.get") as get:
        get.return_value.json.return_value = {"rates": {"COP": 3900}}
        get.return_value.raise_for_status.return_value = None

        response = api.post(
            f"/books/{book.id}/calculate-price", {"currency": "cop"}, format="json"
        )

    assert response.status_code == 200
    assert response.data["currency"] == "COP"
