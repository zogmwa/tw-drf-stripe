from django.db import models

from api.models import Attribute, Asset


class LinkedAttribute(models.Model):
    """An attribute linked to an asset (supporting the M2M relationship between the attribute and the asset)"""

    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
