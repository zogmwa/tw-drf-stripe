from rest_framework.serializers import ModelSerializer

from api.models import AssetVote
from api.serializers.user import UserSerializer


class AssetVoteSerializer(ModelSerializer):
    class Meta:
        model = AssetVote
        fields = [
            'id',
            'asset',
            'voted_on',
        ]
        lookup_field = 'id'
