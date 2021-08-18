from rest_framework.serializers import ModelSerializer

from api.models import AssetReview
from api.serializers.user import UserSerializer


class AssetReviewSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AssetReview
        fields = [
            'id', 'user', 'asset', 'content', 'rating', 'created',
        ]

    def create(self, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super(AssetReviewSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super().update(instance, validated_data)
