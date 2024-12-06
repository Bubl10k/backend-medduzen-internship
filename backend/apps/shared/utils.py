from collections.abc import Callable

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Model
from rest_framework import status
from rest_framework.response import Response

from backend.apps.quiz.models import Quiz
from backend.apps.users.models import CustomUser


def update_instance_status(
    self, instance: Model, new_status: str, additional_action: Callable[[], None] | None = None
) -> Response:
    """
    Function to update the status of the model instance and perform any additional actions
    """
    data = {"status": instance.status}
    serializer = self.get_serializer(instance, data=data, partial=True)

    if serializer.is_valid():
        data["status"] = new_status
        serializer.update(instance, data)

        if additional_action:
            additional_action()

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_email_quiz_notification(user: CustomUser, quiz: Quiz) -> None:
    """
    Function to send email notification to a user about a quiz.
    """
    subject = "It's time to take another quiz!"
    message = (
        f"Hi {user.first_name},\n\n"
        f"You haven't attempted the quiz '{quiz.title}' in a while. "
        f"Don't miss the opportunity to test your knowledge and improve your skills!\n\n"
        f"Best regards,\nYour TestHub Team"
    )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(subject, message, email_from, recipient_list)
