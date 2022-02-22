from rest_framework import viewsets, permissions
from rest_framework.response import Response

from api.models.registered_webhook import RegisteredWebhook
from api.serializers.registered_webhook import RegisteredWebhookSerializer


class RegisteredWebhookViewSet(viewsets.ModelViewSet):
    queryset = RegisteredWebhook.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = RegisteredWebhookSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        event_name = self.request.data.get('event_name')
        receiver_url = self.request.data.get('receiver_url')
        registered_webhook, created = RegisteredWebhook.objects.get_or_create(
            organization=user.organization,
            event_name=event_name,
            receiver_url=receiver_url,
        )
        registered_webhook_serializer = RegisteredWebhookSerializer(registered_webhook)
        return Response(registered_webhook_serializer.data)
