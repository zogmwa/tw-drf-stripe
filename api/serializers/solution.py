from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.serializers.organization import OrganizationSerializer
from api.serializers.solution_price import SolutionPriceSerializer
from api.serializers.tag import TagSerializer


class SolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    prices = SolutionPriceSerializer(required=False, many=True)
    tags = TagSerializer(read_only=True, many=True)
    primary_tag = TagSerializer(read_only=True)

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
            'scope_of_work',
            'primary_tag',
            'is_published',
        ]


class SolutionRelatedAssetSerializer(SolutionSerializer):
    """
    Serializer for related products of solution
    """

    related_assets = serializers.SerializerMethodField(
        method_name='_get_related_assets'
    )

    class Meta(SolutionSerializer.Meta):
        fields = SolutionSerializer.Meta.fields + ['related_assets']

    def _get_related_assets(self, instance):
        solution = Solution.objects.get(pk=instance.pk)
        query_assets = solution.assets.all()
        assets = []
        for query_asset in query_assets:
            assets.append(
                {
                    'slug': query_asset.slug,
                    'name': query_asset.name,
                    'logo_url': query_asset.logo_url,
                    'website': query_asset.website,
                }
            )

        return assets
