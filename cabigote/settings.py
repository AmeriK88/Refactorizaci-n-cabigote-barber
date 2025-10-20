# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.

from core.whitenoise_headers import add_custom_headers
from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
import environ
import pymysql
pymysql.install_as_MySQLdb()
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa django-environ
env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)


ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=(["127.0.0.1", "localhost"] if DEBUG else []),
)


INSTALLED_APPS = [
# Application definition
    'whitenoise.runserver_nostatic',
    'admin_interface',
    'colorfield',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Oauth & google login
    'django.contrib.sites',     
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    # Installed apps
    'django_recaptcha',

    # My apps
    'appointments',
    'products',
    'services',
    'reviews',
    'reports',
    'users',
    'core',
    'widget_tweaks', 
    "crispy_forms",
    "crispy_bootstrap5",

    # Content Security Policy
    'csp',
    # Seguridad
    'axes',
]


MIDDLEWARE = [
    # Seguridad y estáticos primero
    'django.middleware.security.SecurityMiddleware',
    'core.middlewares.block_probes.BlockProbesMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # Sesión y localización
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware', 
    'django.middleware.common.CommonMiddleware',

    # Protección de formularios
    'django.middleware.csrf.CsrfViewMiddleware',

    # Auth + Allauth + Mensajes
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    # Contador/bloqueo de intentos fallidos
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Cabeceras de seguridad
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # CSP (cabecera en la respuesta, bien al final)
    'csp.middleware.CSPMiddleware',

    # Middleware de redirección
    'core.middlewares.redirection.RedirectionDomainMiddleware',
]

ROOT_URLCONF = 'cabigote.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'core', 'templates'),  
            os.path.join(BASE_DIR, 'templates'),          
        ],
        
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.mensaje_especial_context',
            ],
        },
    },
]


# Autenticación
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'cabigote.wsgi.application'



# ───────── DATABASE CONFIG ─────────
db_url = env('DATABASE_URL', default='') 

if db_url:
    # django-environ parsea la URL y devuelve un dict listo para Django
    db_config = env.db('DATABASE_URL') 
else:
    # Config local por variables sueltas
    db_config = {
        'ENGINE':   env('DB_ENGINE'),
        'NAME':     env('DB_NAME'),
        'USER':     env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST':     env('DB_HOST'),
        'PORT':     env('DB_PORT'),
    }

# Asegura que OPTIONS es un dict y añade charset + timeouts
opts = db_config.get('OPTIONS') or {}
if not isinstance(opts, dict):
    opts = {}
opts.update({
    'charset': 'utf8mb4',
    'init_command': "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci', time_zone = '+00:00'",
    'connect_timeout': 10,
    'read_timeout': 20,
    'write_timeout': 20,
})
db_config['OPTIONS'] = opts

# Conexiones persistentes (segundos).
db_config['CONN_MAX_AGE'] = 300

DATABASES = {'default': db_config}



# PASSWORD CONFIGURATION
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ─────────── GOOGLE ALLAUTH CONFIG ───────────
GOOGLE_CLIENT_ID     = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")

# Allauth ― configuración global
SITE_ID = env.int("SITE_ID")   
SOCIALACCOUNT_ADAPTER = "core.adapters.CustomSocialAdapter"

# ─── LOCAL AUTH ────────────────────────────────────────────
ACCOUNT_LOGIN_METHODS = {"email"}  
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_UNIQUE_EMAIL      = True     

# ─── SOCIAL ─────────────────────────────────────────────────────────
SOCIALACCOUNT_AUTO_SIGNUP  = False
SOCIALACCOUNT_QUERY_EMAIL  = True
SOCIALACCOUNT_STORE_TOKENS = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret":    GOOGLE_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}


# Internationalization & CONFIG TIME ZONE
LANGUAGE_CODE = 'es'

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Español'),
]

TIME_ZONE = 'Atlantic/Canary'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# EMAIL CONFIG PRODUCTION
EMAIL_BACKEND = env('EMAIL_BACKEND') 
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')


# READS & PROCESS ADMINS FROM .ENV
admins_env = env('ADMINS', default='') 

ADMINS = [tuple(admin.split(',')) for admin in admins_env.split(';')] if admins_env else []  # type: ignore[arg-type]

# CAPCHA CONFIG
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')

# REDIRECT URLS
LOGIN_URL = '/users/login/' 
LOGIN_REDIRECT_URL = '/users/perfil/'  
LOGOUT_REDIRECT_URL = '/' 

# MEDIA FILES CONFIG (UPLOADED FILES WILL BE REMOVED ON EVERY DEPLOY!)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# STATIC FILES DIR CONFIG
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WHITENOISE (always active, dev + prod)
WHITENOISE_ALLOW_ALL_ORIGINS = True
WHITENOISE_ADD_HEADERS_FUNCTION = add_custom_headers
WHITENOISE_MEDIA_PREFIX = 'media'
# ignore duplicates (see §2-A)
WHITENOISE_IGNORE_PATTERNS = ['admin/js/popup_response.js', 'admin/js/cancel.js']

