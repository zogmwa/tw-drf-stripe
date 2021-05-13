from email.headerregistry import Group

from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import User, Tag, Asset


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


class AssetSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Asset
        fields = ['slug', 'name', 'website', 'description']
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
