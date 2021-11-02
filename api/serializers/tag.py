from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from api.models import Tag, Asset


class TagSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ['slug', 'name', 'description']
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}


class AssetFeaturedSerializer(ModelSerializer):
    class Meta:
        model = Asset
        fields = ['name', 'slug', 'logo_url']


class TagFeaturedSerializer(ModelSerializer):
    assets = serializers.SerializerMethodField(method_name='_get_asset_featured')

    class Meta:
        model = Tag
        fields = ['slug', 'name', 'assets']

    def _get_asset_featured(self, instance):
        assets_featured = instance.assets.filter(is_homepage_featured=True).order_by(
            '-upvotes_count'
        )[:10]
        serializer = AssetFeaturedSerializer(assets_featured, many=True)
        return serializer.data
