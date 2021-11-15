from rest_framework.serializers import ModelSerializer

from api.models.solution_price import SolutionPrice


class SolutionPriceSerializer(ModelSerializer):
    class Meta:
        model = SolutionPrice
        fields = [
            'id',
            'solution',
            'stripe_price_id',
            'price',
            'currency',
            'is_primary',
        ]
        read_only_fields = [
            'id',
            'solution',
            'stripe_price_id',
            'price',
            'currency',
            'is_primary',
        ]
