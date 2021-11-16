from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import SolutionQuestion


class SolutionQuestionSerializer(ModelSerializer):
    class Meta:
        model = SolutionQuestion
        fields = [
            'id',
            'solution',
            'title',
            'primary_answer',
            'created',
            'updated',
        ]
        read_only_fields = [
            'created',
            'updated',
        ]

    # Create action is for admins/staff only
    def create(self, validated_data):
        request = self.context['request']
        if request.user and request.user.is_authenticated:
            # Set the user to the logged in user, because that is whom the solution Question will be associated with
            validated_data['submitted_by'] = request.user

        return super().create(validated_data)
