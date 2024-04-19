# models.py adjustment for conceptual clarity, actual implementation might vary

from django.db import models
from django.utils import timezone

from django.db import models

class ScheduledTask(models.Model):
    name = models.CharField(max_length=255)
    command = models.TextField(blank=True)  # Allow blank
    schedule = models.CharField(max_length=100)
    script = models.FileField(upload_to='scripts/', blank=True)  # Allow blank
    shell = models.CharField(max_length=50, choices=(('bash', 'Bash'), ('tcsh', 'Tcsh')), blank=True)  # Allow blank for shell as well
    # skip script and shell 

    def __str__(self):
        return self.name


class TaskResult(models.Model):
    task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='results')
    result = models.TextField()
    execution_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, default='Success')  # Example field to indicate result status

    def __str__(self):
        return f'Result of {self.task.name} at {self.execution_time.strftime("%Y-%m-%d %H:%M:%S")}'
