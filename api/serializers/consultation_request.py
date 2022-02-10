from rest_framework import serializers
from api.models.consultation_request import ConsultationRequest
from api.models.solution import Solution

# from serializers.solution import SolutionSerializer


class SolutionSerializerForConsultationRequest(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = [
            "id",
            "slug",
            "title",
        ]


class ConsultationRequestSerializer(serializers.ModelSerializer):
    solution = SolutionSerializerForConsultationRequest(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ConsultationRequest
        fields = [
            "solution",
            "customer_email",
            "customer_first_name",
            "customer_last_name",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]
