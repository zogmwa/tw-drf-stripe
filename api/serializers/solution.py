from rest_framework.serializers import ModelSerializer

from api.models.solution import Solution
from api.serializers.organization import OrganizationSerializer


class SolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Solution
        fields = [
            'id',
            'title',
            'type',
            'price',
            'currency',
            'detailed_description',
            'point_of_contact',
            'organization',
        ]
