from rest_framework import serializers
from api.models import SolutionReview
from api.serializers.user import UserSerializer
from api.serializers.solution import SolutionSerializer


class SolutionReviewSerializer(serializers.ModelSerializer):
    solution = SolutionSerializer(read_only=True)

    class Meta:
        model = SolutionReview
        fields = [
            'id',
            'solution',
            'type',
            'created',
        ]
