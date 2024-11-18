from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.apps.shared.models import TimeStamp
from backend.apps.users.models import CustomUser


# Create your models here.
class Company(TimeStamp):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owned_companies")
    members = models.ManyToManyField(CustomUser, related_name="companies", blank=True)
    description = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    admins = models.ManyToManyField(CustomUser, related_name="admin_companies", blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class CompanyInvitation(TimeStamp):
    class StatusChoices(models.TextChoices):
        PENDING = "P", _("Pending")
        ACCEPTED = "A", _("Accepted")
        DECLINED = "D", _("Declined")
        REVOKED = "R", _("Revoked")

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_invitations")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_invitations")

    class Meta:
        verbose_name_plural = "Company Invitations"
        unique_together = ("company", "receiver")
