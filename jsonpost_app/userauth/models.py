# Create your models here.

from django.db import models

class EditorLog(models.Model):
    editor = models.CharField(max_length=150)  # Name like 'API', 'admin', 'nevin'
    action = models.CharField(max_length=255)  # What was done: 'Edited Post #12'
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.editor} - {self.action} at {self.timestamp}"
