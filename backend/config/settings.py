import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "local-development-only-not-for-production")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
INSTALLED_APPS = ["django.contrib.contenttypes", "rest_framework", "corsheaders"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://weather-aware-truck-routing-fronten-ruby.vercel.app").split(
    ","
)
REST_FRAMEWORK = {
    "UNAUTHENTICATED_USER": None,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "60/min", "analysis": "6/min"},
    "EXCEPTION_HANDLER": "trips.views.exception_handler",
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "spotter",
        "OPTIONS": {"MAX_ENTRIES": 2000},
    }
}
USE_TZ = True
TIME_ZONE = "UTC"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
if os.getenv("ENVIRONMENT") == "production":
    if SECRET_KEY.startswith("local-") or len(SECRET_KEY) < 32:
        raise RuntimeError("Set a strong DJANGO_SECRET_KEY for production.")
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
