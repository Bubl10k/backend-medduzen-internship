from django.contrib import admin

from backend.apps.quiz.models import Answer, Question, Quiz


# Register your models here.
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "frequency"]
    search_fields = ["title", "company__name"]
    list_filter = [
        "company",
    ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "quiz"]
    search_fields = ["text", "quiz__title"]
    list_filter = [
        "quiz",
    ]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["text", "question", "is_correct"]
    search_fields = ["text", "question__text"]
    list_filter = [
        "question",
    ]
