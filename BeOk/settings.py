from pathlib import Path
import os
import environ
from datetime import timedelta
# import dj_database_url
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
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://localhost:8000",
    "https://localhost:[0-9]*", # with arbitrary port number
    "http://localhost:[0-9]*", # with arbitrary port number unencrypted
]

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
    'drf_spectacular',
    'rest_framework',
    'rest_framework_simplejwt',
    # 'cloudinary_storage',
    # 'cloudinary',
    'storages',
]

CUSTOM_APPS = [
    'accounts',
    'patients',
    'doctors',
    'chats',
    'settings',
    'hospital',
]

INSTALLED_APPS += CUSTOM_APPS

MIDDLEWARE = [
    # MiddlewareToCaptureRequestHeader
    # 'utils.customer_middle_ware.MiddlewareToCaptureRequestHeader',
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
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'BEOK BACKEND API',
    'DESCRIPTION': 'API for BeOk Backend',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

# simple jwt setup
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3650), # Set to 10 years
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
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

USE_S3  = env('USE_S3') == 'True'
if USE_S3 :
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
    AWS_S3_SIGNATURE_NAME = env('AWS_S3_SIGNATURE_NAME')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_VERIFY = True
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
        'ACL': 'public-read',
    }
    STORAGES = {
        'default': {
            "BACKEND": "storages.backends.s3.S3Storage",

        },
        "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "LOCATION": "static",
        },
    }
else:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env("CLOUDINARY_CLOUD_NAME"),
    'API_KEY': env("CLOUDINARY_API_KEY"),
    'API_SECRET': env("CLOUDINARY_API_SECRET"),
}

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# MEDIA_URL = '/media/'
# # MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
