"""
Django settings for buergerbus project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import copy
from decouple import config, Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=Csv())


# Application definition

INSTALLED_APPS = [
	'smart_selects',
	'Basis.apps.BasisConfig',
	'Einsatzmittel.apps.EinsatzmittelConfig',
	'Einsatztage.apps.EinsatztageConfig',
	'Klienten.apps.KlientenConfig',
	'Kommunen.apps.KommunenConfig',
	'Team.apps.TeamConfig',
	'Tour.apps.TourConfig',
	'Faq.apps.FaqConfig',
	'jet.dashboard',
	'jet',
	'django_filters',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django_nose',
	'multiselectfield',
	'django_tables2',
	'django_cron',
	'qr_code',
	'logtailer',
]

# Use nose to run all tests
#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the 'foo' and 'bar' apps
#NOSE_ARGS = [
#    '--with-coverage',
#    '--cover-package=Einsatzmittel,Einsatztage,Klienten,Team,Tour,Basis',
#]

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
	'Basis.cron.BackupCronJob',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 100
        }
    }
}

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
		'ENGINE': 	config('DATABASE_ENGINE'),
		'NAME': 	config('DATABASE_NAME'),
		'USER': 	config('DATABASE_USER'),
		'PASSWORD': config('DATABASE_PASSWORD'),
		'HOST': 	config('DATABASE_HOST', default='localhost'),
		'PORT': 	config('DATABASE_PORT', cast=int),
		'OPTIONS':  eval(config('DATABASE_OPTIONS', default='{}')),
	},
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
	{
		'NAME': 'Basis.utils.MyPasswordValidator',
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

STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default='')

STATICFILES_DIRS = [
	os.path.join(BASE_DIR, "static"),
]

SECURE_CONTENT_TYPE_NOSNIFF 	= config('SECURE_CONTENT_TYPE_NOSNIFF', default=False, cast=bool)
X_FRAME_OPTIONS 				= config('X_FRAME_OPTIONS', default='DENY')
CSRF_COOKIE_SECURE 				= config('CSRF_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_SECURE 			= config('SESSION_COOKIE_SECURE', default=False, cast=bool)
SECURE_SSL_REDIRECT 			= config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_BROWSER_XSS_FILTER 		= config('SECURE_BROWSER_XSS_FILTER', default=False, cast=bool)
SECURE_HSTS_SECONDS 			= config('SECURE_HSTS_SECONDS', default=3600, cast=int)
SECURE_HSTS_PRELOAD 			= config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
SECURE_HSTS_INCLUDE_SUBDOMAINS  = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)

USE_DJANGO_JQUERY = True

# JET_DEFAULT_THEME = 'light-gray'
JET_SIDE_MENU_COMPACT = True
JET_CHANGE_FORM_SIBLING_LINKS = True

INTERNAL_IPS = config('INTERNAL_IPS', default='127.0.0.1', cast=Csv())

LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/accounts/logout_success/'

LOCAL_APPS = [
	'Basis',
	'Einsatzmittel',
	'Einsatztage',
	'Faq',
	'Klienten',
	'Team',
	'Tour'
]

local_logger_conf = {
	'handlers':['file'],
	'propagate': True,
	'level': config('LOG_LEVEL', default='INFO'),
}

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
				'()': 'django.utils.log.RequireDebugFalse',
		},
		'require_debug_true': {
				'()': 'django.utils.log.RequireDebugTrue',
		},
	},	
	'formatters': {
		'verbose': {
			'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
			'datefmt' : "%Y-%m-%d %H:%M:%S"
		},
		'simple': {
			'format': '%(levelname)s %(message)s'
		},
	},
	'handlers': {
		'file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': '/var/log/buergerbus.log',
			'formatter': 'verbose'
		},
		'mail_admins': {
			'level': 'ERROR',
			'class': 'django.utils.log.AdminEmailHandler',
			'filters': ['require_debug_false'],
		}
	},
	'loggers': {
		'django': {
			'handlers':['file'],
			'propagate': True,
			'level': config('LOG_LEVEL', default='INFO'),
		},
		'django.request': {
			'handlers': ['file','mail_admins'],
			'propagate': True,
			'level': 'ERROR',
		}
	}
}
LOGGING['loggers'].update({app: copy.deepcopy(local_logger_conf) for app in LOCAL_APPS})

ADMINS = [
	(config('ADMIN_NAME', default='Admin'), config('ADMIN_EMAIL', default=''))
]
SERVER_EMAIL = config('SERVER_EMAIL', default=None)

MEDIA_URL 			= '/uploads/'
MEDIA_ROOT 			= os.path.join(BASE_DIR, 'uploads')

# Expire nach 30 min
SESSION_EXPIRE_SECONDS 				= config('SESSION_EXPIRE_SECONDS', default=1800, cast=int)
# Expire nach Aktivität
SESSION_EXPIRE_AFTER_LAST_ACTIVITY 	= config('SESSION_EXPIRE_AFTER_LAST_ACTIVITY', default=True, cast=bool)


# Klienten von ausserhalb der VG können hinzugefügt werden
ALLOW_OUTSIDE_CLIENTS = config('ALLOW_OUTSIDE_CLIENTS', default=False, cast=bool)
# Anzahl planbarer Fahrtage (Fahrer) /Bürotage (Koordinatoren)
COUNT_DRIVING_DAYS 	= config('COUNT_DRIVING_DAYS', default=30, cast=int)
COUNT_OFFICE_DAYS  	= config('COUNT_OFFICE_DAYS', default=30, cast=int)
# Tour Anfangs- und Endzeiten berücksichtigen
USE_TOUR_HOURS		= config('USE_TOUR_HOURS', default=False, cast=bool)

# Anzahl planbarer Tage für Touren
COUNT_TOUR_DAYS 	= config('COUNT_TOUR_DAYS', default=13, cast=int)

# Pfad für die Tourlisten zu speichern
TOUR_PATH  			= config('TOUR_PATH', default='tour\\')

# Fahrzeit und Ankunftszeit mittels Google Maps errechnen
USE_GOOGLE 			= config('USE_GOOGLE', default=True, cast=bool)
GOOGLEMAPS_KEY 		= config('GOOGLEMAPS_KEY', default='')
# Ein/Aussteigezeit in Minuten (nur relevant mit USE_GOOGLE)
TRANSFER_TIME 		= config('TRANSFER_TIME', default=3, cast=int)

# DSGVO mit dem Fahrplan versenden
SEND_DSGVO 			= config('SEND_DSGVO', default=False, cast=bool)

DSGVO_PATH          = config('DSGVO_PATH', default='tour\\')
EMAIL_HOST          = config('EMAIL_HOST', default='localhost')
EMAIL_PORT          = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS       = config('EMAIL_USE_TLS', default=False, cast=bool)
EMAIL_USE_SSL       = config('EMAIL_USE_SSL', default=False, cast=bool)
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL', default='Bürgerbus Team <noreply@example.com>')

PORTAL              = config('PORTAL', default='Bürgerbus Portal')
WELCOME 			= config('PORTAL', default='Willkommen auf dem Bürgerbus Portal')

LOGTAILER_HISTORY_LINES = 100