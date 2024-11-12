from django.shortcuts import get_object_or_404
from rest_framework import permissions

from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.users.models import UserRequest


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            company_id = request.data.get("company")
            if company_id:
                company = get_object_or_404(Company, id=company_id)
                return company.owner == request.user
        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, CompanyInvitation) or isinstance(obj, UserRequest):
            return obj.company.owner == request.user
        return False
