from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.company.serializers import CompanyInvitationSerializer
from backend.apps.shared.utils import update_instance_status
from backend.apps.users.models import CustomUser, UserRequest
from backend.apps.users.pagination import CustomUserPagination
from backend.apps.users.permissions import IsRequestOwner
from backend.apps.users.serializers import UserListSerializer, UserRequestSerializer, UserSerializer


# Create your views here.
class CustomUserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    pagination_class = CustomUserPagination

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer


class UserInvitationViewset(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CompanyInvitationSerializer
    queryset = CompanyInvitation.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(receiver=self.request.user)

    @action(detail=True, methods=["patch"], url_path="accept")
    def accept(self, request, pk=None):
        invitation = self.get_object()

        def add_user_to_company():
            company = invitation.company
            company.members.add(invitation.receiver)
            company.save()

        return update_instance_status(
            self, invitation, CompanyInvitation.StatusChoices.ACCEPTED, additional_action=add_user_to_company
        )

    @action(detail=True, methods=["patch"], url_path="decline")
    def decline(self, request, pk=None):
        invitation = self.get_object()
        return update_instance_status(self, invitation, CompanyInvitation.StatusChoices.DECLINED)


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

        if company.members.all().filter(id=sender.id).exists():
            raise serializers.ValidationError({"detail": "User is already a member of the company"})

        serializer.save(sender=sender, company=company)

    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        request = self.get_object()
        return update_instance_status(self, request, UserRequest.StatusChoices.CANCELED)
