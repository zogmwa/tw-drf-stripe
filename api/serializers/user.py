from email.headerregistry import Group

from rest_framework.serializers import HyperlinkedModelSerializer
from .organization import OrganizationSerializer
from api.models import User, Organization


class UserSerializer(HyperlinkedModelSerializer):
    organization = OrganizationSerializer(many=False, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'organization']
        lookup_field = 'username'
        extra_kwargs = {'url': {'lookup_field': 'username'}}

    def link_organization(self, organization_dict, user):
        organization, is_created = Organization.objects.get_or_create(
            **organization_dict
        )
        organization.users.add(user)
        organization.save()

    def create(self, validated_data):
        organization_dict = validated_data.pop('organization', {})
        user = super().create(validated_data)
        self.link_organization(organization_dict, user)

        return user

    def update(self, instance, validated_data):
        organization_dict = validated_data.pop('organization', {})
        user = super().update(instance, validated_data)
        self.link_organization(organization_dict, user)

        return user


class GroupSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
