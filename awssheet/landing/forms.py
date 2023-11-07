from django import forms

class AWSCredentialsForm(forms.Form):
    aws_access_key_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='AWS Access Key ID')
    aws_secret_access_key = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='AWS Secret Access Key')
