from django.test import TestCase
from rest_framework.test import APIClient

from backend.apps.users.models import CustomUser


class TestCustomUserSetup(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
