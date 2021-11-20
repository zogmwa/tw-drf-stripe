from django.db import models
from django.db.models import UniqueConstraint

from api.models.solution import Solution


class SolutionPrice(models.Model):
    """
    Mimics the concept of a Stripe Price. See the following documentation for details:
    https://stripe.com/docs/billing/prices-guide

    Why have multiple prices per solution? (Stripe Prices doc explains it but to summarize it in our context):
    - Some solutions may have a one time payment
    - For some solutions we may want to amortize payments in equal installments say over 12 months
      (give discounts for longer term contracts)
    """

    solution = models.ForeignKey(
        Solution, on_delete=models.CASCADE, related_name='prices'
    )

    # If the price is None that doesn't mean it is 0, it's just that we don't know that yet and this specific
    # solution requires the solution provider to send the user a quote. This will be more of an estimated price
    # and not an actual price.
    stripe_price_id = models.CharField(null=True, blank=True, max_length=254)

    # The price value should be stored on the stripe price object as well but we store it here to show it before the
    # user is sent to the checkout page. On the checkout page they will see the price pulled from the mirrored stripe
    # price object.
    price = models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    # Whether this price is primary for the solution in question. We may want to mark this as a default.
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Solution Price'
        verbose_name_plural = 'Solution Prices'

        # One solution can only have one price object as primary
        constraints = [
            UniqueConstraint(
                fields=['solution', 'is_primary'], name='primary_price_of_solution'
            )
        ]
