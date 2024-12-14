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
        questions_data = validated_data.pop("questions", [])
        existing_questions = {q.id: q for q in instance.questions.all().prefetch_related("answers")}
        existing_question_ids = set(existing_questions.keys())

        updated_question_ids = set()
        questions_to_create = []
        for question_data in questions_data:
            question_id = question_data.get("id")

            # update questions
            if question_id and question_id in existing_questions:
                question_instance = existing_questions[question_id]
                updated_question_ids.add(question_id)

                question_serializer = QuestionSerializer(question_instance, data=question_data)
                question_serializer.is_valid(raise_exception=True)
                question_serializer.save()
            # create new question
            else:
                questions_to_create.append(question_data)

        # bulk create new questions
        if questions_to_create:
            questions_serializer = QuestionSerializer(data=questions_to_create, many=True)
            questions_serializer.is_valid(raise_exception=True)
            questions_serializer.save(quiz=instance)

        question_ids_to_delete = existing_question_ids - updated_question_ids
        if question_ids_to_delete:
            instance.questions.filter(id__in=question_ids_to_delete).delete()

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
