import pandas as pd
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action, parser_classes
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.apps.company.models import Company
from backend.apps.quiz.enums import FileFormatEnum
from backend.apps.quiz.filters import QuizFilter, ResultFilter
from backend.apps.quiz.models import Answer, Question, Quiz, Result
from backend.apps.quiz.pagination import QuizPagination
from backend.apps.quiz.permissions import IsCompanyMember, IsOwnerOrAdmin
from backend.apps.quiz.serializers import (
    QuestionSerializer,
    QuizAverageScoreSerializer,
    QuizResultSerializer,
    QuizSerializer,
    ResultSerializer,
)
from backend.apps.quiz.utils import (
    calculate_average_quiz_scores,
    calculate_quiz_result,
    create_or_update_quiz_via_excel,
    export_csv,
    export_json,
)
from backend.apps.users.models import CustomUser


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuizFilter
    pagination_class = QuizPagination

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsOwnerOrAdmin(), IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=["patch"], url_path="add-question", permission_classes=[IsOwnerOrAdmin])
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(quiz=quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="remove-question", permission_classes=[IsOwnerOrAdmin])
    def remove_question(self, request, pk=None):
        quiz = self.get_object()
        question_id = request.data.get("question")

        if not question_id:
            raise serializers.ValidationError({"detail": _("Question is required.")})

        question = get_object_or_404(Question, id=question_id)
        if question.quiz != quiz:
            raise serializers.ValidationError({"detail": _("Question does not belong to this quiz.")})

        question.delete()
        return Response({"detail": _("Question removed successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="start-quiz", permission_classes=[IsCompanyMember])
    def start_quiz(self, request, pk=None):
        quiz = self.get_object()
        user = request.user
        questions_count = quiz.questions.count()

        result, created = Result.objects.get_or_create(
            user=user, company=quiz.company, quiz=quiz, total_question=questions_count
        )

        if not created and result.status == Result.QuizStatus.COMPLETED:
            return Response({"detail": _("You have already completed this quiz.")}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResultSerializer(result, data={"state": Result.QuizStatus.STARTED}, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="complete-quiz", permission_classes=[IsCompanyMember])
    def complete_quiz(self, request, pk=None):
        quiz = self.get_object()
        user = request.user

        try:
            result = Result.objects.get(user=user, quiz=quiz, status=Result.QuizStatus.STARTED)
        except Result.DoesNotExist:
            return Response(
                {"detail": _("Quiz has not been started or already completed.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_answers = request.data.get("answers")
        if not user_answers:
            raise serializers.ValidationError({"detail": _("Answers are required.")})

        score = 0
        for user_answer in user_answers:
            question = get_object_or_404(Question, id=user_answer.get("question"))
            correct_answer = get_object_or_404(Answer, question=question, is_correct=True)
            if correct_answer.id == user_answer.get("answer"):
                score += 1

        result.score = score
        result.total_question = len(user_answers)
        result.status = Result.QuizStatus.COMPLETED
        result.save()

        return Response({"detail": _("Quiz completed successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="results", permission_classes=[IsCompanyMember])
    def get_scores(self, request, pk=None):
        quiz = self.get_object()
        user = request.user

        company = quiz.company

        company_queryset = Result.objects.filter(
            user=user, status=Result.QuizStatus.COMPLETED, quiz__company=company
        ).values("score", "total_question")
        company_results = calculate_quiz_result(company_queryset)

        global_queryset = Result.objects.filter(user=user, status=Result.QuizStatus.COMPLETED).values(
            "score", "total_question"
        )
        global_results = calculate_quiz_result(global_queryset)

        company_results_serialized = QuizResultSerializer(company_results).data
        global_results_serialized = QuizResultSerializer(global_results).data

        data = {
            "company_results": company_results_serialized,
            "global_results": global_results_serialized,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="export-quiz-results", permission_classes=[IsOwnerOrAdmin])
    def export_quiz_results(self, request, pk=None):
        quiz = self.get_object()
        file_format = request.query_params.get("file_format")

        results = Result.objects.filter(quiz=quiz, status=Result.QuizStatus.COMPLETED).select_related("quiz")

        if file_format == FileFormatEnum.CSV.value:
            return export_csv(results)
        elif file_format == FileFormatEnum.JSON.value:
            return export_json(results)

        return Response({"detail": _("Invalid format.")}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="export-user-results", permission_classes=[IsAuthenticated])
    def export_user_results(self, request):
        user = request.user
        file_format = request.query_params.get("file_format")

        results = Result.objects.filter(user=user, status=Result.QuizStatus.COMPLETED).select_related("quiz")

        if file_format == FileFormatEnum.CSV.value:
            return export_csv(results)
        elif file_format == FileFormatEnum.JSON.value:
            return export_json(results)

        return Response({"detail": _("Invalid format.")}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="list-average-scores")
    def list_average_scores(self, request):
        results = Result.objects.filter(status=Result.QuizStatus.COMPLETED).select_related("quiz")
        serializer = QuizAverageScoreSerializer(calculate_average_quiz_scores(results), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="all-users-scores")
    def all_users_average_scores(self, request):
        users_ids = CustomUser.objects.values_list("id", flat=True)
        results = Result.objects.filter(user__in=users_ids, status=Result.QuizStatus.COMPLETED).select_related("quiz")
        serializer = QuizAverageScoreSerializer(calculate_average_quiz_scores(results), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="average-user-scores")
    def average_user_scores(self, request):
        user_id = request.query_params.get("user")

        if not user_id:
            return Response({"detail": _("User ID is required.")}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(CustomUser, id=user_id)
        results = Result.objects.filter(user=user, status=Result.QuizStatus.COMPLETED).select_related("quiz")

        serializer = QuizAverageScoreSerializer(calculate_average_quiz_scores(results), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @parser_classes([MultiPartParser])
    @action(detail=False, methods=["post"], url_path="import-quiz", permission_classes=[IsOwnerOrAdmin])
    def import_quiz(self, request):
        """
        Method to create or update quiz via excel
        """
        company_id = request.query_params.get("company")
        file = request.FILES.get("file")

        try:
            df = pd.read_excel(file)

            required_columns = ["Quiz Title", "Description", "Frequency", "Question Text", "Answer Text", "Is Correct"]

            if not all(col in df.columns for col in required_columns):
                return Response(
                    {"detail": "Excel file must contain the required columns: " + ", ".join(required_columns)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not company_id:
                return Response({"detail": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            company = get_object_or_404(Company, id=company_id)
            grouped = df.groupby("Quiz Title")

            return create_or_update_quiz_via_excel(grouped, company)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Error importing quiz: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class ResultDetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    queryset = Result.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ResultFilter

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return super().get_permissions()
