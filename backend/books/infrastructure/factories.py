"""Punto de composición: aquí se eligen las implementaciones concretas.

Es el único lugar del backend que conoce a la vez los puertos y sus
adaptadores; el caso de uso recibe ya resueltas sus dependencias.
"""

from django.conf import settings

from books.application.use_cases.calculate_selling_price import CalculateSellingPrice

from .exchange_rate.fallback_provider import StaticFallbackRateProvider
from .exchange_rate.http_provider import ExchangeRateApiProvider
from .exchange_rate.resilient import ResilientRateProvider
from .repositories import DjangoBookRepository


def build_calculate_selling_price() -> CalculateSellingPrice:
    rates = ResilientRateProvider(
        primary=ExchangeRateApiProvider(
            base_url=settings.EXCHANGE_RATE_API_URL,
            timeout=settings.EXCHANGE_RATE_TIMEOUT_SECONDS,
            cache_seconds=settings.EXCHANGE_RATE_CACHE_SECONDS,
        ),
        fallback=StaticFallbackRateProvider(settings.FALLBACK_EXCHANGE_RATES),
    )
    return CalculateSellingPrice(
        books=DjangoBookRepository(),
        rates=rates,
        margin_percentage=settings.PROFIT_MARGIN_PERCENTAGE,
        base_currency=settings.BASE_CURRENCY,
    )
