from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.apps.quiz.filters import QuizFilter
from backend.apps.quiz.models import Answer, Question, Quiz, Result
from backend.apps.quiz.pagination import QuizPagination
from backend.apps.quiz.permissions import IsCompanyMember, IsOwnerOrAdmin
from backend.apps.quiz.serializers import QuestionSerializer, QuizSerializer, ResultSerializer
from backend.apps.quiz.utils import calculate_quiz_result


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

    @action(detail=True, methods=["patch"], url_path="add_question", permission_classes=[IsOwnerOrAdmin])
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(quiz=quiz)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="remove_question", permission_classes=[IsOwnerOrAdmin])
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

    @action(detail=True, methods=["post"], url_path="start_quiz", permission_classes=[IsCompanyMember])
    def start_quiz(self, request, pk=None):
        quiz = self.get_object()
        user = request.user
        questions_count = quiz.questions.count()

        result, created = Result.objects.get_or_create(
            user=user, company=quiz.company, quiz=quiz, total_question=questions_count
        )

        if not created:
            return Response({"detail": _("You have already completed this quiz.")}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResultSerializer(result, data={"state": Result.QuizStatus.STARTED}, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="complete_quiz", permission_classes=[IsCompanyMember])
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

        company_queryset = Result.objects.filter(user=user, status=Result.QuizStatus.COMPLETED, quiz__company=company)
        company_results = calculate_quiz_result(company_queryset)

        global_queryset = Result.objects.filter(user=user, status=Result.QuizStatus.COMPLETED)
        global_results = calculate_quiz_result(global_queryset)

        data = {
            "company_results": company_results,
            "global_results": global_results,
        }

        return Response(data, status=status.HTTP_200_OK)


class ResultDetailView(generics.RetrieveAPIView):
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]
    queryset = Result.objects.all()
