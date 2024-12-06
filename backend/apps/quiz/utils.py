import csv
import json

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpResponse

from backend.apps.quiz.models import Result
from backend.apps.quiz.schemas import QuizResult
from backend.apps.quiz.serializers import ResultExportSerializer


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


def export_csv(results: QuerySet[Result]) -> HttpResponse:
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="quiz_results.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["id", "user", "company", "quiz", "score", "date passed"])

    serializer = ResultExportSerializer(results, many=True)

    for result in serializer.data:
        writer.writerow(
            [result["id"], result["user"], result["company"], result["quiz"], result["score"], result["date_passed"]]
        )

    return response


def export_json(results: QuerySet[Result]) -> HttpResponse:
    serializer = ResultExportSerializer(results, many=True)

    json_data = json.dumps(serializer.data, indent=4)

    response = HttpResponse(
        json_data,
        content_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="quiz_results.json"'},
    )
    return response


def calculate_average_quiz_scores(results: QuerySet[Result]) -> list[dict[str, str | float]]:
    average_scores = []

    for result in results:
        correct_answers = result.score
        total_questions = result.total_question

        if total_questions > 0:
            average_score = round((correct_answers / total_questions) * 10, 2)
        else:
            average_score = 0.0

        average_scores.append(
            {
                "quiz_id": result.quiz.id,
                "title": result.quiz.title,
                "average_score": average_score,
                "timestamp": result.updated_at,
            }
        )

    return average_scores
