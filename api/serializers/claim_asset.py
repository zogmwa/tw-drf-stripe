from rest_framework.serializers import ModelSerializer
from api.models.claim_asset import ClaimAsset
from api.serializers.user import UserSerializer
from rest_framework import serializers

from api.serializers.asset import AssetSerializer


class ClaimAssetAdminSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    updated = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ClaimAsset
        fields = [
            'id',
            'user',
            'asset',
            'status',
            'comment',
            'created',
            'updated',
        ]

    def create(self, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super(ClaimAssetAdminSerializer, self).create(validated_data)


class ClaimAssetUserSerializer(ClaimAssetAdminSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = ClaimAsset
        fields = [
            'id',
            'user',
            'asset',
            'status',
            'comment',
            'created',
            'updated',
        ]
