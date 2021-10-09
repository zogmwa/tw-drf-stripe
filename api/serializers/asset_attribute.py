from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Attribute, Asset, AssetAttributeVote


class AssetAttributeSerializer(ModelSerializer):
    # Upvotes count for asset in content
    upvotes_count = serializers.SerializerMethodField(
        method_name='get_upvote_counts_for_asset_in_request'
    )

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'is_con', 'upvotes_count']

    def get_upvote_counts_for_asset_in_request(self, instance):
        request = self.context.get('request')
        asset_slug = request.query_params.get('asset', '')
        asset_slug = asset_slug.strip()

        if asset_slug:
            asset = Asset.objects.get(slug=asset_slug)
            upvote_count_for_given_asset_attribute = AssetAttributeVote.objects.filter(
                is_upvote=True, asset=asset, attribute=instance
            ).count()
            return upvote_count_for_given_asset_attribute
        return 'Cannot be calculated (asset unknown)'


class AuthenticatedAssetAttributeSerializer(AssetAttributeSerializer):
    """
    Serializer for asset attributes for authenticated users
    """

    voted_by_me = serializers.SerializerMethodField(method_name='_get_voted_by_me')

    class Meta(AssetAttributeSerializer.Meta):
        fields = AssetAttributeSerializer.Meta.fields + ['voted_by_me']

    def _get_voted_by_me(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return False

        if not instance.attribute_votes.filter(user=logged_in_user):
            return False

        return True
