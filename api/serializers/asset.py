import logging

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import Asset, AssetQuestion
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
    avg_rating = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=7
    )
    reviews_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        # Set submitted_by to logged-in user if we have one
        logged_in_user = self.context['request'].user
        if logged_in_user:
            validated_data['submitted_by'] = self.context['request'].user

        # Nested objects in DRF are not supported/are-read only by default so we have to pop this and create snapshot
        # objects and associate them with the asset separately after creation of the asset.
        snapshots_dicts = validated_data.pop('snapshots', [])

        asset = super().create(validated_data)

        for snapshot_dict in snapshots_dicts:
            AssetSnapshot.objects.get_or_create(
                **snapshot_dict,
                asset=asset,
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
        ]
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
