# forms.py
from django import forms
from .models import LogsModel

class LogsForm(forms.ModelForm):
    class Meta:
        model = LogsModel
        fields = ['command']
