from django.shortcuts import get_object_or_404
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from backend.apps.company.models import Company, CompanyInvitation
from backend.apps.users.models import CustomUser, UserRequest
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
        response = self.client.get("/api/users/users/")
        serializer_data = UserListSerializer(CustomUser.objects.all(), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data["results"])

    def test_get_user_by_id(self):
        response = self.client.get("/api/users/users/3/")
        user = get_object_or_404(CustomUser, id=3)
        serializer_data = UserSerializer(user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_update_user(self):
        response = self.client.patch("/api/users/users/6/", {"username": "testuser2"})
        user = get_object_or_404(CustomUser, id=6)
        serializer_data = UserSerializer(user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_create_user_without_email(self):
        context = {"username": "testuser2", "password": "testpassword", "password2": "testpassword"}
        response = self.client.post("/api/users/users/", context)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_repeatable_email_user2(self):
        context = {"username": "testuser2", "password": "testpassword", "email": "testuser@example.com"}
        response = self.client.post("/api/users/users/", context)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user(self):
        response = self.client.delete("/api/users/users/5/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUserSerializer(TestCustomUserSetup):
    def test_user_serializer(self):
        data = UserSerializer(self.user).data

        expected_data = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "image_path": None,
            "created_at": data.get("created_at"),
        }

        self.assertEqual(data["id"], expected_data["id"])
        self.assertEqual(data["username"], expected_data["username"])
        self.assertEqual(data["first_name"], expected_data["first_name"])
        self.assertEqual(data["last_name"], expected_data["last_name"])
        self.assertEqual(data["email"], expected_data["email"])
        self.assertEqual(data["image_path"], expected_data["image_path"])

        if "created_at" in data:
            self.assertIsNotNone(data["created_at"])


class TestUserListSerializerTest(TestCustomUserSetup):
    def test_user_list_serializer(self):
        user_2 = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        data = UserListSerializer([self.user, user_2], many=True).data
        expected_data = [
            {
                "id": self.user.id,
                "username": self.user.username,
                "image_path": None,
                "email": self.user.email,
            },
            {"id": user_2.id, "username": user_2.username, "image_path": user_2.image_path, "email": user_2.email},
        ]
        self.assertEqual(data, expected_data)


class TestUserInvitation(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        self.company = Company.objects.create(name="Test Company", owner=self.owner)
        self.invitation = CompanyInvitation.objects.create(company=self.company, receiver=self.user, sender=self.owner)
        self.company.members.add(self.owner)

    def test_list_invitations(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/invitations/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["receiver"], self.user.id)

    def test_accept_invitation(self):
        self.client.force_authenticate(user=self.user)

        self.assertFalse(self.company.members.all().filter(id=self.user.id).exists())
        response = self.client.patch(f"/api/users/invitations/{self.invitation.id}/accept/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CompanyInvitation.StatusChoices.ACCEPTED)
        self.assertEqual(response.data["status"], "A")
        self.assertTrue(self.company.members.all().filter(id=self.user.id).exists())

    def test_decline_invitation(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f"/api/users/invitations/{self.invitation.id}/decline/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, CompanyInvitation.StatusChoices.DECLINED)
        self.assertEqual(response.data["status"], "D")


class TestUserRequest(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        self.company = Company.objects.create(name="Test Company", owner=self.owner)
        self.company.members.add(self.owner)

    def test_create_request(self):
        self.client.force_authenticate(user=self.user)
        request_data = {"company": self.company.id, "sender": self.user.id}
        response = self.client.post("/api/users/requests/", data=request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], UserRequest.StatusChoices.PENDING)

    def test_list_requests(self):
        request = UserRequest.objects.create(company=self.company, sender=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/requests/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sender"], self.user.id)

    def test_cancel_request(self):
        request = UserRequest.objects.create(company=self.company, sender=self.user)
        self.company.members.add(self.owner)
        self.client.force_authenticate(user=self.user)
        request.status = UserRequest.StatusChoices.PENDING
        request.save()
        response = self.client.patch(f"/api/users/requests/{request.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], UserRequest.StatusChoices.CANCELED)
