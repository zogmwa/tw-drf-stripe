from email.headerregistry import Group

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from api.models import User, Tag, Asset, AssetQuestion, PricePlan, AssetVote, Attribute


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


class AssetAttributeSerializer(ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['name', 'is_con']


class PricePlanSerializer(ModelSerializer):
    class Meta:
        model = PricePlan
        fields = ['asset', 'name', 'summary', 'currency', 'price', 'per', 'features']


class AssetQuestionSerializer(ModelSerializer):
    class Meta:
        model = AssetQuestion
        fields = ['asset', 'question', 'answer', 'upvote_count']


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


class AssetVoteSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AssetVote
        fields = [
            'id', 'user', 'asset', 'voted_on',
        ]
