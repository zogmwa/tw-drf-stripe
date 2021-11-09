from rest_framework.serializers import ModelSerializer

from api.models.solution import SolutionBooking


class SolutionBookingSerializer(ModelSerializer):
    class Meta:
        model = SolutionBooking
        fields = []
        read_only_fields = [
            'booked_by',
            'manager',
            'status',
            'created',
            'updated',
            'provider_notes',
        ]
