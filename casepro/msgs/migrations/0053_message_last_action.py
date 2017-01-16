# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-08 07:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0052_triggers'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='last_action',
            field=models.DateTimeField(auto_now=True, help_text='Last action taken on this message', null=True),
        ),
    ]