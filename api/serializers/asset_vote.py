from rest_framework.serializers import ModelSerializer

from api.models import AssetVote
from api.serializers.user import UserSerializer


class AssetVoteSerializer(ModelSerializer):
    class Meta:
        model = AssetVote
        fields = [
            'id',
            'user',
            'asset',
            'voted_on',
        ]
        read_only_fields = ['user']
        lookup_field = 'id'
