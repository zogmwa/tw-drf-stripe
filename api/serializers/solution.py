from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.serializers.organization import OrganizationSerializer
from api.serializers.solution_price import SolutionPriceSerializer
from api.serializers.tag import TagSerializer
from api.serializers.asset import AssetSerializerForSolution


class SolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    prices = SolutionPriceSerializer(required=False, many=True)
    tags = TagSerializer(read_only=True, many=True)
    primary_tag = TagSerializer(read_only=True)
    assets = AssetSerializerForSolution(read_only=True, many=True)

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
            'tags',
            'assets',
            'scope_of_work',
            'primary_tag',
            'is_published',
        ]
