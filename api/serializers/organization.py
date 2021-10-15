from rest_framework.serializers import ModelSerializer

from api.models import Organization


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'website', 'logo_url']
        extra_kwargs = {
            'name': {'validators': []},
        }
        read_only_fields = ['website', 'logo_url']
