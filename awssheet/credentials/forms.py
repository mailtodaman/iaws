from django import forms
from .models import AzureCredential, GCPCredential, AWSCredential, ChatGPTCredential

class AzureCredentialForm(forms.ModelForm):
    """
    Form for managing Azure credentials.
    """
    class Meta:
        model = AzureCredential
        fields = '__all__'

class GCPCredentialForm(forms.ModelForm):
    """
    Form for managing GCP credentials.
    """
    class Meta:
        model = GCPCredential
        fields = '__all__'

class AWSCredentialForm(forms.ModelForm):
    """
    Form for managing AWS credentials.
    """
    class Meta:
        model = AWSCredential
        fields = '__all__'

class ChatGPTCredentialForm(forms.ModelForm):
    """
    Form for managing ChatGPT credentials.
    """
    class Meta:
        model = ChatGPTCredential
        fields = '__all__'
