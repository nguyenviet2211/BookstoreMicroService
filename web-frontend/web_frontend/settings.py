import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "web-frontend-secret-key-change-me")
DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "web_frontend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "app.context_processors.cart_count",
            ],
        },
    },
]

WSGI_APPLICATION = "web_frontend.wsgi.application"

DATABASES = {}

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Microservice URLs
STAFF_SERVICE_URL = os.environ.get("STAFF_SERVICE_URL", "http://localhost:8001")
MANAGER_SERVICE_URL = os.environ.get("MANAGER_SERVICE_URL", "http://localhost:8002")
CUSTOMER_SERVICE_URL = os.environ.get("CUSTOMER_SERVICE_URL", "http://localhost:8003")
CATALOG_SERVICE_URL = os.environ.get("CATALOG_SERVICE_URL", "http://localhost:8004")
BOOK_SERVICE_URL = os.environ.get("BOOK_SERVICE_URL", "http://localhost:8005")
CART_SERVICE_URL = os.environ.get("CART_SERVICE_URL", "http://localhost:8006")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://localhost:8007")
SHIP_SERVICE_URL = os.environ.get("SHIP_SERVICE_URL", "http://localhost:8008")
PAY_SERVICE_URL = os.environ.get("PAY_SERVICE_URL", "http://localhost:8009")
COMMENT_SERVICE_URL = os.environ.get("COMMENT_SERVICE_URL", "http://localhost:8010")
RECOMMENDER_SERVICE_URL = os.environ.get("RECOMMENDER_SERVICE_URL", "http://localhost:8011")
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL", "http://localhost:8000")

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
