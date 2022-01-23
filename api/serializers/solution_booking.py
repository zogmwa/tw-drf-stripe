"""
This module contains serializers for the Solution Bookings API, consumed on the solution bookings pages on the frontend.
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.user import User
from api.models.solution import Solution
from api.models.solution_booking import SolutionBooking
from api.models.solution_review import SolutionReview
from api.models.asset import Asset
from api.serializers.organization import OrganizationSerializer


class UserContactSerializerForSolution(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'email']


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
    point_of_contact = UserContactSerializerForSolution(read_only=True)
    avg_rating = serializers.SerializerMethodField(
        method_name="_get_solution_review_avg_rating"
    )
    my_solution_review = serializers.SerializerMethodField(
        method_name="_get_my_solution_review"
    )
    my_solution_review_id = serializers.SerializerMethodField(
        method_name="_get_my_solution_review_id"
    )
    booked_count = serializers.SerializerMethodField(method_name="_get_bookings_count")

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'title',
            'type',
            'description',
            'point_of_contact',
            'organization',
            'assets',
            'questions',
            'scope_of_work',
            'primary_tag',
            'eta_days',
            'follow_up_hourly_rate',
            'capacity',
            'has_free_consultation',
            'upvotes_count',
            'avg_rating',
            'is_published',
            'booked_count',
            'is_searchable',
            'consultation_scheduling_link',
            'capacity_used',
            'avg_rating',
            'my_solution_review',
            'my_solution_review_id',
            'is_metered',
        ]
        read_only_fields = [
            # TODO: Deprecated
            'pay_now_price_unit_amount',
            'stripe_primary_price_unit_amount',
            'my_solution_review',
            'my_solution_review_id',
            'avg_rating',
            'type',
            'is_metered',
        ]

    def _get_bookings_count(self, instance):
        """
        This is more of a total bookings count than a users count because it counts all the bookings for this solution.
        Maybe renamne this later if appropriate.
        """
        solution_instance = instance
        return solution_instance.bookings.count()

    def _get_my_solution_review_id(self, instance):
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
            return solution_review.id
        except SolutionReview.DoesNotExist:
            return None

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
    metered_booking_info = serializers.SerializerMethodField(
        method_name="_get_metered_booking_info"
    )

    class Meta:
        model = SolutionBooking
        fields = [
            'id',
            'solution',
            'booked_by',
            'manager',
            'status',
            'created',
            'updated',
            'provider_notes',
            'started_at',
            'is_payment_completed',
            'stripe_session_id',
            'price_at_booking',
            'metered_booking_info',
        ]
        read_only_fields = [
            'solution',
            'booked_by',
            'manager',
            'status',
            'created',
            'updated',
            'provider_notes',
            'started_at',
            'is_payment_completed',
            'stripe_session_id',
            'price_at_booking',
            'metered_booking_info',
        ]

    def _get_metered_booking_info(self, instance):
        """
        Return metered solution's booking information
        """
        if instance.solution.is_metered:
            if instance.stripe_subscription is not None:
                return dict(
                    metered_status=instance.stripe_subscription.status,
                    start_date=instance.stripe_subscription.start_date,
                    billing_cycle_anchor=instance.stripe_subscription.billing_cycle_anchor,
                    collection_method=instance.stripe_subscription.collection_method,
                    current_period_end=instance.stripe_subscription.current_period_end,
                )
            else:
                return None
        else:
            return None


class AuthenticatedSolutionBookingSerializer(ModelSerializer):
    solution = SolutionSerializerForSolutionBooking(read_only=True)
    metered_booking_info = serializers.SerializerMethodField(
        method_name="_get_metered_booking_info"
    )

    class Meta:
        model = SolutionBooking
        fields = [
            'id',
            'solution',
            'booked_by',
            'manager',
            'status',
            'price_at_booking',
            'created',
            'updated',
            'provider_notes',
            'started_at',
            'is_payment_completed',
            'stripe_session_id',
            'price_at_booking',
            'rating',
            'metered_booking_info',
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
            'started_at',
            'is_payment_completed',
            'stripe_session_id',
            'price_at_booking',
            'metered_booking_info',
        ]

    def _get_metered_booking_info(self, instance):
        """
        Return metered solution's booking information
        """
        if instance.solution.is_metered:
            if instance.stripe_subscription is not None:
                return dict(
                    metered_status=instance.stripe_subscription.status,
                    start_date=instance.stripe_subscription.start_date,
                    billing_cycle_anchor=instance.stripe_subscription.billing_cycle_anchor,
                    collection_method=instance.stripe_subscription.collection_method,
                    current_period_end=instance.stripe_subscription.current_period_end,
                )
            else:
                return None
        else:
            return None

    def update(self, instance, validated_data):
        solution_booking_instance = instance
        solution_booking_instance.rating = validated_data['rating']
        solution_booking_instance.save()

        return solution_booking_instance
