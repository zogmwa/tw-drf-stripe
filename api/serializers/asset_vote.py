from rest_framework.serializers import ModelSerializer

from api.models import AssetVote
from api.serializers.user import UserSerializer


class AssetVoteSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AssetVote
        fields = [
            'id', 'user', 'asset', 'voted_on',
        ]
