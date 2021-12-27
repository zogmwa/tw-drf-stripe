from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.models.solution_booking import SolutionBooking
from api.models.solution_review import SolutionReview
from api.models.asset import Asset
from api.serializers.organization import OrganizationSerializer


class AssetSerializerForSolutionBooking(ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id',
            'slug',
            'name',
            'logo_url',
            'logo',
            'website',
        ]


class SolutionSerializerForSolutionBooking(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    assets = AssetSerializerForSolutionBooking(read_only=True, many=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.SerializerMethodField(
        method_name="_get_solution_review_avg_rating"
    )
    my_solution_review = serializers.SerializerMethodField(
        method_name="_get_my_solution_review"
    )

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'title',
            'pay_now_price_unit_amount',
            'organization',
            'assets',
            'upvotes_count',
            'avg_rating',
            'my_solution_review',
        ]
        read_only_fields = [
            'pay_now_price_unit_amount',
            'my_solution_review',
            'avg_rating',
        ]

    def _get_my_solution_review(self, instance):
        """
        Return solution review type of authenticated user
        """
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return None

        try:
            solution_review = SolutionReview.objects.get(
                user=logged_in_user, solution=instance
            )
            return solution_review.type
        except SolutionReview.DoesNotExist:
            return None

    def _get_solution_review_avg_rating(self, instance):
        """
        Calculating avg_rating from status counts
        """
        solution_instance = instance
        sad_count = solution_instance.sad_count
        happy_count = solution_instance.happy_count
        return happy_count - sad_count


class SolutionBookingSerializer(ModelSerializer):
    class Meta:
        model = SolutionBooking
        fields = [
            'solution',
            'booked_by',
            'manager',
            'status',
            'created',
            'updated',
            'provider_notes',
        ]
        read_only_fields = [
            'solution',
            'booked_by',
            'manager',
            'status',
            'created',
            'updated',
            'provider_notes',
        ]


class AuthenticatedSolutionBookingSerializer(ModelSerializer):
    solution = SolutionSerializerForSolutionBooking(read_only=True)

    class Meta:
        model = SolutionBooking
        fields = [
            'solution',
            'booked_by',
            'manager',
            'status',
            'price_at_booking',
            'created',
            'updated',
            'provider_notes',
        ]
        read_only_fields = [
            'solution',
            'booked_by',
            'manager',
            'status',
            'price_at_booking',
            'created',
            'updated',
            'provider_notes',
        ]
