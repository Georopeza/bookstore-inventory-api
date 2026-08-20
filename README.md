# Bookstore Inventory API

API REST para la gestión del inventario de una cadena de librerías, con cálculo
del precio de venta sugerido a partir de tasas de cambio en tiempo real, y una
SPA que consume la totalidad de los endpoints.

## Stack

| Capa | Tecnología |
| --- | --- |
| Backend | Python 3.12, Django 5.1, Django REST Framework |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Base de datos | SQLite por defecto, PostgreSQL bajo Docker |
| Pruebas | pytest, pytest-django |

## Requisitos previos

Para la ruta con Docker basta con **Docker** y **Docker Compose**.

Para la ejecución local se necesitan **Python 3.12+** y **Node.js 20.19+ o
22.12+**.

## Puesta en marcha

### Con Docker

```bash
docker compose up --build
```

Levanta PostgreSQL, la API en `http://localhost:8000` y la interfaz en
`http://localhost:5173`. Las migraciones se aplican al arrancar el contenedor
del backend.

### En local

**Backend**

```bash
cd backend
python -m venv .venv
```

Activa el entorno (`.venv\Scripts\activate` en Windows, `source .venv/bin/activate`
en Linux o macOS) y continúa:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_books
python manage.py runserver 8000
```

`seed_books` carga un catálogo de ejemplo de doce libros para poder probar la
interfaz de inmediato; es opcional y admite `--flush` para vaciar antes de
cargar.

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

La interfaz queda en `http://localhost:5173` y espera la API en la URL indicada
por `VITE_API_BASE_URL` (por defecto `http://localhost:8000`). Copia
`.env.example` a `.env` para modificarla.

## Variables de entorno

Copia `.env.example` a `.env` en la raíz del proyecto. Todas tienen un valor por
defecto razonable para desarrollo.

| Variable | Por defecto | Descripción |
| --- | --- | --- |
| `SECRET_KEY` | clave de desarrollo | Clave de firma de Django |
| `DEBUG` | `True` | Modo de depuración |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0` | Hosts admitidos |
| `DATABASE_URL` | SQLite local | Cadena de conexión a la base de datos |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Orígenes autorizados |
| `LOCAL_CURRENCY` | `EUR` | Moneda local del cálculo de precio |
| `PROFIT_MARGIN_PERCENTAGE` | `40` | Margen aplicado sobre el costo convertido |
| `EXCHANGE_RATE_API_URL` | exchangerate-api | Proveedor de tasas |
| `EXCHANGE_RATE_TIMEOUT_SECONDS` | `5` | Tiempo máximo de espera |
| `EXCHANGE_RATE_CACHE_SECONDS` | `600` | Vigencia de la tasa en caché |

## Endpoints

Todas las rutas admiten opcionalmente la barra final.

| Método | Ruta | Descripción |
| --- | --- | --- |
| `POST` | `/books` | Crear libro |
| `GET` | `/books` | Listar libros (paginación opcional) |
| `GET` | `/books/{id}` | Obtener libro por ID |
| `PUT` | `/books/{id}` | Actualizar libro |
| `DELETE` | `/books/{id}` | Eliminar libro |
| `GET` | `/books/search?category=` | Buscar por categoría |
| `GET` | `/books/low-stock?threshold=10` | Libros con stock bajo |
| `POST` | `/books/{id}/calculate-price` | Calcular precio de venta sugerido |

### Crear un libro

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "El Quijote",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": 15.99,
    "stock_quantity": 25,
    "category": "Literatura Clasica",
    "supplier_country": "ES"
  }'
```

```json
{
  "id": 1,
  "title": "El Quijote",
  "author": "Miguel de Cervantes",
  "isbn": "9788437604947",
  "cost_usd": 15.99,
  "selling_price_local": null,
  "stock_quantity": 25,
  "category": "Literatura Clasica",
  "supplier_country": "ES",
  "created_at": "2026-08-20T10:30:00Z",
  "updated_at": "2026-08-20T10:30:00Z"
}
```

### Listar con paginación

Sin el parámetro `page` la respuesta es una lista plana. Con él se envuelve en
la forma paginada:

```bash
curl "http://localhost:8000/books?page=1&page_size=5"
```

```json
{
  "count": 12,
  "next": "http://localhost:8000/books?page=2&page_size=5",
  "previous": null,
  "results": [ ... ]
}
```

### Buscar y filtrar

```bash
curl "http://localhost:8000/books/search?category=Novela"
curl "http://localhost:8000/books/low-stock?threshold=10"
```

### Calcular el precio de venta

```bash
curl -X POST http://localhost:8000/books/1/calculate-price \
  -H "Content-Type: application/json" -d '{}'
```

```json
{
  "book_id": 1,
  "cost_usd": 15.99,
  "exchange_rate": 0.85,
  "cost_local": 13.59,
  "margin_percentage": 40,
  "selling_price_local": 19.03,
  "currency": "EUR",
  "rate_source": "live",
  "calculation_timestamp": "2026-08-20T10:30:00Z"
}
```

La moneda puede indicarse por petición con `{"currency": "COP"}`.

### Formato de error

Todos los errores comparten una misma envoltura, de modo que el cliente tenga
un único contrato que interpretar:

