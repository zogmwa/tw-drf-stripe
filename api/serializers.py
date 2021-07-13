from email.headerregistry import Group

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from api.models import User, Tag, Asset, AssetQuestion, PricePlan, AssetVote


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }


class GroupSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class TagSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Tag
        fields = ['slug', 'name']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class PricePlanSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = PricePlan
        fields = ['name', 'summary', 'currency', 'price', 'per', 'features']


class AssetQuestionSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = AssetQuestion
        fields = ['question', 'answer', 'upvote_count']


class AssetSerializer(HyperlinkedModelSerializer):
    """
    This is the serializer for the listing page, not all fields are to be returned
    on the listing page.
    """
    tags = TagSerializer(read_only=True, many=True)
    price_plans = PricePlanSerializer(read_only=True, many=True)
    tweb_url = serializers.URLField(read_only=True)
    upvotes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'slug', 'name', 'logo_url', 'website', 'affiliate_link', 'short_description', 'description',
            'promo_video', 'tags', 'tweb_url', 'upvotes_count', 'og_image_url', 'price_plans',
        ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class AssetVoteSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AssetVote
        fields = [
            'user', 'asset', 'voted_on',
        ]
