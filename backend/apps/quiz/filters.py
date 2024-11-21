from django_filters import rest_framework as filters

from backend.apps.quiz.models import Quiz


class QuizFilter(filters.FilterSet):
    company = filters.NumberFilter(
        field_name="company__id", lookup_expr="exact", help_text="Filter requests by company ID."
    )

    class Meta:
        model = Quiz
        fields = [
            "company",
        ]
