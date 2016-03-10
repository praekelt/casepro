from __future__ import unicode_literals

import regex
import six

from casepro.backend import get_backend
from casepro.contacts.models import Contact
from casepro.utils import normalize, parse_csv
from casepro.utils.export import BaseExport
from dash.orgs.models import Org
from dash.utils import chunks
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from enum import Enum
from redis_cache import get_redis_connection


SAVE_CONTACT_ATTR = '__data__contact'
SAVE_LABELS_ATTR = '__data__labels'

LABEL_LOCK_KEY = 'lock:label:%d:%s'
MESSAGE_LOCK_KEY = 'lock:message:%d:%d'


class MessageFolder(Enum):
    inbox = 1
    flagged = 2
    archived = 3
    unlabelled = 4


@python_2_unicode_compatible
class Label(models.Model):
    """
    Corresponds to a message label in RapidPro. Used for determining visibility of messages to different partners.
    """
    KEYWORD_MIN_LENGTH = 3

    org = models.ForeignKey(Org, verbose_name=_("Organization"), related_name='labels')

    uuid = models.CharField(max_length=36, unique=True)

    name = models.CharField(verbose_name=_("Name"), max_length=32, help_text=_("Name of this label"))

    description = models.CharField(verbose_name=_("Description"), null=True, max_length=255)

    keywords = models.CharField(verbose_name=_("Keywords"), null=True, blank=True, max_length=1024)

    is_active = models.BooleanField(default=True, help_text="Whether this label is active")

    @classmethod
    def create(cls, org, name, description, keywords):
        remote_uuid = get_backend().create_label(org, name)

        return cls.objects.create(org=org,
                                  uuid=remote_uuid,
                                  name=name,
                                  description=description,
                                  keywords=','.join(keywords))

    @classmethod
    def get_all(cls, org, user=None):
        if not user or user.can_administer(org):
            return cls.objects.filter(org=org, is_active=True)

        partner = user.get_partner()
        return partner.get_labels() if partner else cls.objects.none()

    @classmethod
    def get_keyword_map(cls, org):
        """
        Gets a map of all keywords to their corresponding labels
        :param org: the org
        :return: map of keywords to labels
        """
        labels_by_keyword = {}
        for label in Label.get_all(org):
            for keyword in label.get_keywords():
                labels_by_keyword[keyword] = label
        return labels_by_keyword

    @classmethod
    def lock(cls, org, uuid):
        return get_redis_connection().lock(LABEL_LOCK_KEY % (org.pk, uuid), timeout=60)

    def get_keywords(self):
        return parse_csv(self.keywords) if self.keywords else []

    def get_partners(self):
        return self.partners.filter(is_active=True)

    def release(self):
        self.is_active = False
        self.save(update_fields=('is_active',))

    def as_json(self):
        return {'id': self.pk, 'name': self.name}

    @classmethod
    def is_valid_keyword(cls, keyword):
        return len(keyword) >= cls.KEYWORD_MIN_LENGTH and regex.match(r'^\w[\w\- ]*\w$', keyword)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Message(models.Model):
    """
    A incoming message from the backend
    """
    TYPE_INBOX = 'I'
    TYPE_FLOW = 'F'

    TYPE_CHOICES = ((TYPE_INBOX, _("Inbox")), (TYPE_FLOW, _("Flow")))

    DIRECTION = 'I'

    org = models.ForeignKey(Org, verbose_name=_("Organization"), related_name='incoming_messages')

    backend_id = models.IntegerField(unique=True, help_text=_("Backend identifier for this message"))

    contact = models.ForeignKey(Contact, related_name='incoming_messages')

    type = models.CharField(max_length=1)

    text = models.TextField(max_length=640, verbose_name=_("Text"))

    labels = models.ManyToManyField(Label, help_text=_("Labels assigned to this message"),
                                    related_name='messages', through='Labelling')
    is_flagged = models.BooleanField(default=False)

    is_archived = models.BooleanField(default=False)

    created_on = models.DateTimeField()

    is_handled = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    case = models.ForeignKey('cases.Case', null=True, related_name="incoming_messages")

    def __init__(self, *args, **kwargs):
        if SAVE_CONTACT_ATTR in kwargs:
            setattr(self, SAVE_CONTACT_ATTR, kwargs.pop(SAVE_CONTACT_ATTR))
        if SAVE_LABELS_ATTR in kwargs:
            setattr(self, SAVE_LABELS_ATTR, kwargs.pop(SAVE_LABELS_ATTR))

        super(Message, self).__init__(*args, **kwargs)

    @classmethod
    def get_unhandled(cls, org):
        return cls.objects.filter(org=org, is_handled=False)

    @classmethod
    def lock(cls, org, backend_id):
        return get_redis_connection().lock(MESSAGE_LOCK_KEY % (org.pk, backend_id), timeout=60)

    @classmethod
    def search(cls, org, user, search):
        """
        Search for messages
        """
        labels = Label.get_all(org, user)

        # only show non-deleted handled messages
        queryset = org.incoming_messages.filter(is_active=True, is_handled=True)

        # filter by user labels.. or exclude them for the unlabelled view
        if search['folder'] == MessageFolder.unlabelled:
            queryset = queryset.filter(type=Message.TYPE_INBOX)

            # TODO need a trigger based has_labels flag on Message to speed up this view and the inbox view for admins
            # For now we just return all messages, and let angular remove the labelled ones

            # queryset = queryset.exclude(labels__in=labels)  # too slow...
            pass
        else:
            if search['label']:
                labels = labels.filter(pk=search['label'])
            else:
                # if not filtering by a single label, need distinct to avoid duplicates
                queryset = queryset.distinct()

            queryset = queryset.filter(labels__in=list(labels))

        # archived messages can be implicitly or explicitly included depending on folder
        if search['folder'] == MessageFolder.archived:
            queryset = queryset.filter(is_archived=True)
        elif search['folder'] == MessageFolder.flagged:
            if not search['include_archived']:
                queryset = queryset.filter(is_archived=False)
        else:
            queryset = queryset.filter(is_archived=False)

        # only show flagged messages in flagged folder
        if search['folder'] == MessageFolder.flagged:
            queryset = queryset.filter(is_flagged=True)

        if search['text']:
            queryset = queryset.filter(text__icontains=search['text'])

        if search['contact']:
            queryset = queryset.filter(contact__uuid=search['contact'])
        if search['groups']:
            queryset = queryset.filter(contact__groups__uuid__in=search['groups']).distinct()

        if search['after']:
            queryset = queryset.filter(created_on__gt=search['after'])
        if search['before']:
            queryset = queryset.filter(created_on__lt=search['before'])

        queryset = queryset.select_related('contact').prefetch_related('labels', 'case__assignee')

        return queryset.order_by('-created_on')

    def auto_label(self, labels_by_keyword):
        """
        Applies the auto-label matcher to this message
        :param labels_by_keyword: a map of labels by each keyword
        :return: the set of matching labels
        """
        norm_text = normalize(self.text)
        matches = set()

        for keyword, label in six.iteritems(labels_by_keyword):
            if regex.search(r'\b' + keyword + r'\b', norm_text, flags=regex.IGNORECASE | regex.UNICODE | regex.V0):
                matches.add(label)

        return matches

    def add_labels(self, *labels):
        cur_labellings = Labelling.objects.filter(message=self, label__in=labels).values_list('message', 'label')
        non_existing = [label for label in labels if (self.pk, label.pk) not in cur_labellings]
        new_labellings = [Labelling(message=self, label=l, message_created_on=self.created_on) for l in non_existing]
        Labelling.objects.bulk_create(new_labellings)

    def remove_labels(self, *labels):
        Labelling.objects.filter(message=self, label__in=labels).delete()

    def get_history(self):
        """
        Gets the actions for this message in reverse chronological order
        :return: the actions
        """
        return self.actions.select_related('created_by', 'label').order_by('-pk')

    def release(self):
        """
        Deletes this message, removing it from any labels (only callable by sync)
        """
        self.labels.clear()

        self.is_active = False
        self.save(update_fields=('is_active',))

    def update_labels(self, user, labels):
        """
        Updates this message's labels to match the given set, creating label and unlabel actions as necessary
        """
        with self.lock(self.org, self.backend_id):
            current_labels = set(self.labels.all())

            add_labels = [l for l in labels if l not in current_labels]
            rem_labels = [l for l in current_labels if l not in labels]

            for label in add_labels:
                self.bulk_label(self.org, user, [self], label)
            for label in rem_labels:
                self.bulk_unlabel(self.org, user, [self], label)

    @staticmethod
    def bulk_flag(org, user, messages):
        messages = list(messages)
        if messages:
            org.incoming_messages.filter(org=org, pk__in=[m.pk for m in messages]).update(is_flagged=True)

            get_backend().flag_messages(org, messages)

            MessageAction.create(org, user, messages, MessageAction.FLAG)

    @staticmethod
    def bulk_unflag(org, user, messages):
        messages = list(messages)
        if messages:
            org.incoming_messages.filter(org=org, pk__in=[m.pk for m in messages]).update(is_flagged=False)

            get_backend().unflag_messages(org, messages)

            MessageAction.create(org, user, messages, MessageAction.UNFLAG)

    @staticmethod
    def bulk_label(org, user, messages, label):
        messages = list(messages)
        if messages:
            for msg in messages:
                msg.add_labels(label)

            get_backend().label_messages(org, messages, label)

            MessageAction.create(org, user, messages, MessageAction.LABEL, label)

    @staticmethod
    def bulk_unlabel(org, user, messages, label):
        messages = list(messages)
        if messages:
            for msg in messages:
                msg.remove_labels(label)

            get_backend().unlabel_messages(org, messages, label)

            MessageAction.create(org, user, messages, MessageAction.UNLABEL, label)

    @staticmethod
    def bulk_archive(org, user, messages):
        messages = list(messages)
        if messages:
            org.incoming_messages.filter(org=org, pk__in=[m.pk for m in messages]).update(is_archived=True)

            get_backend().archive_messages(org, messages)

            MessageAction.create(org, user, messages, MessageAction.ARCHIVE)

    @staticmethod
    def bulk_restore(org, user, messages):
        messages = list(messages)
        if messages:
            org.incoming_messages.filter(org=org, pk__in=[m.pk for m in messages]).update(is_archived=False)

            get_backend().restore_messages(org, messages)

            MessageAction.create(org, user, messages, MessageAction.RESTORE)

    def as_json(self):
        """
        Prepares this message for JSON serialization
        """
        case_json = {'id': self.case.pk, 'assignee': self.case.assignee.as_json()} if self.case else None

        return {
            'id': self.backend_id,
            'contact': self.contact.as_json(),
            'text': self.text,
            'time': self.created_on,
            'labels': [l.as_json() for l in self.labels.all()],
            'flagged': self.is_flagged,
            'archived': self.is_archived,
            'direction': self.DIRECTION,
            'flow': self.type == self.TYPE_FLOW,
            'case': case_json,
            'sender': None
        }

    def __str__(self):
        return self.text if self.text else self.pk


