from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import environ

env = environ.FileAwareEnv()

BASE_DIR = Path(__file__).parent.parent.parent

BASE_PATH = env.str("OPENMAPS_AUTH_BASE_PATH", default="")
if len(BASE_PATH):
    if not BASE_PATH.startswith("/"):
        raise ImproperlyConfigured("Customized base paths must start with a /.")
    BASE_URL_PATTERN = f"{BASE_PATH}/".lstrip("/")
else:
    BASE_URL_PATTERN = ""

# Smallstep CA must be configured for client TLS certificate use.
STEPPATH = Path(env.str("STEPPATH", default=BASE_DIR / ".step"))
STEP_CERTS = STEPPATH / "certs"
STEP_CLI = env.str("STEP_CLI", default="step")
STEP_PROVISIONER = env.str("STEP_PROVISIONER", default=None)
STEP_PROVISIONER_PASSWORD_FILE = env.str("STEP_PROVISIONER_PASSWORD_FILE", default=None)
STEP_SECRETS = STEPPATH / "secrets"

OPENMAPS_AUTH_BACKEND = env.str("OPENMAPS_AUTH_BACKEND", default=None)
if OPENMAPS_AUTH_BACKEND:
    OPENMAPS_AUTH_SECRET = env.str("OPENMAPS_AUTH_SECRET", default="")
OPENMAPS_AUTH_TITLE = env.str("OPENMAPS_AUTH_TITLE", default="VantorMaps")
OPENMAPS_AUTH_APP_LINKS = env.json(
    "OPENMAPS_AUTH_APP_LINKS", default=[{"link": "/", "text": "MapEdit"}]
)
OPENMAPS_AUTH_CLIENT_TLS = env.bool(
    "OPENMAPS_AUTH_CLIENT_TLS",
    default=STEP_PROVISIONER and STEP_PROVISIONER_PASSWORD_FILE,
)
OPENMAPS_AUTH_CLIENT_TLS_CERT_HEADER = env.bool(
    "OPENMAPS_AUTH_CLIENT_TLS_CERT_HEADER", default="X-TLS-Client-Cert"
)
OPENMAPS_AUTH_CLIENT_TLS_VERIFY_HEADER = env.bool(
    "OPENMAPS_AUTH_CLIENT_TLS_VERIFY_HEADER", default="X-TLS-Client-Verify"
)
OPENMAPS_AUTH_CLIENT_TLS_DURATION = env.str(
    "OPENMAPS_AUTH_CLIENT_TLS_DURATION", default="744h"
)
OPENMAPS_AUTH_CLIENT_TLS_MAX_CERTS = env.int(
    "OPENMAPS_AUTH_CLIENT_TLS_MAX_CERTS", default=5
)
OPENMAPS_AUTH_CLIENT_TLS_VERIFY_SERIAL = env.bool(
    "OPENMAPS_AUTH_CLIENT_TLS_VERIFY_SERIAL", default=True
)
OPENMAPS_AUTH_OSM_SESSION = env.bool("OPENMAPS_AUTH_OSM_SESSION", default=False)

OSM_BASE_URL = env.str("OSM_BASE_URL", default="https://www.openstreetmap.org")
OSM_AUTH_URL = env.str("OSM_AUTH_URL", default=OSM_BASE_URL)
OSM_LOGIN_URL = env.str("OSM_LOGIN_URL", default=f"{OSM_BASE_URL}/login")
OSM_NEW_USER_URL = env.str("OSM_NEW_USER_URL", default=f"{OSM_BASE_URL}/user/new")

