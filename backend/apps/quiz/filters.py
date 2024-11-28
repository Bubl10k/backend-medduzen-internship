from django_filters import rest_framework as filters

from backend.apps.quiz.models import Quiz, Result


class QuizFilter(filters.FilterSet):
    company = filters.NumberFilter(
        field_name="company__id", lookup_expr="exact", help_text="Filter requests by company ID."
    )

    class Meta:
        model = Quiz
        fields = [
            "company",
        ]


class ResultFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name="user__id", lookup_expr="exact", help_text="Filter results by user ID.")
    quiz = filters.NumberFilter(field_name="quiz__id", lookup_expr="exact", help_text="Filter results by quiz ID.")

    class Meta:
        model = Result
        fields = [
            "user",
            "quiz",
        ]
