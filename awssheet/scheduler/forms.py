# scheduler/forms.py

from django import forms
from .models import ScheduledTask
from django.core.exceptions import ValidationError

class ScheduledTaskForm(forms.ModelForm):
    class Meta:
        model = ScheduledTask
        fields = ['name', 'command', 'schedule', 'script', 'shell']

    def clean(self):
        """
        Custom validation to ensure either command or script is provided.
        """
        cleaned_data = super().clean()
        command = cleaned_data.get("command")
        script = cleaned_data.get("script")

        # Check if both command and script are missing
        if not command and not script:
            raise ValidationError("Either a command or a script must be provided.")

        # No need to return anything as we are modifying cleaned_data in place
