from email.headerregistry import Group

from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import User


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']
        lookup_field = 'username'
        extra_kwargs = {'url': {'lookup_field': 'username'}}


class GroupSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
