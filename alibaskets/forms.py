from  django.forms import ModelForm, Textarea, Form, ValidationError
from .models import Basket
from django import forms
import os.path
class BasketForm(ModelForm):
    def clean_path(self):
        path = self.cleaned_data['path']
        if os.path.exists(path):
           raise ValidationError('path exists')
        return path
    class Meta:
        model = Basket
        fields = ['name', 'path', 'mode', 'delta_time', 'max_size']
        labels = {'max_size': ('Max size in megabytes'),}
        labels = {'delta_time': ('Cleaning interval : D HH:MM:SS'),}

class BasketEditForm(ModelForm):
    class Meta:
        model = Basket
        fields = ['mode', 'delta_time', 'max_size']
        labels = {'max_size': ('Max size in megabytes'),}
        labels = {'delta_time': ('Cleaning interval : D HH:MM:SS'),}

class PathForm(Form):
    path = forms.CharField(label='path', max_length=100)
    def clean_path(self):
        # path = self.cleaned_data['path']
        # if not os.path.exists(path):
        #     raise ValidationError('path not exists')
        # return path
        if 'remove_button' in self.data:
            path = self.cleaned_data['path']
            if not os.path.exists(path):
                raise ValidationError('path not exists')
            return path
        elif 'restore_button' in self.data:
            path = self.cleaned_data['path']
        # if not os.path.exists(path):
        #     raise ValidationError('path not exists')
            return path