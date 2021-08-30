from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import AssetQuestion, AssetQuestionVote


class AssetQuestionSerializer(ModelSerializer):
    class Meta:
        model = AssetQuestion
        fields = ['asset', 'title', 'primary_answer', 'upvotes_count']
