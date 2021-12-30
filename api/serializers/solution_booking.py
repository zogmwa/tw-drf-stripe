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
    my_solution_review_id = serializers.SerializerMethodField(
        method_name="_get_my_solution_review_id"
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
            'my_solution_review_id',
        ]
        read_only_fields = [
            'pay_now_price_unit_amount',
            'my_solution_review',
            'my_solution_review_id',
            'avg_rating',
        ]

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
        ]


class AuthenticatedSolutionBookingSerializer(ModelSerializer):
    solution = SolutionSerializerForSolutionBooking(read_only=True)

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
        ]
        extra_kwargs = {'booked_by': {'required': False}}

    def _inject_logged_in_user_into_validated_data(self, validated_data: dict):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['booked_by'] = self.context['request'].user
            if self.context['request'].data.get('solution'):
                solution = Solution.objects.get(
                    slug=self.context['request'].data.get('solution')
                )
                price_at_booking = solution.pay_now_price.unit_amount / 100
                validated_data['solution'] = solution
                validated_data['price_at_booking'] = price_at_booking

            if self.context['request'].data.get('is_payment_completed'):
                validated_data['is_payment_completed'] = self.context[
                    'request'
                ].data.get('is_payment_completed')
            else:
                validated_data['is_payment_completed'] = False

            if self.context['request'].data.get('status'):
                validated_data['status'] = self.context['request'].data.get('status')
            else:
                validated_data['status'] = SolutionBooking.Status.PENDING

            if self.context['request'].data.get('stripe_session_id'):
                validated_data['stripe_session_id'] = self.context['request'].data.get(
                    'stripe_session_id'
                )

    def validate(self, attrs: dict):
        validated_data = super().validate(attrs)
        self._inject_logged_in_user_into_validated_data(validated_data)
        return validated_data

    def create(self, validated_data):
        try:
            solution_booking = SolutionBooking.objects.get(
                stripe_session_id=validated_data['stripe_session_id'],
                solution=validated_data['solution'],
            )
            return solution_booking
        except SolutionBooking.DoesNotExist:
            return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
