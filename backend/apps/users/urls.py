from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('users', views.CustomUserViewset)

urlpatterns = [
    path('auth/', views.auth),
] + router.urls
