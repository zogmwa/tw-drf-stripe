from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint

from api.models import Asset


class AssetVote(models.Model):
    # For now we will only have upvotes, no downvotes
    is_upvote = models.BooleanField(
        default=True, help_text='Whether this is an Upvote=true (or Downvote=false)'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='votes',
        on_delete=models.CASCADE,
    )
    voted_on = models.DateTimeField(auto_now_add=True)
    asset = models.ForeignKey(Asset, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return "{}: {}".format(self.asset, self.user)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['asset', 'user'], name='user_asset_vote')
        ]
        verbose_name = 'Web Service Vote'
        verbose_name_plural = 'Web Service Votes'
