"""
Django settings for taggedweb project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-rvyqw!#&stjgu+!8c2(ss(eybp&ypyhd)i*k6v#n2i9)y1=pdc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TAGGEDWEB_ELASTIC_IP = '18.213.87.2'
ALLOWED_HOSTS = [TAGGEDWEB_ELASTIC_IP, 'api.taggedweb.com', 'taggedweb.com', 'localhost', '127.0.0.1']

# Difference between ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS:
# https://stackoverflow.com/a/47229671/1819254
CORS_ALLOWED_ORIGINS = [
    "https://taggedweb.com",
    "https://www.taggedweb.com",
    "https://api.taggedweb.com",

    # This is temporary, just for making local development easy on port 3000
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3P Apps
    'corsheaders',
    'guardian',
    'rest_framework',
    'rest_framework.authtoken',
    'storages',
    'django_extensions',
    'phonenumber_field',

    # Project Apps
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'taggedweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'taggedweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'api.User'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# For S3 and SES access
AWS_ACCESS_KEY_ID = "AKIA4Y3JRSCZCU6XIXWE"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = 'taggedweb'
AWS_DEFAULT_ACL = 'public-read'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_AUTO_CREATE_BUCKET = True
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'api.custom_storages.StaticStorage'
AWS_S3_REGION_NAME = 'us-east-1'
STATIC_URL = "https://{}/{}/".format(AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)
AWS_QUERYSTRING_AUTH = False

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    # ModelBackend is the default, but we also want object level permissions with django-guardian
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

GUARDIAN_MONKEY_PATCH = False
GUARDIAN_GET_INIT_ANONYMOUS_USER = 'api.models.get_anonymous_user_instance'

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],

    'DEFAULT_THROTTLE_CLASSES': [
        # 'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'api.throttling.SubscriptionDailyRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        # 'anon': '2/day',
        'user': '200/day',
        'subscription': '1000/day',
    },

    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

try:
    # Over-ride settigs be defined for customization on production servers/local
    from .override_settings import *
except ImportError:
    pass
