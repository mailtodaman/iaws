from django.contrib import admin
from .models import ScheduledTask, TaskResult
# Register your models here.
model_list = [ScheduledTask, TaskResult]

admin.site.register(model_list)


