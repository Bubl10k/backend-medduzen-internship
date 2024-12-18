from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework import viewsets

from backend.apps.users.models import CustomUser
from backend.apps.users.pagination import CustomUserPagination
from backend.apps.users.serializers import UserListSerializer, UserSerializer


class CustomUserViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    pagination_class = CustomUserPagination

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserSerializer


class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.GITHUB_CALLBACK_URL
    client_class = OAuth2Client
