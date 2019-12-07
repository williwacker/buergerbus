"""
Django settings for buergerbus project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = [
    'smart_selects',
    'Basis.apps.BasisConfig',
    'Einsatzmittel.apps.EinsatzmittelConfig',
    'Einsatztage.apps.EinsatztageConfig',
    'Klienten.apps.KlientenConfig',
    'Team.apps.TeamConfig',
    'Tour.apps.TourConfig',
    'jet.dashboard',
    'jet',
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'multiselectfield',
    'django_tables2',
    'django_cron',
    'qr_code',
#    'crispy_forms',
#    'test_app',
#    'bootstrap_modal_forms',
#    'bootstrap',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CRON_CLASSES = [
    'Basis.cron.EinsatztageCronJob',
]

ROOT_URLCONF = 'buergerbus.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Basis.utils.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'buergerbus.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


USE_DJANGO_JQUERY = True

# JET_DEFAULT_THEME = 'light-gray'
JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = True

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/Basis/'
LOGOUT_REDIRECT_URL = '/accounts/logout_success/'

# Expire nach 30 min
SESSION_EXPIRE_SECONDS = 1800
# Expire nach Aktivität
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True


# Klienten von ausserhalb der VG können hinzugefügt werden
ALLOW_OUTSIDE_CLIENTS = True
# Anzahl planbarer Fahrtage (Fahrer) /Bürotage (Koordinatoren)
COUNT_DRIVING_DAYS = 30
COUNT_OFFICE_DAYS  = 30

# Anzahl planbarer Tage für Touren
COUNT_TOUR_DAYS = 13

# Pfad für die Tourlisten zu speichern
TOUR_PATH = ''

# Fahrzeit und Ankunftszeit mittels Google Maps errechnen
USE_GOOGLE = True
# Ein/Aussteigezeit in Minuten (nur relevant mit USE_GOOGLE)
TRANSFER_TIME = 3

# DSGVO mit dem Fahrplan versenden
SEND_DSGVO = True

PORTAL = 'Bürgerbus Portal'
WELCOME = 'Willkommen auf dem Bürgerbus Portal'

# import settings.json
import json
base_dir = os.path.dirname(__file__)
overrides = json.loads(open(os.path.join(base_dir,'settings.json'), encoding='UTF-8').read())
globals().update(overrides)