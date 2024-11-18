from django.shortcuts import get_object_or_404
from rest_framework import permissions

from backend.apps.company.models import Company


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsInvitationOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            company_id = request.data.get("company")
            if not company_id:
                return False
            company = get_object_or_404(Company, id=company_id)
            return company.owner == request.user
        return True

    def has_object_permission(self, request, view, obj):
        return obj.company.owner == obj.sender


class IsRequestOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.company.owner == request.user
