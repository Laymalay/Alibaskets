from  django.forms import ModelForm, Textarea, Form, ValidationError
from .models import Basket, Task
from django import forms
import os




class BasketForm(ModelForm):
    # def clean_path(self):
    #     path = self.cleaned_data['path']
    #     if os.path.exists(path):
    #        raise ValidationError('path exists')
    #     return path 
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
        labels = {'mode': ('Cleaning mode'),}
        labels = {'delta_time': ('Cleaning interval : D HH:MM:SS'),}


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['params', 'action', 'path_to_removing_file', 'restorename', 'regexp','is_force']
        labels = {'restorename': ('filename to restore'),}
        labels = {'path_to_removing_file': ('path to file'),}
        labels = {'is_force': ('force'),}
