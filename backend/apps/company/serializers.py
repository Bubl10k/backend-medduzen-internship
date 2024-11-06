from rest_framework import serializers

from backend.apps.company.models import Company


class CompanySerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Company
        fields = "__all__"


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
