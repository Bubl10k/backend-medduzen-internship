from rest_framework import serializers

from backend.apps.company.models import Company, CompanyInvitation


class CompanySerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    admins = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Company
        fields = "__all__"

    def create(self, validated_data):
        owner = validated_data.pop("owner")
        company = Company.objects.create(owner=owner, **validated_data)
        company.members.add(owner)
        return company


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class CompanyInvitationSerializer(serializers.ModelSerializer):   
    class Meta:
        model = CompanyInvitation
        fields = ["id", "company", "receiver", "sender", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "company", "receiver", "sender", "created_at", "updated_at"]