OSM_OAUTH1_ACCESS_TOKEN_URL = env.str(
    "OSM_OAUTH1_ACCESS_TOKEN_URL", default=f"{OSM_AUTH_URL}/oauth/access_token"
)
OSM_OAUTH1_AUTHORIZATION_URL = env.str(
    "OSM_OAUTH1_AUTHORIZATION_URL", default=f"{OSM_AUTH_URL}/oauth/authorize"
)
OSM_OAUTH1_REQUEST_TOKEN_URL = env.str(
    "OSM_OAUTH1_REQUEST_TOKEN_URL", default=f"{OSM_AUTH_URL}/oauth/request_token"
)
OSM_OAUTH2_ACCESS_TOKEN_URL = env.str(
    "OSM_OAUTH2_ACCESS_TOKEN_URL", default=f"{OSM_AUTH_URL}/oauth2/token"
)
OSM_OAUTH2_AUTHORIZATION_URL = env.str(
    "OSM_OAUTH2_AUTHORIZATION_URL", default=f"{OSM_AUTH_URL}/oauth2/authorize"
)
OSM_OAUTH2_DEFAULT_SCOPE = env.list("OSM_OAUTH2_DEFAULT_SCOPE", default=["read_prefs"])
OSM_USER_ADMINS = env.json("OSM_USER_ADMINS", default=[])
OSM_USER_ALL_ADMINS = env.bool("OSM_USER_ALL_ADMINS", default=False)
OSM_USER_COUNTRY = env.str("OSM_USER_COUNTRY", default=None)
OSM_SESSION_KEY = env.str("OSM_SESSION_KEY", default="_osm_session")
OSM_USER_DETAILS_URL = env.str(
    "OSM_USER_DETAILS_URL", default=f"{OSM_AUTH_URL}/api/0.6/user/details"
)
OSM_USER_EMAIL_DOMAIN = env.str("OSM_USER_EMAIL_DOMAIN", default="openstreetmap.arpa")
OSM_USER_HOME_LAT = env.float("OSM_USER_HOME_LAT", default=None)
OSM_USER_HOME_LON = env.float("OSM_USER_HOME_LON", default=None)
OSM_USER_HOME_ZOOM = env.int("OSM_USER_HOME_ZOOM", default=14)
OSM_USER_LANGUAGES = env.str("OSM_USER_LANGUAGES", default=None)
OSM_USER_NAME_LOWER = env.bool("OSM_USER_NAME_LOWER", default=False)
OSM_USER_NAME_REPLACE_SPACE = env.str("OSM_USER_NAME_REPLACE_SPACE", default=None)
OSM_USER_ORGANIZATION = env.str("OSM_USER_ORGANIZATION", default=None)

JOSM_OAUTH1_CALLBACK_URI = env.str(
    "JOSM_OAUTH1_CALLBACK_URI", default="http://localhost:8111/callback"
)
JOSM_OAUTH1_NAME = env.str("JOSM_OAUTH1_NAME", "JOSM - Java OpenStreetMap Editor")
JOSM_PREFERENCES = env.json(
    "JOSM_PREFERENCES",
    default={
        "tags": {
            "default.osm.tile.source.url": "https://tile.openstreetmap.org/{zoom}/{x}/{y}.png",
        }
    },
)
JOSM_PREFERENCES_VERSION = env.str("JOSM_PREFERENCES_VERSION", "18303")
JOSM_PREFERENCES_XMLNS = env.str(
    "JOSM_PREFERENCES_XMLNS", "http://josm.openstreetmap.de/preferences-1.0"
)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])
DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env.str(
    "SECRET_KEY",
    default="django-insecure-$#zokn+#tb4^z-k@l32umk&d=3299qoc%b@z@^23+3mh&4i##g",
)
SITE_ID = env.int("SITE_ID", default=1)

# Application definition
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "openmaps_auth",
)

AUTH_USER_MODEL = "openmaps_auth.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

if OPENMAPS_AUTH_CLIENT_TLS:
    MIDDLEWARE.append("openmaps_auth.tls.middleware.TLSClientMiddleware")

ROOT_URLCONF = env.str("ROOT_URLCONF", default="openmaps_auth.urls")

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
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "openmaps_auth.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = env.str("WSGI_APPLICATION", default="openmaps_auth.wsgi.application")

# Database
DATABASES = {
    "default": env.db_url(
        "DATABASE_URL", default="sqlite:///{}".format(BASE_DIR / "db.sqlite3")
    ),
}

