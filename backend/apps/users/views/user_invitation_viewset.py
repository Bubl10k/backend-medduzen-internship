from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.apps.company.models import CompanyInvitation
from backend.apps.company.serializers import CompanyInvitationSerializer
from backend.apps.shared.utils import update_instance_status
from backend.apps.users.filters import UserInvitationFilter


class UserInvitationViewset(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = CompanyInvitationSerializer
    queryset = CompanyInvitation.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserInvitationFilter

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
