from rest_framework import serializers
from api.models import SolutionReview, Solution


class SolutionReviewSerializer(serializers.ModelSerializer):
    solution_avg_rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = SolutionReview
        fields = [
            'id',
            'solution',
            'type',
            'created',
            'solution_avg_rating',
        ]

    def _inject_logged_in_user_into_validated_data(self, validated_data: dict):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

    def validate(self, attrs: dict):
        validated_data = super().validate(attrs)
        self._inject_logged_in_user_into_validated_data(validated_data)
        return validated_data

    def create(self, validated_data):
        solution_review_instance = super().create(validated_data)
        solution_instance = Solution.objects.get(
            pk=solution_review_instance.solution.id
        )
        solution_review_instance.solution_avg_rating = (
            solution_instance.happy_count - solution_instance.sad_count
        )
        return solution_review_instance

    def update(self, instance, validated_data):
        solution_review_instance = super().update(instance, validated_data)
        solution_instance = Solution.objects.get(
            pk=solution_review_instance.solution.id
        )
        solution_review_instance.solution_avg_rating = (
            solution_instance.happy_count - solution_instance.sad_count
        )
        return solution_review_instance
