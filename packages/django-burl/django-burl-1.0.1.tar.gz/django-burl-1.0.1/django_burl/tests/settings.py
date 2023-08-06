import os
from datetime import timedelta


def get_env(name, default=None):
    env = os.environ.get(name)
    return env if env else default


DEBUG = False
ALLOWED_HOSTS = ["*"]

SETTINGS_MODULE = os.path.dirname(os.path.abspath(__file__))
MODULE_ROOT = os.path.dirname(SETTINGS_MODULE)
BASE_DIR = MODULE_ROOT
PROJECT_ROOT = os.path.dirname(MODULE_ROOT)

HOME = get_env("HOME")
SECRET_KEY = get_env("BURL_SECRET_KEY")
HASHID_ALPHABET = get_env(
    "BURL_HASHID_ALPHABET", "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
)
BURL_BLACKLIST = ["admin", "api", "static", "media"]
ROUGH_COUNT_MIN = 1000

ROOT_URLCONF = "django_burl.urls"

DEFAULT_REDIRECT_URL = get_env("DEFAULT_REDIRECT_URL", "https://wryfi.net")

# Application definition

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "django.contrib.admin",
    "django.contrib.sites",
    "django_filters",
    "django_burl",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": get_env("BURL_POSTGRES_DB", "burl"),
        "USER": get_env("BURL_POSTGRES_USER", "burl"),
        "PASSWORD": get_env("BURL_POSTGRES_PASSWORD", "burl"),
        "HOST": get_env("BURL_POSTGRES_HOST", "127.0.0.1"),
        "PORT": int(get_env("BURL_POSTGRES_PORT", 5432)),
    },
}


# DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": "db.sqlite",
#    },
# }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIMEZONE = get_env("BURL_TIMEZONE", "America/Los_Angeles")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"


LOG_DIR = get_env("BURL_LOG_DIR", PROJECT_ROOT)

BURL_LOG_LEVEL = get_env("BURL_LOG_LEVEL", "WARNING")
APP_LOG_LEVEL = get_env("BURL_APP_LOG_LEVEL", "INFO")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "level": BURL_LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "burl.log"),
            "maxBytes": 1024 * 1024 * 5,  # 5MiB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": BURL_LOG_LEVEL,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": APP_LOG_LEVEL,
        },
        "burl": {
            "handlers": ["console"],
            "level": BURL_LOG_LEVEL,
        },
    },
}

API_PAGE_SIZE = int(get_env("BURL_API_PAGE_SIZE", 20))

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": API_PAGE_SIZE,
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/api/v1/swagger/"
LOGOUT_URL = "/accounts/logout/"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "token": {"type": "apiKey", "in": "header", "name": "Authorization"},
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=600),
}

SENDGRID_API_KEY = get_env("BURL_SENDGRID_API_KEY", 1)

if SENDGRID_API_KEY == 1 or SENDGRID_API_KEY == "":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# AUTH_USER_MODEL = "django_burl.BurlUser"
