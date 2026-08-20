from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.views import exception_handler as drf_exception_handler

from books.domain.exceptions import BookNotFoundError, ExchangeRateUnavailableError


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = (
        "The exchange rate service is unavailable and no fallback rate is "
        "configured for the requested currency."
    )


def _to_api_exception(exc: Exception) -> Exception:
    """Traduce los errores de dominio al vocabulario HTTP.

    El dominio y los casos de uso desconocen los códigos de estado; la
    correspondencia vive aquí, en el borde de la aplicación.
    """
    if isinstance(exc, BookNotFoundError):
        return NotFound(str(exc))
    if isinstance(exc, ExchangeRateUnavailableError):
        return ServiceUnavailable(str(exc) or None)
    return exc


def api_exception_handler(exc, context):
    """Envuelve las respuestas de error en una forma uniforme.

    Todo error responde con `{"error": {"code", "message", "details"}}`, de modo
    que el cliente tenga un único contrato que interpretar.
    """
    response = drf_exception_handler(_to_api_exception(exc), context)
    if response is None:
        return None

    payload = response.data
    message = "Request failed"
    details = None

    if isinstance(payload, dict) and "detail" in payload:
        message = str(payload["detail"])
    elif isinstance(payload, dict):
        message = "Validation failed"
        details = payload
    elif isinstance(payload, list):
        message = "Validation failed"
        details = {"non_field_errors": payload}

    response.data = {
        "error": {
            "code": response.status_code,
            "message": message,
            "details": details,
        }
    }
    return response
