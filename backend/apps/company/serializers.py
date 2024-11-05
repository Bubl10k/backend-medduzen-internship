from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from backend.apps.company.models import Company


class CompanySerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Company
        fields = ["id", "name", "owner", "members", "description", "visible"]

    def validate(self, attrs):
        if Company.objects.filter(name=attrs.get("name")).exists():
            raise serializers.ValidationError(_("Company with this name already exists"))
        return attrs


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "owner", "members", "description"]
