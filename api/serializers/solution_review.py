from rest_framework import serializers
from api.models import SolutionReview, Solution


class SolutionSerializerForSolutionReview(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField(
        method_name="_get_solution_review_avg_rating"
    )

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'avg_rating',
        ]

    def _get_solution_review_avg_rating(self, solution_instance):
        """
        Calculating avg_rating from status counts
        """
        sad_count = solution_instance.sad_count
        happy_count = solution_instance.happy_count
        if happy_count - sad_count > 0:
            return 1
        elif happy_count - sad_count == 0:
            return 0
        else:
            return -1


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
