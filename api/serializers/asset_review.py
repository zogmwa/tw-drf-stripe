from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from api.models import AssetReview, Asset
from api.serializers.user import UserSerializer


class AssetReviewSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    asset_reviews_count = serializers.IntegerField(read_only=True)
    asset_avg_rating = serializers.DecimalField(
        read_only=True, decimal_places=7, max_digits=10
    )

    class Meta:
        model = AssetReview
        fields = [
            'id',
            'user',
            'asset',
            'content',
            'rating',
            'created',
            'video_url',
            'asset_reviews_count',
            'asset_avg_rating',
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
        instance = super().create(validated_data)
        asset = Asset.objects.get(pk=instance.asset.id)
        instance.asset_reviews_count = asset.reviews_count
        instance.asset_avg_rating = asset.avg_rating
        return instance

    def update(self, instance, validated_data):
        logged_in_user = self.context['request'].user
        if logged_in_user:
            # Only set user if we have a reference to a logged in user instance
            validated_data['user'] = self.context['request'].user

        return super().update(instance, validated_data)