class Labelling(models.Model):
    """
    The message and label many-to-many relationship is defined through this model which adds an extra field to hold the
    message created_on datetime. This allows us to make faster queries based on combinations of labels and the message
    creation time because we don't have to fetch all messages with those labels.
    """
    message = models.ForeignKey(Message)

    label = models.ForeignKey(Label)

    message_created_on = models.DateTimeField()


class MessageAction(models.Model):
    """
    An action performed on a set of messages
    """
    FLAG = 'F'
    UNFLAG = 'N'
    LABEL = 'L'
    UNLABEL = 'U'
    ARCHIVE = 'A'
    RESTORE = 'R'

    ACTION_CHOICES = ((FLAG, _("Flag")),
                      (UNFLAG, _("Un-flag")),
                      (LABEL, _("Label")),
                      (UNLABEL, _("Remove Label")),
                      (ARCHIVE, _("Archive")),
                      (RESTORE, _("Restore")))

    org = models.ForeignKey(Org, verbose_name=_("Organization"), related_name='message_actions')

    messages = models.ManyToManyField(Message, related_name='actions')

    action = models.CharField(max_length=1, choices=ACTION_CHOICES)

    created_by = models.ForeignKey(User, related_name="message_actions")

    created_on = models.DateTimeField(auto_now_add=True)

    label = models.ForeignKey(Label, null=True)

    @classmethod
    def create(cls, org, user, messages, action, label=None):
        action_obj = MessageAction.objects.create(org=org, action=action, created_by=user, label=label)
        action_obj.messages.add(*messages)
        return action_obj

    def as_json(self):
        return {'id': self.pk,
                'action': self.action,
                'created_by': self.created_by.as_json(),
                'created_on': self.created_on,
                'label': self.label.as_json() if self.label else None}


