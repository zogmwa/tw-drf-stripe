from rest_framework.serializers import ModelSerializer

from api.models import SolutionVote
from api.serializers.user import UserSerializer


class SolutionVoteSerializer(ModelSerializer):
    class Meta:
        model = SolutionVote
        fields = [
            'id',
            'solution',
            'voted_on',
        ]
