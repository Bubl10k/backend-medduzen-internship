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
    sender = filters.NumberFilter(
        field_name="sender__id",
        lookup_expr="exact",
        help_text="Filter invitations by sender ID."
    )
    receiver = filters.NumberFilter(
        field_name="receiver__id",
        lookup_expr="exact",
        help_text="Filter invitations by receiver ID."
    )
    
    class Meta:
        model = CompanyInvitation
        fields = ["status", "receiver", "sender"]


class CompanyRequestFilter(filters.FilterSet):
    status = filters.ChoiceFilter(
        choices=UserRequest.StatusChoices.choices,
        field_name="status",
        lookup_expr="exact",
    )
    sender = filters.NumberFilter(
        field_name="sender__id",
        lookup_expr="exact",
        help_text="Filter requests by sender ID."
    )
    company = filters.NumberFilter(
        field_name="company__id",
        lookup_expr="exact",
        help_text="Filter requests by company ID."
    )
    
    class Meta:
        model = UserRequest
        fields = ["status", "sender", "company"]
