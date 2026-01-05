from django.db import models

class DownloadTask(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    url = models.URLField()
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    progress = models.PositiveSmallIntegerField(default=0)
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Local path to downloaded video"
    )
    error_message = models.TextField(blank=True, null=True)
    platform = models.CharField(
        max_length=20,
        choices=[
            ("instagram", "Instagram"),
            ("youtube", "YouTube"),
            ("reddit", "Reddit"),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # def is_expired(self, ttl_minutes=10):
    #     if not self.completed_at:
    #         return False
    #     return timezone.now() > self.completed_at + timezone.timedelta(minutes=ttl_minutes)

    def __str__(self):
        return f"{self.task_id} - {self.status}"


