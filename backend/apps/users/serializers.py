from rest_framework import serializers

from backend.apps.users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name", "email", "image_path"]


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "image_path"]

    def to_representation(self, instance):
        if isinstance(instance, (list, serializers.ListSerializer)):
            instance = sorted(instance, key=lambda x: x.created_at)
        else:
            return super().to_representation(instance)
        return [super().to_representation(user) for user in instance]
