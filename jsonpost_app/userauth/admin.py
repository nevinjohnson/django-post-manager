# Register your models here.

from django.contrib import admin
from .models import EditorLog

@admin.register(EditorLog)
class EditorLogAdmin(admin.ModelAdmin):
    list_display = ('editor', 'action', 'timestamp')