```json
{
  "error": {
    "code": 400,
    "message": "Validation failed",
    "details": { "isbn": ["A book with this ISBN already exists."] }
  }
}
```

| Código | Cuándo |
| --- | --- |
| `400` | Datos inválidos o que incumplen una regla de negocio |
| `404` | El libro no existe |
| `500` | Error inesperado del servidor |
| `503` | No hay tasa disponible, ni remota ni de respaldo |

## Reglas de negocio

- `cost_usd` debe ser mayor que 0.
- `stock_quantity` no puede ser negativo.
- El ISBN debe tener 10 o 13 dígitos, con guiones o espacios opcionales.
- No se admiten dos libros con el mismo ISBN.
- Si el proveedor de tasas falla, se usa la tasa por defecto configurada.

Las dos primeras se aplican además como restricciones `CHECK` en la base de
datos: la validación protege a la API, y las restricciones protegen a los datos
frente a cualquier otra vía de escritura.

## Decisiones de diseño

El enunciado deja cuatro puntos abiertos. Estas son las decisiones tomadas y su
motivo.

**La "moneda local" no está definida.** Se parametriza mediante
`LOCAL_CURRENCY`, con `EUR` por defecto para coincidir con el ejemplo del
enunciado, y puede sobrescribirse en cada petición. Fijarla en el código habría
atado el servicio a un único mercado.

**Qué hacer cuando falla el proveedor de tasas.** El enunciado pide a la vez
usar una tasa por defecto y contemplar el 503, que no pueden ser el mismo caso.
La API devuelve **200** con `rate_source: "fallback"` cuando el proveedor falla
pero existe una tasa de respaldo para esa moneda, y reserva el **503** para
cuando no hay ninguna forma de obtener la tasa. El campo `rate_source` es una
adición al contrato original: sin él, el cliente no podría distinguir un precio
calculado con una cotización real de otro calculado con una tasa fija, que es
una diferencia que el negocio necesita conocer.

**Sobre qué importe se aplica el margen.** Se convierte primero y se marca
después. Es lo que reproduce las cifras del propio enunciado: 15.99 USD a una
tasa de 0.85 da 13.59, y ese importe con un 40% da 19.03. Todo el cálculo usa
`Decimal` con redondeo `ROUND_HALF_UP`, nunca coma flotante, porque en punto
flotante ese 19.026 puede acabar en 19.02.

**Validación del ISBN.** Se comprueba la forma (10 o 13 dígitos) pero no el
dígito de control, que es lo que pide literalmente el enunciado; validar el
checksum rechazaría ISBN inventados durante una prueba manual. El código se
almacena normalizado, sin separadores, para que la restricción de unicidad no
pueda burlarse escribiendo el mismo ISBN con guiones distintos.

Además, el umbral de stock bajo es **inclusivo**: `threshold=10` incluye los
libros con exactamente 10 unidades, que ya están en el límite de reposición.

## Arquitectura

El backend separa el dominio de la infraestructura donde esa separación aporta
algo, que es la integración externa:

```
books/
├── domain/           value objects (ISBN, redondeo monetario) y errores
├── application/
│   ├── ports.py      ExchangeRateProvider, BookRepository
│   └── use_cases/    CalculateSellingPrice
├── infrastructure/
│   ├── models.py     modelo de Django
│   ├── repositories.py
│   ├── exchange_rate/  adaptador HTTP, adaptador de respaldo, composición
│   └── factories.py  punto de composición
└── api/              serializers, viewset, rutas, manejo de errores
```

El caso de uso del cálculo de precio depende solo de dos abstracciones y
desconoce tanto Django como `requests`. La infraestructura aporta un adaptador
HTTP con caché, un adaptador de tasas fijas y un tercero que los compone: si el
primero falla, delega en el segundo, y si ninguno cotiza la moneda el error se
propaga hasta convertirse en un 503. Añadir un proveedor nuevo no obliga a
tocar la lógica de negocio, y las pruebas del cálculo se ejecutan con dobles en
memoria sin tocar la red.

El CRUD se resuelve con las herramientas propias de Django REST Framework: un
`ViewSet` ya es el adaptador de entrada del modelo hexagonal, y envolverlo en
capas adicionales habría añadido indirección sin ganar nada.

El frontend mantiene la misma dirección de dependencias hacia dentro:
`pages` → `hooks` → `api` → `types`, con componentes de presentación que
desconocen el transporte HTTP.

## Pruebas

```bash
cd backend
pytest -v
```

39 pruebas que cubren el objeto de valor ISBN, las reglas de negocio sobre los
endpoints CRUD y el cálculo de precio, incluidas la ruta de respaldo y la de
tasa no disponible.

## Colección de Postman

En `postman/bookstore-inventory-api.postman_collection.json`. Se importa desde
Postman con *Import → File*. La variable `base_url` apunta a
`http://localhost:8000`; la petición de creación guarda automáticamente el `id`
del libro en `book_id` para reutilizarlo en el resto de peticiones.

Incluye una carpeta de errores con casos que devuelven 400, 404 y 503.

## Resolución de problemas

**`Cannot find native binding` al compilar el frontend.** Es un fallo conocido
de npm con las dependencias opcionales. Se resuelve reinstalando:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**La interfaz no muestra datos.** Verifica que la API responde en
`http://localhost:8000/books` y que `VITE_API_BASE_URL` apunta a esa dirección.
