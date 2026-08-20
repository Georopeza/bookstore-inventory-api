from collections.abc import Mapping
from datetime import datetime, timezone
from decimal import Decimal

from books.application.ports import FALLBACK_RATE, ExchangeRateProvider, RateQuote
from books.domain.exceptions import ExchangeRateUnavailableError


class StaticFallbackRateProvider(ExchangeRateProvider):
    """Tasas fijas de configuración, usadas cuando el proveedor remoto falla.

    Solo cotiza contra la moneda base del mapa configurado. Una moneda ausente
    no se aproxima: es preferible un 503 explícito a devolver un precio que el
    negocio no puede sostener.
    """

    def __init__(self, rates: Mapping[str, Decimal], base: str = "USD") -> None:
        self._rates = rates
        self._base = base

    def get_rate(self, base: str, target: str) -> RateQuote:
        if base != self._base:
            raise ExchangeRateUnavailableError(
                f"No fallback rates are configured for base {base}"
            )

        rate = self._rates.get(target)
        if rate is None:
            raise ExchangeRateUnavailableError(
                f"No fallback rate is configured for {target}"
            )

        return RateQuote(
            base=base,
            target=target,
            rate=Decimal(str(rate)),
            source=FALLBACK_RATE,
            retrieved_at=datetime.now(timezone.utc),
        )