# Use compressed-manifest storage only in prod
if not DEBUG:
    STATICFILES_STORAGE = (
        'whitenoise.storage.CompressedManifestStaticFilesStorage'
    )


# LOGGING CONFIGURATION
LOG_FILE_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, 'log.error')

if not os.path.exists(LOG_FILE_DIR):
    os.makedirs(LOG_FILE_DIR)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE_PATH,
            "maxBytes": 500000,
            "backupCount": 5,
            "formatter": "verbose",
        },
        # Seguridad: guarda eventos de Axes y avisos de seguridad
        "security_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_FILE_DIR, "security.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
        },
    },

    "formatters": {
        "verbose": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },

    "root": {
        "handlers": ["file"],
        "level": "ERROR",
    },

    "loggers": {
        # Intentos y bloqueos de django-axes
        "axes": {
            "handlers": ["security_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # Avisos de seguridad de Django (CSRF, etc.)
        "django.security": {
            "handlers": ["security_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        # Errores 500 en peticiones
        "django.request": {
            "handlers": ["security_file", "console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}


# CSRF CONFIGURATION
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=(["http://127.0.0.1", "http://localhost"] if DEBUG else []),
)

if not DEBUG:
    if not ALLOWED_HOSTS:
        raise ImproperlyConfigured("ALLOWED_HOSTS must be set in production.")
    if not CSRF_TRUSTED_ORIGINS:
        raise ImproperlyConfigured("CSRF_TRUSTED_ORIGINS must be set in production (include https://).")
    

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# BLACKLISTED USERNAMES
BLACKLISTED_USERNAMES = ['admin', 'root', 'superuser', 'test', 'cabigote']

# CRISPY FORMS CONFIGURATION
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Content Security Policy (CSP)
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        # ───────── BASE ─────────
        "default-src": ("'self'",),
        "object-src": ("'none'",),
        "base-uri": ("'self'",),

        # ───────── SCRIPTS ─────────
        "script-src": (
            "'self'",
            "'unsafe-inline'",
            "https://code.jquery.com",
            "https://cdnjs.cloudflare.com",
            "https://stackpath.bootstrapcdn.com",
            "https://cdn.jsdelivr.net",
            "https://www.google.com",
            "https://www.gstatic.com",
        ),
        "script-src-elem": (
            "'self'",
            "'unsafe-inline'",
            "https://code.jquery.com",
            "https://cdnjs.cloudflare.com",
            "https://stackpath.bootstrapcdn.com",
            "https://cdn.jsdelivr.net",
            "https://www.google.com",
            "https://www.gstatic.com",
            "https://connect.facebook.net",
            "https://www.instagram.com",
        ),

        # ───────── ESTILOS ─────────
        "style-src": (
            "'self'",
            "'unsafe-inline'",
            "https://cdnjs.cloudflare.com",
            "https://stackpath.bootstrapcdn.com",
            "https://fonts.googleapis.com",
            "https://cdn.jsdelivr.net",
            "https://www.gstatic.com",
        ),

        # ───────── FUENTES ─────────
        "font-src": (
            "'self'",
            "data:",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com",
        ),

        # ───────── IMÁGENES ─────────
        "img-src": (
            "'self'",
            "data:",
            "https://www.instagram.com",
            "https://maps.gstatic.com",
            "https://maps.googleapis.com",
            "https://www.gstatic.com/recaptcha",
        ),

        # ───────── IFRAME / EMBEDS ─────────
        "frame-src": (
            "'self'",
            "https://www.google.com",
            "https://recaptcha.google.com",
            "https://www.instagram.com",
        ),

        # ───────── AJAX / FETCH ─────────
        # Añadidos jsDelivr y cdnjs para evitar el error del .map de Bootstrap
        "connect-src": (
            "'self'",
            "https://www.google.com",
            "https://www.gstatic.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
        ),

        # Proteger contra clickjacking
        "frame-ancestors": ("'self'",),
    }
}


X_FRAME_OPTIONS = 'SAMEORIGIN' 

# ───────── CACHÉ (Redis) ─────────
REDIS_URL = env('REDIS_URL', default='')

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
            },
            "TIMEOUT": 60 * 10,  # 10 minutos por defecto
        }
    }
else:
    # Fallback a memoria local si no hay Redis (dev)
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-dev",
        }
    }

# ───────── django-axes ─────────
AXES_ENABLED = not DEBUG                       # activo solo en prod
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1                          # horas
AXES_LOCKOUT_TEMPLATE = 'errors/locked_out.html'

# Usa handler de caché si hay Redis; si no, DB handler (evita el warning W001)
if REDIS_URL:
    AXES_HANDLER = 'axes.handlers.cache.AxesCacheHandler'
    AXES_CACHE = 'default'
else:
    AXES_HANDLER = 'axes.handlers.database.AxesDatabaseHandler'



SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 7 * 24 * 60 * 60

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_CONTENT_TYPE_NOSNIFF = True



# APP VERSION
APP_VERSION = env("APP_VERSION", default="2.0.0")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'