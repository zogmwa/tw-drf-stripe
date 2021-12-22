from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.models.solution_booking import SolutionBooking
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
    avg_rating = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=7
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
        ]
        read_only_fields = [
            'pay_now_price_unit_amount',
        ]


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
