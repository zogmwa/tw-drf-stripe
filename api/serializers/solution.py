from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.models.asset import Asset
from api.serializers.organization import OrganizationSerializer
from api.serializers.solution_price import SolutionPriceSerializer
from api.serializers.tag import TagSerializer
from api.serializers.solution_question import SolutionQuestionSerializer


class AssetSerializerForSolution(ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id',
            'slug',
            'name',
            'logo_url',
            'logo',
            'website',
        ]


class SolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    prices = SolutionPriceSerializer(required=False, many=True)
    tags = TagSerializer(read_only=True, many=True)
    primary_tag = TagSerializer(read_only=True)
    assets = AssetSerializerForSolution(read_only=True, many=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    questions = SolutionQuestionSerializer(read_only=True, many=True)

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
            'questions',
            'scope_of_work',
            'primary_tag',
            'has_free_trial',
            'upvotes_count',
            'is_published',
        ]
