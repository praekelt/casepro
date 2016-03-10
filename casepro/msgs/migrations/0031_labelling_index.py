# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


INDEX_SQL = """
CREATE INDEX msgs_labelling_label_message_created_on ON msgs_labelling(label_id, message_created_on DESC);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0030_labelling_pt4'),
    ]

    operations = [
        migrations.RunSQL(INDEX_SQL)
    ]
