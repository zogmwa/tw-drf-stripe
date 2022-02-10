from django.db import models
from django.db.models import UniqueConstraint
from djstripe.models import Subscription as StripeSubscription

from api.models import AssetPricePlan
from api.models.third_party_customer import ThirdPartyCustomer


class AssetPricePlanSubscription(models.Model):
    # Not needed right now but we can add a user field later if needed / if we want to store that information
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    # )

    # This represents whatever the third-party asset owner uses to represent a customer, whether it is a username
    # or it is a unique id associated with the customer.
    customer = models.ForeignKey(
        ThirdPartyCustomer, related_name='subscriptions', on_delete=models.CASCADE
    )

    # Which plan is this user/third-party asset customer subscribed to.
    price_plan = models.ForeignKey(
        AssetPricePlan, related_name='subscriptions', on_delete=models.CASCADE
    )

    stripe_subscription = models.OneToOneField(
        StripeSubscription,
        blank=True,
        null=True,
        related_name='subscriptions',
        on_delete=models.SET_NULL,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['customer', 'price_plan'],
                name='customer_price_plan_subscription',
            )
        ]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
