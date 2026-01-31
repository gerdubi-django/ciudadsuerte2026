import os
from pathlib import Path

# =======================================
# RUTAS BASE DEL PROYECTO
# =======================================
BASE_DIR = Path(__file__).resolve().parent.parent


# =======================================
# CONFIGURACIÓN BÁSICA
# =======================================
SECRET_KEY = "django-insecure-3*b&z7s5b^kq$rf&sfkgjaiyt=yo_auoh+b7q1rvo%y1iwpz0)"
DEBUG = True

ALLOWED_HOSTS = ["*"]  # Ajustar en producción


# =======================================
# APLICACIONES INSTALADAS
# =======================================
INSTALLED_APPS = [
    "accounts",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # App principal
    "raffle",
]


# =======================================
# MIDDLEWARE
# =======================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =======================================
# URLS / WSGI
# =======================================
ROOT_URLCONF = "ciudad_suerte.urls"
WSGI_APPLICATION = "ciudad_suerte.wsgi.application"


# =======================================
# TEMPLATES
# =======================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Templates globales
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =======================================
# BASE DE DATOS
# =======================================
USE_SQL_SERVER = os.environ.get("USE_SQL_SERVER", "1") == "1"
CONN_MAX_AGE = max(60, min(int(os.environ.get("CONN_MAX_AGE", "60")), 300))
CONN_HEALTH_CHECKS = True

if USE_SQL_SERVER:
    DATABASES = {
        "default": {
            "ENGINE": "mssql",
            "NAME": "CiudadDeLaSuerte",
            "USER": "galasql",
            "PASSWORD": "hh@yMhDqubDse4g",
            "HOST": "ciudadsuerte-sqlserver.database.windows.net",
            "PORT": "1433",
            "CONN_MAX_AGE": CONN_MAX_AGE,
            "CONN_HEALTH_CHECKS": CONN_HEALTH_CHECKS,
            "OPTIONS": {
                "driver": "ODBC Driver 18 for SQL Server",
                "Encrypt": "yes",
                "TrustServerCertificate": "yes",
                "ConnectionPooling": False,
                "timeout": 10,
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
            "CONN_MAX_AGE": CONN_MAX_AGE,
            "CONN_HEALTH_CHECKS": CONN_HEALTH_CHECKS,
        }
    }


# =======================================
# VALIDACIÓN DE CONTRASEÑAS
# =======================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# =======================================
# INTERNACIONALIZACIÓN
# =======================================
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = False


# =======================================
# ARCHIVOS ESTÁTICOS
# =======================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"


# =======================================
# ARCHIVOS MEDIA (IMÁGENES SUBIDAS)
# =======================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =======================================
# LOGIN / LOGOUT
# =======================================
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/admin/login/"
AUTH_USER_MODEL = "accounts.User"
SESSION_COOKIE_AGE = 60 * 60 * 2
SESSION_SAVE_EVERY_REQUEST = True
CSRF_FAILURE_VIEW = "raffle.controllers.security.csrf_failure"


# =======================================
# CONFIG ADICIONAL
# =======================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
