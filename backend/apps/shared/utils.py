from rest_framework import status
from rest_framework.response import Response


def update_instance_status(self, instance, new_status, additional_action=None):
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
