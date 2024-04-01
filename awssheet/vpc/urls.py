from django.urls import path
from django.urls import  include


from django.conf.urls import handler404

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path('createS3_bucket', views.f_createS3_bucket, name='createS3_bucket'),
]