from rest_framework.serializers import ModelSerializer

from api.models import AssetPricePlan


class PricePlanSerializer(ModelSerializer):
    class Meta:
        model = AssetPricePlan
        fields = [
            'id',
            'asset',
            'name',
            'summary',
            'currency',
            'price',
            'per',
            'features',
            'most_popular',
        ]
