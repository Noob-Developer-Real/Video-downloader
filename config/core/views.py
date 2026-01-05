from django.http import JsonResponse, FileResponse, Http404
from .models import DownloadTask
from django.shortcuts import render
from django_ratelimit.decorators import ratelimit
from .utils import (
    is_valid_instagram_url,
    is_valid_youtube_url,
    is_valid_reddit_url,
)
from .tasks import download_instagram_video
import os

def home(request):
    return render(request, "core/index.html")
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@ratelimit(key="ip", rate="5/m", block=True)
def start_download(request):
    url = request.GET.get("url")
    if not url:
        return JsonResponse({"error": "URL required"}, status=400)
    if is_valid_instagram_url(url):
        platform = "instagram"
    elif is_valid_youtube_url(url):
        platform = "youtube"
    elif is_valid_reddit_url(url):
        platform = "reddit"
    else:
        return JsonResponse(
            {"error": "Only Instagram, YouTube, and Reddit URLs are supported"},
            status=400
        )

    if not url:
        return JsonResponse({"error": "URL required"}, status=400)

    ip = get_client_ip(request)

    # ---- ACTIVE TASK CAP (max 2 per IP) ----
    active_count = DownloadTask.objects.filter(
        ip_address=ip,
        status__in=["PENDING", "STARTED"]
    ).count()

    if active_count >= 2:
        return JsonResponse(
            {"error": "Too many active downloads"},
            status=429
        )

    # ---- DUPLICATE URL SUPPRESSION ----
    existing = DownloadTask.objects.filter(
        url=url,
        status="SUCCESS"
    ).order_by("-id").first()

    if existing:
        return JsonResponse({
            "task_id": existing.task_id,
            "status": "SUCCESS",
            "file_path": existing.file_path,
        })

    # ---- CREATE TASK ----
    task_record = DownloadTask.objects.create(
    url=url,
    platform=platform,
    status="PENDING",
    ip_address=ip,
    )


    celery_task = download_instagram_video.delay(task_record.id)
    task_record.task_id = celery_task.id
    task_record.save()

    return JsonResponse({
        "task_id": task_record.task_id,
        "status": task_record.status,
    })

@ratelimit(key="ip", rate="20/m", block=True)
def task_status(request, task_id):
    try:
        task = DownloadTask.objects.get(task_id=task_id)
        return JsonResponse({
            "status": task.status,
            "progress": task.progress,
            "file_path": task.file_path,
            "error": task.error_message,
        })
    except DownloadTask.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)


@ratelimit(key="ip", rate="10/h", block=True)
def download_file(request, task_id):
    try:
        task = DownloadTask.objects.get(task_id=task_id)
    except DownloadTask.DoesNotExist:
        raise Http404("Task not found")

    if task.status != "SUCCESS":
        return JsonResponse(
            {"error": "File not ready"},
            status=400
        )

    if not task.file_path or not os.path.exists(task.file_path):
        raise Http404("File not found")

    return FileResponse(
        open(task.file_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(task.file_path)
    )
