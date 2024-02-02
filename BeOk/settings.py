from pathlib import Path
import os
import environ
from datetime import timedelta
import dj_database_url
from django.utils.module_loading import import_string

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(
                    v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super(ObjDict, self).__getattribute__(item)

        return val
    
ACOUNT_CONSTANTS = ObjDict({"messages": "accounts.constants.Messages"})
PATIENT_CONSTANTS = ObjDict({"messages": "patients.constants.Messages"})


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'accounts',
    'patients',
    'doctors',
    'chats',
    'settings',
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # corsheaders
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'BeOk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.add_variable_to_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'BeOk.wsgi.application'
AUTH_USER_MODEL = 'accounts.User'
LOGIN_FIELD = 'username'

AUTHENTICATION_BACKENDS = [
    'utils.auth_backends.EmailBackend',
]


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# if DEBUG:

# DATABASES = {
#     'default': {
#         'ENGINE':   env("DEV_DB_ENGINE"),
#         'NAME':     env("DEV_DB_NAME"),
#         'USER':     env("DEV_DB_USER"),
#         'PASSWORD': env("DEV_DB_PASSWORD"),
#         'HOST':     env("DEV_DB_HOST"),
#         'PORT':     env("DEV_DB_PORT")
#     }
# }
# else:
    # DATABASES = {
    #     'default': dj_database_url.parse(
    #        env("DATABASE_URL")
    #     )
    # }

DATABASES = {
    'default': {
        'ENGINE':   env("PROD_DB_ENGINE"),
        'NAME':     env("PROD_DB_NAME"),
        'USER':     env("PROD_DB_USER"),
        'PASSWORD': env("PROD_DB_PASSWORD"),
        'HOST':     env("PROD_DB_HOST"),
        'PORT':     env("PROD_DB_PORT")
    }
}

EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

# simple jwt setup
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3650), # Set to 10 years
    # 'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    # 'ROTATE_REFRESH_TOKENS': True,
    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
    )
}

PAYPACK_APP_ID=env('PAYPACK_APP_ID')
PAYPACK_APP_SECRET=env('PAYPACK_APP_SECRET')


# Celery Broker - Redis
# CELERY_BROKER_URL = 'redis://localhost:6379'
# RESULT_BACKEND = 'redis://localhost:6379'
# ACCEPT_CONTENT = ['application/json']
# TASK_SERIALIZER = 'json'
# RESULT_SERIALIZER = 'json'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'sopho',
    'API_KEY': '724246444325248',
    'API_SECRET': 'b6cUJFsNoBtUf_bibpdE74Udarg',
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
