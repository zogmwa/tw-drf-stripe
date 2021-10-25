from django.conf import settings
from django.db import models

from api.models import Asset, Organization


class AssetSolution(models.Model):
    """
    An asset solution can be an integration support/solution, usage support, or some other form solution/support
    related to a web service, which is provided by a specific organization or a user.
    """

    title = models.CharField(max_length=255)
    detailed_description = models.TextField(blank=True, null=True)

    class Type(models.TextChoices):
        INTEGRATION = 'I'
        USAGE_SUPPORT = 'U'

    type = models.CharField(
        max_length=2, choices=Type.choices, default=Type.INTEGRATION
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    # There may or may not be an organization providing this solution (in that case point_of_contact user will be
    # proving the support)
    organization = models.ForeignKey(
        Organization, blank=True, null=True, on_delete=models.SET_NULL
    )

    # The user who will be the point of contact for the customer
    point_of_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name = 'Web Service Solution'
        verbose_name_plural = 'Web Service Solutions'
