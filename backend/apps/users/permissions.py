from rest_framework import permissions


class IsRequestOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user
