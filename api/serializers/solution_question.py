from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import SolutionQuestion, SolutionQuestionVote


class SolutionQuestionSerializer(ModelSerializer):
    upvotes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SolutionQuestion
        fields = [
            'id',
            'solution',
            'title',
            'primary_answer',
            'upvotes_count',
            'created',
            'updated',
        ]
        read_only_fields = [
            'created',
            'updated',
            'upvotes_count',
        ]

    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the solution Question will be associated with
            validated_data['submitted_by'] = request.user

        return super().create(validated_data)


class AuthenticatedSolutionQuestionSerializer(SolutionQuestionSerializer):
    """
    Serializer for solution questions for authenticated users
    """

    my_solution_question_vote = serializers.SerializerMethodField(
        method_name='_get_my_solution_question_vote'
    )

    class Meta(SolutionQuestionSerializer.Meta):
        fields = SolutionQuestionSerializer.Meta.fields + ['my_solution_question_vote']

    def _get_my_solution_question_vote(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return None

        try:
            solution_question_vote = instance.votes.get(user=logged_in_user)
            return solution_question_vote.id
        except SolutionQuestionVote.DoesNotExist:
            return None
