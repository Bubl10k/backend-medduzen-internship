import csv
import json

from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from backend.apps.company.models import Company
from backend.apps.quiz.models import Quiz, Result
from backend.apps.quiz.schemas import QuizResult
from backend.apps.quiz.serializers import QuizSerializer, ResultExportSerializer


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


def create_or_update_quiz_via_excel(file_data, company: Company) -> Response:
    """
    Function to create or update quiz via an Excel file.
    """
    quiz_dict = {}
    quiz = None

    for quiz_title, quiz_data in file_data:
        quiz = Quiz.objects.filter(title=quiz_title, company=company).first()
        questions_data = []
        for question_text, question_group in quiz_data.groupby("Question Text"):
            answers_data = []
            for _, row in question_group.iterrows():
                answers_data.append({"text": row["Answer Text"], "is_correct": bool(row["Is Correct"])})
            questions_data.append({"text": question_text, "answers": answers_data})

        quiz_dict = {
            "title": quiz_title,
            "description": quiz_data.iloc[0]["Description"],
            "frequency": quiz_data.iloc[0]["Frequency"],
            "company": company.id,
            "questions": questions_data,
        }

        quiz_serializer = QuizSerializer(quiz, data=quiz_dict) if quiz else QuizSerializer(data=quiz_dict)

    quiz_serializer.is_valid(raise_exception=True)
    quiz_serializer.save()

    return Response(quiz_serializer.data, status=status.HTTP_201_CREATED)
