from channels.consumer import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.apps.notification.models import Notification
from backend.apps.quiz.models import Quiz


@receiver(post_save, sender=Quiz)
def send_notification(sender, instance, created, **kwargs):
    if created:
        company_members = instance.company.members.all()
        for user in company_members:
            notification = Notification.objects.create(
                user=user,
                text=f"New quiz '{instance.title}' is available. Take the quiz now!",
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user.id}",
                {
                    "type": "send_notification",
                    "notification": notification.text,
                },
            )
