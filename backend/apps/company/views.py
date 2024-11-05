from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from backend.apps.company.models import Company
from backend.apps.company.permissions import IsOwner
from backend.apps.company.serializers import CompanyListSerializer, CompanySerializer


# Create your views here.
class CompanyCreateDeleteUpdateViewset(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsOwner, IsAuthenticated]
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    @action(detail=True, methods=["patch"], permission_classes=[IsOwner])
    def toggle_visibility(self, request, pk=None):
        company = self.get_object()
        company.visible = not company.visible
        company.save()
        return Response({"visible": company.visible}, status=HTTP_200_OK)


class CompanyListRetrieveViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return CompanyListSerializer
        return CompanySerializer
