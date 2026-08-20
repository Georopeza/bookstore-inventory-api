from decimal import Decimal

from django.core.management.base import BaseCommand

from books.models import Book

SAMPLE_BOOKS = [
    ("El Quijote", "Miguel de Cervantes", "9788437604947", "15.99", 25, "Literatura Clasica", "ES"),
    ("Rayuela", "Julio Cortazar", "9788437604954", "18.50", 4, "Novela", "AR"),
    ("Ficciones", "Jorge Luis Borges", "9788420633121", "12.75", 8, "Cuento", "AR"),
    ("Cien anos de soledad", "Gabriel Garcia Marquez", "9788497592208", "21.00", 40, "Novela", "CO"),
    ("La casa de los espiritus", "Isabel Allende", "9788401242144", "17.30", 2, "Novela", "CL"),
    ("Pedro Paramo", "Juan Rulfo", "9788437604961", "10.99", 15, "Novela", "MX"),
    ("Veinte poemas de amor", "Pablo Neruda", "9788437604978", "9.50", 6, "Poesia", "CL"),
    ("El Aleph", "Jorge Luis Borges", "9788420633138", "14.25", 33, "Cuento", "AR"),
    ("La ciudad y los perros", "Mario Vargas Llosa", "9788420471839", "19.80", 11, "Novela", "PE"),
    ("Los detectives salvajes", "Roberto Bolano", "9788433920423", "23.40", 1, "Novela", "CL"),
    ("Historia universal de la infamia", "Jorge Luis Borges", "9788420633145", "11.60", 18, "Cuento", "AR"),
    ("Poeta en Nueva York", "Federico Garcia Lorca", "9788437604985", "13.10", 9, "Poesia", "ES"),
]


class Command(BaseCommand):
    help = "Carga un catálogo de ejemplo para probar la API y la interfaz."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Elimina los libros existentes antes de cargar el ejemplo.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            deleted, _ = Book.objects.all().delete()
            self.stdout.write(f"Se eliminaron {deleted} registros.")

        created = 0
        for title, author, isbn, cost, stock, category, country in SAMPLE_BOOKS:
            _, was_created = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    "title": title,
                    "author": author,
                    "cost_usd": Decimal(cost),
                    "stock_quantity": stock,
                    "category": category,
                    "supplier_country": country,
                },
            )
            created += was_created

        self.stdout.write(
            self.style.SUCCESS(f"{created} libros añadidos ({Book.objects.count()} en total).")
        )
