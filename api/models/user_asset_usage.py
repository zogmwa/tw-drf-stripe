from django.db import models
from django.db.models import UniqueConstraint

from api.models import User, Asset


class UserAssetUsage(models.Model):
    """A model to track asset usage. Serves as a through model for M2M relation between User >-< Asset"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'asset'],
                name='user_asset_usage',
            )
        ]
