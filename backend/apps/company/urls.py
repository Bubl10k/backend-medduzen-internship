from rest_framework.routers import DefaultRouter

from backend.apps.company import views

router = DefaultRouter()
router.register("companies", views.CompanyCreateDeleteUpdateViewset, basename="company-management")

urlpatterns = [] + router.urls
