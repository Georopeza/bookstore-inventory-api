"""Objetos de valor del dominio de inventario."""

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .exceptions import InvalidISBNError

_ISBN_SEPARATORS = re.compile(r"[\s\-]")
_ISBN_10 = re.compile(r"^\d{9}[\dX]$")
_ISBN_13 = re.compile(r"^\d{13}$")

MONEY_PRECISION = Decimal("0.01")


def quantize_money(amount: Decimal) -> Decimal:
    """Redondea un importe monetario a dos decimales.

    Se usa ROUND_HALF_UP porque es la convención comercial; el modo por defecto
    de Decimal (ROUND_HALF_EVEN) redondearía 19.025 a 19.02 en lugar de 19.03.
    """
    return amount.quantize(MONEY_PRECISION, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ISBN:
    """ISBN normalizado, sin separadores.

    Se persiste en forma normalizada para que la restricción de unicidad no
    pueda burlarse escribiendo el mismo código con guiones distintos
    ("978-84-376-0494-7" y "9788437604947" son el mismo libro).

    Se valida únicamente la forma (10 o 13 dígitos, con X admitida como dígito
    de control en ISBN-10) y no el checksum, tal como pide el enunciado.
    """

    value: str

    @classmethod
    def parse(cls, raw: str) -> "ISBN":
        if raw is None:
            raise InvalidISBNError("ISBN is required")

        normalized = _ISBN_SEPARATORS.sub("", str(raw)).upper()

        if not (_ISBN_10.match(normalized) or _ISBN_13.match(normalized)):
            raise InvalidISBNError(
                "ISBN must contain 10 or 13 digits, optionally separated by "
                "hyphens or spaces"
            )

        return cls(normalized)

    def __str__(self) -> str:
        return self.value
