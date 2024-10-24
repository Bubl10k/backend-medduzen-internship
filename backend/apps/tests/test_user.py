from django.shortcuts import get_object_or_404
from rest_framework import status

from backend.apps.tests.test_setup import TestCustomUserSetup
from backend.apps.users.models import CustomUser
from backend.apps.users.serializers import UserListSerializer, UserSerializer


class TestCustomUser(TestCustomUserSetup):
    def test_get_users(self):
        response = self.client.get('/api_users/users/')
        serializer_data = UserListSerializer(
            CustomUser.objects.all(), many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data['results'])
    
    def test_get_user_by_id(self):
        response = self.client.get('/api_users/users/2/')
        user = get_object_or_404(CustomUser, id=2)
        serializer_data = UserSerializer(user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
        
    def test_update_user(self):
        response = self.client.patch('/api_users/users/4/', {'username': 'testuser2'})
        user = get_object_or_404(CustomUser, id=4)
        serializer_data = UserSerializer(user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)
        
    def test_delete_user(self):
        response = self.client.delete('/api_users/users/-1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        