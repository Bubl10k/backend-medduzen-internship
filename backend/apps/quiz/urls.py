from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz-management")
router.register("results", views.ResultDetailViewSet, basename="result-detail")

urlpatterns = [] + router.urls
