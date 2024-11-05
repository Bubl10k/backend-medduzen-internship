from django.contrib import admin

from backend.apps.company.models import Company


# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ["name", "owner__username"]
    filter_fields = ["name", "owner__username", "visible"]
    list_display = ["name", "owner", "visible"]
