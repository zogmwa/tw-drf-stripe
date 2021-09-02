import logging

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import Asset, AssetQuestion
from api.models.user import User, UserAssetLink
from api.models.asset_snapshot import AssetSnapshot
from api.serializers.asset_attribute import AssetAttributeSerializer
from api.serializers.asset_question import AssetQuestionSerializer
from api.serializers.asset_snapshot import AssetSnapshotSerializer
from api.serializers.organization import OrganizationSerializer
from api.serializers.price_plan import PricePlanSerializer
from api.serializers.tag import TagSerializer


class AssetSerializer(HyperlinkedModelSerializer):
    """
    This is the serializer for the listing page, not all fields are to be returned
    on the listing page.
    """

    tags = TagSerializer(read_only=True, many=True)
    customer_organizations = OrganizationSerializer(required=False, many=True)
    attributes = AssetAttributeSerializer(read_only=True, many=True)
    price_plans = PricePlanSerializer(read_only=True, many=True)
    questions = AssetQuestionSerializer(read_only=True, many=True)
    # Don't allow more than 20 snapshots for now to be added
    snapshots = AssetSnapshotSerializer(required=False, many=True)

    # Represents a masked url that should be used instead of affiliate_link so that click-throughs are tracked.
    tweb_url = serializers.URLField(read_only=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    users_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=7
    )
    used_by_me = serializers.BooleanField(write_only=True, required=False)
    reviews_count = serializers.IntegerField(read_only=True)

    @staticmethod
    def _create_snapshots_and_associate_with_asset(
        snapshots: dict,
        asset: Asset,
    ) -> None:
        for snapshot_dict in snapshots:
            AssetSnapshot.objects.get_or_create(
                **snapshot_dict,
                asset=asset,
            )

    def _set_submitted_by_to_logged_in_user(self, validated_data):
        # Mutate validated_data to set submitted_by to logged-in user if we have one
        logged_in_user = self.context['request'].user
        if logged_in_user:
            validated_data['submitted_by'] = self.context['request'].user

    def create(self, validated_data):
        validated_data.pop('used_by_me', None)
        self._set_submitted_by_to_logged_in_user(validated_data)
        # Nested objects in DRF are not supported/are-read only by default so we have to pop this and create snapshot
        # objects and associate them with the asset separately after creation of the asset.
        snapshots_dicts = validated_data.pop('snapshots', [])
        asset = super().create(validated_data)

        AssetSerializer._create_snapshots_and_associate_with_asset(
            snapshots_dicts, asset
        )

        return asset

    def _get_filter_kwargs_for_asset_user_link_queryset(self, asset_id):
        kwargs = {"asset_id": asset_id, "user_id": self.context['request'].user.id}
        return kwargs

    def update(self, instance, validated_data):
        asset_used = validated_data.pop('used_by_me', None)
        self._set_submitted_by_to_logged_in_user(validated_data)
        snapshots_dicts = validated_data.pop('snapshots', [])
        asset = super().update(instance, validated_data)

        if asset_used is not None:
            if asset_used:
                UserAssetLink.objects.get_or_create(
                    **self._get_filter_kwargs_for_asset_user_link_queryset(asset.id)
                )
            if not asset_used:
                UserAssetLink.objects.filter(
                    **self._get_filter_kwargs_for_asset_user_link_queryset(asset.id)
                ).delete()

        AssetSerializer._create_snapshots_and_associate_with_asset(
            snapshots_dicts, asset
        )

        return asset

    class Meta:
        model = Asset
        fields = [
            'id',
            'slug',
            'name',
            'logo_url',
            'logo',
            'website',
            'affiliate_link',
            'short_description',
            'description',
            'promo_video',
            'tags',
            'attributes',
            'tweb_url',
            'upvotes_count',
            'og_image_url',
            'price_plans',
            'questions',
            'customer_organizations',
            'avg_rating',
            'reviews_count',
            'has_free_trial',
            'snapshots',
            'users_count',
            'used_by_me',
        ]
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
