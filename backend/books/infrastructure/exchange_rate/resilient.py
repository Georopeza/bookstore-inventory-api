import logging

from books.application.ports import ExchangeRateProvider, RateQuote
from books.domain.exceptions import ExchangeRateUnavailableError

logger = logging.getLogger(__name__)


class ResilientRateProvider(ExchangeRateProvider):
    """Compone un proveedor principal con uno de respaldo.

    Es a su vez un ExchangeRateProvider, de modo que el caso de uso no sabe si
    habla con una fuente o con una cadena de ellas. Si el respaldo tampoco
    cotiza la moneda, el error se propaga y la API responde 503.
    """

    def __init__(
        self, primary: ExchangeRateProvider, fallback: ExchangeRateProvider
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    def get_rate(self, base: str, target: str) -> RateQuote:
        try:
            return self._primary.get_rate(base, target)
        except ExchangeRateUnavailableError:
            logger.warning("Falling back to the configured %s/%s rate", base, target)
            return self._fallback.get_rate(base, target)
