from django import forms
from django.core.files.base import File
import json
from django.contrib.sites.models import Site
from django.core.serializers.json import DjangoJSONEncoder

from .fields import FieldFile
from .models import Configuration

class ConfigurationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.key = kwargs.pop('key')
        super(ConfigurationForm, self).__init__(*args, **kwargs)
        if self.instance:
            initial = self.instance.data
            # model based fields don't know what to due with objects,
            # but they do know what to do with pks
            for key, value in initial.items():
                if hasattr(value, 'pk'):
                    initial[key] = value.pk
            self.initial.update(initial)
            
    def clean(self):
        if self.is_multipart:
            # Save data for any File- or ImageFields:
            for fld, value in self.cleaned_data.items():
                if isinstance(value, File):
                    f = FieldFile(value.name)
                    f.save(value.name, value)
                    self.cleaned_data[fld] = f
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(ConfigurationForm, self).save(False)
        data = dict(self.cleaned_data)
        del data['site']
        instance.data = data
        instance.key = self.key
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Configuration
        fields = ['site']