# Cache
CACHE_URL = env.cache_url(
    default=None,
    backend=env.str("CACHE_BACKEND", "django.core.cache.backends.redis.RedisCache"),
)
if CACHE_URL:
    CACHES = {"default": CACHE_URL}
    DEFAULT_SESSION_ENGINE = "django.contrib.sessions.backends.cache"
else:
    DEFAULT_SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Sessions
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=1209600)
SESSION_COOKIE_DOMAIN = env.str("SESSION_COOKIE_DOMAIN", default=None)
SESSION_COOKIE_HTTPONLY = env.bool("SESSION_COOKIE_HTTPONLY", default=True)
SESSION_COOKIE_NAME = env.str("SESSION_COOKIE_NAME", default="openmapsid")
SESSION_COOKIE_PATH = env.str("SESSION_COOKIE_PATH", default="/")
SESSION_COOKIE_SAMESITE = env.str("SESSION_COOKIE_SAMESITE", default="Lax")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
SESSION_ENGINE = env.str("SESSION_ENGINE", default=DEFAULT_SESSION_ENGINE)
SESSION_EXPIRE_AT_BROWSER_CLOSE = env.bool(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False
)
SESSION_FILE_PATH = env.str("SESSION_FILE_PATH", default=None)
SESSION_SAVE_EVERY_REQUEST = env.bool("SESSION_SAVE_EVERY_REQUEST", default=False)
SESSION_SERIALIZER = env.str(
    "SESSION_SERIALIZER", default="django.contrib.sessions.serializers.JSONSerializer"
)

# CSRF
CSRF_COOKIE_AGE = env.int("CSRF_COOKIE_AGE", default=SESSION_COOKIE_AGE)
CSRF_COOKIE_DOMAIN = env.str("CSRF_COOKIE_DOMAIN", default=SESSION_COOKIE_DOMAIN)
CSRF_COOKIE_HTTPONLY = env.bool("CSRF_COOKIE_HTTPONLY", default=False)
CSRF_COOKIE_NAME = env.str("CSRF_COOKIE_NAME", default="openmapscsrf")
CSRF_COOKIE_PATH = env.str("CSRF_COOKIE_PATH", default=SESSION_COOKIE_PATH)
CSRF_COOKIE_SAMESITE = env.str("CSRF_COOKIE_SAMESITE", default=SESSION_COOKIE_SAMESITE)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=SESSION_COOKIE_SECURE)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CSRF_USE_SESSIONS = env.bool("CSRF_USE_SESSIONS", default=False)

# Authentication
OPENMAPS_AUTH_KEY = env.str("OPENMAPS_AUTH_KEY", default="")
OPENMAPS_AUTH_OIDC_ENDPOINT = env.str("OPENMAPS_AUTH_OIDC_ENDPOINT", default=None)

# Always have fallback model backend.
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
if OPENMAPS_AUTH_CLIENT_TLS:
    AUTHENTICATION_BACKENDS = AUTHENTICATION_BACKENDS + (
        "openmaps_auth.tls.backend.TLSClientBackend",
    )

# Set up social_auth variables when backend is set.
if OPENMAPS_AUTH_BACKEND == "login-gov":
    AUTHENTICATION_BACKENDS = (
        "openmaps_auth.social.backends.LoginGovOpenIdConnect",
    ) + AUTHENTICATION_BACKENDS
    SOCIAL_AUTH_LOGIN_GOV_KEY = OPENMAPS_AUTH_KEY
    SOCIAL_AUTH_LOGIN_GOV_SECRET = OPENMAPS_AUTH_SECRET
    if OPENMAPS_AUTH_OIDC_ENDPOINT:
        SOCIAL_AUTH_LOGIN_GOV_OIDC_ENDPOINT = OPENMAPS_AUTH_OIDC_ENDPOINT
