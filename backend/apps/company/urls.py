from rest_framework.routers import DefaultRouter

from backend.apps.company import views

router = DefaultRouter()
router.register("companies", views.CompanyViewset, basename="company-management")
router.register("invitations", views.CompanyInvitationViewset, basename="company-owner-invitations")
router.register("requests", views.CompanyRequestViewset, basename="company-member-requests")

urlpatterns = [] + router.urls
