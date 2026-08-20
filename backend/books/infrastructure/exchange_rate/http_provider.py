import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import requests
from django.core.cache import cache

from books.application.ports import LIVE_RATE, ExchangeRateProvider, RateQuote
from books.domain.exceptions import ExchangeRateUnavailableError

logger = logging.getLogger(__name__)


class ExchangeRateApiProvider(ExchangeRateProvider):
    """Obtiene tasas de exchangerate-api.

    La respuesta trae todas las monedas para una base dada, así que se cachea
    el mapa completo: pedir varias monedas seguidas cuesta una sola llamada.
    """

    def __init__(self, base_url: str, timeout: float, cache_seconds: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._cache_seconds = cache_seconds

    def get_rate(self, base: str, target: str) -> RateQuote:
        rates = self._rates_for(base)
        try:
            rate = Decimal(str(rates[target]))
        except (KeyError, InvalidOperation, TypeError) as exc:
            raise ExchangeRateUnavailableError(
                f"The rate provider does not quote {target}"
            ) from exc

        return RateQuote(
            base=base,
            target=target,
            rate=rate,
            source=LIVE_RATE,
            retrieved_at=datetime.now(timezone.utc),
        )

    def _rates_for(self, base: str) -> dict:
        cache_key = f"exchange-rates:{base}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            response = requests.get(f"{self._base_url}/{base}", timeout=self._timeout)
            response.raise_for_status()
            rates = response.json()["rates"]
        except (requests.RequestException, ValueError, KeyError) as exc:
            logger.warning("Exchange rate provider unavailable: %s", exc)
            raise ExchangeRateUnavailableError(str(exc)) from exc

        cache.set(cache_key, rates, self._cache_seconds)
        return rates
