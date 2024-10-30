from rest_framework import viewsets

from backend.apps.users.models import CustomUser
from backend.apps.users.pagination import CustomUserPagination
from backend.apps.users.serializers import UserListSerializer, UserSerializer


# Create your views here.
class CustomUserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    pagination_class = CustomUserPagination

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer
