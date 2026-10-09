import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = []
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware",
              "whitenoise.middleware.WhiteNoiseMiddleware"]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DATABASES = {}
USE_TZ = True
WHITENOISE_ROOT = BASE_DIR / "frontend_dist"   # built React app (served at /)
WHITENOISE_INDEX_FILE = True
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
TRUCK_TIME_FACTOR = float(os.environ.get("TRUCK_TIME_FACTOR", "1.1"))  # OSRM is car-speed