elif OPENMAPS_AUTH_BACKEND == "okta-openidconnect":
    AUTHENTICATION_BACKENDS = (
        "openmaps_auth.social.backends.OktaOpenIdConnect",
    ) + AUTHENTICATION_BACKENDS
    SOCIAL_AUTH_OKTA_OPENIDCONNECT_KEY = OPENMAPS_AUTH_KEY
    SOCIAL_AUTH_OKTA_OPENIDCONNECT_SECRET = OPENMAPS_AUTH_SECRET
    if OPENMAPS_AUTH_OIDC_ENDPOINT:
        SOCIAL_AUTH_OKTA_OPENIDCONNECT_API_URL = OPENMAPS_AUTH_OIDC_ENDPOINT
    else:
        raise ImproperlyConfigured("Must provide endpoint for Okta")
elif OPENMAPS_AUTH_BACKEND == "openstreetmap":
    AUTHENTICATION_BACKENDS = (
        "openmaps_auth.social.backends.OpenStreetMapOAuth",
    ) + AUTHENTICATION_BACKENDS
    SOCIAL_AUTH_OPENSTREETMAP_KEY = OPENMAPS_AUTH_KEY
    SOCIAL_AUTH_OPENSTREETMAP_SECRET = OPENMAPS_AUTH_SECRET
elif OPENMAPS_AUTH_BACKEND == "openstreetmap-oauth2":
    AUTHENTICATION_BACKENDS = (
        "openmaps_auth.social.backends.OpenStreetMapOAuth2",
    ) + AUTHENTICATION_BACKENDS
    SOCIAL_AUTH_OPENSTREETMAP_OAUTH2_KEY = OPENMAPS_AUTH_KEY
    SOCIAL_AUTH_OPENSTREETMAP_OAUTH2_SECRET = OPENMAPS_AUTH_SECRET

SOCIAL_AUTH_STRATEGY = "openmaps_auth.social.strategy.OpenMapsStrategy"
# Username is email address.
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True

# Ensure proper redirects when using email or social login.
CALLBACK_URL = env.str("OPENMAPS_AUTH_CALLBACK_URL", default="callback")
INDEX_URL = env.str("OPENMAPS_AUTH_INDEX_URL", default="index")
LOGIN_REDIRECT_URL = CALLBACK_URL
LOGOUT_REDIRECT_URL = INDEX_URL
SOCIAL_AUTH_LOGIN_REDIRECT_URL = INDEX_URL

# When using social or tls login, restrict access based on email or domain
# whitelists if they are defined.
OPENMAPS_AUTH_WHITELISTED_DOMAINS = env.json(
    "OPENMAPS_AUTH_WHITELISTED_DOMAINS", default=[]
)
SOCIAL_AUTH_WHITELISTED_DOMAINS = OPENMAPS_AUTH_WHITELISTED_DOMAINS
OPENMAPS_AUTH_WHITELISTED_EMAILS = env.json(
    "OPENMAPS_AUTH_WHITELISTED_EMAILS", default=[]
)
SOCIAL_AUTH_WHITELISTED_EMAILS = OPENMAPS_AUTH_WHITELISTED_EMAILS

# Only use scrypt and pbkdf2 for password hashes.
PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
)

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": True,
        },
        "openmaps_auth": {
            "handlers": ["console"],
            "level": env.str("OPENMAPS_AUTH_LOG_LEVEL", default="INFO"),
            "propagate": True,
        },
    },
}

# Set when running behind a proxy.
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=False)
USE_X_FORWARDED_PORT = env.bool("USE_X_FORWARDED_PORT", default=False)
SECURE_PROXY_SSL_HEADER = env.list("SECURE_PROXY_SSL_HEADER", default=None)

# Internationalization
LANGUAGE_CODE = env.str("LANGUAGE_CODE", default="en-us")
TIME_ZONE = env.str("TIME_ZONE", default="UTC")
USE_I18N = env.bool("USE_I18N", default=True)
USE_L10N = env.bool("USE_L10N", default=True)
USE_TZ = env.bool("USE_TZ", default=True)

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = env.str("STATIC_ROOT", default=BASE_DIR / "static")
STATIC_URL = env.str("STATIC_URL", default=f"{BASE_PATH}/static/")
