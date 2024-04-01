# scheduler/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.list, name='list'),
    path('create/', views.create, name='create'),
    path('delete/', views.delete_logs, name='delete_logs'),  # The new URL pattern for deletion
]
