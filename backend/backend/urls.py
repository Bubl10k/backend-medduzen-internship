"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/healthcheck/", include("backend.apps.healthcheck.urls")),
    path("api/users/", include("backend.apps.users.urls")),
    path("api/companies/", include("backend.apps.company.urls")),
    path("api/quiz/", include("backend.apps.quiz.urls")),
    path("api/notification/", include("backend.apps.notification.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/social/", include("allauth.urls")),
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
