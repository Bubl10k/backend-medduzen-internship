from django.db.models import Sum
from django.db.models.query import QuerySet

from backend.apps.quiz.models import Result
from backend.apps.quiz.schemas import QuizResult


def calculate_quiz_result(queryset: QuerySet[Result]) -> dict[str, float]:
    aggregated_data = queryset.aggregate(total_correct=Sum("score"), total_questions=Sum("total_question"))

    total_correct = aggregated_data.get("total_correct") or 0
    total_question = aggregated_data.get("total_questions") or 0

    if total_question > 0:
        average_percentage = total_correct / total_question
        average_score = round(average_percentage * 10, 2)
    else:
        average_percentage = 0
        average_score = 0

    result = QuizResult(
        average_score=average_score,
        percentage=average_percentage,
        total_correct=total_correct,
        total_questions=total_question,
    )

    return result.model_dump()
