from rest_framework.serializers import ModelSerializer

from api.models import AssetQuestionVote
from api.serializers.user import UserSerializer


class AssetQuestionVoteSerializer(ModelSerializer):

    # Read-Only because this isn't explicitly provided by the user
    user = UserSerializer(read_only=True)

    class Meta:
        model = AssetQuestionVote
        fields = [
            'id',
            'user',
            'question',
            'voted_on',
        ]

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the asset Question vote will be associated with
            validated_data['user'] = request.user

        return super().create(validated_data)
