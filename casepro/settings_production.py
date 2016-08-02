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

HOSTNAME = os.environ.get('HOSTNAME', 'localhost:8000')

SITE_API_HOST = os.environ.get('SITE_API_HOST', 'http://localhost:8001/')

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get(
            'CASEPRO_DATABASE',
            'postgres://casepro:nyaruka@localhost/casepro')),
}

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

INSTALLED_APPS += (
    'casepropods.dummy.plugin.DummyPodPlugin',
    'casepropods.family_connect_registration.plugin.RegistrationPlugin',
)

# Pods
PODS = [{
    'label': 'dummy_pod',
    'title': 'Maternal Health Info',
    'data': {
        'items': [{
            'name': 'EDD',
            'value': '2015-07-18'
        }, {
            'name': 'Clinic Code',
            'value': '2034 6524 6421'
        }],
        'actions': [{
            'type': 'opt_out',
            'name': 'Opt out',
            'confirm': True,
            'busy_name': 'Opting out',
            'payload': {
                'delay': 1,
                'result': (True, {'message': 'User opted out'})
            }
        }, {
            'type': 'birth_message_set',
            'name': 'Switch to birth message set',
            'payload': {
                'result': (
                    False, {
                        'message': (
                            'The user appears to no longer be on the '
                            'birth message set')
                    })
            }
        }]
    }
}, {
    'label': "family_connect_registration_pod",
    'title': "Registration Information",
    'url': "http://registration.familyconnect.seed.p16n.org/api/v1/registrations/",
    'token': "5c5286055b314b09394f2f648cc1409822343ed5",
    'field_mapping': [
        {"field": "mama_name", "field_name": "Mother Name"},
        {"field": "mama_surname", "field_name": "Mother Surname"},
        {"field": "last_period_date", "field_name": "Date of last period"},
        {"field": "language", "field_name": "Language Preference"},
        {"field": "mama_id_type", "field_name": "ID Type"},
        {"field": "mama_id_no", "field_name": "ID Number"},
        {"field": "msg_receiver", "field_name": "Message Receiver"},
        {"field": "receiver_id", "field_name": "Receiver ID"},
        {"field": "hoh_name", "field_name": "Head of Household Name"},
        {"field": "hoh_surname", "field_name": "Head of Household Surname"},
        {"field": "hoh_id", "field_name": "Head of Household ID"},
        {"field": "operator_id", "field_name": "Operator ID"},
        {"field": "msg_type", "field_name": "Receives Messages As"},
    ]
}]
