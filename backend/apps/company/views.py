from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.company.pagination import CompanyPagination
from backend.apps.company.permissions import IsOwner
from backend.apps.company.serializers import CompanyInvitationSerializer, CompanyListSerializer, CompanySerializer
from backend.apps.shared.utils import update_instance_status
from backend.apps.users.models import CustomUser, UserRequest
from backend.apps.users.serializers import UserListSerializer, UserRequestSerializer


# Create your views here.
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


class CompanyInvitationViewset(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CompanyInvitation.objects.all()
    serializer_class = CompanyInvitationSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return CompanyInvitation.objects.filter(sender=self.request.user)

    def perform_create(self, serializer):
        sender = self.request.user
        company_id = self.request.data.get("company")
        receiver_id = self.request.data.get("receiver")

        if not company_id or not receiver_id:
            raise serializers.ValidationError({"detail": _("Company and receiver are required.")})

        company = get_object_or_404(Company, id=company_id)
        receiver = get_object_or_404(CustomUser, id=receiver_id)

        if company.members.all().filter(id=receiver.id).exists():
            raise serializers.ValidationError({"detail": _("User is already a member of the company")})

        serializer.save(sender=sender, company=company, receiver=receiver)

    @action(detail=True, methods=["patch"], url_path="revoke")
    def revoke(self, request, pk=None):
        invitation = self.get_object()
        return update_instance_status(self, invitation, CompanyInvitation.StatusChoices.REVOKED)


class CompanyRequestViewset(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = UserRequest.objects.all()
    serializer_class = UserRequestSerializer

    def get_queryset(self):
        company_ids = Company.objects.filter(owner=self.request.user).values_list("id", flat=True)
        return UserRequest.objects.filter(company_id__in=company_ids)

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        user_request = self.get_object()

        def add_user_to_company():
            company = user_request.company
            company.members.add(user_request.sender)
            company.save()

        return update_instance_status(self, user_request, UserRequest.StatusChoices.APPROVED, add_user_to_company)

    @action(detail=True, methods=["patch"], url_path="reject")
    def reject(self, request, pk=None):
        request = self.get_object()

        return update_instance_status(self, request, UserRequest.StatusChoices.REJECTED)
