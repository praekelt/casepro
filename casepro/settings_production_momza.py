from __future__ import unicode_literals
import os

# import our default settings
from settings_production import *  # noqa

PODS[0]['contact_id_fieldname'] = os.environ.get(  # noqa: F405
    'REGISTRATION_CONTACT_ID_FIELDNAME',
    'registrant_id',
)

PODS[0]['field_mapping'] = [  # noqa: F405
    {"field": "msisdn_registrant", "field_name": "Cell Number"},
    {"field": "language", "field_name": "Language Preference"},
    {"field": "faccode", "field_name": "Facility Code"},
    {"field": "reg_type", "field_name": "Registration Type"},
    {"field": "mom_dob", "field_name": "Mother's Date of Birth"},
    {"field": "edd", "field_name": "Expected Due Date"},
]
