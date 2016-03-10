# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0026_auto_20160309_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='Labelling',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message_created_on', models.DateTimeField()),
                ('label', models.ForeignKey(to='msgs.Label')),
                ('message', models.ForeignKey(to='msgs.Message')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='labels_new',
            field=models.ManyToManyField(help_text='Labels assigned to this message', related_name='messages_new', through='msgs.Labelling', to='msgs.Label'),
        ),
    ]
