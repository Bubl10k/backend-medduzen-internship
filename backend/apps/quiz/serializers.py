from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from backend.apps.quiz.models import Answer, Question, Quiz, Result


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ["id", "text", "answers"]

    def create(self, validated_data):
        answers = validated_data.pop("answers", [])
        question = Question.objects.create(**validated_data)
        answers_to_create = [Answer(question=question, **answer) for answer in answers]
        Answer.objects.bulk_create(answers_to_create)

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
        fields = ["id", "title", "description", "questions", "frequency", "company", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is None:
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

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.frequency = validated_data.get("frequency", instance.frequency)
        instance.company = validated_data.get("company", instance.company)
        instance.description = validated_data.get("description", instance.description)

        questions_data = validated_data.pop("questions", [])
        existing_questions = {question.id: question for question in instance.questions.all()}

        for question_data in questions_data:
            question_id = question_data.get("id")
            answers_data = question_data.pop("answers", [])

            if question_id and question_id in existing_questions:
                question_instance = existing_questions.pop(question_id)
                question_instance.text = question_data.get("text", question_instance.text)
                question_instance.save()

                existing_answers = {answer.id: answer for answer in question_instance.answers.all()}
                for answer_data in answers_data:
                    answer_id = answer_data.get("id")
                    if answer_id and answer_id in existing_answers:
                        answer_instance = existing_answers.pop(answer_id)
                        answer_instance.text = answer_data.get("text", answer_instance.text)
                        answer_instance.is_correct = answer_data.get("is_correct", answer_instance.is_correct)
                        answer_instance.save()
                    else:
                        Answer.objects.create(question=question_instance, **answer_data)

                for answer in existing_answers.values():
                    answer.delete()
            else:
                new_question = Question.objects.create(quiz=instance, **question_data)
                Answer.objects.bulk_create(
                    [Answer(question=new_question, **answer_data) for answer_data in answers_data]
                )

        for question in existing_questions.values():
            question.delete()

        instance.save()
        return instance


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ["id", "score", "total_question", "status", "created_at", "updated_at"]


class ResultExportSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    quiz = serializers.SerializerMethodField()
    date_passed = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ["id", "user", "company", "quiz", "score", "date_passed"]

    def get_date_passed(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_user(self, obj):
        return obj.user.username

    def get_company(self, obj):
        return obj.company.name

    def get_quiz(self, obj):
        return obj.quiz.title


class QuizResultSerializer(serializers.Serializer):
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_correct = serializers.IntegerField()
    total_questions = serializers.IntegerField()

    def to_representation(self, instance):
        return {
            "average_score": instance["average_score"],
            "percentage": instance["percentage"],
            "total_correct": instance["total_correct"],
            "total_question": instance["total_questions"],
        }


class QuizAverageScoreSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    title = serializers.CharField()
    average_score = serializers.FloatField()
    timestamp = serializers.DateTimeField()
