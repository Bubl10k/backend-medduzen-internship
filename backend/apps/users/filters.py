from backend.apps.company.filters import CompanyInvitationFilter, CompanyRequestFilter


class UserRequestFilter(CompanyRequestFilter):
    pass


class UserInvitationFilter(CompanyInvitationFilter):
    pass
