# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.
from pathlib import Path
import environ
import pymysql
pymysql.install_as_MySQLdb()
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa django-environ
env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False) # type: ignore[arg-type]


ALLOWED_HOSTS = [
    'if9hv3ou.up.railway.app',
    '127.0.0.1','localhost', '0.0.0.0',
    'refactorizaci-n-cabigote-barber-production.up.railway.app', 
    'cabigotebarbershop.com', 
    'www.cabigotebarbershop.com',
]


INSTALLED_APPS = [
# Application definition
    'whitenoise.runserver_nostatic',
    'admin_interface',
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
    'appointments',
    'products',
    'services',
    'reviews',
    'reports',
    'users',
    'colorfield',
    'core',
    'widget_tweaks', 
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cabigote.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core', 'templates')],
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

WSGI_APPLICATION = 'cabigote.wsgi.application'



# DB CONFIG
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=None, # type: ignore
    )
}

if not DATABASES['default']:
    raise ValueError("DATABASE_URL no está configurada en las variables de entorno")

# FORCE CHARSET utf8mb4
DATABASES['default']['OPTIONS'] = {
    'charset': 'utf8mb4',
    'init_command': "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci'",
}


# DB development
# # 3) DEVELOPMENT DATABASE CONFIGURATION
# DATABASES = {
#     'default': {
#         'ENGINE': env('DB_ENGINE'),
#         'NAME': env('DB_NAME'),
#         'USER': env('DB_USER'),
#         'PASSWORD': env('DB_PASSWORD'),
#         'HOST': env('DB_HOST'),
#         'PORT': env('DB_PORT'),
#     }
# }



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

# GOOGLE OAUTH CONFIGURATION
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET')

# SITE ID for Allauth
SITE_ID = env.int('SITE_ID')


# SITE ID for Allauth
SITE_ID = env.int('SITE_ID')

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
# ——— EMAIL CONFIG ———
EMAIL_HOST      = env('EMAIL_HOST')     
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_PORT    = env.int('EMAIL_PORT', default=587) # type: ignore[arg-type]
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True) # type: ignore[arg-type]
    EMAIL_USE_SSL = False
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT    = 465
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True

EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', default=20) # type: ignore[arg-type]


# READS & PROCESS ADMINS FROM .ENV
admins_env = env('ADMINS', default='')   # type: ignore[name-defined]

ADMINS = [tuple(admin.split(',')) for admin in admins_env.split(';')] if admins_env else []  # type: ignore[arg-type]

# CAPCHA CONFIG
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')

# Configuraciones relacionadas con la autenticación
LOGIN_URL = '/users/login/' 
LOGIN_REDIRECT_URL = '/users/perfil/'  
LOGOUT_REDIRECT_URL = '/' 

# MEDIA FILES CONFIG (UPLOADED FILES WILL BE REMOVED ON EVERY DEPLOY!)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# STATIC FILE
STATIC_URL = '/static/'

# DIRECTORIES FOR STATIC FILES
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WHITENOISE CONFIG
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ALLOW_ALL_ORIGINS = True
WHITENOISE_MEDIA_PREFIX = 'media'

# LOGGING CONFIGURATION
LOG_FILE_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, 'log.error')

if not os.path.exists(LOG_FILE_DIR):
    os.makedirs(LOG_FILE_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_PATH, 
            'maxBytes': 500000,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}

# DEFAULT AUTO FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CSRF CONFIGURATION
CSRF_TRUSTED_ORIGINS = [
    'https://if9hv3ou.up.railway.app',
    'https://refactorizaci-n-cabigote-barber-production.up.railway.app',
    'https://cabigotebarbershop.com',
    'https://www.cabigotebarbershop.com',
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# BLACKLISTED USERNAMES
BLACKLISTED_USERNAMES = ['admin', 'root', 'superuser', 'test', 'cabigote']

# SOCIAL ACCOUNT CONFIGURATION
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# ALLAUTH CONFIGURATION
ACCOUNT_LOGIN_METHODS       = {'email'}
ACCOUNT_SIGNUP_FIELDS       = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION  = 'optional'   # o 'mandatory'


# APP VERSION
APP_VERSION = "2.3.1"  
