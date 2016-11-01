from __future__ import unicode_literals
import os
import dj_database_url

# import our default settings
from settings_common import *  # noqa

SECRET_KEY = os.environ.get('SECRET_KEY', 'REPLACEME')
if os.environ.get('DEBUG', 'False') == 'True':  # envvars are strings
    DEBUG = True
else:
    DEBUG = False
TEMPLATE_DEBUG = DEBUG

SEND_EMAILS = True

HOSTNAME = os.environ.get('HOSTNAME', 'localhost:8000')
SITE_HOST_PATTERN = os.environ.get('SITE_HOST_PATTERN', 'http://%s.localhost:8000')

SITE_API_HOST = os.environ.get('SITE_API_HOST', 'http://localhost:8001/')

SENTRY_DSN = os.environ.get('SENTRY_DSN')

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get(
            'CASEPRO_DATABASE',
            'postgres://casepro:nyaruka@localhost/casepro')),
}

# SMTP Settings
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# junebug configuration
JUNEBUG_API_ROOT = os.environ.get('JUNEBUG_API_ROOT', 'http://localhost:8080/')
JUNEBUG_CHANNEL_ID = os.environ.get('JUNEBUG_CHANNEL_ID', 'replace-me')
JUNEBUG_FROM_ADDRESS = os.environ.get('JUNEBUG_FROM_ADDRESS', None)

SITE_BACKEND = 'casepro.backend.junebug.JunebugBackend'

# identity store configuration
IDENTITY_API_ROOT = os.environ.get('IDENTITY_API_ROOT',
                                   'http://localhost:8081/')
IDENTITY_AUTH_TOKEN = os.environ.get('IDENTITY_AUTH_TOKEN',
                                     'replace-with-auth-token')
IDENTITY_ADDRESS_TYPE = os.environ.get('IDENTITY_ADDRESS_TYPE',
                                       'msisdn')
IDENTITY_LANGUAGE_FIELD = os.environ.get('IDENTITY_LANGUAGE_FIELD',
                                         'language')

# Time until a case is re-assigned (specified in minutes)
case_response_required_time_str = os.environ.get(
    'SITE_CASE_RESPONSE_REQUIRED_TIME')

if case_response_required_time_str:
    SITE_CASE_RESPONSE_REQUIRED_TIME = int(case_response_required_time_str)

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost:6379')

BROKER_URL = 'redis://%s/%d' % (REDIS_HOST, 10 if TESTING else 15)
CELERY_RESULT_BACKEND = BROKER_URL
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '%s:15' % REDIS_HOST,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += (
    'casepropods.family_connect_subscription.plugin.SubscriptionPlugin',
)

if SENTRY_DSN:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )
    RAVEN_CONFIG = {
        'dsn': SENTRY_DSN,
    }

# Pods
PODS = [{
    'label': "family_connect_subscription_pod",
    'title': "Subscription Information",
    'url': "http://stage-based-messaging.familyconnect.seed.p16n.org/api/v1/",
    'token': "a6734782aeea2abf9a3ccb4e7a7077491966b115",
}]
