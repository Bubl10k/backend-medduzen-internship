from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.apps.company.filters import CompanyFilter
from backend.apps.company.models import Company
from backend.apps.company.pagination import CompanyPagination
from backend.apps.company.permissions import IsAdmin, IsOwner
from backend.apps.company.serializers import (
    CompanyListSerializer,
    CompanySerializer,
    QuizLastCompletionSerializer,
    UserLastCompletionSerializer,
)
from backend.apps.quiz.models import Quiz, Result
from backend.apps.users.models import CustomUser
from backend.apps.users.serializers import UserListSerializer


class CompanyViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    pagination_class = CompanyPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CompanyListSerializer
        return CompanySerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsOwner(), IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=["patch"], permission_classes=[IsOwner])
    def toggle_visibility(self, request, pk=None):
        company = self.get_object()
        company.visible = not company.visible
        company.save()
        return Response({"visible": company.visible}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsOwner], url_path="remove-member")
    def remove_member(self, request, pk=None):
        member_id = request.data.get("member")
        company = self.get_object()

        if not member_id:
            raise serializers.ValidationError({"detail": _("Member is required.")})

        member = get_object_or_404(CustomUser, id=member_id)
        if not company.members.filter(id=member_id).exists():
            raise serializers.ValidationError({"detail": _("User is not a member of the company")})

        company.members.remove(member)
        return Response({"detail": _("Member removed successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated], url_path="leave")
    def leave_company(self, request, pk=None):
        company = self.get_object()
        user = request.user

        if not company.members.filter(id=user.id).exists():
            raise serializers.ValidationError({"detail": _("User is not a member of the company")})

        company.members.remove(user)
        return Response({"detail": _("Successfully left the company.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def list_members(self, request, pk=None):
        company = self.get_object()
        members = company.members.all()
        serializer = UserListSerializer(members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="appoint-admin", permission_classes=[IsAuthenticated, IsOwner])
    def appoint_admin(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get("user")

        if not user_id:
            raise serializers.ValidationError({"detail": _("User is required to appoint an admin.")})

        user = get_object_or_404(CustomUser, id=user_id)

        if not company.members.filter(id=user_id).exists():
            raise serializers.ValidationError({"detail": _("User is not a member of the company")})

        if company.admins.filter(id=user_id).exists():
            raise serializers.ValidationError({"detail": _("User is already an admin of the company")})

        company.admins.add(user)
        return Response({"detail": _("User appointed as admin successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated, IsOwner], url_path="remove-admin")
    def remove_admin(self, request, pk=None):
        company = self.get_object()
        user_id = request.data.get("user")

        if not user_id:
            raise serializers.ValidationError({"detail": _("User is required to remove an admin.")})

        user = get_object_or_404(CustomUser, id=user_id)

        if not company.admins.filter(id=user_id).exists():
            raise serializers.ValidationError({"detail": _("User is not an admin of the company")})

        company.admins.remove(user)
        return Response({"detail": _("User removed as admin successfully.")}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated], url_path="admins")
    def admin_list(self, request):
        company = self.get_object()
        admins = company.admins.all()
        serializer = UserListSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="last-completions-quizzes", permission_classes=[IsOwner, IsAdmin])
    def last_completions_quizzes(self, request, pk=None):
        company = self.get_object()

        last_completions = (
            Quiz.objects.filter(company=company, results__status=Result.QuizStatus.COMPLETED)
            .annotate(last_completed_at=Max("results__updated_at"))
            .values("id", "title", "last_completed_at")
        )

        if not last_completions.exists():
            return Response({"detail": _("No completions found.")}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizLastCompletionSerializer(last_completions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="last-completions-users", permission_classes=[IsOwner, IsAdmin])
    def last_completions_users(self, request, pk=None):
        company = self.get_object()

        last_completions = (
            CustomUser.objects.filter(results__quiz__company=company, results__status=Result.QuizStatus.COMPLETED)
            .annotate(last_completed_at=Max("results__updated_at"))
            .values("id", "username", "last_completed_at")
        )

        if not last_completions.exists():
            return Response({"detail": _("No completions found.")}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserLastCompletionSerializer(last_completions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
