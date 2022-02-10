import os
from django.db.models import UniqueConstraint, F
from djstripe.models import Customer as StripeCustomer
from django.db import models


class PartnerCustomer(models.Model):
    """
    This model is for save partner's customer stripe instance.
    """

    # Every user will have a corresponding customer offering on Stripe
    stripe_customer = models.OneToOneField(
        StripeCustomer, null=True, blank=True, on_delete=models.SET_NULL
    )

    customer_id = models.CharField(max_length=150)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['customer_id'], name='partner_customer')
        ]
        verbose_name = 'Partner Customer'
        verbose_name_plural = 'Partner Customers'
