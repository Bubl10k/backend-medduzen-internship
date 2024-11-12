from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("users", views.CustomUserViewset, basename="user-management")
router.register("invitations", views.UserInvitationViewset, basename="user-invitations")
router.register("requests", views.UserRequestViewset, basename="user-requests")

urlpatterns = [] + router.urls
