from django.contrib import admin

from backend.apps.company.models import Company, CompanyInvitation


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ["name", "owner__username"]
    filter_fields = ["name", "owner__username", "visible"]
    list_display = ["name", "owner", "visible"]


@admin.register(CompanyInvitation)
class CompanyInvitationAdmin(admin.ModelAdmin):
    search_fields = ["company__name", "sender__username", "receiver__username", "status"]
    list_filter = ["status", "company", "sender", "receiver"]
    list_display = ["company", "sender", "receiver", "status"]
