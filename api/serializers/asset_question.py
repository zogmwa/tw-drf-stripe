from rest_framework.serializers import ModelSerializer

from api.models import AssetQuestion


class AssetQuestionSerializer(ModelSerializer):
    class Meta:
        model = AssetQuestion
        fields = ['asset', 'question', 'answer', 'upvote_count']
