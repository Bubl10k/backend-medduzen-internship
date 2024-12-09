from celery import shared_task
from django.db.models import Prefetch
from django.utils.timezone import now

from backend.apps.quiz.models import Quiz, Result
from backend.apps.shared.utils import send_email_quiz_notification
from backend.apps.users.models import CustomUser


@shared_task
def notify_users():
    users = CustomUser.objects.all().prefetch_related(
        Prefetch("company__quizzes", queryset=Quiz.objects.all(), to_attr="prefetched_quizzes"),
        Prefetch(
            "results", queryset=Result.objects.filter(status=Result.QuizStatus.COMPLETED), to_attr="prefetched_results"
        ),
    )

    for user in users:
        quizzes = getattr(user.company, "prefetched_quizzes", [])
        user_results = {result.quiz.id: result for result in user.prefetched_results}

        for quiz in quizzes:
            last_attempt = user_results.get(quiz.id)

            if last_attempt and last_attempt.status == Result.QuizStatus.COMPLETED:
                time_since_last_attempt = (now() - last_attempt.updated_at).days
            else:
                time_since_last_attempt = float("inf")

            if time_since_last_attempt >= quiz.frequency:
                send_email_quiz_notification(user, quiz)
