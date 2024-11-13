# Register your models here.
from django.contrib import admin

from backend.apps.users.models import UserRequest


@admin.register(UserRequest)
class UserRequestAdmin(admin.ModelAdmin):
    search_fields = ["company__name", "sender__username", "status"]
    list_filter = ["status", "company", "sender"]
    list_display = ["company", "sender", "status", "created_at", "updated_at"]
