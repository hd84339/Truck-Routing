import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "False") == "True"

_allowed = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(",") if h.strip()] if _allowed else ["localhost", "127.0.0.1"]

INSTALLED_APPS = ["corsheaders"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

_cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(",") if o.strip()] if _cors_origins else ["http://localhost:5173"]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {}
USE_TZ = True
WHITENOISE_ROOT = BASE_DIR / "frontend_dist"   # built React app (served at /)
WHITENOISE_INDEX_FILE = True
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
TRUCK_TIME_FACTOR = float(os.environ.get("TRUCK_TIME_FACTOR", "1.1"))  # OSRM is car-speed
