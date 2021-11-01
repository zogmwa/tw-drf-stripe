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
    assets = AssetFeaturedSerializer(many=True, read_only=True)

    class Meta:
        model = Tag
        fields = ['slug', 'name', 'assets']
