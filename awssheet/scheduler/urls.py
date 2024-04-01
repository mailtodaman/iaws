# scheduler/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_task, name='add_task'),
    path('', views.list_tasks, name='list_tasks'),
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),  # New URL for editing tasks
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/delete/<int:task_id>/', views.delete_scheduled_task, name='delete_scheduled_task'),
    path('result/delete/<int:result_id>/', views.delete_task_result, name='delete_task_result'),
]
