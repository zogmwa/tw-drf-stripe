from rest_framework.serializers import ModelSerializer

from api.models.solution_booking import SolutionBooking


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
