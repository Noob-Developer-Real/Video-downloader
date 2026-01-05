from django.urls import path
from .views import start_download, task_status, download_file,home

urlpatterns = [
    path("", home),
    path("download/", start_download),
    path("status/<str:task_id>/", task_status),
    path("file/<str:task_id>/", download_file),
]
