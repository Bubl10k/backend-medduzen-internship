from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz-management")

urlpatterns = [] + router.urls