from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import DownloadTask
import subprocess
import os
import glob

@shared_task(bind=True)
def download_instagram_video(self, download_task_id):
    task = DownloadTask.objects.get(id=download_task_id)

    try:
        task.status = "STARTED"
        task.progress = 5
        task.save()

        output_dir = os.path.join(
            settings.MEDIA_ROOT,
            "downloads",
            task.platform
        )
        os.makedirs(output_dir, exist_ok=True)

        # Use task ID to avoid collisions
        output_template = os.path.join(
            output_dir,
            f"{task.id}_%(id)s.%(ext)s"
        )

        cmd = [
            settings.YTDLP_BINARY,
            "--no-playlist",
            "-f", "mp4",
            "-o", output_template,
            task.url,
        ]

        task.progress = 20
        task.save()

        # Track files before download
        before = set(glob.glob(os.path.join(output_dir, "*.mp4")))

        subprocess.run(cmd, check=True)

        after = set(glob.glob(os.path.join(output_dir, "*.mp4")))
        new_files = list(after - before)

        if not new_files:
            raise RuntimeError("Download completed but file not found")

        final_path = new_files[0]

        task.status = "SUCCESS"
        task.progress = 100
        task.file_path = final_path
        task.completed_at = timezone.now()
        task.save()

    except Exception as e:
        task.status = "FAILED"
        task.error_message = str(e)
        task.save()


@shared_task
def cleanup_old_downloads(minutes=1):
    cutoff = timezone.now() - timezone.timedelta(minutes=minutes)

    old_tasks = DownloadTask.objects.filter(
        status="SUCCESS",
        completed_at__isnull=False,
        completed_at__lt=cutoff
    )

    for task in old_tasks:
        if task.file_path and os.path.exists(task.file_path):
            try:
                os.remove(task.file_path)
            except Exception:
                return "file cannot be deleted"

        task.delete()
