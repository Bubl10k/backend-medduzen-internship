from backend.apps.tests.test_setup import TestCustomUserSetup
from backend.apps.users.models import CustomUser
from backend.apps.users.serializers import UserListSerializer, UserSerializer


class UserSerializerTest(TestCustomUserSetup):
    def test_user_serializer(self):
        data = UserSerializer(self.user).data
        excepted_data = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'image_path': self.user.image_path
        }
        self.assertEqual(data, excepted_data)


class UserListSerializerTest(TestCustomUserSetup):
    def test_user_list_serializer(self):
        user_2 = CustomUser.objects.create_user(
            username='testuser2',
            password='testpassword',
            email='testuser2@example.com'
        )
        data = UserListSerializer([self.user, user_2], many=True).data
        expected_data = [
            {
                'id': self.user.id,
                'username': self.user.username,
                'image_path': self.user.image_path
            },
            {
                'id': user_2.id,
                'username': user_2.username,
                'image_path': user_2.image_path
            }
        ]
        self.assertEqual(data, expected_data)