@python_2_unicode_compatible
class Outgoing(models.Model):
    """
    An outgoing message (i.e. broadcast) sent by a user
    """
    BULK_REPLY = 'B'
    CASE_REPLY = 'C'
    FORWARD = 'F'

    ACTIVITY_CHOICES = ((BULK_REPLY, _("Bulk Reply")), (CASE_REPLY, "Case Reply"), (FORWARD, _("Forward")))

    DIRECTION = 'O'

    org = models.ForeignKey(Org, verbose_name=_("Organization"), related_name='outgoing_messages')

    activity = models.CharField(max_length=1, choices=ACTIVITY_CHOICES)

    text = models.TextField(max_length=640, null=True)

    backend_id = models.IntegerField(unique=True, help_text=_("Broadcast id from the backend"))

    recipient_count = models.PositiveIntegerField()

    created_by = models.ForeignKey(User, related_name="outgoing_messages")

    created_on = models.DateTimeField()

    case = models.ForeignKey('cases.Case', null=True, related_name="outgoing_messages")

    @classmethod
    def create(cls, org, user, activity, text, contacts, urns, case=None):
        if not text:
            raise ValueError("Message text cannot be empty")

        backend_id, backend_created_on = get_backend().create_outgoing(org, text, list(contacts), urns)

        return cls.objects.create(org=org,
                                  backend_id=backend_id,
                                  recipient_count=len(contacts) + len(urns),
                                  activity=activity, case=case,
                                  text=text,
                                  created_by=user,
                                  created_on=backend_created_on)

    def as_json(self):
        """
        Prepares this message for JSON serialization
        """
        return {
            'id': self.pk,
            'contact': self.case.contact.as_json(),
            'text': self.text,
            'time': self.created_on,
            'labels': [],
            'flagged': False,
            'archived': False,
            'direction': self.DIRECTION,
            'sender': self.created_by.as_json()
        }

    def __str__(self):
        return self.text


