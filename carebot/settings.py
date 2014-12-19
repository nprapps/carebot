#!/usr/bin/env python

import app_config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '=_1*x-_9+d_5xn#$cx%yap+@y-#13%1=1$lay5@c#^f%-u2nj-'
DEBUG = app_config.DEBUG
TEMPLATE_DEBUG = app_config.DEBUG
ALLOWED_HOSTS = []

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'carebot.urls'
WSGI_APPLICATION = 'carebot.wsgi.application'

secrets = app_config.get_secrets()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': app_config.PROJECT_SLUG,
        'USER': secrets.get('POSTGRES_USER') or app_config.PROJECT_SLUG,
        'PASSWORD': secrets.get('POSTGRES_PASSWORD'),
        'HOST': secrets.get('POSTGRES_HOST') or 'localhost',
        'PORT': secrets.get('POSTGRES_PORT') or '5432'
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = 'static'
