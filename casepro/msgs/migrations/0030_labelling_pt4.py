# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0029_labelling_pt3'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='labels_new',
        ),
        migrations.AddField(
            model_name='message',
            name='labels',
            field=models.ManyToManyField(help_text='Labels assigned to this message', related_name='messages', through='msgs.Labelling', to='msgs.Label'),
        ),
    ]
