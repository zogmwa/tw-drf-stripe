from django.db import models

from api.models import Asset


class PricePlan(models.Model):
    """
    A price plan associated with an asset. An asset can have one or more price plans. If the price is 0,
    then the plan is free, if price is not set then the plan is a CUSTOM plan.
    """

    asset = models.ForeignKey(
        Asset, related_name='price_plans', on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=128, null=False, blank=False, help_text='Name of the Price Plan'
    )
    summary = models.CharField(max_length=1024, blank=True, null=True)

    currency = models.CharField(max_length=3, default='USD')
    # Price along with the caveats price per month per user, price pear seat
    # This can be nullable because for Custom price plans, price is not known upfront
    price = models.CharField(max_length=16, null=True, blank=True)

    # Day, Month, Year, X Requests, User per Month
    per = models.CharField(max_length=32, null=True, blank=True)

    # This will contain bulleted features to be stored in Markdown format
    features = models.TextField(null=True, blank=True)

    most_popular = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Price Plan'
        verbose_name_plural = 'Price Plans'

    def __str__(self):
        return "{}: {} - {} {} per {}".format(
            self.asset.name, self.name, self.currency, self.price, self.per
        )
