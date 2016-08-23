from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _
from timezones.forms import TimeZoneField
from casepro.msgs.models import Label

from .models import Partner


class PartnerForm(forms.ModelForm):
    timezone = TimeZoneField(required=False)
    labels = forms.ModelMultipleChoiceField(label=_("Can Access"),
                                            queryset=Label.objects.none(),
                                            widget=forms.CheckboxSelectMultiple(),
                                            required=False)

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('org')
        super(PartnerForm, self).__init__(*args, **kwargs)

        self.fields['primary_contact'].queryset = org.get_users()
        self.fields['labels'].queryset = Label.get_all(org).order_by('name')

    class Meta:
        model = Partner
        fields = ('name', 'description', 'timezone', 'primary_contact', 'logo', 'is_restricted', 'labels')
