from django.db import models
from django.db.models import UniqueConstraint


class Organization(models.Model):
    """
    A Organization could be the owner of multiple assets (only one organization per asset).
    """

    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(max_length=2048, null=True, blank=True)
    logo_url = models.URLField(max_length=2048, null=True, blank=True)

    def __str__(self):
        return self.name


class OrganizationUsingAsset(models.Model):
    """
    An Organization could be using asset. This is a through model to support the M2M relation between Asset and it's
    customer_organizations. Asset >-< Organization. Note that one organization cannot use an asset multiple times.
    """

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "{}: {}".format(self.organization, self.asset)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['organization', 'asset'], name='organization_using_asset'
            )
        ]
