from django import forms
import yaml
from django.conf import settings
from django.core.validators import RegexValidator
from django.forms.widgets import DateInput


dynamic_form_file = settings.DYNAMIC_FORM



class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


# class DynamicForm_OLD(forms.Form):
#     def __init__(self, yaml_dynamic_form, *args, **kwargs):
#         super(DynamicForm_OLD, self).__init__(*args, **kwargs)
      
        
#         if yaml_dynamic_form is not None:
#             self.form_heading = yaml_dynamic_form.get('form_heading', 'Dynamic Form')  # Default heading
#             for property_name, property_attrs in yaml_dynamic_form['resources'][0]['properties'].items():
#                 field_help_text = property_attrs.get('help_text', '')  # Get help text if available

#                 if property_attrs['type'] == 'input':
#                     self.fields[property_name] = forms.CharField(required=property_attrs['required'], help_text=field_help_text)
#                     if 'regex' in property_attrs:
#                         validators = [RegexValidator(
#                             regex=property_attrs['regex'],
#                             message='Invalid input. Please follow the format: {}'.format(property_attrs['regex'])
#                         )]
#                         self.fields[property_name].validators.extend(validators)
#                 elif property_attrs['type'] == 'select':
#                     choices = [(option, option) for option in property_attrs['options']]
#                     self.fields[property_name] = forms.ChoiceField(choices=choices, required=property_attrs['required'], help_text=field_help_text)
#                 elif property_attrs['type'] == 'boolean':
#                     self.fields[property_name] = forms.BooleanField(required=property_attrs.get('required', False), help_text=field_help_text)
#                 elif property_attrs['type'] == 'date':
#                     self.fields[property_name] = forms.DateField(required=property_attrs['required'], help_text=field_help_text)
#                 elif property_attrs['type'] == 'textarea':
#                     self.fields[property_name] = forms.CharField(widget=forms.Textarea, required=property_attrs['required'], help_text=field_help_text)
#                     if 'regex' in property_attrs:
#                         validators = [RegexValidator(
#                             regex=property_attrs['regex'],
#                             message='Invalid input. Please follow the format: {}'.format(property_attrs['regex'])
#                         )]
#                         self.fields[property_name].validators.extend(validators)
                
#                 # Add additional field types as needed
#         else:
#             # Set default values if yaml_dynamic_form is None
#             self.form_heading = 'Dynamic Form'


class DynamicForm(forms.Form):
    def __init__(self, yaml_dynamic_form, *args, **kwargs):
        super(DynamicForm, self).__init__(*args, **kwargs)

        if yaml_dynamic_form is not None:
            self.create_fields_from_yaml(yaml_dynamic_form)
        else:
            self.form_heading = 'Dynamic Form'  # Default heading

    def create_fields_from_yaml(self, yaml_dynamic_form):
        self.form_heading = yaml_dynamic_form.get('form_heading', 'Dynamic Form')
        for property_name, property_attrs in yaml_dynamic_form['resources'][0]['properties'].items():
            field_type = property_attrs.get('type')
            field_required = property_attrs.get('required', False)
            field_help_text = property_attrs.get('help_text', '')
            field_regex = property_attrs.get('regex', None)

            # Add fields based on type
            if field_type == 'input':
                self.add_input_field(property_name, field_required, field_help_text, field_regex)
            elif field_type == 'select':
                self.add_select_field(property_name, property_attrs['options'], field_required, field_help_text)
            elif field_type == 'boolean':
                self.add_boolean_field(property_name, field_required, field_help_text)
            elif field_type == 'date':
                self.add_date_field(property_name, field_required, field_help_text)
            elif field_type == 'textarea':
                self.add_textarea_field(property_name, field_required, field_help_text, field_regex)
            else:
                # Handle unexpected field types or log a warning
                pass

    def add_input_field(self, name, required, help_text, regex):
        self.fields[name] = forms.CharField(required=required, help_text=help_text)
        if regex:
            self.fields[name].validators.append(RegexValidator(regex=regex, message='Invalid input. Please follow the format: {}'.format(regex)))

    def add_select_field(self, name, options, required, help_text):
        choices = [(option, option) for option in options]
        self.fields[name] = forms.ChoiceField(choices=choices, required=required, help_text=help_text)

    def add_boolean_field(self, name, required, help_text):
        self.fields[name] = forms.BooleanField(required=required, help_text=help_text)

    def add_date_field(self, name, required, help_text):
        self.fields[name] = forms.DateField(
            widget=DateInput(attrs={'type': 'date'}),
            required=required,
            help_text=help_text
        )

    def add_textarea_field(self, name, required, help_text, regex):
        self.fields[name] = forms.CharField(widget=forms.Textarea, required=required, help_text=help_text)
        if regex:
            self.fields[name].validators.append(RegexValidator(regex=regex, message='Invalid input. Please follow the format: {}'.format(regex)))
