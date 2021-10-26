from rest_framework.serializers import ModelSerializer

from api.models.asset_solution import AssetSolution
from api.serializers.organization import OrganizationSerializer


class AssetSolutionSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = AssetSolution
        fields = [
            'id',
            'title',
            'type',
            'detailed_description',
            'asset',
            'point_of_contact',
            'organization',
        ]
