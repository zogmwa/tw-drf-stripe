from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models.registered_webhook import RegisteredWebhook
from api.serializers.organization import OrganizationSerializer


class RegisteredWebhookSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = RegisteredWebhook
        fields = [
            'event_name',
            'organization',
            'receiver_url',
        ]
