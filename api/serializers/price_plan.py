from rest_framework.serializers import ModelSerializer

from api.models import PricePlan


class PricePlanSerializer(ModelSerializer):
    class Meta:
        model = PricePlan
        fields = [
            'asset',
            'name',
            'summary',
            'currency',
            'price',
            'per',
            'features',
            'most_popular',
        ]
