"""Caso de uso: calcular y persistir el precio de venta sugerido."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

from books.application.ports import BookRepository, ExchangeRateProvider
from books.domain.exceptions import BookNotFoundError
from books.domain.value_objects import quantize_money

ONE_HUNDRED = Decimal("100")


@dataclass(frozen=True)
class PriceCalculation:
    book_id: int
    cost_usd: Decimal
    exchange_rate: Decimal
    cost_local: Decimal
    margin_percentage: Decimal
    selling_price_local: Decimal
    currency: str
    rate_source: str
    calculation_timestamp: datetime


class CalculateSellingPrice:
    def __init__(
        self,
        books: BookRepository,
        rates: ExchangeRateProvider,
        margin_percentage: Decimal,
        base_currency: str,
    ) -> None:
        self._books = books
        self._rates = rates
        self._margin_percentage = margin_percentage
        self._base_currency = base_currency

    def execute(self, book_id: int, currency: str) -> PriceCalculation:
        book = self._books.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError(f"Book {book_id} does not exist")

        quote = self._rates.get_rate(self._base_currency, currency)

        # El margen se aplica sobre el costo ya convertido, no sobre el costo en
        # dólares: convertir primero y marcar después es lo que reproduce las
        # cifras del contrato (15.99 USD a 0.85 da 13.59, y 13.59 da 19.03).
        cost_local = quantize_money(book.cost_usd * quote.rate)
        multiplier = Decimal("1") + (self._margin_percentage / ONE_HUNDRED)
        selling_price_local = quantize_money(cost_local * multiplier)

        self._books.update_selling_price(book.id, selling_price_local)

        return PriceCalculation(
            book_id=book.id,
            cost_usd=book.cost_usd,
            exchange_rate=quote.rate,
            cost_local=cost_local,
            margin_percentage=self._margin_percentage,
            selling_price_local=selling_price_local,
            currency=currency,
            rate_source=quote.source,
            calculation_timestamp=datetime.now(timezone.utc),
        )
