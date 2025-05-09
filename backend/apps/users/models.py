from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from backend.apps.shared.models import TimeStamp


# Create your models here.
class CustomUserManager(models.Manager):
    def create_user(self, username, password=None, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        if not username:
            raise ValueError(_("The Username must be set"))

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class CustomUser(TimeStamp, AbstractUser):
    image_path = models.ImageField(upload_to="avatars/", null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    def __str__(self):
        return self.username


class UserRequest(TimeStamp):
    class StatusChoices(models.TextChoices):
        PENDING = "P", _("Pending")
        APPROVED = "A", _("Approved")
        REJECTED = "R", _("Rejected")
        CANCELED = "C", _("Canceled")

    company = models.ForeignKey("company.Company", on_delete=models.CASCADE, related_name="requests")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_requests")
    status = models.CharField(max_length=1, choices=StatusChoices.choices, default=StatusChoices.PENDING)

    class Meta:
        verbose_name_plural = "User Requests"
