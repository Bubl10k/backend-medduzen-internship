from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response

from backend.apps.quiz.filters import QuizFilter
from backend.apps.quiz.models import Quiz
from backend.apps.quiz.permissions import IsOwnerOrAdmin
from backend.apps.quiz.serializers import QuestionSerializer, QuizSerializer


# Create your views here.
class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = QuizFilter
    
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=True, methods=["patch"], url_path="remove_question", permission_classes=[IsOwnerOrAdmin])
    def remove_question(self, request, pk=None):
        quiz = self.get_object()
        question = request.data.get("question")
        
        if not question:
            raise serializers.ValidationError({"detail": _("Question is required.")})
        
        quiz.questions.remove(question)
        return Response({"detail": _("Question removed successfully.")}, status=status.HTTP_200_OK)
        