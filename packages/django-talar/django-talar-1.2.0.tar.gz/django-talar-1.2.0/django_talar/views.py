from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import signals
from .serializers import NotifySerializerV0, NotifySerializerV1


@method_decorator(csrf_exempt, name='dispatch')
class NotifyView(APIView):

    @staticmethod
    def success(message_type, message_data):
        signals.notification_received.send(
            sender=None,
            name=message_type,
            data=message_data
        )
        return Response(message_data)

    def post(self, request, format=None):
        serializer = NotifySerializerV1(data=request.data)
        if serializer.is_valid():
            signals.webhook_message_received.send(
                sender=None,
                type=serializer.data["type"],
                data=serializer.data["data"],
                id=serializer.data["id"],
                created_at=serializer.data["created_at"],
            )
            return Response(serializer.data)

        serializer_v0 = NotifySerializerV0(data=request.data)
        if serializer_v0.is_valid():
            signals.notification_received.send(
                sender=None,
                name=serializer_v0.data["name"],
                data=serializer_v0.data
            )
            return Response(serializer_v0.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
