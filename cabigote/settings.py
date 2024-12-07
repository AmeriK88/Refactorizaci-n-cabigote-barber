# Autor: José Félix Gordo Castaño
# Copyright (C) 2024 José Félix Gordo Castaño
# Este archivo está licenciado para uso exclusivo con fines educativos y de aprendizaje. 
# No se permite la venta ni el uso comercial sin autorización expresa del autor.

from pathlib import Path
import environ
import os
import pymysql
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Inicializa django-environ
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'
print(f"DEBUG leído directamente: {DEBUG}")

ALLOWED_HOSTS = ['127.0.0.1','localhost','refactorizaci-n-cabigote-barber-production.up.railway.app', 'cabigotebarbershop.com', 'www.cabigotebarbershop.com',]


# Application definition
INSTALLED_APPS = [
    'admin_interface',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'appointments',
    'products',
    'services',
    'reviews',
    'reports',
    'users',
    'django_recaptcha',
    'colorfield',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'cabigote.wsgi.application'

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Cambia a 'postgresql', 'sqlite3', etc., si usas otra base de datos
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'), 
        'PORT': env('DB_PORT'), 
    }
}

"""
# Configuración de la base de datos
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=None,
    )
}

if not DATABASES['default']:
    raise ValueError("DATABASE_URL no está configurada en las variables de entorno")


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization & config zona horaria

LANGUAGE_CODE = 'es'

LANGUAGES = [
    ('en', 'English'),
    ('es', 'Español'),
]

TIME_ZONE = 'Atlantic/Canary'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configuración envío email
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Leer y procesar ADMINS desde el archivo .env
admins_env = env('ADMINS', default='')

# Convertir el valor en una lista de tuplas
ADMINS = [tuple(admin.split(',')) for admin in admins_env.split(';')] if admins_env else []

# Configuraciones capchat
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')

# Configuraciones relacionadas con la autenticación
LOGIN_URL = '/users/login/' 
LOGIN_REDIRECT_URL = '/users/perfil/'  
LOGOUT_REDIRECT_URL = '/' 

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# Directorio donde se almacenarán los archivos estáticos recogidos
STATIC_ROOT = BASE_DIR / "/staticfiles/"

# Directorios adicionales para archivos estáticos
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  
]

# Configuración adicional para WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Define la ruta absoluta para el archivo de logs
LOG_FILE_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, 'log.error')


# Verifica si el directorio de logs existe; si no, créalo
if not os.path.exists(LOG_FILE_DIR):
    os.makedirs(LOG_FILE_DIR)

# Config logging de errores
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

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Banned usernames
BLACKLISTED_USERNAMES = ['admin', 'root', 'superuser', 'test']