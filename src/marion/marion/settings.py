"""
Django settings for marion project.
"""

from pathlib import Path
from tempfile import mkdtemp

from configurations import Configuration, values

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = Path("/data")


# pylint: disable=no-init
class Base(Configuration):
    """
    This is the base configuration every configuration (aka environnement)
    should inherit from. It is recommended to configure third-party
    applications by creating a configuration mixins in ./configurations and
    compose the Base configuration with those mixins.

    It depends on an environment variable that SHOULD be defined:

      * DJANGO_SECRET_KEY

    You may also want to override default configuration by setting the
    following environment variables:

      * DB_NAME
      * DB_HOST
      * DB_PASSWORD
      * DB_USER
    """

    DEBUG = False

    # Security
    ALLOWED_HOSTS = []
    SECRET_KEY = values.Value(None)

    # SECURE_PROXY_SSL_HEADER allows to fix the scheme in Django's HttpRequest
    # object when you application is behind a reverse proxy.
    #
    # Keep this SECURE_PROXY_SSL_HEADER configuration only if :
    # - your Django app is behind a proxy.
    # - your proxy strips the X-Forwarded-Proto header from all incoming requests
    # - Your proxy sets the X-Forwarded-Proto header and sends it to Django
    #
    # In other cases, you should comment the following line to avoid security issues.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": (
                "django.contrib.auth.password_validation."
                "UserAttributeSimilarityValidator"
            ),
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Application
    ROOT_URLCONF = "marion.urls"
    WSGI_APPLICATION = "marion.wsgi.application"

    # Database
    DATABASES = {
        "default": {
            "ENGINE": values.Value(
                "django.db.backends.postgresql_psycopg2",
                environ_name="DB_ENGINE",
                environ_prefix=None,
            ),
            "NAME": values.Value("marion", environ_name="DB_NAME", environ_prefix=None),
            "USER": values.Value("fun", environ_name="DB_USER", environ_prefix=None),
            "PASSWORD": values.Value(
                "pass", environ_name="DB_PASSWORD", environ_prefix=None
            ),
            "HOST": values.Value(
                "localhost", environ_name="DB_HOST", environ_prefix=None
            ),
            "PORT": values.Value(5432, environ_name="DB_PORT", environ_prefix=None),
        }
    }

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = "/static/"
    STATIC_ROOT = DATA_DIR.joinpath("static")
    MEDIA_URL = "/media/"
    MEDIA_ROOT = DATA_DIR.joinpath("media")

    # Internationalization
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Application definition
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "rest_framework",
        "marion.certificates",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
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


class Development(Base):
    """
    Development environment settings
    We set DEBUG to True and configure the server to respond from all hosts.
    """

    DEBUG = True
    ALLOWED_HOSTS = ["*"]

    ROOT_URLCONF = "marion.urls.debug"


class Test(Base):
    """Test environment settings"""

    MEDIA_ROOT = Path(mkdtemp())

    ROOT_URLCONF = "marion.urls.debug"
