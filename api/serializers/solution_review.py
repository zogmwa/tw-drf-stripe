from rest_framework import serializers
from api.models import SolutionReview, Solution
from api.serializers.user import UserSerializer


class SolutionReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    solution_reviews_count = serializers.IntegerField(read_only=True)
    solution_avg_rating = serializers.DecimalField(
        read_only=True, decimal_places=7, max_digits=10
    )

    class Meta:
        model = SolutionReview
        fields = [
            'id',
            'user',
            'solution',
            'content',
            'rating',
            'created',
            'solution_reviews_count',
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
        instance = super().create(validated_data)
        solution = Solution.objects.get(pk=instance.solution.id)
        instance.solution_reviews_count = solution.reviews_count
        instance.solution_avg_rating = solution.avg_rating
        return instance

    def update(self, instance, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super().update(instance, validated_data)
