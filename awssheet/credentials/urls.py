from django.urls import path
from . import views

urlpatterns = [

    path('',  views.manage_credentials, name='manage_credentials'),
    path('test-credentials/azure/', views.test_azure_credentials, name='test_azure_credentials'),
    path('test-credentials/aws/', views.test_aws_credentials, name='test_aws_credentials'),
    path('test-credentials/gcp/', views.test_gcp_credentials, name='test_gcp_credentials'),
    path('test-credentials/chatgpt/', views.test_chatgpt_credentials, name='test_chatgpt_credentials'),
    # Add any other credential management URLs as needed
]