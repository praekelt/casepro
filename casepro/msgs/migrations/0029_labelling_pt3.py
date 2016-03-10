# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0028_labelling_pt2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='labels',
        ),
    ]
