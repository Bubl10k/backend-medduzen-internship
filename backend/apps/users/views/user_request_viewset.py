from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.apps.company.models import Company
from backend.apps.shared.utils import update_instance_status
from backend.apps.users.models import UserRequest
from backend.apps.users.permissions import IsRequestOwner
from backend.apps.users.serializers import UserRequestSerializer


class UserRequestViewset(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = UserRequestSerializer
    queryset = UserRequest.objects.all()
    permission_classes = [IsAuthenticated, IsRequestOwner]

    def get_queryset(self):
        return self.queryset.filter(sender=self.request.user)

    def perform_create(self, serializer):
        sender = self.request.user
        company_id = self.request.data.get("company")

        if not company_id:
            raise serializers.ValidationError({"detail": "Company are required."})

        company = get_object_or_404(Company, id=company_id)

        if company.members.filter(id=sender.id).exists():
            raise serializers.ValidationError({"detail": "User is already a member of the company"})

        serializer.save(sender=sender, company=company)

    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        request = self.get_object()
        return update_instance_status(self, request, UserRequest.StatusChoices.CANCELED)
