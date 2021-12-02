from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.models.solution_vote import SolutionVote
from api.models.solution_bookmark import SolutionBookmark
from api.models.solution_booking import SolutionBooking
from api.models.asset import Asset
from api.serializers.organization import OrganizationSerializer
from api.serializers.solution_price import SolutionPriceSerializer
from api.serializers.tag import TagSerializer
from api.serializers.solution_question import SolutionQuestionSerializer


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
    prices = SolutionPriceSerializer(required=False, many=True)
    tags = TagSerializer(read_only=True, many=True)
    primary_tag = TagSerializer(read_only=True)
    assets = AssetSerializerForSolution(read_only=True, many=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    questions = SolutionQuestionSerializer(read_only=True, many=True)
    avg_rating = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=7
    )
    reviews_count = serializers.IntegerField(read_only=True)

    booked_count = serializers.SerializerMethodField(
        method_name="_get_booked_users_count"
    )

    def _get_booked_users_count(self, instance):
        return instance.solution_bookings.count()

    class Meta:
        model = Solution
        fields = [
            'id',
            'slug',
            'stripe_product_id',
            'title',
            'type',
            'prices',
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
            'reviews_count',
            'is_published',
            'booked_count',
            'bookings_pending_fulfillment_count',
        ]


class AuthenticatedSolutionSerializer(SolutionSerializer):
    my_solution_vote = serializers.SerializerMethodField(
        method_name="_get_my_solution_vote"
    )
    my_solution_bookmark = serializers.SerializerMethodField(
        method_name="_get_my_solution_bookmark"
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

    class Meta(SolutionSerializer.Meta):
        fields = SolutionSerializer.Meta.fields + [
            'my_solution_vote',
            'my_solution_bookmark',
        ]


class AuthenticatedSolutionForBookmarkSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    prices = SolutionPriceSerializer(required=False, many=True)
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
            'prices',
            'upvotes_count',
            'organization',
            'title',
            'prices',
            'my_solution_vote',
        ]
