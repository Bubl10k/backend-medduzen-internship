from django.shortcuts import get_object_or_404
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from backend.apps.users.models import CustomUser
from backend.apps.users.serializers import UserListSerializer, UserSerializer


# Create your tests here.
class TestCustomUserSetup(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )


class TestCustomUser(TestCustomUserSetup):
    def test_get_users(self):
        response = self.client.get("/api_users/users/")
        serializer_data = UserListSerializer(CustomUser.objects.all(), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data["results"])

    def test_get_user_by_id(self):
        response = self.client.get("/api_users/users/3/")
        user = get_object_or_404(CustomUser, id=3)
        serializer_data = UserSerializer(user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_update_user(self):
        response = self.client.patch("/api_users/users/6/", {"username": "testuser2"})
        user = get_object_or_404(CustomUser, id=6)
        serializer_data = UserSerializer(user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_create_user_without_email(self):
        context = {"username": "testuser2", "password": "testpassword", "password2": "testpassword"}
        response = self.client.post("/api_users/users/", context)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_repeatable_email_user2(self):
        context = {"username": "testuser2", "password": "testpassword", "email": "testuser@example.com"}
        response = self.client.post("/api_users/users/", context)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user(self):
        response = self.client.delete("/api_users/users/5/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserSerializerTest(TestCustomUserSetup):
    def test_user_serializer(self):
        data = UserSerializer(self.user).data
        excepted_data = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "image_path": self.user.image_path,
        }
        self.assertEqual(data, excepted_data)


class UserListSerializerTest(TestCustomUserSetup):
    def test_user_list_serializer(self):
        user_2 = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        data = UserListSerializer([self.user, user_2], many=True).data
        expected_data = [
            {"id": self.user.id, "username": self.user.username, "image_path": self.user.image_path},
            {"id": user_2.id, "username": user_2.username, "image_path": user_2.image_path},
        ]
        self.assertEqual(data, expected_data)
