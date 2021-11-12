from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.serializers.organization import OrganizationSerializer
from api.serializers.solution_price import SolutionPriceSerializer


class SolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    prices = SolutionPriceSerializer(required=False, many=True)

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'stripe_product_id',
            'title',
            'type',
            'prices',
            'description',
            'point_of_contact',
            'organization',
            'is_published',
        ]
