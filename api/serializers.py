from email.headerregistry import Group

from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer

from api.models import User, Tag, Asset, AssetQuestion, PricePlan, AssetVote, Attribute, AttributeVote


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
    # Upvotes count for asset in content
    upvotes_count = serializers.SerializerMethodField(method_name='get_upvote_counts_for_asset_in_request')

    class Meta:
        model = Attribute
        fields = ['name', 'is_con', 'upvotes_count']

    def get_upvote_counts_for_asset_in_request(self, instance):
        request = self.context.get('request')
        asset_slug = request.query_params.get('asset', '')
        asset_slug = asset_slug.strip()

        if asset_slug:
            asset = Asset.objects.get(slug=asset_slug)
            upvote_count_for_given_asset_attribute = AttributeVote.objects.filter(
                is_upvote=True, asset=asset, attribute=instance
            ).count()
            return upvote_count_for_given_asset_attribute
        return 'Cannot be calculated (asset unknown)'


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


class AssetAttributeVoteSerializer(ModelSerializer):

    # Read-Only because this isn't explicitly provided by the user
    user = UserSerializer(read_only=True)

    class Meta:
        model = AttributeVote
        fields = [
            'is_upvote', 'user', 'attribute', 'asset', 'voted_on',
        ]

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the asset attribute vote will be associated with
            validated_data['user'] = request.user

        return super().create(validated_data)
