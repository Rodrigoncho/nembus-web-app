# nembus_project/settings.py

import os # Necesario para leer variables de entorno
import dj_database_url # Necesario para configurar la base de datos desde una URL
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECRET_KEY: Lee desde variable de entorno en producción, usa una clave simple para desarrollo.
# ¡NO USES LA CLAVE DE DESARROLLO EN PRODUCCIÓN! Render te permitirá setearla de forma segura.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'dev-insecure-k3y-pl4c3h0ld3r-@$!abc*&^' # Clave simple y aleatoria para desarrollo
)

# DEBUG: Lee desde variable de entorno. Por defecto es False para producción.
# En Render, NO definas DJANGO_DEBUG o ponla en False. En local, puedes crearla y ponerla en True si necesitas.
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# ALLOWED_HOSTS: Configuración para desarrollo y producción (Render)
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] # Para desarrollo local

# Obtiene el hostname externo proporcionado por Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    print(f"Añadido RENDER_EXTERNAL_HOSTNAME a ALLOWED_HOSTS: {RENDER_EXTERNAL_HOSTNAME}") # Para depuración

# Si tienes un dominio personalizado configurado en Render, añádelo aquí
# o léelo desde otra variable de entorno.
# CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
# if CUSTOM_DOMAIN:
#     ALLOWED_HOSTS.append(CUSTOM_DOMAIN)

print(f"ALLOWED_HOSTS configurados: {ALLOWED_HOSTS}") # Para depuración al iniciar


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'nembus_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # --- Configuración para WhiteNoise (archivos estáticos en producción) ---
    # Debe ir DESPUÉS de SecurityMiddleware y ANTES que todo lo demás
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ---------------------------------------------------------------------
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nembus_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Directorio de plantillas a nivel de proyecto
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

WSGI_APPLICATION = 'nembus_project.wsgi.application'


# Database
# Configuración dinámica: usa DATABASE_URL de Render si existe, si no, usa SQLite local.
DATABASES = {
    'default': dj_database_url.config(
        # Busca la variable de entorno DATABASE_URL
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', # Fallback a SQLite local
        conn_max_age=600 # Opcional: Reutiliza conexiones a la BD por 10 minutos
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-cl' # Español Chileno

TIME_ZONE = 'America/Santiago' # Zona horaria de Chile Continental

USE_I18N = True

USE_TZ = True # Habilitar soporte para zonas horarias


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
# Directorio donde `collectstatic` reunirá todos los archivos estáticos para producción.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración para WhiteNoise (servir estáticos en producción)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Media files (User Uploads)
# https://docs.djangoproject.com/en/5.2/topics/files/

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Donde se guardan localmente (OJO: No persistente en Render por defecto)


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIONES PERSONALIZADAS ---
LOGIN_URL = 'nembus_app:login' # URL a la que redirige @login_required

# CSRF Trusted Origins - Necesario cuando DEBUG=False
CSRF_TRUSTED_ORIGINS = []
if RENDER_EXTERNAL_HOSTNAME: # Usa la variable que extrajimos antes
    # Render usa HTTPS, así que añadimos la URL completa
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Si tienes un dominio personalizado, añádelo también con https://
# if CUSTOM_DOMAIN:
#     CSRF_TRUSTED_ORIGINS.append(f"https://{CUSTOM_DOMAIN}")

print(f"CSRF_TRUSTED_ORIGINS configurados: {CSRF_TRUSTED_ORIGINS}") # Para depuración


# --- CONFIGURACIONES ADICIONALES (OPCIONALES PERO RECOMENDADAS) ---

# Logging (básico para ver errores en Render)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO', # Cambia a 'DEBUG' si necesitas más detalle temporalmente
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}