class MessageExport(BaseExport):
    """
    An export of messages
    """
    directory = 'message_exports'
    download_view = 'msgs.messageexport_read'
    email_templates = 'msgs/email/message_export'

    def get_search(self):
        search = super(MessageExport, self).get_search()
        search['folder'] = MessageFolder[search['folder']]
        return search

    def render_book(self, book, search):
        from casepro.contacts.models import Field

        base_fields = ["Time", "Message ID", "Flagged", "Labels", "Text", "Contact"]
        contact_fields = Field.get_all(self.org, visible=True)
        all_fields = base_fields + [f.label for f in contact_fields]

        # load all messages to be exported
        messages = Message.search(self.org, self.created_by, search)

        def add_sheet(num):
            sheet = book.add_sheet(unicode(_("Messages %d" % num)))
            for col in range(len(all_fields)):
                field = all_fields[col]
                sheet.write(0, col, unicode(field))
            return sheet

        # even if there are no messages - still add a sheet
        if not messages:
            add_sheet(1)
        else:
            sheet_number = 1
            for msg_chunk in chunks(messages, 65535):
                current_sheet = add_sheet(sheet_number)

                row = 1
                for msg in msg_chunk:
                    current_sheet.write(row, 0, self.excel_datetime(msg.created_on), self.DATE_STYLE)
                    current_sheet.write(row, 1, msg.backend_id)
                    current_sheet.write(row, 2, 'Yes' if msg.is_flagged else 'No')
                    current_sheet.write(row, 3, ', '.join([l.name for l in msg.labels.all()]))
                    current_sheet.write(row, 4, msg.text)
                    current_sheet.write(row, 5, msg.contact.uuid)

                    fields = msg.contact.get_fields()

                    for cf in range(len(contact_fields)):
                        contact_field = contact_fields[cf]
                        current_sheet.write(row, len(base_fields) + cf, fields.get(contact_field.key, None))

                    row += 1

                sheet_number += 1

        return book
