from celery import shared_task
from django.utils.timezone import now

from backend.apps.quiz.models import Quiz, Result
from backend.apps.shared.utils import send_email_quiz_notification
from backend.apps.users.models import CustomUser


@shared_task
def notify_users():
    users = CustomUser.objects.all()

    for user in users:
        for quiz in Quiz.objects.filter(company__members=user):
            last_attempt = Result.objects.filter(user=user, quiz=quiz).order_by("-updated_at").first()

            if last_attempt and last_attempt.status == Result.QuizStatus.COMPLETED:
                time_since_last_attempt = (now() - last_attempt.updated_at).days
            else:
                time_since_last_attempt = float("inf")

            if time_since_last_attempt > quiz.frequency:
                send_email_quiz_notification(user, quiz)
