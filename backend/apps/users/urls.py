from django.urls import path
from rest_framework.routers import DefaultRouter

from backend.apps.users import views

router = DefaultRouter()
router.register("users", views.custom_user_viewset.CustomUserViewset, basename="user-management")
router.register("invitations", views.user_invitation_viewset.UserInvitationViewset, basename="user-invitations")
router.register("requests", views.user_request_viewset.UserRequestViewset, basename="user-requests")

urlpatterns = [path("github/", views.custom_user_viewset.GitHubLogin.as_view(), name="github_login")] + router.urls
