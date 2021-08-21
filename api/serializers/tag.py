from rest_framework.serializers import HyperlinkedModelSerializer

from api.models import Tag


class TagSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ['slug', 'name']
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}
