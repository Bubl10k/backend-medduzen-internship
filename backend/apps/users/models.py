from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.apps.shared.models import TimeStamp


# Create your models here.
class CustomUser(TimeStamp, AbstractUser):
    image_path = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username
