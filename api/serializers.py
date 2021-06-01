from email.headerregistry import Group

from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import User, Tag, Asset, AssetQuestion


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


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

    class Meta:
        model = Asset
        fields = ['slug', 'name', 'logo_url', 'website', 'affiliate_link', 'short_description', 'description', 'tags']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
