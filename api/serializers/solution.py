from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.user import User
from api.models.solution import Solution
from api.models.solution_vote import SolutionVote
from api.models.solution_bookmark import SolutionBookmark
from api.models.solution_booking import SolutionBooking
from api.models.solution_review import SolutionReview
from api.models.asset import Asset
from api.serializers.organization import OrganizationSerializer
from api.serializers.solution_booking import SolutionBookingSerializer
from api.serializers.tag import TagSerializer
from api.serializers.solution_question import SolutionQuestionSerializer


class UserContactSerializerForSolution(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar']


class AssetSerializerForSolution(ModelSerializer):
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


class SolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    primary_tag = TagSerializer(read_only=True)
    assets = AssetSerializerForSolution(read_only=True, many=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    questions = SolutionQuestionSerializer(read_only=True, many=True)
    point_of_contact = UserContactSerializerForSolution(read_only=True)
    avg_rating = serializers.SerializerMethodField(
        method_name="_get_solution_review_avg_rating"
    )
    booked_count = serializers.SerializerMethodField(
        method_name="_get_booked_users_count"
    )

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'stripe_product_id',
            'title',
            'type',
            'pay_now_price_stripe_id',
            'pay_now_price_unit_amount',
            'description',
            'point_of_contact',
            'organization',
            'tags',
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
            'bookings_pending_fulfillment_count',
            'consultation_scheduling_link',
        ]
        read_only_fields = [
            'pay_now_price_stripe_id',
            'pay_now_price_unit_amount',
        ]

    def _get_booked_users_count(self, instance):
        """
        This is more of a total bookings count than a users count because it counts all the bookings for this solution.
        Maybe renamne this later if appropriate.
        """
        solution_instance = instance
        return solution_instance.bookings.count()

    def _get_solution_review_avg_rating(self, instance):
        """
        Calculating avg_rating from status counts
        """
        solution_instance = instance
        sad_count = solution_instance.sad_count
        happy_count = solution_instance.happy_count
        return happy_count - sad_count


class AuthenticatedSolutionSerializer(SolutionSerializer):
    my_solution_vote = serializers.SerializerMethodField(
        method_name="_get_my_solution_vote"
    )
    my_solution_bookmark = serializers.SerializerMethodField(
        method_name="_get_my_solution_bookmark"
    )
    my_solution_review = serializers.SerializerMethodField(
        method_name="_get_my_solution_review"
    )

    last_solution_booking = serializers.SerializerMethodField()

    def get_last_solution_booking(self, obj):
        try:
            queryset = SolutionBooking.objects.filter(
                booked_by_id=self.context['request'].user.pk,
                solution_id=obj.id,
            ).order_by('-updated')[:1]
            return SolutionBookingSerializer(queryset, many=True).data
        except ():
            return None

    def _get_my_solution_vote(self, instance):
        logged_in_user = self.context['request'].user
        if not logged_in_user:
            return None

        try:
            solution_vote = SolutionVote.objects.get(
                user=logged_in_user, solution=instance
            )
            return solution_vote.id
        except SolutionVote.DoesNotExist:
            return None

    def _get_my_solution_bookmark(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return None

        try:
            solution_bookmark = SolutionBookmark.objects.get(
                user=logged_in_user, solution=instance
            )
            return solution_bookmark.id
        except SolutionBookmark.DoesNotExist:
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

    class Meta(SolutionSerializer.Meta):
        fields = SolutionSerializer.Meta.fields + [
            'my_solution_vote',
            'my_solution_bookmark',
            'last_solution_booking',
            'my_solution_review',
        ]


class AuthenticatedSolutionForBookmarkSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    my_solution_vote = serializers.SerializerMethodField(
        method_name="_get_my_solution_vote"
    )

    def _get_my_solution_vote(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return None

        try:
            solution_vote = SolutionVote.objects.get(
                user=logged_in_user, solution=instance
            )
            return solution_vote.id
        except SolutionVote.DoesNotExist:
            return None

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'tags',
            'upvotes_count',
            'organization',
            'title',
            'my_solution_vote',
        ]
