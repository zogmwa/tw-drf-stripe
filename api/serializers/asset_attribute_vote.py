from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from api.models import AssetAttributeVote


class AssetAttributeVoteSerializer(ModelSerializer):
    is_upvote = serializers.BooleanField(required=False)

    class Meta:
        model = AssetAttributeVote
        fields = [
            'id',
            'user',
            'attribute',
            'asset',
            'voted_on',
            'is_upvote',
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
