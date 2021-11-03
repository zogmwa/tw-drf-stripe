from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import AssetQuestion, AssetQuestionVote


class AssetQuestionSerializer(ModelSerializer):
    upvotes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = AssetQuestion
        fields = ['id', 'asset', 'title', 'created', 'modified', 'primary_answer', 'upvotes_count']
        read_only_fields = ('created', 'modified')

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the asset Question will be associated with
            validated_data['submitted_by'] = request.user

        return super().create(validated_data)


class AuthenticatedAssetQuestionSerializer(AssetQuestionSerializer):
    """
    Serializer for asset questions for authenticated users
    """

    my_asset_question_vote = serializers.SerializerMethodField(
        method_name='_get_my_asset_question_vote'
    )

    class Meta(AssetQuestionSerializer.Meta):
        fields = AssetQuestionSerializer.Meta.fields + ['my_asset_question_vote']

    def _get_my_asset_question_vote(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return None

        try:
            asset_question_vote = instance.votes.get(user=logged_in_user)
            return asset_question_vote.id
        except AssetQuestionVote.DoesNotExist:
            return None
