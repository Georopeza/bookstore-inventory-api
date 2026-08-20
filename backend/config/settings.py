"""Django settings for the bookstore inventory API."""

import os
from decimal import Decimal
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR.parent / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-local-development-key")
DEBUG = env_bool("DEBUG", True)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "books",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# SQLite por defecto para que el revisor pueda clonar y ejecutar sin instalar
# un motor de base de datos; DATABASE_URL apunta a Postgres bajo docker-compose.
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "books.api.pagination.BookPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "EXCEPTION_HANDLER": "books.api.exception_handler.api_exception_handler",
}

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "exchange-rates",
    }
}

# --- Reglas de negocio ---------------------------------------------------

# El enunciado nunca define cuál es la "moneda local", así que se parametriza.
# EUR es el valor por defecto porque es la moneda del ejemplo del enunciado.
LOCAL_CURRENCY = os.getenv("LOCAL_CURRENCY", "EUR")
BASE_CURRENCY = "USD"

PROFIT_MARGIN_PERCENTAGE = Decimal(os.getenv("PROFIT_MARGIN_PERCENTAGE", "40"))

EXCHANGE_RATE_API_URL = os.getenv(
    "EXCHANGE_RATE_API_URL", "https://api.exchangerate-api.com/v4/latest"
)
EXCHANGE_RATE_TIMEOUT_SECONDS = float(os.getenv("EXCHANGE_RATE_TIMEOUT_SECONDS", "5"))
EXCHANGE_RATE_CACHE_SECONDS = int(os.getenv("EXCHANGE_RATE_CACHE_SECONDS", "600"))

# Tasas usadas cuando el proveedor HTTP no responde. Una moneda ausente de este
# mapa provoca 503 en lugar de devolver un precio inventado.
FALLBACK_EXCHANGE_RATES = {
    "EUR": Decimal("0.85"),
    "COP": Decimal("3900.00"),
    "MXN": Decimal("17.00"),
    "GBP": Decimal("0.79"),
    "USD": Decimal("1.00"),
}
