from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from backend.apps.quiz.models import Answer, Question, Quiz


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "answers"]

    def create(self, validated_data):
        answers = validated_data.pop("answers", [])
        question = Question.objects.create(**validated_data)
        for answer in answers:
            Answer.objects.create(question=question, **answer)
        return question

    def validate(self, attrs):
        answers = attrs.get("answers", [])

        if len(answers) < 2:
            raise serializers.ValidationError({"answers": _("Each question must have at least two answers.")})

        correct_answers = [answer for answer in answers if answer.get("is_correct", False)]
        if len(correct_answers) != 1:
            raise serializers.ValidationError({"answers": _("Each question must have one correct answer.")})

        return attrs


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions", "frequency", "company", "created_at", "updated_at"]

    def validate(self, attrs):
        questions = attrs.get("questions", [])

        if len(questions) < 2:
            raise serializers.ValidationError({"questions": _("Each quiz must have at least two questions.")})
        return attrs

    def create(self, validated_data):
        questions = validated_data.pop("questions", [])
        quiz = Quiz.objects.create(**validated_data)
        questions_serializer = QuestionSerializer(data=questions, many=True)

        questions_serializer.is_valid(raise_exception=True)
        questions_serializer.save(quiz=quiz)

        return quiz
