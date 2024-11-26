from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz-management")

urlpatterns = [
    path("results/<int:pk>/", views.ResultDetailView.as_view(), name="result-detail"),
] + router.urls
