from rest_framework.routers import DefaultRouter

from backend.apps.company import views

router = DefaultRouter()
router.register("companies", views.company_viewset.CompanyViewset, basename="company-management")
router.register(
    "invitations", views.company_invitation_viewset.CompanyInvitationViewset, basename="company-owner-invitations"
)
router.register("requests", views.company_request_viewset.CompanyRequestViewset, basename="company-member-requests")

urlpatterns = [] + router.urls
