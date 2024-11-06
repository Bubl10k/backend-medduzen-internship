from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from backend.apps.company.models import Company
from backend.apps.company.permissions import IsOwner
from backend.apps.company.serializers import CompanyListSerializer, CompanySerializer


# Create your views here.
class CompanyCreateDeleteUpdateViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CompanyListSerializer
        return CompanySerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy", "toggle_visibility"]:
            return [IsOwner(), IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=["patch"], permission_classes=[IsOwner])
    def toggle_visibility(self, request, pk=None):
        company = self.get_object()
        company.visible = not company.visible
        company.save()
        return Response({"visible": company.visible}, status=HTTP_200_OK)
