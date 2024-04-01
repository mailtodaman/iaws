from django.urls import path
from . import views


urlpatterns = [
    path('reports/<str:platform>/', views.ReportsView.as_view()),
]
