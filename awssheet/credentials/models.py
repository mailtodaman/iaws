from django.db import models

class AzureCredential(models.Model):
    """
    Model to store Azure credentials, including client ID, client secret, tenant ID, and subscription ID.
    """
    client_id = models.CharField(max_length=100, help_text="Azure Client ID")
    client_secret = models.CharField(max_length=100, help_text="Azure Client Secret")
    tenant_id = models.CharField(max_length=100, help_text="Azure Tenant ID")
    subscription_id = models.CharField(max_length=100, help_text="Azure Subscription ID")

    def __str__(self):
        return f"{self.client_id} - {self.subscription_id}"

class GCPCredential(models.Model):
    """
    Model to store GCP credentials as a file.
    """
    name = models.CharField(max_length=100, help_text="Name of the GCP service account")
    credential_file = models.FileField(upload_to='gcp_credentials/', help_text="GCP JSON key file")

    def __str__(self):
        return self.name

class AWSCredential(models.Model):
    """
    Model to store AWS credentials, including support for cross-account access through role assumption.
    """
    access_key_id = models.CharField(max_length=100, help_text="AWS Access Key ID")
    secret_access_key = models.CharField(max_length=100, help_text="AWS Secret Access Key")
    role_arn = models.CharField(max_length=2048, blank=True, null=True, help_text="Role ARN for cross-account access")
    session_name = models.CharField(max_length=100, blank=True, null=True, help_text="Session name for assuming the role")

    def __str__(self):
        return f"{self.access_key_id} ({'Cross-Account' if self.role_arn else 'Standard'})"


class ChatGPTCredential(models.Model):
    """
    Model to store ChatGPT credentials, primarily focused on storing an API key.
    """
    api_key = models.CharField(max_length=255, help_text="ChatGPT API Key")
    description = models.CharField(max_length=255, blank=True, null=True, help_text="Description or purpose of the API key")

    def __str__(self):
        return f"ChatGPT API Key - {self.description or 'No Description'}"
