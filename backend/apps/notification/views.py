from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.apps.notification.models import Notification
from backend.apps.notification.serializers import NotificationSerializer
from backend.apps.shared.utils import update_instance_status


class NotificationReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(user=user)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        return update_instance_status(self, notification, Notification.NotificationStatus.READ)
