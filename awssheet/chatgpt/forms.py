# forms.py
from django import forms
from .models import ChatGPTModel

class ChatGPTForm(forms.ModelForm):
    class Meta:
        model = ChatGPTModel
        fields = ['command']
