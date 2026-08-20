from django.core.validators import MinValueValidator
from django.db import models


class Book(models.Model):
    """Libro del inventario.

    Las reglas de negocio se declaran además como restricciones de base de
    datos: la validación en el serializer protege a la API, y las constraints
    protegen a los datos frente a cualquier otra vía de escritura.
    """

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    cost_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    selling_price_local = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Lo calcula el endpoint calculate-price; nace vacío.",
    )
    stock_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    category = models.CharField(max_length=120)
    supplier_country = models.CharField(max_length=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["stock_quantity"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cost_usd__gt=0),
                name="book_cost_usd_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(stock_quantity__gte=0),
                name="book_stock_quantity_not_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.isbn})"
