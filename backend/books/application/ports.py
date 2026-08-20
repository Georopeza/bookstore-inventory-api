"""Puertos: las abstracciones de las que depende la capa de aplicación.

Los casos de uso hablan únicamente con estas interfaces, nunca con Django ni
con `requests`. Eso permite ejercitarlos con dobles de prueba y sustituir el
origen de las tasas sin tocar la lógica de negocio.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

LIVE_RATE = "live"
FALLBACK_RATE = "fallback"


@dataclass(frozen=True)
class RateQuote:
    """Tasa de cambio junto con su procedencia.

    `source` viaja hasta la respuesta HTTP para que el consumidor sepa si el
    precio se calculó con una tasa real o con el respaldo configurado.
    """

    base: str
    target: str
    rate: Decimal
    source: str
    retrieved_at: datetime


@dataclass(frozen=True)
class BookSnapshot:
    """Los únicos datos del libro que el cálculo de precio necesita."""

    id: int
    cost_usd: Decimal


class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rate(self, base: str, target: str) -> RateQuote:
        """Devuelve la tasa base->target o lanza ExchangeRateUnavailableError."""


class BookRepository(ABC):
    @abstractmethod
    def get_by_id(self, book_id: int) -> BookSnapshot | None: ...

    @abstractmethod
    def update_selling_price(self, book_id: int, price: Decimal) -> None: ...
