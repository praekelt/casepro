from __future__ import unicode_literals
import os

# import our default settings
from settings_production import *  # noqa


LOGGING['loggers']['casepro.backend.junebug'] = {  # noqa: F405
    'handlers': ['console'],
    'level': 'INFO',
}

DATA_API_BACKEND_TYPES = (("casepro.backend.junebug", "Junebug Backend Type"),)
DATA_API_BACKEND_TYPES = (("casepro.backend.rapidpro.RapidProBackend", "RapidPro Backend Type"),)


PODS[0]['contact_id_fieldname'] = os.environ.get(  # noqa: F405
    'REGISTRATION_CONTACT_ID_FIELDNAME',
    'registrant_id',
)

PODS[0]['field_mapping'] = [  # noqa: F405
    {"field": "faccode", "field_name": "Facility Code"},
    {"field": "reg_type", "field_name": "Registration Type"},
    {"field": "mom_dob", "field_name": "Mother's Date of Birth"},
    {"field": "edd", "field_name": "Expected Due Date"},
]
