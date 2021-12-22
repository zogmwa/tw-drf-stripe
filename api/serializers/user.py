from email.headerregistry import Group
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from api.serializers.asset import AssetSerializer
from api.serializers.solution_booking import AuthenticatedSolutionBookingSerializer
from api.serializers.solution_bookmark import SolutionBookmarkSerializerForUserProfile
from .organization import OrganizationSerializer
from api.models.solution_booking import SolutionBooking
from api.models import User, Organization


class UserSerializer(ModelSerializer):
    organization = OrganizationSerializer(many=False, required=False)
    # TODO: later try to send submitted_asssets only when asked by the user by some additional parameter
    submitted_assets = AssetSerializer(many=True, read_only=True)
    owned_assets = AssetSerializer(many=True, read_only=True)
    pending_asset_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0), read_only=True
    )
    social_accounts = serializers.ListField(read_only=True)
    bookmarked_solutions = serializers.SerializerMethodField(
        method_name='_get_bookmarked_solutions'
    )
    contracts = serializers.SerializerMethodField(method_name='_get_contracts')

    def _get_bookmarked_solutions(self, instance):
        request = self.context.get('request')
        serialize_context = {'request': request}
        bookmarked_solutions_serializer = SolutionBookmarkSerializerForUserProfile(
            instance.bookmarks, context=serialize_context, many=True
        )

        return bookmarked_solutions_serializer.data

    def _get_contracts(self, instance):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return None
        else:
            solution_booking_queryset = SolutionBooking.objects.filter(
                booked_by=request.user
            )
            solution_booking_serializer = AuthenticatedSolutionBookingSerializer(
                solution_booking_queryset, many=True
            )

            return solution_booking_serializer.data

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'organization',
            'used_assets',
            'submitted_assets',
            'owned_assets',
            'pending_asset_ids',
            'social_accounts',
            'bookmarked_solutions',
            'contracts',
        ]
        read_only_fields = ['is_business_user']
        lookup_field = 'username'
        extra_kwargs = {'url': {'lookup_field': 'username'}}

    def _create_organization_and_link_user(self, organization_dict, user) -> None:
        organization, is_created = Organization.objects.get_or_create(
            **organization_dict
        )
        organization.users.add(user)
        organization.save()

    def create(self, validated_data):
        organization_dict = validated_data.pop('organization', {})
        user = super().create(validated_data)
        self._create_organization_and_link_user(organization_dict, user)

        return user

    def update(self, instance, validated_data):
        organization_dict = validated_data.pop('organization', {})
        user = super().update(instance, validated_data)
        self._create_organization_and_link_user(organization_dict, user)

        return user


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
