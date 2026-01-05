from django.contrib import admin
from .models import DownloadTask

#<--- Admin Panel settings --->
@admin.register(DownloadTask)
class DownloadTaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_id",
        "status",
        "progress",
        "created_at",
    )
    search_fields = ("task_id", "url")
    list_filter = ("status",)