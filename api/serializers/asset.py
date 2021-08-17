from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import Asset
from api.serializers.asset_attribute import AssetAttributeSerializer
from api.serializers.price_plan import PricePlanSerializer
from api.serializers.tag import TagSerializer


class AssetSerializer(HyperlinkedModelSerializer):
    """
    This is the serializer for the listing page, not all fields are to be returned
    on the listing page.
    """
    tags = TagSerializer(read_only=True, many=True)
    attributes = AssetAttributeSerializer(read_only=True, many=True)
    price_plans = PricePlanSerializer(read_only=True, many=True)

    # Represents a masked url that should be used instead of affiliate_link so that click-throughs are tracked.
    tweb_url = serializers.URLField(read_only=True)
    upvotes_count = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set submitted_by if we have a reference to a logged in user instance
            validated_data['submitted_by'] = self.context['request'].user

        return super(AssetSerializer, self).create(validated_data)

    class Meta:
        model = Asset
        fields = [
            'id', 'slug', 'name', 'logo_url', 'website', 'affiliate_link', 'short_description', 'description',
            'promo_video', 'tags', 'attributes', 'tweb_url', 'upvotes_count', 'og_image_url', 'price_plans',
        ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
