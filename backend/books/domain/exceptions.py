"""Errores de dominio, independientes del framework web."""


class DomainError(Exception):
    """Raíz de los errores originados por una regla de negocio."""


class InvalidISBNError(DomainError):
    pass


class ExchangeRateUnavailableError(DomainError):
    """No hay forma de obtener una tasa: ni el proveedor remoto ni el respaldo."""


class BookNotFoundError(DomainError):
    pass
