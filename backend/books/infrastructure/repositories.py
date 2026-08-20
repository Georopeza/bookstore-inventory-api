from decimal import Decimal

from books.application.ports import BookRepository, BookSnapshot
from books.models import Book


class DjangoBookRepository(BookRepository):
    """Adaptador de persistencia sobre el ORM de Django."""

    def get_by_id(self, book_id: int) -> BookSnapshot | None:
        row = Book.objects.filter(pk=book_id).values("id", "cost_usd").first()
        if row is None:
            return None
        return BookSnapshot(id=row["id"], cost_usd=row["cost_usd"])

    def update_selling_price(self, book_id: int, price: Decimal) -> None:
        # update() evita releer y reescribir la fila completa, y con ello el
        # riesgo de pisar cambios concurrentes en el resto de los campos.
        Book.objects.filter(pk=book_id).update(selling_price_local=price)
