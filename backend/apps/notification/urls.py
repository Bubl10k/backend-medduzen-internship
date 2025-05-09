from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("notifications", views.NotificationReadOnlyViewSet, basename="notification-management")

urlpatterns = [] + router.urls
