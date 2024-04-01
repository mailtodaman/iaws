# models.py
from django.db import models

class ChatGPTModel(models.Model):
    username = models.CharField(max_length=255)
    command = models.TextField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - Command logged on {self.created_at}"