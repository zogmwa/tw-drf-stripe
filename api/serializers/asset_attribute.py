from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Attribute, Asset, AssetAttributeVote


class AssetAttributeSerializer(ModelSerializer):
    # Upvotes count for asset in content
    upvotes_count = serializers.SerializerMethodField(
        method_name='get_upvote_counts_for_asset_in_context'
    )

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'is_con', 'upvotes_count']

    def get_upvote_counts_for_asset_in_context(self, instance):
        request = self.context.get('request')
        asset_id = self.context.get('asset_id')
        asset_slug = request.query_params.get('asset', '')
        asset_slug = asset_slug.strip()

        asset = None
        if asset_slug:
            asset = Asset.objects.get(slug=asset_slug)
        elif asset_id:
            asset = Asset.objects.get(id=asset_id)

        if asset:
            upvote_count_for_given_asset_attribute = AssetAttributeVote.objects.filter(
                is_upvote=True, asset=asset, attribute=instance
            ).count()
            return upvote_count_for_given_asset_attribute
        return 'Cannot be calculated (asset unknown)'


class AuthenticatedAssetAttributeSerializer(AssetAttributeSerializer):
    """
    Serializer for asset attributes for authenticated users
    """

    my_asset_attribute_vote = serializers.SerializerMethodField(
        method_name='_get_my_asset_attribute_vote'
    )

    class Meta(AssetAttributeSerializer.Meta):
        fields = AssetAttributeSerializer.Meta.fields + ['my_asset_attribute_vote']

    def _get_my_asset_attribute_vote(self, instance):
        logged_in_user = self.context['request'].user
        asset_id = self.context.get('asset_id')
        asset_slug = self.context['request'].query_params.get('asset', '')
        asset_slug = asset_slug.strip()

        asset = None
        if asset_slug:
            asset = Asset.objects.get(slug=asset_slug)
        elif asset_id:
            asset = Asset.objects.get(id=asset_id)

        if not logged_in_user:
            return None

        try:
            asset_attribute_vote = instance.attribute_votes.get(
                user=logged_in_user, asset=asset
            )
            return asset_attribute_vote.id
        except AssetAttributeVote.DoesNotExist:
            return None

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            validated_data['submitted_by'] = request.user

        attribute = super().create(validated_data)
        asset_id = request.data.get('asset')

        if asset_id:
            asset = Asset.objects.get(id=asset_id)
            attribute.assets.add(asset)
            attribute.save()

        return attribute
