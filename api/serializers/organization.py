from rest_framework.serializers import ModelSerializer

from api.models import Organization


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name']
        extra_kwargs = {
            'name': {'validators': []},
        }
