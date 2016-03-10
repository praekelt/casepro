# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def populate_message_labellings(apps, schema_editor):
    Org = apps.get_model('orgs', 'Org')
    Labelling = apps.get_model('msgs', 'Labelling')

    for org in Org.objects.order_by('pk'):
        print "Migrating labels for org #%d..." % org.pk

        for label in org.labels.order_by('name'):
            messages = list(label.messages.all())

            for message in messages:
                Labelling.objects.create(message=message, label=label, message_created_on=message.created_on)

            print " > Migrated label '%s' (%d messages)" % (label.name, len(messages))


class Migration(migrations.Migration):

    dependencies = [
        ('msgs', '0027_labelling_pt1'),
    ]

    operations = [
        migrations.RunPython(populate_message_labellings)
    ]
