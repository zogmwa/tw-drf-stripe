from rest_framework.serializers import ModelSerializer

from api.models.solution_booking import SolutionBooking
from api.serializers.solution import SolutionSerializer


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
    solution = SolutionSerializer(read_only=True)

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
