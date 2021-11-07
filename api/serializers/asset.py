from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Asset, AssetVote, PricePlan
from api.models.asset_snapshot import AssetSnapshot
from api.serializers.asset_attribute import (
    AssetAttributeSerializer,
    AuthenticatedAssetAttributeSerializer,
)
from api.serializers.asset_question import AssetQuestionSerializer
from api.serializers.asset_snapshot import AssetSnapshotSerializer
from api.serializers.solution import SolutionSerializer
from api.serializers.organization import OrganizationSerializer
from api.serializers.price_plan import PricePlanSerializer
from api.serializers.tag import TagSerializer


class AssetSerializer(ModelSerializer):
    """
    This is the serializer for the listing page, not all fields are to be returned
    on the listing page.
    """

    tags = TagSerializer(read_only=True, many=True)
    customer_organizations = OrganizationSerializer(required=False, many=True)
    solutions = SolutionSerializer(read_only=True, many=True)
    attributes = serializers.SerializerMethodField(method_name='_get_attributes')
    price_plans = PricePlanSerializer(read_only=True, many=True)
    questions = AssetQuestionSerializer(read_only=True, many=True)
    # Don't allow more than 20 snapshots for now to be added
    snapshots = AssetSnapshotSerializer(required=False, many=True)
    price_plans = PricePlanSerializer(required=False, many=True)

    # Represents a masked url that should be used instead of affiliate_link so that click-throughs are tracked.
    tweb_url = serializers.URLField(read_only=True)
    upvotes_count = serializers.IntegerField(read_only=True)
    users_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=7
    )

    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id',
            'slug',
            'name',
            'logo_url',
            'logo',
            'website',
            'affiliate_link',
            'short_description',
            'description',
            'promo_video',
            'tags',
            'attributes',
            'tweb_url',
            'upvotes_count',
            'og_image_url',
            'price_plans',
            'questions',
            'customer_organizations',
            'solutions',
            'avg_rating',
            'reviews_count',
            'has_free_trial',
            'trial_days',
            'snapshots',
            'users_count',
        ]
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field': 'slug'}}

    def _get_attributes(self, instance):
        request = self.context.get('request')
        serialize_context = {'request': request, 'asset_id': instance.id}
        if request.user.is_anonymous:
            serializer = AssetAttributeSerializer(
                instance.attributes, many=True, context=serialize_context
            )
        else:
            serializer = AuthenticatedAssetAttributeSerializer(
                instance.attributes, many=True, context=serialize_context
            )
        return serializer.data


class AuthenticatedAssetSerializer(AssetSerializer):
    used_by_me = serializers.SerializerMethodField(
        method_name="_get_asset_usage_status_in_request"
    )
    my_asset_vote = serializers.SerializerMethodField(method_name="_get_my_asset_vote")
    is_owned = serializers.SerializerMethodField(method_name="_get_is_owned")
    edit_allowed = serializers.SerializerMethodField(method_name="_get_edit_allowed")

    @staticmethod
    def _create_snapshots_and_associate_with_asset(
        snapshots: dict,
        asset: Asset,
    ) -> None:
        for snapshot_dict in snapshots:
            AssetSnapshot.objects.get_or_create(**snapshot_dict, asset=asset)

    @staticmethod
    def _update_snapshots_and_associate_with_asset(
        snapshots: dict,
        asset: Asset,
    ) -> None:
        snapshot_urls = [snapshot['url'] for snapshot in snapshots]
        rows_to_delete = AssetSnapshot.objects.filter(asset=asset).exclude(
            url__in=snapshot_urls
        )
        rows_to_delete.all().delete()

        for snapshot_dict in snapshots:
            AssetSnapshot.objects.get_or_create(**snapshot_dict, asset=asset)

    @staticmethod
    def _update_price_plans_and_associate_with_asset(
        price_plans_dicts: dict, asset: Asset
    ) -> None:
        rows_to_delete = PricePlan.objects.filter(asset=asset)
        rows_to_delete.all().delete()

        for price_plans_dict in price_plans_dicts:
            price_plans_dict['asset'] = asset
            PricePlan.objects.get_or_create(**price_plans_dict)

    def _get_asset_usage_status_in_request(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return False

        if not instance.users.filter(pk=logged_in_user.id):
            return False

        return True

    def _get_my_asset_vote(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return None

        try:
            asset_vote = AssetVote.objects.get(user=logged_in_user, asset=instance)
            return asset_vote.id
        except AssetVote.DoesNotExist:
            return None

    def _get_is_owned(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return False

        return instance.owner == logged_in_user

    def _get_edit_allowed(self, instance):
        logged_in_user = self.context['request'].user

        if not logged_in_user:
            return False

        if instance.owner == logged_in_user:
            return True

        if instance.submitted_by == logged_in_user and instance.owner is None:
            return True

        return False

    def _set_submitted_by_to_logged_in_user(self, validated_data):
        # Mutate validated_data to set submitted_by to logged-in user if we have one
        logged_in_user = self.context['request'].user
        if logged_in_user:
            validated_data['submitted_by'] = self.context['request'].user

    def create(self, validated_data):
        self._set_submitted_by_to_logged_in_user(validated_data)
        # Nested objects in DRF are not supported/are-read only by default so we have to pop this and create snapshot
        # objects and associate them with the asset separately after creation of the asset.
        snapshots_dicts = validated_data.pop('snapshots', [])
        asset = super().create(validated_data)

        self._create_snapshots_and_associate_with_asset(snapshots_dicts, asset)

        return asset

    def update(self, instance, validated_data):
        snapshots_dicts = validated_data.pop('snapshots', None)
        price_plans_dicts = validated_data.pop('price_plans', None)

        asset = super().update(instance, validated_data)

        if snapshots_dicts is not None:
            self._update_snapshots_and_associate_with_asset(snapshots_dicts, asset)

        if price_plans_dicts is not None:
            self._update_price_plans_and_associate_with_asset(price_plans_dicts, asset)

        return asset

    class Meta(AssetSerializer.Meta):
        fields = AssetSerializer.Meta.fields + [
            'used_by_me',
            'my_asset_vote',
            'is_owned',
            'edit_allowed',
        ]
