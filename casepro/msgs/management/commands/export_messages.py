from __future__ import absolute_import, unicode_literals

import json
from dash.orgs.models import Org
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Exports all outbound messages with their matching original inbound message as JSON'

    def add_arguments(self, parser):
        parser.add_argument('org_id', type=int, metavar='ORG', help="The org to pull messages for")

    def handle(self, *args, **options):
        org_id = int(options['org_id'])
        try:
            org = Org.objects.get(pk=org_id)
        except Org.DoesNotExist:
            raise CommandError("No such org with id %d" % org_id)

        for message in org.outgoing_messages.filter(reply_to__isnull=False):
            self.stdout.write(json.dumps({
                'outbound_reply': message.text,
                'inbound_message': message.reply_to.text,
                'inbound_message_labels': [{
                    'name': label.name,
                    'description': label.description
                } for label in message.reply_to.labels.all()],
            }))
