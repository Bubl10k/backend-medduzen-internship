from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from backend.apps.users.models import CustomUser, UserRequest


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)
    image_path = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
            "image_path",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        if "password" in attrs and "password2" in attrs:
            if attrs.get("password") != attrs.get("password2"):
                raise serializers.ValidationError(_("Password fields don't match"))
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.image_path = validated_data.get("image_path", instance.image_path)

        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "image_path", "email"]

    def to_representation(self, instance):
        if isinstance(instance, list | serializers.ListSerializer):
            instance = sorted(instance, key=lambda x: x.created_at)
        else:
            return super().to_representation(instance)
        return [super().to_representation(user) for user in instance]


class UserRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = UserRequest

        fields = ["id", "company", "sender", "status", "status_display", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "company", "sender"]

    def validate(self, attrs):
        if not self.instance:
            sender = self.context["request"].user
            company = attrs.get("company")

            if UserRequest.objects.filter(
                sender=sender, company=company, status=UserRequest.StatusChoices.PENDING
            ).exists():
                raise serializers.ValidationError(
                    {"detail": _("A pending request already exists for this sender and company.")}
                )

        return attrs
