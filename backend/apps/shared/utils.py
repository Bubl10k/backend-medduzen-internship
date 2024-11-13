from collections.abc import Callable

from django.db.models import Model
from rest_framework import status
from rest_framework.response import Response


def update_instance_status(
    self, instance: Model, new_status: str, additional_action: Callable[[], None] | None = None
) -> Response:
    """
    Function to update the status of the model instance and perform any additional actions
    """
    data = {"status": instance.status}
    serializer = self.get_serializer(instance, data=data, partial=True)

    if serializer.is_valid():
        data["status"] = new_status
        serializer.update(instance, data)

        if additional_action:
            additional_action()

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
