from django.core import serializers
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.apps.company.models import Company
from backend.apps.company.pagination import CompanyPagination
from backend.apps.company.permissions import IsOwner
from backend.apps.company.serializers import CompanyListSerializer, CompanySerializer
from backend.apps.users.models import CustomUser
from backend.apps.users.serializers import UserListSerializer


class CompanyViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    pagination_class = CompanyPagination

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CompanyListSerializer
        return CompanySerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwner(), IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=["patch"], permission_classes=[IsOwner])
    def toggle_visibility(self, request, pk=None):
        company = self.get_object()
        company.visible = not company.visible
        company.save()
        return Response({"visible": company.visible}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsOwner])
    def remove_member(self, request, pk=None):
        member_id = request.data.get("member")
        company = self.get_object()

        if not member_id:
            raise serializers.ValidationError({"detail": _("Member is required.")})

        member = get_object_or_404(CustomUser, id=member_id)
        if not company.members.filter(id=member_id).exists():
            raise serializers.ValidationError({"detail": _("User is not a member of the company")})

        company.members.remove(member)
        return Response({"detail": _("Member removed successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def leave_company(self, request, pk=None):
        company = self.get_object()
        user = request.user

        if not company.members.filter(id=user.id).exists():
            raise serializers.ValidationError({"detail": _("User is not a member of the company")})

        company.members.remove(user)
        return Response({"detail": _("Successfully left the company.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def list_members(self, request, pk=None):
        company = self.get_object()
        members = company.members.all()
        serializer = UserListSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
