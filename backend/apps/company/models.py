from django.db import models

from backend.apps.shared.models import TimeStamp
from backend.apps.users.models import CustomUser


# Create your models here.
class Company(TimeStamp, models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owned_companies")
    members = models.ManyToManyField(CustomUser, related_name="companies", blank=True)
    description = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
