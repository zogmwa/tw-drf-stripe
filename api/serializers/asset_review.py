from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
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

    def _inject_logged_in_user_into_validated_data(self, validated_data: dict):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

    def validate(self, attrs: dict):
        validated_data = super().validate(attrs)
        self._inject_logged_in_user_into_validated_data(validated_data)
        return validated_data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super().update(instance, validated_data)
