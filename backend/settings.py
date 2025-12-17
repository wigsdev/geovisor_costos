"""
Django settings for backend project.

Configuración para Geovisor de Costos Forestales.
Usa PostgreSQL/PostGIS y Django REST Framework.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/
"""

from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ===========================================
# SEGURIDAD
# ===========================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost:8000', cast=Csv())


# ===========================================
# APLICACIONES INSTALADAS
# ===========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # GeoDjango (comentado hasta configurar GDAL)
    # 'django.contrib.gis',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local apps
    'gestion_forestal',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise para archivos estáticos en producción
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # CORS Middleware - debe ir ANTES de CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# ===========================================
# BASE DE DATOS - PostgreSQL/PostGIS
# ===========================================
import dj_database_url

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuración dinámica para producción (Railway)
if config('DATABASE_URL', default=None):
    DATABASES['default'] = dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
    # GeoDjango requiere este motor específico
    DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'


# ===========================================
# VALIDACIÓN DE CONTRASEÑAS
# ===========================================

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


# ===========================================
# INTERNACIONALIZACIÓN
# ===========================================

LANGUAGE_CODE = 'es-pe'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_TZ = True


# ===========================================
# ARCHIVOS ESTÁTICOS
# ===========================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Compresión y almacenamiento eficiente en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ===========================================
# CONFIGURACIÓN CORS (para React dev server)
# ===========================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite default
    "http://localhost:5174",  # Vite alternate port
    "http://localhost:3000",  # React default
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True


# ===========================================
# DJANGO REST FRAMEWORK
# ===========================================

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# ===========================================
# CONFIGURACIÓN GDAL/GEOS (Windows)
# ===========================================

import os

# Detectar automáticamente la ruta de GDAL en Windows
if os.name == 'nt':
    OSGEO4W = r"C:\OSGeo4W"
    POSTGIS_PATH = r"C:\Program Files\PostgreSQL\18\bin"
    
    if os.path.isdir(POSTGIS_PATH):
        os.environ['PATH'] = POSTGIS_PATH + ';' + os.environ['PATH']
        # PostGIS incluye GDAL/GEOS con números de versión
        GDAL_LIBRARY_PATH = os.path.join(POSTGIS_PATH, 'libgdal-35.dll')
        GEOS_LIBRARY_PATH = os.path.join(POSTGIS_PATH, 'libgeos_c.dll')
        # Configurar PROJ_LIB para proyecciones
        PROJ_DATA = os.path.join(
            os.path.dirname(POSTGIS_PATH), 'share', 'contrib', 'postgis-3.5', 'proj'
        )
        if os.path.isdir(PROJ_DATA):
            os.environ['PROJ_LIB'] = PROJ_DATA
    elif os.path.isdir(OSGEO4W):
        os.environ['OSGEO4W_ROOT'] = OSGEO4W
        os.environ['GDAL_DATA'] = os.path.join(OSGEO4W, 'share', 'gdal')
        os.environ['PROJ_LIB'] = os.path.join(OSGEO4W, 'share', 'proj')
        os.environ['PATH'] = os.path.join(OSGEO4W, 'bin') + ';' + os.environ['PATH']


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
