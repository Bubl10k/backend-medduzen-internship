from django.db.models import Sum

from backend.apps.quiz.models import Result


def calculate_quiz_result(queryset: list[Result]) -> dict[str, float]:
    aggregated_data = queryset.aggregate(total_correct=Sum("score"), total_questions=Sum("total_question"))

    total_correct = aggregated_data.get("total_correct") or 0
    total_questions = aggregated_data.get("total_questions") or 0

    if total_questions > 0:
        average_percentage = total_correct / total_questions
        average_points = round(average_percentage * 10, 2)
    else:
        average_percentage = 0
        average_points = 0

    return {
        "average_score": average_points,
        "percentage": average_percentage,
        "total_correct": total_correct,
        "total_questions": total_questions,
    }
