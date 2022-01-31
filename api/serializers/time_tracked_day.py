from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models.time_tracked_day import TimeTrackedDay


class TimeTrackedDaySerializer(ModelSerializer):
    class Meta:
        model = TimeTrackedDay
        fields = [
            'solution_booking',
            'date',
            'tracking_amount',
        ]
