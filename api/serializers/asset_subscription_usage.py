from rest_framework import serializers
import uuid
import stripe
import datetime
from rest_framework.serializers import ModelSerializer

from api.models.asset_price_plan import AssetPricePlan
from api.models.asset_subscription_usage import AssetSubscriptionUsage
from api.models.asset_price_plan_subscription import AssetPricePlanSubscription
from djstripe.models import SubscriptionItem as StripeSubscriptionItem


class AssetSubscriptionUsageSerializer(ModelSerializer):
    customer_uid = serializers.CharField()
    price_plan_id = serializers.IntegerField()

    class Meta:
        model = AssetSubscriptionUsage
        fields = [
            'customer_uid',
            'price_plan_id',
            'tracked_units',
            'usage_effective_date',
            'usage_period',
            'status',
        ]
        read_only_fields = ['usage_period', 'status']

    def create(self, validated_data):
        customer_uid = validated_data.pop('customer_uid', '')
        asset_price_plan_id = validated_data.pop('price_plan_id', '')
        try:
            asset_price_plan = AssetPricePlan.objects.get(id=asset_price_plan_id)
            asset_subscription = self._get_asset_subscription(
                customer_uid, asset_price_plan.id
            )

            if asset_subscription is None:
                raise serializers.ValidationError(
                    "Customer: {} is not subscribed to price plan: {} on TaggedWeb. Please ask the user to subscribe to the plan id or reach out to TaggedWeb team for assistance".format(
                        customer_uid, asset_price_plan_id
                    )
                )

            validated_data['asset_subscription'] = asset_subscription
            asset_subscription_usage = super().create(validated_data)
            asset_subscription_usage.customer_uid = customer_uid
            asset_subscription_usage.price_plan_id = asset_price_plan_id

            self._report_usage_to_stripe(asset_subscription_usage)

            return asset_subscription_usage
        except AssetPricePlan.DoesNotExist:
            raise serializers.ValidationError(
                "PricePlan with provided id: {} does not exist".format(
                    asset_price_plan_id
                )
            )

    def _get_asset_subscription(self, customer_uid, asset_price_plan_id):
        if customer_uid and asset_price_plan_id:
            try:
                asset_subscription = AssetPricePlanSubscription.objects.get(
                    price_plan__id=asset_price_plan_id,
                    customer__customer_uid=customer_uid,
                )
                return asset_subscription
            except AssetPricePlanSubscription.DoesNotExist:
                return None

    def _report_usage_to_stripe(self, asset_subscription_usage):
        idempotency_key = uuid.uuid4()
        stripe_subscription_item = StripeSubscriptionItem.objects.filter(
            subscription__id=asset_subscription_usage.asset_subscription.stripe_subscription.id
        )[0]
        stripe.SubscriptionItem.create_usage_record(
            stripe_subscription_item.id,
            quantity=int(asset_subscription_usage.tracked_units),
            timestamp=int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
            action='set',
            idempotency_key=str(
                idempotency_key,
            ),
        )
