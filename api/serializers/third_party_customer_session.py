from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import ThirdPartyCustomer


class ThirdPartyCustomerSessionSerializer(ModelSerializer):
    class Meta:
        model = ThirdPartyCustomer
        fields = [
            'third_party_customer',
            'session_id',
            'expire_date',
            'is_expired',
        ]
