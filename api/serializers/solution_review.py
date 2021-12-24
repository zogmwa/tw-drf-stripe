from rest_framework import serializers
from api.models import SolutionReview, Solution


class SolutionSerializerForSolutionReview(serializers.ModelSerializer):
    model = Solution

    class Meta:
        model = Solution
        fields = [
            'id',
            'title',
            'slug',
            'sad_count',
            'neutral_count',
            'happy_count',
        ]


class SolutionReviewSerializer(serializers.ModelSerializer):
    solution = SolutionSerializerForSolutionReview(read_only=True)

    class Meta:
        model = SolutionReview
        fields = [
            'id',
            'solution',
            'type',
            'created',
        ]
