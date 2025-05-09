from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.apps.company.filters import CompanyRequestFilter
from backend.apps.company.models import Company
from backend.apps.company.permissions import IsRequestOwner
from backend.apps.shared.utils import update_instance_status
from backend.apps.users.models import UserRequest
from backend.apps.users.serializers import UserRequestSerializer


class CompanyRequestViewset(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsRequestOwner]
    queryset = UserRequest.objects.all()
    serializer_class = UserRequestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyRequestFilter

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
