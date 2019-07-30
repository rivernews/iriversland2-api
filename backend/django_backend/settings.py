"""
Django settings for django_backend project.

Generated by 'django-admin startproject' using Django 1.11.13.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import datetime

try:
    # deployed local
    from .database_credentials import *
    from .s3_credentials import *
    from .other_credentials import *
    
    PRODUCTION = False  

except ImportError:
    # deployed on amz eb
    PRODUCTION = True

def is_production():
    return PRODUCTION


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
if is_production():
    DEBUG = False
else:
    DEBUG = True

# TODO: delete below
print("INFO: special prod debug mode; DEBUG={}, SECRET_KEY={}".format(DEBUG, SECRET_KEY))
print("INFO: print all env...")
print(os.environ)

if is_production():
    # ALLOWED_HOSTS = ['shaungc.com', 'www.shaungc.com', 'localhost', '127.0.0.1']
    ALLOWED_HOSTS = ['*'] # TODO: set to some stable value
else:
    ALLOWED_HOSTS = ['*']

if is_production():
    SECURE_SSL_REDIRECT = False # TODO: set to True when ssl available
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'corsheaders',
    'storages',
    # 'ckeditor',
    # 'ckeditor_uploader',

    'account',
    'api',
    'blog',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'django_backend.urls'

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

WSGI_APPLICATION = 'django_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

# RESTful permission & authentication
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        # IsAuthenticatedOrReadOnly will only allow django backend login to edit an object. Annonymous can only read (but all).
        # See how to setup permission at http://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
        # 1) To allow frontend logged in user to edit: setup JWT first, then use REST's token authorization to login and you're ready to post from frontend.
        # 2) To restrict some objects not even able to be read by annonymous, you first need 1) to setup login check, then use a filter in REST.
        # See more permission options at http://www.django-rest-framework.org/api-guide/permissions/
        # 'api.permissions...',
        # 'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=60), # 1 hour
    # JWT_REFRESH_EXPIRATION_DELTA = datetime.timedelta(days=7), # default is 7 days
}


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


AUTH_USER_MODEL = 'account.CustomUser'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

CORS_ORIGIN_ALLOW_ALL = True

ANGULAR_APP_DIR = os.path.join(BASE_DIR, 'frontend-bundle-dist') # django input static

STATICFILES_DIRS = [
    os.path.join(ANGULAR_APP_DIR), # additional path for django to collect static
]

# django output static. collectstatic will put the collected static files in STATIC_ROOT. www is for Elastic Beanstalk
# see https://docs.djangoproject.com/en/2.2/howto/static-files/deployment/
STATIC_ROOT = os.path.join(BASE_DIR, 'www', 'static')

STATIC_URL = '/static/'


# CKEDitor & S3 storage for Media files (Images, Files)
# https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html

# for media files
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'django_backend.custom_storages.MediaStorage'
MEDIA_FILES_BUCKET_NAME = 'iriversland2-media'

# for static file
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage' # already using elastic beanstalk handling static in S3 so don't bother
# But when not using elastic beanstalk, we have to config ourselves using S3
# see https://docs.djangoproject.com/en/2.2/howto/static-files/deployment/
STATICFILES_STORAGE = 'django_backend.custom_storages.StaticStorage'
# STATICFILES_STORAGE = 'django_backend.custom_storages.MediaStorage'
STATIC_FILES_BUCKET_NAME = 'iriversland2-static'

# bucket permission control
AWS_AUTO_CREATE_BUCKET = True
AWS_DEFAULT_ACL = 'public-read'
    
AWS_STORAGE_BUCKET_NAME = MEDIA_FILES_BUCKET_NAME
AWS_S3_REGION_NAME = os.environ.get('AWS_REGION', 'us-east-2') 
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % MEDIA_FILES_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# AWS_LOCATION = 'static'

# ckeditor settings
MEDIA_URL = 'http://%s/' % AWS_S3_CUSTOM_DOMAIN
MEDIA_ROOT = '/'
CKEDITOR_UPLOAD_PATH = 'editor_uploads/'
AWS_QUERYSTRING_AUTH = False # to make djjango-storage work with django-ckeditor

CKEDITOR_CONFIGS = {
    "default": {
        "height": "50vh",
        # "extraPlugins": "autogrow",
        'autoGrow_onStartup': True,
        'contentsCss': ['body { font-family: Roboto; }'],

        # 'toolbar': "full",
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Format', '-', 'Bold', 'Italic', 'Underline', 'Strike'],
            ['NumberedList', 'BulletedList', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink', '-', 'Image'],
            ['RemoveFormat', 'Source', 'Preview'],
        ],

        "removePlugins": "stylesheetparser",
        'extraAllowedContent': 'iframe[*]',
    }
}
CKEDITOR_ALLOW_NONIMAGE_FILES = False


# Email settings
SERVER_EMAIL = ''
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_PORT = int(os.environ['EMAIL_PORT'])
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = '[Test mail]'