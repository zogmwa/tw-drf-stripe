from rest_framework.serializers import ModelSerializer
from api.models.claim_asset import AssetClaim
from api.serializers.user import UserSerializer
from rest_framework import serializers

from api.serializers.asset import AssetSerializer


class AssetClaimSerializer(ModelSerializer):
    """
    This serializer exposes status/staff_comment as writeable fields and should not be used directly until we want to
    implement an endpoint that allows changing status/staff fields and for that we will also have to limit permissions
    to owners/admin only. Preferably consider use of the ClaimAssetUserSerializer below.
    """

    user = UserSerializer(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AssetClaim
        fields = [
            'id',
            'user',
            'asset',
            'status',
            'user_comment',
            'staff_comment',
            'created',
            'updated',
        ]

    def create(self, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super(AssetClaimSerializer, self).create(validated_data)


class AssetClaimUserSerializer(AssetClaimSerializer):
    """
    This serializer we will use for any API endpoint that handles the user's claim requests.
    """

    class Meta:
        model = AssetClaim
        fields = [
            'id',
            'user',
            'asset',
            'status',
            'user_comment',
            'staff_comment',
            'created',
            'updated',
        ]
        read_only_fields = ['status', 'staff_comment']
