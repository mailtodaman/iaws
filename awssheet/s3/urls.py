from django.urls import path
from django.urls import  include


from django.conf.urls import handler404

from . import views

urlpatterns = [
    path("", views.index, name="s3"),
    path('createS3_bucket', views.f_createS3_bucket, name='createS3_bucket'),
    path('removeS3_bucket', views.f_removeS3_bucket, name='removeS3_bucket'),
]