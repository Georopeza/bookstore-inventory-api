from decimal import Decimal

from rest_framework import serializers

from books.domain.exceptions import InvalidISBNError
from books.domain.value_objects import ISBN
from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    # El ISBN se declara sin los validadores que ModelSerializer deriva de
    # unique=True: esos correrían sobre el valor crudo, antes de normalizar, y
    # dejarían pasar un duplicado escrito con otros separadores.
    isbn = serializers.CharField(max_length=17, validators=[])
    cost_usd = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )
    stock_quantity = serializers.IntegerField(min_value=0)
    # Se acepta una entrada más larga que el campo para que el error lo
    # produzca el validador de abajo, con un mensaje que explica el formato.
    supplier_country = serializers.CharField(max_length=8)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "isbn",
            "cost_usd",
            "selling_price_local",
            "stock_quantity",
            "category",
            "supplier_country",
            "created_at",
            "updated_at",
        ]
        # selling_price_local es de solo lectura porque su único origen
        # legítimo es el endpoint de cálculo de precio.
        read_only_fields = ["id", "selling_price_local", "created_at", "updated_at"]

    def validate_isbn(self, value: str) -> str:
        try:
            isbn = ISBN.parse(value)
        except InvalidISBNError as exc:
            raise serializers.ValidationError(str(exc)) from exc

        duplicates = Book.objects.filter(isbn=isbn.value)
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("A book with this ISBN already exists.")

        return isbn.value

    def validate_supplier_country(self, value: str) -> str:
        code = value.strip().upper()
        if len(code) != 2 or not code.isalpha():
            raise serializers.ValidationError(
                "supplier_country must be a two-letter country code."
            )
        return code
