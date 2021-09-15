from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import AssetQuestion, AssetQuestionVote


class AssetQuestionSerializer(ModelSerializer):
    upvotes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AssetQuestion
        fields = ['asset', 'title', 'primary_answer', 'upvotes_count']

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the asset Question will be associated with
            validated_data['submitted_by'] = request.user

        return super().create(validated_data)
