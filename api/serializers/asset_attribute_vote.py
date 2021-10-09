from rest_framework.serializers import ModelSerializer

from api.models import AssetAttributeVote
from api.serializers.asset import AssetSerializer
from api.serializers.user import UserSerializer


class AssetAttributeVoteSerializer(ModelSerializer):
    class Meta:
        model = AssetAttributeVote
        fields = [
            'id',
            'user',
            'attribute',
            'asset',
            'voted_on',
        ]
        read_only_fields = [
            'user',
        ]
        lookup_field = 'id'

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the asset attribute vote will be associated with
            validated_data['user'] = request.user

        return super().create(validated_data)
