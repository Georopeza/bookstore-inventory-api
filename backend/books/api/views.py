from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from books.models import Book

from .serializers import BookSerializer

DEFAULT_LOW_STOCK_THRESHOLD = 10


class BookViewSet(viewsets.ModelViewSet):
    """Adaptador de entrada HTTP para el inventario de libros."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def _paginated(self, queryset) -> Response:
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request: Request) -> Response:
        category = request.query_params.get("category", "").strip()
        if not category:
            raise ValidationError({"category": "This query parameter is required."})
        return self._paginated(self.get_queryset().filter(category__icontains=category))

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request: Request) -> Response:
        raw = request.query_params.get("threshold", DEFAULT_LOW_STOCK_THRESHOLD)
        try:
            threshold = int(raw)
        except (TypeError, ValueError):
            raise ValidationError({"threshold": "Must be an integer."}) from None
        if threshold < 0:
            raise ValidationError({"threshold": "Must be zero or greater."})

        # Inclusivo: un umbral de 10 incluye a los libros con exactamente 10
        # unidades, que ya están en el límite de reposición.
        return self._paginated(self.get_queryset().filter(stock_quantity__lte=threshold))
