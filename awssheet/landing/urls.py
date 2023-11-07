from django.urls import path

from . import views


urlpatterns = [
    path("", views.login, name="login"),
    path('aws_logout', views.aws_logout, name='aws_logout'),
    path("index", views.index, name="index"),
]

