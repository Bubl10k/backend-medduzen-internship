from django_filters import rest_framework as filters

from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.users.models import UserRequest


class CompanyFilter(filters.FilterSet):
    member_id = filters.NumberFilter(field_name="members__id")
    owner_id = filters.NumberFilter(field_name="owner__id")

    class Meta:
        model = Company
        fields = [
            "member_id",
            "owner_id",
        ]


class CompanyInvitationFilter(filters.FilterSet):
    status = filters.ChoiceFilter(
        choices=UserRequest.StatusChoices.choices,
        field_name="status",
        lookup_expr="exact",
    )

    class Meta:
        model = CompanyInvitation
        fields = ["status"]


class CompanyRequestFilter(filters.FilterSet):
    status = filters.ChoiceFilter(
        choices=UserRequest.StatusChoices.choices,
        field_name="status",
        lookup_expr="exact",
    )

    class Meta:
        model = UserRequest
        fields = ["status"]
