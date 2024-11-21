from rest_framework.permissions import BasePermission

from backend.apps.company.models import Company


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            company_id = request.data.get("company")
            if not company_id:
                return False
            company = Company.objects.filter(id=company_id).first()
            if not company:
                return False
            return company.owner == request.user or request.user in company.admins.all()
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ["update", "partial_update", "destroy"]:
            company = obj.company
            user = request.user
            return user == company.owner or user in company.admins.all()
        return False
