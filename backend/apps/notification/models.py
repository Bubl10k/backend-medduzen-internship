from django.db import models

from backend.apps.shared.models import TimeStamp
from backend.apps.users.models import CustomUser


# Create your models here.
class Notification(TimeStamp):
    class NotificationStatus(models.TextChoices):
        READ = "Read"
        UNREAD = "Unread"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    status = models.CharField(max_length=10, choices=NotificationStatus.choices, default=NotificationStatus.UNREAD)
    text = models.TextField()
