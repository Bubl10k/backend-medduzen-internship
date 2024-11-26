from django.db import models

from backend.apps.company.models import Company
from backend.apps.shared.models import TimeStamp
from backend.apps.users.models import CustomUser


# Create your models here.
class Quiz(TimeStamp):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    frequency = models.PositiveIntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="quizzes")

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField()

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        unique_together = ("question", "text")

    def __str__(self):
        return self.text


class Result(TimeStamp):
    class QuizStatus(models.TextChoices):
        STARTED = "Started"
        COMPLETED = "Completed"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="results")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="results")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    score = models.PositiveIntegerField(default=0)
    total_question = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=QuizStatus.choices, default=QuizStatus.STARTED)

    class Meta:
        verbose_name = "Test Result"
        verbose_name_plural = "Test Results"
