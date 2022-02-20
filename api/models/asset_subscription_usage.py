from django.db import models
import django.utils.timezone
from django.db.models import UniqueConstraint

from api.models import AssetPricePlanSubscription


class AssetSubscriptionUsage(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending'
        CUSTOMER_INVOICED = 'Customer Invoiced'

    asset_subscription = models.ForeignKey(
        AssetPricePlanSubscription,
        related_name='asset_subscriptions',
        on_delete=models.CASCADE,
    )
    tracked_units = models.IntegerField(default=0)
    usage_effective_date = models.DateTimeField(default=django.utils.timezone.now)

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    @property
    def usage_period(self):
        return {
            'current_period_start': self.asset_subscription.stripe_subscription.current_period_start,
            'current_period_end': self.asset_subscription.stripe_subscription.current_period_end,
        }

    status = models.CharField(
        max_length=17,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        verbose_name = 'Asset Subscription Usage'
        verbose_name_plural = 'Asset Subscription Usages'
