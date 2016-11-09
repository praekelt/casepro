from __future__ import unicode_literals
import os

# import our default settings
from settings_production import *  # noqa

# Pods
PODS = [{
    'label': "family_connect_registration_pod",
    'title': "Registration Information",
    'url': os.environ.get('REGISTRATION_URL', ''),
    'token': os.environ.get('REGISTRATION_AUTH_TOKEN',
                            'replace-with-auth-token'),
    'contact_id_fieldname': os.environ.get('REGISTRATION_CONTACT_ID_FIELDNAME',
                                           'registrant_id'),
    'field_mapping': [
        {"field": "msisdn_registrant", "field_name": "Cell Number"},
        {"field": "language", "field_name": "Language Preference"},
        {"field": "faccode", "field_name": "Facility Code"},
        {"field": "reg_type", "field_name": "Registration Type"},
        {"field": "mom_dob", "field_name": "Mother's Date of Birth"},
        {"field": "edd", "field_name": "Expected Due Date"},
    ]
}, {
    'label': "family_connect_subscription_pod",
    'title': "Subscription Information",
    'url': os.environ.get('SUBSCRIPTION_URL', ''),
    'token': os.environ.get('SUBSCRIPTION_AUTH_TOKEN',
                            'replace-with-auth-token'),
}]
