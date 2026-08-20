from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    """Envuelve las respuestas de error de DRF en una forma uniforme.

    Todo error de la API responde con `{"error": {"code", "message", "details"}}`
    para que el cliente tenga un único contrato que interpretar.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data
    message = "Request failed"
    details = None

    if isinstance(detail, dict) and "detail" in detail:
        message = str(detail["detail"])
    elif isinstance(detail, dict):
        message = "Validation failed"
        details = detail
    elif isinstance(detail, list):
        message = "Validation failed"
        details = {"non_field_errors": detail}

    response.data = {
        "error": {
            "code": response.status_code,
            "message": message,
            "details": details,
        }
    }
    return response
