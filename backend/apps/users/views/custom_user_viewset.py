import requests
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

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


class GitHubAuthTokenView(APIView):
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://github.com/login/oauth/access_token"
        payload = {
            "client_id": settings.SOCIALACCOUNT_PROVIDERS["github"]["APP"]["client_id"],
            "client_secret": settings.SOCIALACCOUNT_PROVIDERS["github"]["APP"]["secret"],
            "code": code,
        }
        headers = {"Accept": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response_data = response.json()
            access_token = response_data.get("access_token")
            refresh_token = response_data.get("refresh_token")
            return Response({"access_token": access_token, "refresh_token": refresh_token}, status=status.HTTP_200_OK)

        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
