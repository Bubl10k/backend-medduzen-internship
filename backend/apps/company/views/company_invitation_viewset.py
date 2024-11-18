from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.apps.company.filters import CompanyInvitationFilter
from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.company.permissions import IsInvitationOwner
from backend.apps.company.serializers import CompanyInvitationSerializer
from backend.apps.shared.utils import update_instance_status
from backend.apps.users.models import CustomUser


class CompanyInvitationViewset(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CompanyInvitation.objects.all()
    serializer_class = CompanyInvitationSerializer
    permission_classes = [IsAuthenticated, IsInvitationOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyInvitationFilter

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

        if company.members.filter(id=receiver.id).exists():
            raise serializers.ValidationError({"detail": _("User is already a member of the company")})

        serializer.save(sender=sender, company=company, receiver=receiver)

    @action(detail=True, methods=["patch"], url_path="revoke")
    def revoke(self, request, pk=None):
        invitation = self.get_object()
        return update_instance_status(self, invitation, CompanyInvitation.StatusChoices.REVOKED)
